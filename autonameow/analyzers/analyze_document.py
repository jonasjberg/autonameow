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
from util import textutils
from util.text.patternmatching import find_publisher_in_copyright_notice


# TODO: [TD0094] Search text for DOIs and query external services
# Example DOI: `10.1109/TPDS.2010.125`. Could be used to query external
# services for publication metadata, as with ISBN-numbers.


class DocumentAnalyzer(BaseAnalyzer):
    RUN_QUEUE_PRIORITY = 0.5
    HANDLES_MIME_TYPES = ['application/pdf', 'text/*']
    FIELD_LOOKUP = {
        'title': {
            'coercer': 'aw_string',
            'mapped_fields': [
                # TODO: [TD0166] Set probabilities dynamically
                {'WeightedMapping': {'field': 'Title', 'probability': '1'}},
            ],
            'generic_field': 'title'
        },
        'datetime': {
            'coercer': 'aw_timedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'probability': '0.25'}},
                {'WeightedMapping': {'field': 'Date', 'probability': '0.25'}},
            ],
            'generic_field': 'date_created',
        },
        'publisher': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Publisher', 'probability': '1'}},
            ],
            'generic_field': 'publisher',
        }
    }

    def __init__(self, fileobject, config, request_data_callback):
        super().__init__(fileobject, config, request_data_callback)

        self.text = None
        self.num_text_lines = 0
        self.candidate_publishers = {}

    def analyze(self):
        _maybe_text = self.request_any_textual_content()
        if not _maybe_text:
            return

        self.text = _maybe_text
        self.num_text_lines = len(self.text.splitlines())

        # Arbitrarily search the text in chunks of 10%
        # TODO: [TD0134] Consolidate splitting up text into chunks.
        text_chunk_1 = self._extract_leading_text_chunk(chunk_ratio=0.1)

        # TODO: Search text for datetime information.

        text_titles = [
            t for t, _ in find_titles_in_text(text_chunk_1, num_lines_to_search=1)
        ]
        if text_titles:
            # TODO: Pass multiple possible titles with probabilities.
            #       (title is not "multivalued")
            maybe_text_title = text_titles[0]
            self._add_intermediate_results('title', maybe_text_title)

        _options = self.config.get(['NAME_TEMPLATE_FIELDS', 'publisher'])
        if _options:
            self.candidate_publishers = _options.get('candidates', {})

        if self.candidate_publishers:
            # TODO: Pass multiple possible publishers with probabilities.
            #       (publisher is not "multivalued")
            self._add_intermediate_results(
                'publisher',
                self._search_text_for_candidate_publisher(text_chunk_1)
            )
            self._add_intermediate_results(
                'publisher',
                self._search_text_for_copyright_publisher(text_chunk_1)
            )

    def _search_text_for_candidate_publisher(self, text):
        # TODO: [TD0130] Implement general-purpose substring matching/extraction.
        result = find_publisher(text, self.candidate_publishers)
        return result

    def _search_text_for_copyright_publisher(self, text):
        # TODO: [TD0130] Implement general-purpose substring matching/extraction.
        possible_publishers = find_publisher_in_copyright_notice(text)
        if not possible_publishers:
            return None

        # TODO: [cleanup] ..
        result = find_publisher(possible_publishers, self.candidate_publishers)
        return result

    def _extract_leading_text_chunk(self, chunk_ratio):
        assert chunk_ratio >= 0, 'Argument chunk_ratio is negative'

        # Chunk #1: from BEGINNING to (BEGINNING + CHUNK_SIZE)
        _chunk1_start = 1
        _chunk1_end = int(self.num_text_lines * chunk_ratio)
        if _chunk1_end < 1:
            _chunk1_end = 1
        text = textutils.extract_lines(self.text, firstline=_chunk1_start,
                                       lastline=_chunk1_end)
        return text

    @classmethod
    def check_dependencies(cls):
        return True


def find_titles_in_text(text, num_lines_to_search):
    # Add all lines that aren't all whitespace or all dashes, from the
    # first to line number "num_lines_to_search".
    # The first line is assigned probability 1, probabilities decrease for
    # for each line until line number "num_lines_to_search" with probability 0.1.
    assert isinstance(num_lines_to_search, int) and num_lines_to_search > 0

    titles = list()
    line_count = 0
    for line in text.splitlines():
        if line_count == num_lines_to_search:
            break

        if not line.strip():
            continue

        if not line.replace('-', ''):
            # TODO: [TD0130] Improve matching irrelevant lines to be ignored.
            continue

        score = (num_lines_to_search - line_count) / num_lines_to_search
        # TODO: Set probability dynamically ..
        # self._add_intermediate_results(
        #     'title', self._wrap_generic_title(line, score)
        # )
        titles.append((line, score))

        line_count += 1

    return titles


def find_publisher(text, candidates):
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    text = text.lower()
    for repl, patterns in candidates.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return repl
    return None
