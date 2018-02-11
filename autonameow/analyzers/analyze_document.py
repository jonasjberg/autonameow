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

import re

from analyzers import BaseAnalyzer
from core import types
from core.model import WeightedMapping
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

    # TODO: [TD0157] Look into analyzers 'FIELD_LOOKUP' attributes.

    def __init__(self, fileobject, config, request_data_callback):
        super().__init__(fileobject, config, request_data_callback)

        self.text = None
        self.text_lines = 0
        self.candidate_publishers = {}

    def analyze(self):
        _maybe_text = self.request_any_textual_content()
        if not _maybe_text:
            return

        self.text = _maybe_text
        self.text_lines = len(self.text.splitlines())

        # Arbitrarily search the text in chunks of 10%
        # TODO: [TD0134] Consolidate splitting up text into chunks.
        text_chunk_1 = self._extract_leading_text_chunk(chunk_ratio=0.1)

        # TODO: [TD0102] Fix inconsistent results passed back by analyzers.
        # Self._add_results('datetime',
        #                   self._get_datetime_from_text(text_chunk_1))

        self._add_title_from_text_to_results(text_chunk_1)

        _options = self.config.get(['NAME_TEMPLATE_FIELDS', 'publisher'])
        if _options:
            _candidates = _options.get('candidates', {})
            if _candidates:
                self.candidate_publishers = _candidates

        # TODO: [cleanup] ..
        if self.candidate_publishers:
            self._search_text_for_candidate_publisher(text_chunk_1)
            self._search_text_for_copyright_publisher(text_chunk_1)

    def _add_title_from_text_to_results(self, text):
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

    def _search_text_for_candidate_publisher(self, text):
        # TODO: [TD0130] Implement general-purpose substring matching/extraction.
        result = find_publisher(text, self.candidate_publishers)
        if not result:
            return

        self._add_results(
            'publisher', self._wrap_publisher(result)
        )

    def _search_text_for_copyright_publisher(self, text):
        # TODO: [TD0130] Implement general-purpose substring matching/extraction.
        result = find_publisher_in_copyright_notice(text)
        if not result:
            return

        if self.candidate_publishers:
            # TODO: [cleanup] ..
            result = find_publisher(result, self.candidate_publishers)
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
            'generic_field': 'publisher',
            'source': str(self)
        }

    def _wrap_generic_title(self, data, probability):
        return {
            'value': data,
            'coercer': types.AW_STRING,
            'mapped_fields': [
                WeightedMapping(fields.Title, probability=probability),
            ],
            'generic_field': 'title',
            'source': str(self)
        }

    def _get_datetime_from_text(self, text):
        # TODO: [TD0130] Implement general-purpose substring matching/extraction.
        dt_regex = dateandtime.regex_search_str(text)
        if not dt_regex:
            return None

        assert isinstance(dt_regex, list)
        results = []
        for data in dt_regex:
            results.append({
                'value': data,
                'coercer': types.AW_TIMEDATE,
                'mapped_fields': [
                    WeightedMapping(fields.DateTime, probability=0.25),
                    WeightedMapping(fields.Date, probability=0.25)
                ],
                'generic_field': 'date_created',
                'source': str(self)
                })
        return results

    def _extract_leading_text_chunk(self, chunk_ratio):
        assert chunk_ratio >= 0, 'Argument chunk_ratio is negative'

        # Chunk #1: from BEGINNING to (BEGINNING + CHUNK_SIZE)
        _chunk1_start = 1
        _chunk1_end = int(self.text_lines * chunk_ratio)
        if _chunk1_end < 1:
            _chunk1_end = 1
        text = textutils.extract_lines(self.text, firstline=_chunk1_start,
                                       lastline=_chunk1_end)
        return text

    @classmethod
    def check_dependencies(cls):
        return True


def find_publisher(text, candidates):
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    text = text.lower()
    for repl, patterns in candidates.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return repl
    return None
