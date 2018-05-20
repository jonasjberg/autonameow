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


def separator_counts(s, max_count=5):
    assert isinstance(s, str)

    RE_UNICODE_WORDS = r'[^\W_]'
    regex = RegexCache(RE_UNICODE_WORDS)

    non_words = regex.split(s)
    seps = [w for w in non_words if w is not None and len(w) >= 1]

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
    counted_separators = separator_counts(s)
    if not counted_separators:
        return None

    # Detect if first- and second-most common separator_counts have an equal
    # number of occurrences and resolve any tied count separately.
    if len(counted_separators) >= 2:
        if counted_separators[0].count == counted_separators[1].count:
            separator_first = counted_separators[0].value
            separator_second = counted_separators[1].value
            return _resolve_tied_count([separator_first, separator_second])

    if counted_separators:
        try:
            return counted_separators[0].value
        except IndexError:
            return ''

    return None


def _resolve_tied_count(candidate_separators):
    if not candidate_separators:
        return list()

    # Prefer to use the single space.
    if ' ' in candidate_separators:
        return ' '
    elif PREFERRED_FILENAME_CHAR_SEPARATOR in candidate_separators:
        # Use hardcoded preferred main separator character.
        return PREFERRED_FILENAME_CHAR_SEPARATOR
    elif PREFERRED_FILENAME_CHAR_SPACE in candidate_separators:
        # Use hardcoded preferred space separator character.
        return PREFERRED_FILENAME_CHAR_SPACE

    # Last resort arbitrarily uses first value after sorting.
    return sorted(candidate_separators, key=lambda x: x[0])[0]


def split_smart(s):
    # TODO: ..
    pass
