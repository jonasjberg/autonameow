# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
#
#   This file is part of autonameow.
#
#   autonameow is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation.
#
#   autonameow is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with autonameow.  If not, see <http://www.gnu.org/licenses/>.

import logging
import re

from analyzers import BaseAnalyzer
from core import persistence
from core.metadata.canonicalize import canonicalize_language
from core.metadata.canonicalize import canonicalize_publisher
from core.metadata.normalize import cleanup_full_title
from core.metadata.normalize import normalize_full_human_name
from core.metadata.normalize import normalize_full_title
from services import ISBN_METADATA_SERVICE
from util import coercers
from util.misc import flatten_sequence_type
from util.text import find_and_extract_edition
from util.text import html_unescape
from util.text import normalize_horizontal_whitespace
from util.text import normalize_unicode
from util.text import RegexCache
from util.text import remove_blacklisted_lines
from util.text import string_similarity
from util.text import TextChunker
from util.text.distance import longest_common_substring_length
from util.text.humannames import preprocess_names
from vendor import isbnlib


log = logging.getLogger(__name__)


# Known bad or likely incorrect.
BLACKLISTED_ISBN_NUMBERS = [
    '0000000000', '1111111111', '2222222222', '3333333333', '4444444444',
    '5555555555', '6666666666', '7777777777', '8888888888', '9999999999',
    '0123456789', '1101111100', '0111111110', '0111111110', '0000110000',
    '1101100001',
    '9780000000002',  # Title: "De Plattduitsche Baibel: et Aule Testament: ne Psalmeniutwahl"
]

BLACKLISTED_TEXTLINES = frozenset([
    'This page intentionally left blank',
    'Cover'
])


CACHE_KEY_ISBNMETA = 'isbnlib_meta'
CACHE_KEY_ISBNBLACKLIST = 'isbnlib_blacklist'


class EbookAnalyzer(BaseAnalyzer):
    RUN_QUEUE_PRIORITY = 0.5
    HANDLES_MIME_TYPES = ['application/pdf', 'application/epub+zip',
                          'image/vnd.djvu']
    FIELD_LOOKUP = {
        'author': {
            'coercer': 'aw_string',
            'multivalued': 'true',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Author', 'weight': '1'}},
            ],
            'generic_field': 'author'
        },
        'date': {
            'coercer': 'aw_date',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Date', 'weight': '1'}},
                {'WeightedMapping': {'field': 'DateTime', 'weight': '1'}},
            ],
            'generic_field': 'date_created'
        },
        'edition': {
            'coercer': 'aw_integer',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Edition', 'weight': '1'}},
            ],
            'generic_field': 'edition'
        },
        'language': {
            'coercer': 'aw_string',
            'multivalued': 'false',
            'generic_field': 'language'
        },
        'publisher': {
            'coercer': 'aw_string',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Publisher', 'weight': '1'}},
            ],
            'generic_field': 'publisher'
        },
        'title': {
            'coercer': 'aw_string',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Title', 'weight': '1'}},
            ],
            'generic_field': 'title'
        },
    }

    # TODO: [TD0157] Look into analyzers 'FIELD_LOOKUP' attributes.

    def __init__(self, fileobject, config, request_data_callback):
        super().__init__(fileobject, config, request_data_callback)

        self.text = None
        self._isbn_metadata = list()

        self._cached_isbn_metadata = dict()
        self._isbn_num_blacklist = set(BLACKLISTED_ISBN_NUMBERS)

        # NOTE(jonas): Tweak max cache file size. Now 50MB.
        self.cache = persistence.get_cache(str(self), max_filesize=50*10**6)
        if self.cache:
            _cached_isbn_metadata = self.cache.get(CACHE_KEY_ISBNMETA)
            if _cached_isbn_metadata:
                self._cached_isbn_metadata = _cached_isbn_metadata
                self.log.debug('Read %s cached ISBN metadata entries',
                               len(_cached_isbn_metadata))

            _blacklisted_isbn_numbers = self.cache.get(CACHE_KEY_ISBNBLACKLIST)
            if _blacklisted_isbn_numbers:
                self.log.debug('Read %d blacklisted ISBN numbers from cache',
                               len(_blacklisted_isbn_numbers))
                self._isbn_num_blacklist.update(_blacklisted_isbn_numbers)

            self.log.debug('Blacklisted %d ISBN numbers in total',
                           len(self._isbn_num_blacklist))

    def analyze(self):
        _maybe_text = self.request_any_textual_content()
        if not _maybe_text:
            return

        self.text = remove_blacklisted_lines(_maybe_text, BLACKLISTED_TEXTLINES)

        isbn_numbers = self._extract_isbn_numbers_from_text()
        self.log.debug('Extracted %d ISBN numbers from text',
                       len(isbn_numbers))
        if not isbn_numbers:
            isbn_numbers = self._extract_isbn_numbers_from_metadata()
            self.log.debug('Extracted %d ISBN numbers from metadata',
                           len(isbn_numbers))

        if not isbn_numbers:
            return

        isbn_numbers = deduplicate_isbns(isbn_numbers)
        isbn_numbers = filter_isbns(isbn_numbers, self._isbn_num_blacklist)
        self.log.debug('Prepared %d ISBN numbers', len(isbn_numbers))

        # Sort the dictionaries for more deterministic behaviour.
        # TODO: [hack] Sorting is reversed so that earlier releases, as in
        #       lower values in the 'year' field, are processed first.
        #       This applies only when all other fields are identical.
        # TODO: [hack] Fix failing regression test 9017 properly!
        for isbn_number in sorted(isbn_numbers, reverse=True):
            self.log.debug('Processing ISBN: %s', isbn_number)

            metadata_dict = self._get_isbn_metadata(isbn_number)
            if not metadata_dict:
                self.log.warning('Unable to get metadata for ISBN: "%s"',
                                 isbn_number)

                # TODO: [TD0132] Improve blacklisting failed requests..
                # TODO: [TD0132] Prevent hammering APIs with bad request.
                self.log.debug('Blacklisting ISBN: "%s"', isbn_number)
                self._isbn_num_blacklist.add(isbn_number)
                if self.cache:
                    self.cache.set(CACHE_KEY_ISBNBLACKLIST,
                                   self._isbn_num_blacklist)
                continue

            authors = metadata_dict.get('Authors')
            language = metadata_dict.get('Language')
            publisher = metadata_dict.get('Publisher')
            isbn10 = metadata_dict.get('ISBN-10')
            isbn13 = metadata_dict.get('ISBN-13')
            title = metadata_dict.get('Title')
            year = metadata_dict.get('Year')

            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('ISBN metadata dict for ISBN %s:', isbn_number)
                str_metadata_dict = '''Title     : {!s}
Authors   : {!s}
Publisher : {!s}
Year      : {!s}
Language  : {!s}
ISBN-10   : {!s}
ISBN-13   : {!s}'''.format(title, authors, publisher, year, language, isbn10, isbn13)
                for line in str_metadata_dict.splitlines():
                    self.log.debug('metadata_dict ' + line)

            metadata = ISBNMetadata(authors, language, publisher,
                                    isbn10, isbn13, title, year)

            if self.log.isEnabledFor(logging.DEBUG):
                self.log.debug('ISBNMetadata object for ISBN %s', isbn_number)
                for line in metadata.as_string().splitlines():
                    self.log.debug('ISBNMetadata ' + line)

            # Duplicates are removed here.
            if metadata not in self._isbn_metadata:
                self.log.debug('Added metadata for ISBN: %s', isbn_number)
                self._isbn_metadata.append(metadata)
            else:
                # TODO: [TD0190] Join/merge metadata "records" with missing values.
                # TODO: If the ISBN metadata record that is considered duplicate
                #       contains a field value that is missing/empty in the kept
                #       metadata record, copy it to the kept record before
                #       discarding the "duplicate" record.

                self.log.debug('Skipped metadata for ISBN %s considered duplicate',
                               isbn_number)
                # print('Skipped metadata considered a duplicate:')
                # print_copy_pasteable_isbn_metadata('x', metadata)
                # print('Previously Stored metadata:')
                # for n, m in enumerate(self._isbn_metadata):
                #     print_copy_pasteable_isbn_metadata(n, m)

        self.log.debug('Got %d instances of ISBN metadata',
                       len(self._isbn_metadata))
        for n, metadata in enumerate(self._isbn_metadata):
            for line in metadata.as_string().splitlines():
                self.log.debug('ISBNMetadata %d :: %s', n, line)

        if len(self._isbn_metadata) > 1:
            # TODO: [TD0187] Fix clobbering of results
            self.log.debug('Attempting to find most probable ISBN metadata..')
            most_probable_isbn_metadata = self._find_most_probable_isbn_metadata()
            if most_probable_isbn_metadata:
                self._add_intermediate_results_from_metadata([most_probable_isbn_metadata])
        else:
            self._add_intermediate_results_from_metadata(self._isbn_metadata)

    def _add_intermediate_results_from_metadata(self, isbn_metadata):
        for n, metadata in enumerate(isbn_metadata):
            for line in metadata.as_string().splitlines():
                self.log.debug('ISBNMetadata %d :: %s', n, line)

            # TODO: [hack][incomplete] Arbitrary removal of metadata records ..
            # TODO: [TD0190] Join/merge metadata "records" with missing values.
            if not metadata.authors and not metadata.publisher:
                self.log.debug('Skipped ISBN metadata missing both '
                               'authors and publisher')
                continue

            # TODO: [TD0191] Detect and extract subtitles from titles.
            maybe_title = cleanup_full_title(metadata.title)
            self._add_intermediate_results('title', maybe_title)

            maybe_authors = metadata.authors
            if maybe_authors:
                self._add_intermediate_results('author', maybe_authors)

            maybe_publisher = self._filter_publisher(metadata.publisher)
            self._add_intermediate_results('publisher', maybe_publisher)

            maybe_date = self._filter_date(metadata.year)
            self._add_intermediate_results('date', maybe_date)

            maybe_edition = self._filter_edition(metadata.edition)
            self._add_intermediate_results('edition', maybe_edition)

            maybe_language = metadata.language
            if maybe_language:
                self._add_intermediate_results('language', maybe_language)

    def _find_most_probable_isbn_metadata(self):
        # TODO: [TD0185] Rework access to 'master_provider' functionality.
        def _untangle_response(_response):
            if not response:
                return None

            if isinstance(_response, str):
                return _response

            if isinstance(_response, bytes):
                _str_response = coercers.force_string(_response)
                if _str_response:
                    return _str_response

            # TODO: [TD0175] Handle requesting exactly one or multiple alternatives.
            if isinstance(_response, list):
                unique_string_values = set(
                    filter(None, [coercers.force_string(v) for v in _response])
                )
                if len(unique_string_values) == 1:
                    return unique_string_values.pop()

            self.log.debug('Unable to untangle response (%s) %r',
                           type(_response), _response)
            return None

        # TODO: [TD0187] Fix clobbering of results.
        # TODO: [TD0185] Rework access to 'master_provider' functionality.
        response = self.request_data(self.fileobject, 'generic.metadata.description')
        ok_response = _untangle_response(response)
        if not ok_response:
            self.log.debug('Reference metadata title "generic.metadata.description" unavailable.')

            # TODO: [TD0175] Handle requesting exactly one or multiple alternatives.
            # TODO: [TD0185] Rework access to 'master_provider' functionality.
            response = self.request_data(self.fileobject, 'generic.metadata.title')
            ok_response = _untangle_response(response)
            if not ok_response:
                self.log.debug('Reference metadata title "generic.metadata.title" unavailable. Unable to find most probable ISBN metadata..')
                return None

        # TODO: [TD0192] Detect and extract editions from titles
        # TODO: The reference title might be 'Meow for All (4th, 2018)'
        # TODO: Detect and extract other contained fields in the reference.
        #       .. Better yet; pull it from a source that already did it!
        _, ref_title = find_and_extract_edition(ok_response)
        reference_title = normalize_full_title(ref_title)
        self.log.debug('Using reference metadata title "%s"', reference_title)

        candidates = list()
        for metadata in self._isbn_metadata:
            metadata_title = metadata.normalized_title
            if not metadata_title:
                self.log.debug('Skipped ISBN metadata with missing or empty normalized title')
                continue

            title_similarity = calculate_title_similarity(metadata_title, reference_title)
            candidates.append((title_similarity, metadata))

        if candidates:
            sorted_candidates = sorted(candidates, key=lambda x: x[0], reverse=True)

            if self.log.getEffectiveLevel() == logging.DEBUG:
                for n, scored_candidate in enumerate(sorted_candidates, start=1):
                    score, candidate = scored_candidate
                    self.log.debug(
                        'Candidate (%d/%d) Score %.6f  Title "%s"',
                        n, len(sorted_candidates), score, candidate.normalized_title
                    )

            # Return first metadata from list of (title_similarity, metadata) tuples
            most_probable = sorted_candidates[0][1]
            self.log.debug('Using most probable metadata with title "%s"', most_probable.title)
            return most_probable

        return None

    def _extract_isbn_numbers_from_text(self):
        # NOTE(jonas): Works under the assumption that relevant ISBN-numbers
        #              are more likely found either at the beginning or the
        #              end of the text, NOT somewhere in the middle.
        #
        # First try to find "e-book ISBNs" in the beginning, then at the end.
        # Then try to find _any_ ISBNs in the beginning, then at the end.

        # Search the text in arbitrarily sized chunks.
        if is_epub_ebook(self.fileobject):
            # Use bigger chunks for epub text in order to catch ISBNs.
            CHUNK_PERCENTAGE = 0.05
        else:
            CHUNK_PERCENTAGE = 0.025

        text_chunks = TextChunker(self.text, CHUNK_PERCENTAGE)
        leading_text = text_chunks.leading
        leading_text_linecount = len(leading_text.splitlines())

        self.log.debug('Searching leading %d text lines for eISBNs', leading_text_linecount)
        isbn_numbers = extract_ebook_isbns_from_text(leading_text)

        if not isbn_numbers:
            trailing_text = text_chunks.trailing
            trailing_text_linecount = len(trailing_text.splitlines())
            self.log.debug('Searching trailing %d text lines for eISBNs', trailing_text_linecount)
            isbn_numbers = extract_ebook_isbns_from_text(trailing_text)

            if not isbn_numbers:
                self.log.debug('Searching leading %d text lines for *any* ISBNs', leading_text_linecount)
                isbn_numbers = extract_isbnlike_from_text(leading_text)

                if not isbn_numbers:
                    self.log.debug('Searching trailing %d text lines for *any* ISBNs', trailing_text_linecount)
                    isbn_numbers = extract_isbnlike_from_text(trailing_text)

        return isbn_numbers

    def _extract_isbn_numbers_from_metadata(self):
        data = self.request_data(self.fileobject, 'generic.metadata.identifier')
        self.log.debug('Got "generic.metadata.identifier" data "%s"', data)

        found_isbn_numbers = list()

        if data:
            # Values could be a list of lists because of how "generic" are
            # collected and returned from the repository.
            values = flatten_sequence_type(data)

            for value in values:
                value = value.lower()
                if value.startswith('urn:') or value.startswith('isbn'):
                    identifier = value
                    isbn_numbers = extract_isbnlike_from_text(identifier)
                    if isbn_numbers:
                        found_isbn_numbers.extend(isbn_numbers)

        return found_isbn_numbers

    def _get_isbn_metadata(self, isbn_number):
        if isbn_number in self._cached_isbn_metadata:
            self.log.debug('Using cached metadata for ISBN: %s', isbn_number)
            return self._cached_isbn_metadata.get(isbn_number)

        self.log.debug('Querying external service for ISBN: %s', isbn_number)
        metadata = ISBN_METADATA_SERVICE.query(isbn_number)
        if metadata:
            self.log.debug('Caching metadata for ISBN: %s', isbn_number)
            self._cached_isbn_metadata.update({isbn_number: metadata})
            if self.cache:
                self.cache.set(CACHE_KEY_ISBNMETA, self._cached_isbn_metadata)

        return metadata

    def _filter_date(self, raw_string):
        # TODO: [TD0034] Filter out known bad data.
        # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
        # TODO: Cleanup and filter date/year
        try:
            return coercers.AW_DATE(raw_string)
        except coercers.AWTypeError:
            return None

    def _filter_publisher(self, raw_string):
        # TODO: [TD0034] Filter out known bad data.
        # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
        try:
            string_ = coercers.AW_STRING(raw_string)
        except coercers.AWTypeError:
            return None
        else:
            if not string_.strip():
                return None

            # TODO: Cleanup and filter publisher(s)
            return string_

    def _filter_edition(self, raw_string):
        # TODO: [TD0034] Filter out known bad data.
        # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
        try:
            int_ = coercers.AW_INTEGER(raw_string)
        except coercers.AWTypeError:
            return None
        else:
            return int_ if int_ != 0 else None

    @classmethod
    def can_handle(cls, fileobject):
        return bool(
            cls._evaluate_mime_type_glob(fileobject)
            or fileobject.mime_type == 'application/octet-stream'
            and fileobject.basename_suffix in (b'mobi', b'azw', b'azw3', b'azw4')
        )

    @classmethod
    def dependencies_satisfied(cls):
        return bool(ISBN_METADATA_SERVICE.available)


def extract_ebook_isbns_from_text(text):
    regex_e_isbn = RegexCache(r'(^e-ISBN.*|^ISBN.*electronic.*)',
                              flags=re.MULTILINE)
    match = regex_e_isbn.search(text)
    if match:
        return extract_isbnlike_from_text(match.group(0))

    return list()


def validate_isbn(possible_isbn):
    if not possible_isbn:
        return None

    isbn_number = isbnlib.clean(possible_isbn)
    if not isbn_number or isbnlib.notisbn(isbn_number):
        return None

    return isbn_number


def extract_isbnlike_from_text(text):
    assert isinstance(text, str)

    possible_isbns = isbnlib.get_isbnlike(text)
    if possible_isbns:
        return [
            isbnlib.get_canonical_isbn(i) for i in possible_isbns
            if validate_isbn(i)
        ]

    return list()


def deduplicate_isbns(isbn_list):
    """
    De-duplicate a list of ISBN numbers.

    NOTE: Any ISBN-10 numbers will be converted to ISBN-13.
    """
    # TODO: [hack] This conversion to ISBN-13 is way too non-obvious..
    # TODO: [cleanup] Fix "principle of least astonishment" violation!
    deduplicated_isbns = set()

    for number in isbn_list:
        if isbnlib.is_isbn10(number):
            isbn13 = isbnlib.to_isbn13(number)
            deduplicated_isbns.add(isbn13)
        else:
            deduplicated_isbns.add(number)

    return list(deduplicated_isbns)


def filter_isbns(isbn_list, isbn_blacklist):
    # TODO: [TD0034] Filter out known bad data.
    # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
    # Remove known "bad" ISBN numbers.
    return [n for n in isbn_list if n and n not in isbn_blacklist]


class ISBNMetadata(object):
    NORMALIZED_YEAR_UNKNOWN = 1337
    UNKNOWN_PUBLISHER = 'UNKNOWN'

    def __init__(self, authors=None, language=None, publisher=None,
                 isbn10=None, isbn13=None, title=None, year=None, edition=None):
        self._authors = None
        self._language = None
        self._publisher = None
        self._isbn10 = None
        self._isbn13 = None
        self._title = None
        self._year = None
        self._edition = None

        # Used when comparing class instances.
        self._normalized_authors = list()
        self._normalized_language = None
        self._normalized_publisher = None
        self._normalized_title = None
        self._normalized_year = None
        self._normalized_edition = None

        self.authors = authors
        self.language = language
        self.publisher = publisher
        self.isbn10 = isbn10
        self.isbn13 = isbn13
        self.title = title
        self.year = year
        self.edition = edition

    @property
    def authors(self):
        return self._authors or []

    @authors.setter
    def authors(self, value):
        if not value:
            return

        values = value
        if not isinstance(values, list):
            values = [values]

        # TODO: [TD0112] Add some sort of system for normalizing entities.
        # TODO: It is not uncommon that the publisher is listed as an author..
        preprocessed_author_list = preprocess_names(values)

        self._log_attribute_setter('author', preprocessed_author_list, values)
        self._authors = preprocessed_author_list

        # TODO: Do "real" human name parsing here instead.
        #       For improved author comparisons and reduced duplicate code.
        self._normalized_authors = [
            normalize_full_human_name(a) for a in preprocessed_author_list if a
        ]

    @property
    def normalized_authors(self):
        return self._normalized_authors or []

    @property
    def edition(self):
        return self._edition or '0'

    @edition.setter
    def edition(self, value):
        if value and isinstance(value, str):
            self._edition = value
            self._normalized_edition = value.lower().strip()

    @property
    def normalized_edition(self):
        return self._normalized_edition or 0

    @property
    def isbn10(self):
        if self._isbn10:
            return self._isbn10
        elif self._isbn13:
            return isbnlib.to_isbn10(self._isbn13)
        return ''

    @isbn10.setter
    def isbn10(self, value):
        if value and isinstance(value, str):
            if isbnlib.is_isbn10(value):
                self._isbn10 = value

    @property
    def isbn13(self):
        if self._isbn13:
            return self._isbn13
        elif self._isbn10:
            return isbnlib.to_isbn13(self._isbn10)
        return ''

    @isbn13.setter
    def isbn13(self, value):
        if value and isinstance(value, str):
            if isbnlib.is_isbn13(value):
                self._isbn13 = value

    @property
    def language(self):
        return self._language or ''

    @language.setter
    def language(self, value):
        if value and isinstance(value, str):
            str_value = normalize_horizontal_whitespace(value).strip()
            canonical_language = canonicalize_language(str_value)
            self._language = canonical_language
            self._normalized_language = canonical_language.lower()

    @property
    def normalized_language(self):
        return self._normalized_language or ''

    @property
    def publisher(self):
        return self._publisher or self.UNKNOWN_PUBLISHER

    @publisher.setter
    def publisher(self, value):
        if value and isinstance(value, str):
            str_value = normalize_unicode(html_unescape(value))
            str_value = normalize_horizontal_whitespace(str_value).strip()
            canonical_publisher = canonicalize_publisher(str_value)
            self._publisher = canonical_publisher
            self._normalized_publisher = canonical_publisher.lower()

    @property
    def normalized_publisher(self):
        return self._normalized_publisher or self.UNKNOWN_PUBLISHER

    @property
    def year(self):
        return self._year or ''

    @year.setter
    def year(self, value):
        if value and isinstance(value, str):
            self._year = value
            try:
                self._normalized_year = coercers.AW_INTEGER(value)
            except coercers.AWTypeError:
                self._normalized_year = self.NORMALIZED_YEAR_UNKNOWN

    @property
    def normalized_year(self):
        return self._normalized_year or self.NORMALIZED_YEAR_UNKNOWN

    @property
    def title(self):
        return self._title or ''

    @title.setter
    def title(self, value):
        if value and isinstance(value, str):
            # TODO: [TD0191] Detect and extract subtitles from titles.
            # TODO: [TD0192] Detect and extract editions from titles
            edition, modified_value = find_and_extract_edition(value)
            if edition:
                self.edition = edition
                self._title = modified_value.strip()
                self._normalized_title = normalize_full_title(modified_value)
            else:
                self._title = value
                self._normalized_title = normalize_full_title(value)

            self._log_attribute_setter('title', self._title, value)

    @property
    def normalized_title(self):
        return self._normalized_title or ''

    def as_string(self):
        return '''Title     : {}
Authors   : {}
Publisher : {}
Year      : {}
Language  : {}
ISBN-10   : {}
ISBN-13   : {}'''.format(self.title, self.authors, self.publisher, self.year,
                         self.language, self.isbn10, self.isbn13)

    def similarity(self, other):
        """
        Fuzzy comparison with ad-hoc threshold values.
        """
        UNLIKELY_YEAR_DIFF = 42
        FIELDS_MISSING_SIMILARITY = 0.001

        if self.normalized_title and other.normalized_title:
            _sim_title = calculate_title_similarity(self.normalized_title,
                                                    other.normalized_title)
        else:
            _sim_title = FIELDS_MISSING_SIMILARITY

        if (self.normalized_year == self.NORMALIZED_YEAR_UNKNOWN and
                other.normalized_year == self.NORMALIZED_YEAR_UNKNOWN):
            _year_diff = UNLIKELY_YEAR_DIFF
        else:
            _year_diff = int(abs(self.normalized_year - other.normalized_year))

        if not self.normalized_authors or not other.normalized_authors:
            _sim_authors = FIELDS_MISSING_SIMILARITY
        else:
            _sim_authors = calculate_authors_similarity(
                self.normalized_authors,
                other.normalized_authors
            )

        if self.normalized_publisher and other.normalized_publisher:
            _sim_publisher = string_similarity(self.normalized_publisher,
                                               other.normalized_publisher)
        else:
            _sim_publisher = FIELDS_MISSING_SIMILARITY

        # TODO: [TD0181] Use machine learning in ISBN metadata de-duplication.
        # TODO: Arbitrary threshold values..
        # TODO: [TD0181] Replace this with decision tree classifier.
        log.debug('Comparing %s to %s ..', self, other)
        log.debug('     Difference Year: %d', _year_diff)
        log.debug('  Similarity Authors: %.3f  (%s -- %s)', _sim_authors, self.normalized_authors, other.normalized_authors)
        log.debug('Similarity Publisher: %.3f  (%s -- %s)', _sim_publisher, self.normalized_publisher, other.normalized_publisher)
        log.debug('    Similarity Title: %.3f  (%s -- %s)', _sim_title, self.normalized_title, other.normalized_title)

        if _year_diff == 0:
            if _sim_title > 0.95:
                if _sim_publisher > 0.5:
                    if _sim_authors > 0.2:
                        return True
                elif _sim_publisher > 0.2:
                    if _sim_authors > 0.4:
                        return True
                else:
                    if _sim_authors > 0.9:
                        return True
        if _year_diff == 1:
            if _sim_authors > 0.7:
                if _sim_title > 0.9:
                    return True
            elif _sim_authors > 0.5:
                if _sim_publisher > 0.9 and _sim_title > 0.8:
                    return True
            elif _sim_authors > 0.25:
                if _sim_title >= 0.99:
                    return True
        if _year_diff > 1:
            if _sim_authors > 0.9:
                if _sim_publisher > 0.8 and _sim_title > 0.8:
                    return True
            elif _sim_authors > 0.7:
                if _sim_title > 0.9:
                    return True
                if _sim_publisher > 0.9:
                    return True
            elif _sim_authors > 0.2:
                if _sim_title > 0.9:
                    return True

        return False

    def _log_attribute_setter(self, attribute, raw_value, value):
        log.debug('%s attribute %s set (value :: raw) %s :: %s',
                  self.__class__.__name__, attribute, value, raw_value)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.isbn10 == other.isbn10:
            return True
        if self.isbn13 == other.isbn13:
            return True

        return self.similarity(other)

    def __hash__(self):
        return hash((self.isbn10, self.isbn13))

    def __repr__(self):
        return '<{!s}(isbn10={!s}), isbn13={!s})>'.format(
            self.__class__.__name__, self.isbn10, self.isbn13
        )


def print_copy_pasteable_isbn_metadata(n, m):
    print('''
m{} = ISBNMetadata(
    authors={},
    language='{}',
    publisher='{}',
    isbn10='{}',
    isbn13='{}',
    title='{}',
    year='{}'
)'''.format(n, m.authors, m.language, m.publisher, m.isbn10, m.isbn13, m.title, m.year))


def is_epub_ebook(fileobject):
    return fileobject.mime_type == 'application/epub+zip'


def calculate_authors_similarity(authors_a, authors_b):
    def _sort_substrings(_strngs):
        return [' '.join(sorted(s.split(' '))) for s in _strngs]

    def _preprocess(_strngs):
        return _sort_substrings([s.lower() for s in _strngs])

    preprocessed_authors_a = _preprocess(authors_a)
    preprocessed_authors_b = _preprocess(authors_b)
    sorted_authors_a = sorted(preprocessed_authors_a)
    sorted_authors_b = sorted(preprocessed_authors_b)

    # Because 'zip' stops when the shortest iterable is exhausted.
    num_string_similarities_averaged = min(len(authors_a), len(authors_b))

    similarity = float(
        sum(
            string_similarity(a, b)
            for a, b in zip(sorted_authors_a, sorted_authors_b)
        ) / num_string_similarities_averaged
    )
    return similarity


def calculate_title_similarity(title_a, title_b):
    # NOTE(jonas): Titles passed in here should have been suitably
    #              "pre-processed" (lowercased, etc.)

    # Chop to equal length to work around very long titles with a lot of words
    # that might be mistakingly considered similar to a lot of unrelated titles
    # due to the fact that many word and/or substrings might match even though
    # the titles are very different.
    shortest_title_length = min(len(title_a), len(title_b))
    a = title_a[:shortest_title_length]
    b = title_b[:shortest_title_length]
    substring_bonus = longest_common_substring_length(a, b) / shortest_title_length
    return string_similarity(a, b) * substring_bonus
