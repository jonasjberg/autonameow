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

import re

from analyzers import BaseAnalyzer
from core import types
from core.model import WeightedMapping
from core.model import genericfields as gf
from core.namebuilder import fields
from util import (
    dateandtime,
    textutils
)
from util.text.patternmatching import find_publisher_in_copyright_notice


# TODO: [TD0094] Search text for DOIs and query external services
# Example DOI: `10.1109/TPDS.2010.125`. Could be used to query external
# services for publication metadata, as with ISBN-numbers.


class DocumentAnalyzer(BaseAnalyzer):
    RUN_QUEUE_PRIORITY = 0.5
    HANDLES_MIME_TYPES = ['application/pdf', 'text/*']

    def __init__(self, fileobject, config, request_data_callback):
        super(DocumentAnalyzer, self).__init__(
            fileobject, config, request_data_callback
        )

        self.text = None

    def analyze(self):
        _maybe_text = self.request_any_textual_content()
        if not _maybe_text:
            return

        self.text = _maybe_text

        self._add_results('datetime', self.get_datetime())

        self._add_title_from_text_to_results()
        self._search_text_for_candidate_publisher()
        self._search_text_for_copyright_publisher()

    def __collect_results(self, meowuri, weight):
        value = self.request_data(self.fileobject, meowuri)
        if value:
            return result_list_add(value, meowuri, weight)
        else:
            return []

    def get_datetime(self):
        results = []

        if self.text:
            text_timestamps = self._get_datetime_from_text()
            if text_timestamps:
                results += text_timestamps

        return results if results else None

    def _add_title_from_text_to_results(self):
        text = self.text
        if not text:
            return

        # Add all lines that aren't all whitespace or all dashes, from the
        # first to line number "max_lines".
        # The first line is assigned probability 1, probabilities decrease
        # for each line until line number "max_lines" with probability 0.
        max_lines = 1
        for num, line in enumerate(text.splitlines()):
            if num > max_lines:
                break

            if line.strip() and line.replace('-', ''):
                _prob = (max_lines - num) / max_lines
                self._add_results(
                    'title', self._wrap_generic_title(line, _prob)
                )

    def _search_text_for_candidate_publisher(self):
        _options = self.config.get(['NAME_TEMPLATE_FIELDS', 'publisher'])
        if not _options:
            return
        else:
            _candidates = _options.get('candidates', {})

        assert self.text is not None
        _text = textutils.extract_lines(self.text, firstline=0, lastline=1000)
        result = find_publisher(_text, _candidates)
        if not result:
            return

        self._add_results(
            'publisher', self._wrap_publisher(result)
        )

    def _search_text_for_copyright_publisher(self):
        assert self.text is not None
        result = textutils.extractlines_do(find_publisher_in_copyright_notice,
                                           self.text, fromline=0, toline=1000)
        if not result:
            return

        self._add_results(
            'publisher', self._wrap_publisher(result)
        )

    def _wrap_publisher(self, data):
        return {
            'value': data,
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Publisher, probability=1),
            ],
            'generic_field': gf.GenericPublisher
        }

    def _wrap_generic_title(self, data, probability):
        return {
            'value': data,
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Title, probability=probability),
            ],
            'generic_field': gf.GenericTitle
        }

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
            assert isinstance(dt_regex, list)
            for data in dt_regex:
                results.append({
                    'value': data,
                    'coercer': types.AW_TIMEDATE,
                    'mapped_fields': [
                        WeightedMapping(fields.DateTime, probability=0.25),
                        WeightedMapping(fields.Date, probability=0.25)
                    ],
                    'generic_field': gf.GenericDateCreated
                    })

        # TODO: Temporary premature return skips brute force search ..
        return results

        matches = 0
        text_split = text.split('\n')
        self.log.debug('Try getting datetime from text split by newlines')
        for t in text_split:
            dt_brute = dateandtime.bruteforce_str(t)
            if dt_brute:
                matches += 1
                assert isinstance(dt_brute, list)
                for v in dt_brute:
                    results.append({
                        'value': data,
                        'coercer': types.AW_TIMEDATE,
                        'mapped_fields': [
                            WeightedMapping(fields.DateTime, probability=0.1),
                            WeightedMapping(fields.Date, probability=0.1)
                        ],
                        'generic_field': gf.GenericDateCreated
                    })

        if matches == 0:
            self.log.debug('No matches. Trying with text split by whitespace')
            text_split = text.split()
            for t in text_split:
                dt_brute = dateandtime.bruteforce_str(t)
                if dt_brute:
                    matches += 1
                    assert isinstance(dt_brute, list)
                    for v in dt_brute:
                        results.append({
                            'value': data,
                            'coercer': types.AW_TIMEDATE,
                            'mapped_fields': [
                                WeightedMapping(fields.DateTime, probability=0.1),
                                WeightedMapping(fields.Date, probability=0.1)
                            ],
                            'generic_field': gf.GenericDateCreated
                        })

        return results

    @classmethod
    def check_dependencies(cls):
        return True


def result_list_add(value, source, weight):
    return [{'value': value,
             'source': source,
             'weight': weight}]


def find_publisher(text, candidates):
    text = text.lower()
    for repl, patterns in candidates.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return repl
    return None
