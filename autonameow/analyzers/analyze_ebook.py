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
#    model,
    types,
    util
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
    HANDLES_MIME_TYPES = ['application/pdf', 'application/epub+zip']

    def __init__(self, file_object, add_results_callback,
                 request_data_callback):
        super(EbookAnalyzer, self).__init__(
            file_object, add_results_callback, request_data_callback
        )

    def run(self):
        text = self.request_data(self.file_object, 'extractor.text.pdf.full')
        if not text:
            # TODO: Allow querying for text from any source.
            text = self.request_data(self.file_object, 'extractor.text.*.full')
        if not text:
            return

        isbns = _search_initial_text(text, extract_isbns_from_text)
        if isbns:
            isbns = filter_isbns(isbns)
            for isbn in isbns:
                self.log.debug('Extracted ISBN: {!s}'.format(isbn))
                self.log.debug('Querying external service for ISBN metadata ..')
                metadata = fetch_isbn_metadata(isbn)
                if not metadata:
                    self.log.warning(
                        'Unable to get metadata for ISBN: "{}"'.format(isbn)
                    )
                    continue

                self.log.info('Fetched metadata for ISBN: {}'.format(isbn))
                self.log.info('Title     : {}'.format(metadata['Title']))
                self.log.info('Authors   : {}'.format(metadata['Authors']))
                self.log.info('Publisher : {}'.format(metadata['Publisher']))
                self.log.info('Year      : {}'.format(metadata['Year']))
                self.log.info('Language  : {}'.format(metadata['Language']))
                self.log.info('ISBN-13   : {}'.format(metadata['ISBN-13']))

                maybe_title = self._filter_title(metadata.get('Title'))
                if maybe_title:
                    self._add_results('title', self._wrap_title(maybe_title))

                maybe_authors = metadata.get('Authors')
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
                    metadata.get('Publisher')
                )
                if maybe_publisher:
                    self._add_results('publisher',
                                      self._wrap_publisher(maybe_publisher))

                maybe_date = self._filter_date(metadata.get('Year'))
                if maybe_date:
                    self._add_results('date', self._wrap_date(maybe_date))

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
            # generic_field=model.GenericAuthor
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
            ],
            # generic_field=model.GenericDateCreated
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
            ]
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
            ]
        )(title_string)

    @classmethod
    def can_handle(cls, file_object):
        try:
            return util.eval_magic_glob(file_object.mime_type,
                                        cls.HANDLES_MIME_TYPES)
        except (TypeError, ValueError) as e:
            log.error('Error evaluating "{!s}" MIME handling; {!s}'.format(cls,
                                                                           e))
        if (file_object.basename_suffix == b'mobi' and
                file_object.mime_type == 'application/octet-stream'):
            return True

        return False

    @classmethod
    def check_dependencies(cls):
        return isbnlib is not None


# TODO: [TD0030] Plugin for querying APIs with ISBN numbers.


def _search_initial_text(text, callback):
    initial_text_start = 0
    initial_text_end = 100
    lines = textutils.extract_lines(text, initial_text_start, initial_text_end)

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
