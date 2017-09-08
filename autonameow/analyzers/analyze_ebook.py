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

from analyzers import BaseAnalyzer
from core import (
    util,
    types,
    fields
)
from core.util import textutils
from extractors import ExtractedData

try:
    import isbnlib
except (ImportError, ModuleNotFoundError):
    isbnlib = None


log = logging.getLogger(__name__)


# Known bad numbers that keep turning up ..
BLACKLISTED_ISBN_NUMBERS = ['0000000000', '1111111111', '2222222222',
                            '3333333333', '4444444444', '5555555555',
                            '6666666666', '7777777777', '8888888888',
                            '9999999999', '0123456789']


class EbookAnalyzer(BaseAnalyzer):
    run_queue_priority = 1
    handles_mime_types = ['application/pdf', 'application/epub+zip']
    meowuri_root = 'analysis.ebook'

    def __init__(self, file_object, add_results_callback,
                 request_data_callback):
        super(EbookAnalyzer, self).__init__(
            file_object, add_results_callback, request_data_callback
        )

    def run(self):
        text = self.request_data(self.file_object, 'contents.textual.raw_text')
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

                maybe_author = self._filter_author(metadata.get('Author'))
                if maybe_author:
                    self._add_results('author', self._wrap_author(maybe_author))

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
        string_ = types.AW_STRING(raw_string)
        if not string_.strip():
            return

        # TODO: Cleanup and filter author(s)
        return string_

    def _wrap_author(self, author_string):
        return ExtractedData(
            wrapper=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.author, probability=1),
            ]
        )(author_string)

    def _filter_date(self, raw_string):
        string_ = types.AW_DATE(raw_string)
        if not string_.strip():
            return

        # TODO: Cleanup and filter date/year
        return string_

    def _wrap_date(self, date_string):
        return ExtractedData(
            wrapper=types.AW_DATE,
            mapped_fields=[
                fields.WeightedMapping(fields.date, probability=1),
            ]
        )(date_string)

    def _filter_publisher(self, raw_string):
        string_ = types.AW_STRING(raw_string)
        if not string_.strip():
            return

        # TODO: Cleanup and filter publisher(s)
        return string_

    def _wrap_publisher(self, publisher_string):
        return ExtractedData(
            wrapper=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.publisher, probability=1),
            ]
        )(publisher_string)

    def _filter_title(self, raw_string):
        string_ = types.AW_STRING(raw_string)
        if not string_.strip():
            return

        # TODO: Cleanup and filter title.
        return string_

    def _wrap_title(self, title_string):
        return ExtractedData(
            wrapper=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping(fields.title, probability=1),
            ]
        )(title_string)

    def _add_results(self, meowuri_leaf, data):
        if data is None:
            return

        meowuri = '{}.{}'.format(self.meowuri_root, meowuri_leaf)
        self.log.debug(
            '{!s} passing "{}" to "add_results" callback'.format(self, meowuri)
        )
        self.add_results(meowuri, data)

    @classmethod
    def can_handle(cls, file_object):
        try:
            return util.eval_magic_glob(file_object.mime_type,
                                        cls.handles_mime_types)
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
    isbns = [isbnlib.get_canonical_isbn(isbn)
             for isbn in isbnlib.get_isbnlike(text)]
    if isbns:
        return [i for i in isbns if validate_isbn(i)]
    else:
        return []


def validate_isbn(number):
    if not number:
        return None

    n = isbnlib.clean(number)
    if not n or isbnlib.notisbn(n):
        return None
    else:
        return n


def filter_isbns(numbers):
    # Remove all characters except digits and dashes.
    numbers = [re.sub(r'[^\d-]+', '', n) for n in numbers]

    # Remove any duplicates.
    nums = list(set(numbers))

    # Remove known bad ISBN numbers.
    numbers = [n for n in nums
               if n not in BLACKLISTED_ISBN_NUMBERS]
    return numbers


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
