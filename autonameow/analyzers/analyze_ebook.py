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

try:
    import isbnlib
except ImportError:
    isbnlib = None

from analyzers import BaseAnalyzer
from core import (
    cache,
    types,
    util,
    model
)
from core.namebuilder import fields
from core.model import (
    ExtractedData,
    WeightedMapping
)
from core.util import (
    sanity,
    textutils
)


log = logging.getLogger(__name__)


# Known bad numbers that keep turning up ..
BLACKLISTED_ISBN_NUMBERS = ['0000000000', '1111111111', '2222222222',
                            '3333333333', '4444444444', '5555555555',
                            '6666666666', '7777777777', '8888888888',
                            '9999999999', '0123456789']


class EbookAnalyzer(BaseAnalyzer):
    run_queue_priority = 1
    HANDLES_MIME_TYPES = ['application/pdf', 'application/epub+zip',
                          'image/vnd.djvu']

    def __init__(self, fileobject, add_results_callback,
                 request_data_callback):
        super(EbookAnalyzer, self).__init__(
            fileobject, add_results_callback, request_data_callback
        )

        self.text = None
        self._cached_isbn_metadata = {}
        self._isbn_metadata = set()

        _cache = cache.get_cache(str(self))
        if _cache:
            self.cache = _cache
            try:
                self._cached_isbn_metadata = self.cache.get('isbnlib_meta')
            except (KeyError, cache.CacheError):
                pass
        else:
            self.cache = None

    def run(self):
        _maybe_text = self.request_any_textual_content()
        if not _maybe_text:
            return

        self.text = _maybe_text

        isbns = within_text_do(extract_isbns_from_text, self.text,
                               fromline=0, toline=100)
        if isbns:
            isbns = filter_isbns(isbns)
            for isbn in isbns:
                self.log.debug('Extracted ISBN: {!s}'.format(isbn))

                metadata_dict = self._get_isbn_metadata(isbn)
                if not metadata_dict:
                    self.log.warning(
                        'Unable to get metadata for ISBN: "{}"'.format(isbn)
                    )
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
                self._isbn_metadata.add(metadata)

            self.log.info('Got {} instances of ISBN metadata'.format(
                len(self._isbn_metadata)
            ))
            for _isbn_metadata in self._isbn_metadata:
                maybe_title = self._filter_title(_isbn_metadata.title)
                if maybe_title:
                    self._add_results('title', self._wrap_title(maybe_title))

                maybe_authors = _isbn_metadata.authors
                if maybe_authors:
                    # TODO: [TD0084] Use a "list-of-strings" coercer ..
                    if isinstance(maybe_authors, list):
                        for maybe_author in maybe_authors:
                            _author = self._filter_author(maybe_author)
                            if _author:
                                self._add_results('author',
                                                  self._wrap_author(_author))
                    else:
                        self._add_results('author',
                                          self._wrap_author(maybe_authors))

                maybe_publisher = self._filter_publisher(
                    _isbn_metadata.publisher
                )
                if maybe_publisher:
                    self._add_results('publisher',
                                      self._wrap_publisher(maybe_publisher))

                maybe_date = self._filter_date(_isbn_metadata.year)
                if maybe_date:
                    self._add_results('date', self._wrap_date(maybe_date))

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
            # Add new metadata to local cache.
            self._cached_isbn_metadata.update({isbn: metadata})
            if self.cache:
                try:
                    self.cache.set('isbnlib_meta', self._cached_isbn_metadata)
                except cache.CacheError:
                    pass

        return metadata

    def _filter_author(self, raw_string):
        try:
            # TODO: Calling 'ExtractedData' "wraps" the value a second time!
            string_ = types.AW_STRING(raw_string)
        except types.AWTypeError:
            return
        else:
            if not string_.strip():
                return

            # TODO: Cleanup and filter author(s)
            return string_

    def _wrap_author(self, author_string):
        return ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Author, probability=1),
            ],
            generic_field=model.GenericAuthor
        )(author_string)

    def _filter_date(self, raw_string):
        # TODO: Cleanup and filter date/year
        try:
            # TODO: Calling 'ExtractedData' "wraps" the value a second time!
            return types.AW_DATE(raw_string)
        except types.AWTypeError:
            return None

    def _wrap_date(self, date_string):
        return ExtractedData(
            coercer=types.AW_DATE,
            mapped_fields=[
                WeightedMapping(fields.Date, probability=1),
                WeightedMapping(fields.DateTime, probability=1),
            ],
            generic_field=model.GenericDateCreated
        )(date_string)

    def _filter_publisher(self, raw_string):
        try:
            # TODO: Calling 'ExtractedData' "wraps" the value a second time!
            string_ = types.AW_STRING(raw_string)
        except types.AWTypeError:
            return
        else:
            if not string_.strip():
                return

            # TODO: Cleanup and filter publisher(s)
            return string_

    def _wrap_publisher(self, publisher_string):
        return ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Publisher, probability=1),
            ],
            generic_field=model.GenericPublisher
        )(publisher_string)

    def _filter_title(self, raw_string):
        try:
            # TODO: Calling 'ExtractedData' "wraps" the value a second time!
            string_ = types.AW_STRING(raw_string)
        except types.AWTypeError:
            return
        else:
            if not string_.strip():
                return

            # TODO: Cleanup and filter title.
            return string_

    def _wrap_title(self, title_string):
        return ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Title, probability=1),
            ],
            generic_field=model.GenericTitle
        )(title_string)

    @classmethod
    def can_handle(cls, fileobject):
        try:
            return util.eval_magic_glob(fileobject.mime_type,
                                        cls.HANDLES_MIME_TYPES)
        except (TypeError, ValueError) as e:
            log.error('Error evaluating "{!s}" MIME handling; {!s}'.format(cls,
                                                                           e))
        if (fileobject.basename_suffix == b'mobi' and
                fileobject.mime_type == 'application/octet-stream'):
            return True

        return False

    @classmethod
    def check_dependencies(cls):
        return isbnlib is not None


def within_text_do(callback, text, fromline=0, toline=100):
    lines = textutils.extract_lines(text, fromline, toline)

    return callback(lines)


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


def filter_isbns(isbn_list):
    if not isbn_list:
        return []

    sanity.check_isinstance(isbn_list, list)

    # Remove any duplicates.
    isbn_list = list(set(isbn_list))

    # Remove known bad ISBN numbers.
    isbn_list = [n for n in isbn_list if n
                 and n not in BLACKLISTED_ISBN_NUMBERS]
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
    def __init__(self, authors=None, language=None, publisher=None,
                 isbn10=None, isbn13=None, title=None, year=None):
        self._authors = authors
        self._language = language
        self._publisher = publisher
        self._isbn10 = isbn10
        self._isbn13 = isbn13
        self._title = title
        self._year = year

    @property
    def authors(self):
        return self._authors or []

    @authors.setter
    def authors(self, value):
        if value and isinstance(value, list):
            self._authors = value

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

    @property
    def publisher(self):
        return self._publisher or ''

    @publisher.setter
    def publisher(self, value):
        if value and isinstance(value, str):
            self._publisher = value

    @property
    def year(self):
        return self._year or ''

    @year.setter
    def year(self, value):
        if value and isinstance(value, str):
            self._year = value

    @property
    def title(self):
        return self._title or ''

    @title.setter
    def title(self, value):
        if value and isinstance(value, str):
            self._title = value

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.isbn10 == other.isbn10:
            return True
        if self.isbn13 == other.isbn13:
            return True
        if (self.title == other.title
                and self.authors == other.authors
                and self.publisher == other.publisher
                and self.year == other.year
                and self.language == other.language):
            return True

    def __hash__(self):
        return hash((self.isbn10, self.isbn13))
