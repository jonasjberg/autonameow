# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
#   Personal site:   http://www.jonasjberg.com
#   GitHub:          https://github.com/jonasjberg
#   University mail: js224eh[a]student.lnu.se
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

# TODO: [TD0182] Isolate third-party metadata services like 'isbnlib'.
try:
    import isbnlib
except ImportError:
    isbnlib = None

from analyzers import BaseAnalyzer
from core import persistence
from core.metadata.normalize import (
    cleanup_full_title,
    normalize_full_human_name,
    normalize_full_title,
)
from services.isbn import (
    extract_isbnlike_from_text,
    fetch_isbn_metadata,
)
from util import coercers
from util.text import (
    find_and_extract_edition,
    html_unescape,
    normalize_unicode,
    RegexCache,
    remove_blacklisted_lines,
    string_similarity,
    TextChunker
)
from util.text.humannames import (
    filter_multiple_names,
    split_multiple_names
)


log = logging.getLogger(__name__)


# Known bad or likely incorrect.
BLACKLISTED_ISBN_NUMBERS = [
    '0000000000', '1111111111', '2222222222', '3333333333', '4444444444',
    '5555555555', '6666666666', '7777777777', '8888888888', '9999999999',
    '0123456789', '1101111100', '0111111110', '0111111110', '0000110000',
    '1101100001'
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

            _blacklisted_isbn_numbers = self.cache.get(CACHE_KEY_ISBNBLACKLIST)
            if _blacklisted_isbn_numbers:
                self.log.debug('Read {} blacklisted ISBN numbers from cache'.format(
                    len(_blacklisted_isbn_numbers)
                ))
                self._isbn_num_blacklist.update(_blacklisted_isbn_numbers)
            self.log.debug('Blacklisted {!s} ISBN numbers in total'.format(
                len(self._isbn_num_blacklist)
            ))

    def analyze(self):
        _maybe_text = self.request_any_textual_content()
        if not _maybe_text:
            return

        self.text = remove_blacklisted_lines(_maybe_text, BLACKLISTED_TEXTLINES)

        # TODO: [TD0114] Check metadata for ISBNs.
        # Exiftool fields: 'PDF:Keywords', 'XMP:Identifier', "XMP:Subject"
        isbn_numbers = self._extract_isbn_numbers_from_text()
        self.log.debug('Extracted {} ISBN numbers'.format(len(isbn_numbers)))
        if isbn_numbers:
            isbn_numbers = deduplicate_isbns(isbn_numbers)
            isbn_numbers = filter_isbns(isbn_numbers, self._isbn_num_blacklist)
            self.log.debug('Prepared {} ISBN numbers'.format(len(isbn_numbers)))

            for isbn_number in isbn_numbers:
                self.log.debug('Processing ISBN: {!s}'.format(isbn_number))

                metadata_dict = self._get_isbn_metadata(isbn_number)
                if not metadata_dict:
                    self.log.warning(
                        'Unable to get metadata for ISBN: "{}"'.format(isbn_number)
                    )

                    # TODO: [TD0132] Improve blacklisting failed requests..
                    # TODO: [TD0132] Prevent hammering APIs with bad request.
                    self.log.debug('Blacklisting ISBN: "{}"'.format(isbn_number))
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
                self.log.debug('ISBN metadata dict for ISBN {}:'.format(isbn_number))
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
                self.log.debug('ISBNMetadata object for ISBN {}'.format(isbn_number))
                for line in metadata.as_string().splitlines():
                    self.log.debug('ISBNMetadata ' + line)

                # Duplicates are removed here. When both ISBN-10 and ISBN-13
                # text is found and two queries are made, the two metadata
                # results are "joined" when being added to this set.
                if metadata not in self._isbn_metadata:
                    self.log.debug('Added metadata for ISBN: {}'.format(isbn_number))
                    self._isbn_metadata.append(metadata)
                else:
                    # TODO: [TD0190] Join/merge metadata "records" with missing values.
                    # TODO: If the ISBN metadata record that is considered duplicate
                    #       contains a field value that is missing/empty in the kept
                    #       metadata record, copy it to the kept record before
                    #       discarding the "duplicate" record.

                    self.log.debug('Metadata for ISBN {} considered duplicate and skipped'.format(isbn_number))
                    # print('Skipped metadata considered a duplicate:')
                    # print_copy_pasteable_isbn_metadata('x', metadata)
                    # print('Previously Stored metadata:')
                    # for n, m in enumerate(self._isbn_metadata):
                    #     print_copy_pasteable_isbn_metadata(n, m)

            self.log.info('Got {} instances of ISBN metadata'.format(
                len(self._isbn_metadata)
            ))
            for n, metadata in enumerate(self._isbn_metadata):
                for line in metadata.as_string().splitlines():
                    self.log.debug('ISBNMetadata {} :: {!s}'.format(n, line))

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
                self.log.debug('ISBNMetadata {} :: {!s}'.format(n, line))

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
            self._add_intermediate_results('author', maybe_authors)

            maybe_publisher = self._filter_publisher(metadata.publisher)
            self._add_intermediate_results('publisher', maybe_publisher)

            maybe_date = self._filter_date(metadata.year)
            self._add_intermediate_results('date', maybe_date)

            maybe_edition = self._filter_edition(metadata.edition)
            self._add_intermediate_results('edition', maybe_edition)

    def _find_most_probable_isbn_metadata(self):
        # TODO: [TD0187] Fix clobbering of results.
        # TODO: [TD0114] Improve the EbookAnalyzer.
        # TODO: [TD0175] Handle requesting exactly one or multiple alternatives.
        # TODO: [TD0185] Rework access to 'master_provider' functionality.
        response = self.request_data(self.fileobject, 'generic.metadata.description')
        if not response or not isinstance(response, str):
            self.log.debug('Reference metadata title "generic.metadata.description" unavailable.')

            # TODO: [TD0175] Handle requesting exactly one or multiple alternatives.
            # TODO: [TD0185] Rework access to 'master_provider' functionality.
            response = self.request_data(self.fileobject, 'generic.metadata.title')
            if not response or not isinstance(response, str):
                self.log.debug('Reference metadata title "generic.metadata.title" unavailable. Unable to find most probable ISBN metadata..')
                return None

        # TODO: [TD0192] Detect and extract editions from titles
        _, ref_title = find_and_extract_edition(response)
        reference_title = normalize_full_title(ref_title)
        self.log.debug('Using reference metadata title "{!s}"'.format(reference_title))
        # response = self.request_data(self.fileobject, 'generic.contents.text')

        candidates = list()
        for metadata in self._isbn_metadata:
            metadata_title = metadata.normalized_title
            if not metadata_title:
                self.log.debug('Skipped ISBN metadata with missing or empty normalized title')
                continue

            title_similarity = string_similarity(metadata_title, reference_title)
            self.log.debug('Metadata/reference title similarity {} ("{!s}"/"{!s}")'.format(title_similarity, metadata_title, reference_title))
            candidates.append((title_similarity, metadata))

        if candidates:
            sorted_candidates = sorted(candidates, key=lambda x: x[0], reverse=True)
            # Return first metadata from list of (title_similarity, metadata) tuples
            most_probable = sorted_candidates[0][1]
            self.log.debug('Most probable metadata has title "{!s}"'.format(most_probable.title))
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
            CHUNK_PERCENTAGE = 0.05

        text_chunks = TextChunker(self.text, CHUNK_PERCENTAGE)
        leading_text = text_chunks.leading
        leading_text_linecount = len(leading_text.splitlines())

        self.log.debug('Searching leading {} text lines for eISBNs'.format(leading_text_linecount))
        isbn_numbers = extract_ebook_isbns_from_text(leading_text)

        if not isbn_numbers:
            trailing_text = text_chunks.trailing
            trailing_text_linecount = len(trailing_text.splitlines())
            self.log.debug('Searching trailing {} text lines for eISBNs'.format(trailing_text_linecount))
            isbn_numbers = extract_ebook_isbns_from_text(trailing_text)

            if not isbn_numbers:
                self.log.debug('Searching leading {} text lines for *any* ISBNs'.format(leading_text_linecount))
                isbn_numbers = extract_isbns_from_text(leading_text)

                if not isbn_numbers:
                    self.log.debug('Searching trailing {} text lines for *any* ISBNs'.format(trailing_text_linecount))
                    isbn_numbers = extract_isbns_from_text(trailing_text)

        return isbn_numbers

    def _get_isbn_metadata(self, isbn_number):
        if isbn_number in self._cached_isbn_metadata:
            self.log.info(
                'Using cached metadata for ISBN: {!s}'.format(isbn_number)
            )
            return self._cached_isbn_metadata.get(isbn_number)

        self.log.debug('Querying external service for ISBN: {!s}'.format(isbn_number))
        metadata = fetch_isbn_metadata(isbn_number)
        if metadata:
            self.log.info(
                'Caching metadata for ISBN: {!s}'.format(isbn_number)
            )

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
        mime_type_ok = cls._evaluate_mime_type_glob(fileobject)
        if (mime_type_ok
                or fileobject.basename_suffix == b'mobi'
                and fileobject.mime_type == 'application/octet-stream'):
            return True
        return False

    @classmethod
    def dependencies_satisfied(cls):
        return isbnlib is not None


def extract_ebook_isbns_from_text(text):
    regex_e_isbn = RegexCache(r'(^e-ISBN.*|^ISBN.*electronic.*)',
                              flags=re.MULTILINE)
    match = regex_e_isbn.search(text)
    if match:
        return extract_isbns_from_text(match.group(0))
    return list()


def extract_isbns_from_text(text):
    possible_isbns = extract_isbnlike_from_text(text)
    if possible_isbns:
        return possible_isbns
    return list()


def deduplicate_isbns(isbn_list):
    return list(set(isbn_list))


def filter_isbns(isbn_list, isbn_blacklist):
    # TODO: [TD0034] Filter out known bad data.
    # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
    # Remove known "bad" ISBN numbers.
    return [n for n in isbn_list if n and n not in isbn_blacklist]


class ISBNMetadata(object):
    NORMALIZED_YEAR_UNKNOWN = 1337

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
        if not isinstance(value, list):
            values = [values]

        # TODO: [TD0112] Add some sort of system for normalizing entities.
        # TODO: It is not uncommon that the publisher is listed as an author..
        # Fix any malformed entries.
        # Handle this like ['David Astolfo ... Technical reviewers: Mario Ferrari ...']
        _author_list = list()
        for author in values:
            # Handle strings like 'Foo Bar [and Gibson Meow]'
            if re.match(r'.*\[.*\].*', author):
                _splits = author.split('[')
                _cleaned_splits = [
                    re.sub(r'[\[\]]', '', s)
                    for s in _splits
                ]
                _cleaned_splits = [
                    re.sub(r'^and ', '', s)
                    for s in _cleaned_splits
                ]
                _cleaned_splits = [
                    re.sub(r'^[Ww]ritten by ', '', s)
                    for s in _cleaned_splits
                ]
                _author_list.extend(_cleaned_splits)
            else:
                _author_list.append(author)

        stripped_author_list = [a.strip() for a in _author_list if a]
        fixed_author_list = split_multiple_names(stripped_author_list)
        filtered_author_list = filter_multiple_names(fixed_author_list)

        self._log_attribute_setter('author', filtered_author_list, values)
        self._authors = filtered_author_list
        self._normalized_authors = [
            normalize_full_human_name(a) for a in filtered_author_list if a
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
            self._language = value
            self._normalized_language = value.lower().strip()

    @property
    def normalized_language(self):
        return self._normalized_language or ''

    @property
    def publisher(self):
        return self._publisher or ''

    @publisher.setter
    def publisher(self, value):
        # TODO: [TD0189] Canonicalize metadata values by direct replacements.
        if value and isinstance(value, str):
            str_value = normalize_unicode(html_unescape(value)).strip()
            self._publisher = str_value
            self._normalized_publisher = str_value.lower()

    @property
    def normalized_publisher(self):
        return self._normalized_publisher or ''

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
            _sim_title = string_similarity(self.normalized_title,
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
            _sim_authors = float(
                sum(
                    string_similarity(a, b)
                    for a, b in zip(self.normalized_authors,
                                    other.normalized_authors)
                ) / len(self.normalized_authors)
            )

        if self.normalized_publisher and other.normalized_publisher:
            _sim_publisher = string_similarity(self.normalized_publisher,
                                               other.normalized_publisher)
        else:
            _sim_publisher = FIELDS_MISSING_SIMILARITY

        # TODO: [TD0181] Use machine learning in ISBN metadata de-duplication.
        # TODO: Arbitrary threshold values..
        # Solving "properly" requires machine learning techniques; HMM? Bayes?
        log.debug('Comparing {!s} to {!s} ..'.format(self, other))
        log.debug('Difference Year: {}'.format(_year_diff))
        log.debug('Similarity Authors: {}'.format(_sim_authors))
        log.debug('Similarity Publisher: {}'.format(_sim_publisher))
        log.debug('Similarity Title: {}'.format(_sim_title))
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
        if _year_diff < 2:
            if _sim_authors > 0.7:
                if _sim_title > 0.9:
                    return True
                if _sim_publisher > 0.7 and _sim_title > 0.7:
                    return True
            elif _sim_authors > 0.5:
                if _sim_title > 0.7:
                    return True
                if _sim_publisher > 0.7:
                    return True
            elif _sim_authors > 0.25:
                if _sim_title >= 0.99:
                    return True
        else:
            if _sim_authors == 1:
                if _sim_title > 0.5:
                    return True
                if _sim_publisher > 0.5:
                    return True
            elif _sim_authors > 0.5:
                if _sim_title > 0.7:
                    return True
                if _sim_publisher > 0.7:
                    return True
            elif _sim_authors > 0.2:
                if _sim_title > 0.9:
                    return True
        return False

    def _log_attribute_setter(self, attribute, raw_value, value):
        log.debug(
            '{} attribute {} set (value :: raw) {!s} :: {!s}'.format(
                self.__class__.__name__, attribute, value, raw_value)
        )

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
