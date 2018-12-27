# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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
from core.truths import known_data_loader
from core.metadata.normalize import cleanup_full_title
from util.text import collapse_whitespace
from util.text import regexbatch
from util.text import remove_blacklisted_lines
from util.text import TextChunker
from util.text.filter import RegexLineFilter
from util.text.patternmatching import find_publisher_in_copyright_notice


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
    r'^\w$',
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
            'multivalued': 'false',
            'mapped_fields': [
                # TODO: [TD0166] Set weights dynamically
                {'WeightedMapping': {'field': 'Title', 'weight': '0.1'}},
            ],
            'generic_field': 'title'
        },
        'datetime': {
            'coercer': 'aw_timedate',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'DateTime', 'weight': '0.25'}},
                {'WeightedMapping': {'field': 'Date', 'weight': '0.25'}},
            ],
            'generic_field': 'date_created',
        },
        'publisher': {
            'coercer': 'aw_string',
            'multivalued': 'false',
            'mapped_fields': [
                {'WeightedMapping': {'field': 'Publisher', 'weight': '1'}},
            ],
            'generic_field': 'publisher',
        }
    }

    def __init__(self, fileobject, config, request_data_callback):
        super().__init__(fileobject, config, request_data_callback)

    def analyze(self):
        maybe_text = self.request_any_textual_content()
        if not maybe_text:
            return

        filtered_text = remove_blacklisted_lines(maybe_text, BLACKLISTED_TEXTLINES)
        normalized_whitespace_text = collapse_whitespace(filtered_text)

        # Arbitrarily search the text in chunks of 10%
        text_chunks = TextChunker(
            text=normalized_whitespace_text,
            chunk_to_text_ratio=0.02
        )
        leading_text = text_chunks.leading

        # TODO: Search text for datetime information.

        # TODO: [incomplete] Search more than 1 line! Handle multiple matches.
        text_titles = [
            t for t, _ in find_titles_in_text(leading_text, num_lines_to_search=1)
        ]
        if text_titles:
            # TODO: [TD0190] Bundle single fields like this into "records".
            # When attempting to find a "more likely" field value among
            # multiple possible candidate values, operate on the records. This
            # should help with comparing the candidate values against values
            # from other sources and also with other methods that look at
            # relationships between fields within a single record and also
            # betweeen multiple records.
            maybe_text_title = text_titles[0]
            clean_title = cleanup_full_title(maybe_text_title)
            if clean_title:
                self._add_intermediate_results('title', clean_title)

        literal_lookup_dict = known_data_loader.literal_lookup_dict('publisher')
        if literal_lookup_dict:
            # TODO: Pass multiple possible publishers with probabilities.
            #       (publisher is not "multivalued")
            result = self._search_text_for_copyright_publisher(leading_text, literal_lookup_dict)
            if result:
                self._add_intermediate_results('publisher', result)
            else:
                result = self._search_text_for_candidate_publisher(leading_text, literal_lookup_dict)
                if result:
                    self._add_intermediate_results('publisher', result)
                else:
                    regex_lookup_dict = known_data_loader.regex_lookup_dict('publisher')
                    if regex_lookup_dict:
                        # TODO: Pass multiple possible publishers with probabilities.
                        #       (publisher is not "multivalued")
                        result = self._search_text_for_copyright_publisher(leading_text, regex_lookup_dict)
                        if result:
                            self._add_intermediate_results('publisher', result)
                        else:
                            result = self._search_text_for_candidate_publisher(leading_text, regex_lookup_dict)
                            if result:
                                self._add_intermediate_results('publisher', result)

    def _search_text_for_candidate_publisher(self, text, patterns):
        # TODO: [TD0130] Implement general-purpose substring matching/extraction.
        result = find_publisher(text, patterns)
        return result

    def _search_text_for_copyright_publisher(self, text, patterns):
        # TODO: [TD0130] Implement general-purpose substring matching/extraction.
        possible_publishers = find_publisher_in_copyright_notice(text)
        if not possible_publishers:
            return None

        # TODO: [cleanup] ..
        result = find_publisher(possible_publishers, patterns)
        return result

    @classmethod
    def dependencies_satisfied(cls):
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
    replacement = regexbatch.find_replacement_value(candidates, text)
    if replacement:
        return replacement

    return None
