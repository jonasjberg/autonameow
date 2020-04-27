# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

"""
Various content-agnostic utilities related to substrings.
"""

import collections

from util.text.regexcache import RegexCache


# Use two different types of separator_counts;  "SPACE" and "SEPARATOR".
#
# Example filename:   "The-Artist_01_Great-Tune.mp4"
#                         ^      ^  ^     ^
#                     space   separator_counts  space
#
# Splitting the filename by "SEPARATOR" gives some arbitrary "fields".
#
#                     "The-Artist"   "01"   "Great-Tune"
#                       Field #1      #2      Field #3
#
# Splitting the filename by "SPACE" typically gives words.
#
#                     "The"   "Artist"   "01"   "Great"   "Tune"

# TODO: Let the user specify this in the configuration file.
PREFERRED_FILENAME_CHAR_SPACE = '-'
PREFERRED_FILENAME_CHAR_SEPARATOR = '_'

Separator = collections.namedtuple('Separator', 'value count')


def find_separators(s):
    assert isinstance(s, str)

    RE_UNICODE_WORDS = r'[^\W_]'
    regex = RegexCache(RE_UNICODE_WORDS)

    non_words = regex.split(s)
    seps = [w for w in non_words if w and len(w) >= 1]
    return seps


def separator_counts(s, max_count=5):
    assert isinstance(s, str)

    seps = find_separators(s)

    sep_chars = list()
    for sep in seps:
        if len(sep) > 1:
            sep_chars.extend(list(sep))
        else:
            sep_chars.append(sep)

    if not sep_chars:
        return None

    sep_counter = collections.Counter(sep_chars)
    most_common = sep_counter.most_common(max_count)
    separators = [
        Separator(value, count) for value, count in most_common
    ]
    return separators


def main_separator(s):
    assert isinstance(s, str)

    counted_separators = separator_counts(s)
    if not counted_separators:
        return None

    # Sort from highest to lowest number of occurrences.
    counted_separators.sort(key=lambda x: x.count, reverse=True)

    # Detect if multiple separators are tied for most number of occurrences.
    if len(counted_separators) > 1:
        most_common_separator_chars = _get_top_tied_counts(counted_separators)
        if len(most_common_separator_chars) > 1:
            preferred_separator = _resolve_tied_count(most_common_separator_chars)
            if preferred_separator:
                return preferred_separator

    return counted_separators[0].value


def _get_top_tied_counts(counted_separators):
    """
    Given a list of tuples like;

        counted_separators = [
            ('_', 3),
            ('-', 3),
            (' ', 1),
        ]

    Returns a list of the separator values with the most count
    or all separators values with top tied counts; ['_', '-']
    """
    sorted_counted_separators = sorted(counted_separators)

    highest_count = sorted_counted_separators[0][1]
    assert isinstance(highest_count, int)

    tied_separator_values = set()
    for value, count in sorted_counted_separators:
        assert isinstance(count, int)

        if count != highest_count:
            break

        tied_separator_values.add(value)
        highest_count = count

    return list(tied_separator_values)


def _resolve_tied_count(candidate_separators):
    if ' ' in candidate_separators:
        # Prefer to use the single space.
        return ' '

    elif PREFERRED_FILENAME_CHAR_SEPARATOR in candidate_separators:
        # Use hardcoded preferred main separator character.
        return PREFERRED_FILENAME_CHAR_SEPARATOR

    elif PREFERRED_FILENAME_CHAR_SPACE in candidate_separators:
        # Use hardcoded preferred space separator character.
        return PREFERRED_FILENAME_CHAR_SPACE

    # Arbitrarily use first value after sorting as a last resort.
    return sorted(candidate_separators, key=lambda x: x[0])[0]


def smart_split(s):
    # TODO: ..
    if ' ' in s:
        return s.split(' ')

    return [s]
