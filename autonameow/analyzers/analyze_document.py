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

from analyzers import BaseAnalyzer
from core import (
    model,
    types
)
from core.model import (
    ExtractedData,
    WeightedMapping
)
from core.namebuilder import fields
from core.util import (
    dateandtime,
    sanity
)


class DocumentAnalyzer(BaseAnalyzer):
    run_queue_priority = 1
    HANDLES_MIME_TYPES = ['application/pdf', 'text/*']

    def __init__(self, file_object, add_results_callback,
                 request_data_callback):
        super(DocumentAnalyzer, self).__init__(
            file_object, add_results_callback, request_data_callback
        )

        self.text = None

    def run(self):
        _maybe_text = self.request_any_textual_content()
        if not _maybe_text:
            return

        self.text = _maybe_text

        self._add_results('author', self.get_author())
        self._add_results('title', self.get_title())
        self._add_results('datetime', self.get_datetime())
        self._add_results('publisher', self.get_publisher())

        self._add_title_from_text_to_results()

    def __collect_results(self, meowuri, weight):
        value = self.request_data(self.file_object, meowuri)
        if value:
            return result_list_add(value, meowuri, weight)
        else:
            return []

    def get_author(self):
        results = []

        possible_authors = [
            ('generic.metadata.author', 1),
            ('generic.metadata.creator', 0.5),
            ('generic.metadata.producer', 0.1),
        ]
        for meowuri, weight, in possible_authors:
            results += self.__collect_results(meowuri, weight)

        return results if results else None

    def get_title(self):
        results = []

        possible_titles = [
            ('generic.metadata.title', 1),
            ('generic.metadata.subject', 0.25),
        ]
        for meowuri, weight in possible_titles:
            results += self.__collect_results(meowuri, weight)

        return results if results else None

    def get_datetime(self):
        results = []

        if self.text:
            text_timestamps = self._get_datetime_from_text()
            if text_timestamps:
                results += text_timestamps

        return results if results else None

    def get_tags(self):
        raise NotImplementedError('Get "tags" from PdfAnalyzer')

    def get_publisher(self):
        results = []

        possible_publishers = [
            ('extractor.metadata.exiftool.PDF:EBX_PUBLISHER', 1),
            ('extractor.metadata.exiftool.XMP:EbxPublisher', 1),
            ('extractor.metadata.pypdf.EBX_PUBLISHER', 1)
        ]
        for meowuri, weight in possible_publishers:
            results += self.__collect_results(meowuri, weight)

        return results if results else None

    def _is_gmail(self):
        """
        Check whether the text might be a "Gmail".
        :return: True if the text is a Gmail, else False
        """
        text = self.text
        if type(text) is list:
            text = ' '.join(text)

        if text.lower().find('gmail'):
            self.log.debug('Text might be a Gmail (contains "gmail")')
            return True
        else:
            return False

    def _add_title_from_text_to_results(self):
        text = self.text
        if not text:
            return

        # Add all lines that aren't all whitespace or all dashes, from the
        # first to line number "max_lines".
        # The first line is assigned probability 1, probabilities decrease
        # for each line until line number "max_lines" with probability 0.
        max_lines = 10
        for num, line in enumerate(text.splitlines()):
            if num > max_lines:
                break

            if line.strip() and line.replace('-', ''):
                _prob = (max_lines - num + 1) / max_lines
                self._add_results(
                    'title', self._wrap_generic_title(line, _prob)
                )

    def _wrap_generic_title(self, title_string, probability):
        return ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                WeightedMapping(fields.Title, probability=probability),
            ],
            generic_field=model.GenericTitle
        )(title_string)

    def _get_datetime_from_text(self):
        """
        Extracts date and time information from the documents textual content.
        :return: a list of dictionaries on the form:
                 [ { 'value': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : 'content',
                     'weight'  : 0.1
                   }, .. ]
        """
        results = []
        text = self.text
        if type(text) == list:
            text = ' '.join(text)

        dt_regex = dateandtime.regex_search_str(text)
        if dt_regex:
            dt_regex_wrapper = ExtractedData(
                coercer=types.AW_TIMEDATE,
                mapped_fields=[
                    WeightedMapping(fields.DateTime, probability=0.25),
                    WeightedMapping(fields.Date, probability=0.25)
                ],
                generic_field=model.GenericDateCreated
            )

            sanity.check_isinstance(dt_regex, list)
            for v in dt_regex:
                results.append(ExtractedData.from_raw(dt_regex_wrapper, v))

        # TODO: Temporary premature return skips brute force search ..
        return results

        dt_brute_wrapper = ExtractedData(
            coercer=types.AW_TIMEDATE,
            mapped_fields=[
                WeightedMapping(fields.DateTime, probability=0.1),
                WeightedMapping(fields.Date, probability=0.1)
            ],
            generic_field=model.GenericDateCreated
        )
        matches = 0
        text_split = text.split('\n')
        self.log.debug('Try getting datetime from text split by newlines')
        for t in text_split:
            dt_brute = dateandtime.bruteforce_str(t)
            if dt_brute:
                matches += 1
                sanity.check_isinstance(dt_brute, list)
                for v in dt_brute:
                    results.append(ExtractedData.from_raw(dt_brute_wrapper, v))

        if matches == 0:
            self.log.debug('No matches. Trying with text split by whitespace')
            text_split = text.split()
            for t in text_split:
                dt_brute = dateandtime.bruteforce_str(t)
                if dt_brute:
                    matches += 1
                    sanity.check_isinstance(dt_brute, list)
                    for v in dt_brute:
                        results.append(ExtractedData.from_raw(dt_brute_wrapper, v))

        return results

    @classmethod
    def check_dependencies(cls):
        return True


def result_list_add(value, source, weight):
    return [{'value': value,
             'source': source,
             'weight': weight}]
