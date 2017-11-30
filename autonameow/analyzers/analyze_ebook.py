# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2017 Jonas Sjöberg
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

try:
    import isbnlib
except ImportError:
    isbnlib = None

from analyzers import BaseAnalyzer
from core import (
    persistence,
    types,
)
from core.namebuilder import fields
from core.model import WeightedMapping
from core.model import genericfields as gf
from core.model.normalize import (
    normalize_full_human_name,
    normalize_full_title
)
from util import (
    mimemagic,
    sanity
)
from util.textutils import extractlines_do
from util.text import (
    find_edition,
    string_similarity,
    RE_EDITION
)


log = logging.getLogger(__name__)


# Known bad numbers that keep turning up ..
BLACKLISTED_ISBN_NUMBERS = ['0000000000', '1111111111', '2222222222',
                            '3333333333', '4444444444', '5555555555',
                            '6666666666', '7777777777', '8888888888',
                            '9999999999', '0123456789']

IGNORED_TEXTLINES = frozenset([
    'This page intentionally left blank'
])


RE_E_ISBN = re.compile(r'^e-ISBN.*', re.MULTILINE)


CACHE_KEY_ISBNMETA = 'isbnlib_meta'
CACHE_KEY_ISBNBLACKLIST = 'isbnlib_blacklist'


class EbookAnalyzer(BaseAnalyzer):
    RUN_QUEUE_PRIORITY = 0.5
    HANDLES_MIME_TYPES = ['application/pdf', 'application/epub+zip',
                          'image/vnd.djvu']

    def __init__(self, fileobject, config, request_data_callback):
        super(EbookAnalyzer, self).__init__(
            fileobject, config, request_data_callback
        )

        self.text = None
        self._isbn_metadata = []

        self._cached_isbn_metadata = {}
        self._isbn_num_blacklist = set(BLACKLISTED_ISBN_NUMBERS)
        self.cache = persistence.get_cache(str(self))
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

        self.text = _maybe_text

        # TODO: [TD0114] Check metadata for ISBNs.
        # Exiftool fields: 'PDF:Keywords', 'XMP:Identifier'

        # First try to find "e-book ISBNs" from front to back.
        # If that failed, try again but from back to front.
        #
        # Then try to find any ISBNs from front to back and finally reversed.
        #
        _line_from = 0
        _line_to = 1000
        _line_from_rev = len(self.text)
        _line_to_rev = len(self.text) - 1000
        if _line_to_rev < 0:
            _line_to_rev = 0
        isbns = extractlines_do(find_ebook_isbns_in_text, self.text,
                                fromline=_line_from, toline=_line_to)
        if not isbns:
            isbns = extractlines_do(find_ebook_isbns_in_text, self.text,
                                    fromline=_line_from_rev,
                                    toline=_line_to_rev)
        if not isbns:
            isbns = extractlines_do(extract_isbns_from_text, self.text,
                                    fromline=_line_from, toline=_line_to)
        if not isbns:
            isbns = extractlines_do(extract_isbns_from_text, self.text,
                                    fromline=_line_from_rev,
                                    toline=_line_to_rev)

        if isbns:
            isbns = filter_isbns(isbns, self._isbn_num_blacklist)
            for isbn in isbns:
                self.log.debug('Extracted ISBN: {!s}'.format(isbn))

                metadata_dict = self._get_isbn_metadata(isbn)
                if not metadata_dict:
                    self.log.warning(
                        'Unable to get metadata for ISBN: "{}"'.format(isbn)
                    )
                    self.log.debug('Blacklisting ISBN: "{}"'.format(isbn))
                    self._isbn_num_blacklist.add(isbn)
                    if self.cache:
                        self.cache.set(CACHE_KEY_ISBNBLACKLIST,
                                       self._isbn_num_blacklist)
                    continue

                metadata = ISBNMetadata(
                    authors=metadata_dict.get('Authors'),
                    language=metadata_dict.get('Language'),
                    publisher=metadata_dict.get('Publisher'),
                    isbn10=metadata_dict.get('ISBN-10'),
                    isbn13=metadata_dict.get('ISBN-13'),
                    title=metadata_dict.get('Title'),
                    year=metadata_dict.get('Year')
                )
                self.log.debug('Metadata for ISBN: {}'.format(isbn))
                self.log.debug('Title     : {}'.format(metadata.title))
                self.log.debug('Authors   : {}'.format(metadata.authors))
                self.log.debug('Publisher : {}'.format(metadata.publisher))
                self.log.debug('Year      : {}'.format(metadata.year))
                self.log.debug('Language  : {}'.format(metadata.language))
                self.log.debug('ISBN-10   : {}'.format(metadata.isbn10))
                self.log.debug('ISBN-13   : {}'.format(metadata.isbn13))

                # Duplicates are removed here. When both ISBN-10 and ISBN-13
                # text is found and two queries are made, the two metadata
                # results are "joined" when being added to this set.
                if metadata not in self._isbn_metadata:
                    self._isbn_metadata.append(metadata)

            self.log.info('Got {} instances of ISBN metadata'.format(
                len(self._isbn_metadata)
            ))
            for _isbn_metadata in self._isbn_metadata:
                maybe_title = self._filter_title(_isbn_metadata.title)
                if maybe_title:
                    self._add_results('title', self._wrap_title(maybe_title))

                maybe_authors = _isbn_metadata.authors
                if maybe_authors:
                    self._add_results('author',
                                      self._wrap_authors(maybe_authors))

                maybe_publisher = self._filter_publisher(
                    _isbn_metadata.publisher
                )
                if maybe_publisher:
                    self._add_results('publisher',
                                      self._wrap_publisher(maybe_publisher))

                maybe_date = self._filter_date(_isbn_metadata.year)
                if maybe_date:
                    self._add_results('date', self._wrap_date(maybe_date))

                maybe_edition = self._filter_edition(_isbn_metadata.edition)
                if maybe_edition:
                    self._add_results('edition', self._wrap_edition(maybe_edition))

    def _get_isbn_metadata(self, isbn):
        if isbn in self._cached_isbn_metadata:
            self.log.info(
                'Using cached metadata for ISBN: {!s}'.format(isbn)
            )
            return self._cached_isbn_metadata.get(isbn)

        self.log.debug('Querying external service for ISBN: {!s}'.format(isbn))
        metadata = fetch_isbn_metadata(isbn)
        if metadata:
            self.log.info(
                'Caching metadata for ISBN: {!s}'.format(isbn)
            )

            self._cached_isbn_metadata.update({isbn: metadata})
            if self.cache:
                self.cache.set(CACHE_KEY_ISBNMETA, self._cached_isbn_metadata)

        return metadata

    def _wrap_authors(self, list_of_authors):
        if not list_of_authors:
            return

        return {
            'source': str(self),
            'value': list_of_authors,
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Author, probability=1),
            ],
            'generic_field': gf.GenericAuthor,
            'multivalued': True
        }

    def _filter_date(self, raw_string):
        # TODO: Cleanup and filter date/year
        try:
            return types.AW_DATE(raw_string)
        except types.AWTypeError:
            return None

    def _wrap_date(self, date_string):
        if not date_string:
            return

        return {
            'source': str(self),
            'value': date_string,
            'coercer': types.AW_DATE,
            'mapped_fields': [
                WeightedMapping(fields.Date, probability=1),
                WeightedMapping(fields.DateTime, probability=1),
            ],
            'generic_field': gf.GenericDateCreated
        }

    def _filter_publisher(self, raw_string):
        try:
            string_ = types.AW_STRING(raw_string)
        except types.AWTypeError:
            return
        else:
            if not string_.strip():
                return

            # TODO: Cleanup and filter publisher(s)
            return string_

    def _wrap_publisher(self, publisher_string):
        return {
            'source': str(self),
            'value': publisher_string,
            'coercer': types.AW_STRING,
            'multivalued': False,
            'mapped_fields': [
                WeightedMapping(fields.Publisher, probability=1),
            ],
            'generic_field': gf.GenericPublisher
        }

    def _filter_title(self, raw_string):
        try:
            string_ = types.AW_STRING(raw_string)
        except types.AWTypeError:
            return
        else:
            if not string_.strip():
                return

            # TODO: Cleanup and filter title.
            return string_

    def _wrap_title(self, title_string):
        return {
            'source': str(self),
            'value': title_string,
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Title, probability=1),
            ],
            'generic_field': gf.GenericTitle
        }

    def _filter_edition(self, raw_string):
        try:
            int_ = types.AW_INTEGER(raw_string)
        except types.AWTypeError:
            return None
        else:
            return int_ if int_ != 0 else None

    def _wrap_edition(self, edition_integer):
        return {
            'source': str(self),
            'value': edition_integer,
            'coercer': types.AW_INTEGER,
            'mapped_fields': [
                WeightedMapping(fields.Edition, probability=1),
            ],
            'generic_field': gf.GenericEdition
        }

    @classmethod
    def can_handle(cls, fileobject):
        try:
            return mimemagic.eval_glob(fileobject.mime_type,
                                       cls.HANDLES_MIME_TYPES)
        except (TypeError, ValueError) as e:
            cls.log.error(
                'Error evaluating "{!s}" MIME handling; {!s}'.format(cls, e)
            )
        if (fileobject.basename_suffix == b'mobi' and
                fileobject.mime_type == 'application/octet-stream'):
            return True

        return False

    @classmethod
    def check_dependencies(cls):
        return isbnlib is not None


def remove_ignored_textlines(text):
    """
    Removes any text lines that match those in 'IGNORED_TEXTLINES'.

    Args:
        text: The text to process as a Unicode string.

    Returns:
        The given text with any lines matching those in 'IGNORED_TEXTLINES'
        removed, as a Unicode string.
    """
    out = []

    for line in text.splitlines():
        if line in IGNORED_TEXTLINES:
            continue
        out.append(line)

    return '\n'.join(out)


def find_ebook_isbns_in_text(text):
    sanity.check_internal_string(text)

    match = RE_E_ISBN.search(text)
    if not match:
        return []

    possible_isbns = isbnlib.get_isbnlike(match.group(0))
    if possible_isbns:
        return [isbnlib.get_canonical_isbn(i)
                for i in possible_isbns if validate_isbn(i)]
    else:
        return []


def extract_isbns_from_text(text):
    sanity.check_internal_string(text)

    possible_isbns = isbnlib.get_isbnlike(text)
    if possible_isbns:
        return [isbnlib.get_canonical_isbn(i)
                for i in possible_isbns if validate_isbn(i)]
    else:
        return []


def validate_isbn(possible_isbn):
    if not possible_isbn:
        return None

    sanity.check_internal_string(possible_isbn)

    isbn_number = isbnlib.clean(possible_isbn)
    if not isbn_number or isbnlib.notisbn(isbn_number):
        return None
    else:
        return isbn_number


def filter_isbns(isbn_list, isbn_blacklist):
    if not isbn_list:
        return []

    assert isinstance(isbn_list, list)

    # Remove any duplicates.
    isbn_list = list(set(isbn_list))

    # Remove known bad ISBN numbers.
    isbn_list = [n for n in isbn_list if n and n not in isbn_blacklist]
    return isbn_list


def fetch_isbn_metadata(isbn_number):
    logging.disable(logging.DEBUG)

    isbn_metadata = None
    try:
        isbn_metadata = isbnlib.meta(isbn_number)
    except isbnlib.NotValidISBNError:
        log.error(
            'Metadata query FAILED for ISBN: "{}"'.format(isbn_number)
        )

    logging.disable(logging.NOTSET)
    return isbn_metadata


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
        self._normalized_authors = []
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
        if value:
            if not isinstance(value, list):
                value = [value]
            self._authors = value
            self._normalized_authors = [
               normalize_full_human_name(a) for a in value if a
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
        else:
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
        else:
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
        if value and isinstance(value, str):
            self._publisher = value
            self._normalized_publisher = value.lower().strip()

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
                self._normalized_year = types.AW_INTEGER(value)
            except types.AWTypeError:
                self._normalized_year = self.NORMALIZED_YEAR_UNKNOWN

    @property
    def normalized_year(self):
        return self._normalized_year or self.NORMALIZED_YEAR_UNKNOWN

    @property
    def normalized_language(self):
        return self._normalized_language or ''

    @property
    def title(self):
        return self._title or ''

    @title.setter
    def title(self, value):
        if value and isinstance(value, str):
            match = find_edition(value)
            if match:
                self.edition = match
                # TODO: This is WRONG!
                # Result of 'find_edition()' might not come from the part of
                # the string that matched 'RE_EDITION'. Need a better way to
                # identify and extract substrings ("fields") from strings.
                value = re.sub(RE_EDITION, '', value)

            self._title = value
            self._normalized_title = normalize_full_title(value)

    @property
    def normalized_title(self):
        return self._normalized_title or ''

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

        if (len(self.normalized_authors) == 0
                or len(other.normalized_authors) == 0):
            _sim_authors = FIELDS_MISSING_SIMILARITY
        else:
            _sim_authors = float(
                sum(string_similarity(a, b)
                    for a, b in zip(self.normalized_authors,
                                    other.normalized_authors)
                    ) / len(self.normalized_authors)
            )

        if self.normalized_publisher and other.normalized_publisher:
            _sim_publisher = string_similarity(self.normalized_publisher,
                                               other.normalized_publisher)
        else:
            _sim_publisher = FIELDS_MISSING_SIMILARITY

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
                if _sim_title > 0.3:
                    return True
                if _sim_publisher > 0.2:
                    return True
            elif _sim_authors > 0.5:
                if _sim_title > 0.7:
                    return True
                if _sim_publisher > 0.7:
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
        return False

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
