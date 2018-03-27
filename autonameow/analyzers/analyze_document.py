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
from core.model.normalize import normalize_full_title
from util.text.filter import RegexLineFilter
from util.text.patternmatching import find_publisher_in_copyright_notice
from util.text import (
    collapse_whitespace,
    remove_blacklisted_lines,
    TextChunker
)


# TODO: [TD0094] Search text for DOIs and query external services
# Example DOI: `10.1109/TPDS.2010.125`. Could be used to query external
# services for publication metadata, as with ISBN-numbers.


BLACKLISTED_TEXTLINES = frozenset([
    'Advanced PDF Repair at http://www.datanumen.com/apdfr/',
    'Brought to you by:',
    'freepdf-books.com',
    'Get More Refcardz! Visit refcardz.com',
    'http://freepdf-books.com',
    'www.itbookshub.com',
    'Preface:',
    'Table of Contents',
    'This page intentionally left blank',
    'Unknown',
    'www.freepdf-books.com',
    'www.allitebooks.com',
    'www.it-ebooks.info',
    'free ebooks wwwebook777com',
    'free ebooks www.ebook777.com',
    'free ebooks ==> www.ebook777.com',
    'Free ebooks ==> www.ebook777.com',
])


title_filter = RegexLineFilter([
    r'^[\.=-]+$',
    r'.*cncmanual\.com.*',
    r'matter material after the index\.? Please use the Bookmarks',
    r'and Contents at a Glance links to access them\.?',
    r'Contents at a Glance',
    r'about the author.*',
    r'about the technical reviewer.*',
    r'acknowledgments.*',
    r'for your convenience .* has placed some of the front',
    r'.*freepdf-books\.com.*',
    r'introduction.*',
    r'index.?[0-9]+',
    r'.*chapter ?[0-9]+.*',
    r'.*www\.?ebook777\.?com.*',
], ignore_case=True)


class DocumentAnalyzer(BaseAnalyzer):
    RUN_QUEUE_PRIORITY = 0.5
    HANDLES_MIME_TYPES = ['application/pdf', 'text/*']
    FIELD_LOOKUP = {
        'title': {
            'coercer': 'aw_string',
            'mapped_fields': [
                # TODO: [TD0166] Set weights dynamically
                {'WeightedMapping': {'field': 'Title', 'weight': '1'}},
            ],
            'generic_field': 'title'
        },
        'datetime': {
            'coercer': 'aw_timedate',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'weight': '0.25'}},
                {'WeightedMapping': {'field': 'Date', 'weight': '0.25'}},
            ],
            'generic_field': 'date_created',
        },
        'publisher': {
            'coercer': 'aw_string',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Publisher', 'weight': '1'}},
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
        maybe_text = self.request_any_textual_content()
        if not maybe_text:
            return

        filtered_text = remove_blacklisted_lines(maybe_text, BLACKLISTED_TEXTLINES)
        normalized_whitespace_text = collapse_whitespace(filtered_text)
        self.text = normalized_whitespace_text
        self.num_text_lines = len(self.text.splitlines())

        # Arbitrarily search the text in chunks of 10%
        text_chunks = TextChunker(self.text, chunk_to_text_ratio=0.1)
        leading_text = text_chunks.leading

        # TODO: Search text for datetime information.

        # TODO: [incomplete] Search more than 1 line! Handle multiple matches.
        text_titles = [
            t for t, _ in find_titles_in_text(leading_text, num_lines_to_search=1)
        ]
        if text_titles:
            # TODO: Pass multiple possible titles with probabilities.
            #       (title is not "multivalued")
            self.log.debug('TEXTTITLES: ' + str(text_titles))
            maybe_text_title = text_titles[0]
            normalized_title = normalize_full_title(maybe_text_title)
            if normalized_title:
                self._add_intermediate_results('title', normalized_title)

        _options = self.config.get(['NAME_TEMPLATE_FIELDS', 'publisher'])
        if _options:
            self.candidate_publishers = _options.get('candidates', {})

        if self.candidate_publishers:
            # TODO: Pass multiple possible publishers with probabilities.
            #       (publisher is not "multivalued")
            self._add_intermediate_results(
                'publisher',
                self._search_text_for_candidate_publisher(leading_text)
            )
            self._add_intermediate_results(
                'publisher',
                self._search_text_for_copyright_publisher(leading_text)
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

    @classmethod
    def check_dependencies(cls):
        return True


def find_titles_in_text(text, num_lines_to_search):
    # Add all lines that aren't all whitespace or all dashes, from the
    # first to line number "num_lines_to_search".
    # The first line is assigned weight 1, weights decrease for
    # for each line until line number "num_lines_to_search" with weight 0.1.
    assert isinstance(num_lines_to_search, int) and num_lines_to_search > 0

    titles = list()
    line_count = 0
    for line in text.splitlines():
        if line_count == num_lines_to_search:
            break

        if not line.strip():
            continue

        filtered_line = title_filter(line)
        if not filtered_line:
            continue

        score = (num_lines_to_search - line_count) / num_lines_to_search
        # TODO: Set weight dynamically ..
        # self._add_intermediate_results(
        #     'title', self._wrap_generic_title(line, score)
        # )
        titles.append((filtered_line, score))

        line_count += 1

    return titles


def find_publisher(text, candidates):
    # TODO: [TD0130] Implement general-purpose substring matching/extraction.
    text = text.lower()
    for replacement, patterns in candidates.items():
        for pattern in patterns:
            if re.search(pattern, text):
                return replacement
    return None
