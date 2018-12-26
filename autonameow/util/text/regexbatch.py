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

import re


def replace(regex_replacement_tuples, strng, ignore_case=False):
    assert isinstance(strng, str)

    if not strng:
        return strng

    re_flags = 0
    if ignore_case:
        re_flags |= re.IGNORECASE

    matches = list()
    for regex, replacement in regex_replacement_tuples:
        match = re.search(regex, strng, re_flags)
        if match:
            matches.append((regex, replacement))

    sorted_by_longest_replacement = sorted(
        matches, key=lambda x: len(x[1]), reverse=True
    )
    for regex, replacement in sorted_by_longest_replacement:
        strng = re.sub(regex, replacement, strng, flags=re_flags)

    return strng


def find_longest_match(regexes, strng, ignore_case=False):
    """
    Searches a string with a list of regular expressions for the longest match.

    NOTE: Does not handle groups!

    Args:
        regexes: List or set of regular expressions as Unicode strings or
                 compiled regular expressions.
        strng (str): The string to search.
        ignore_case: Whether to ignore letter case.

    Returns:
        The longest match found when searching the string with all given
        regular expressions, as a Unicode string.
    """
    assert isinstance(strng, str)

    if not strng:
        return None

    re_flags = 0
    if ignore_case:
        re_flags |= re.IGNORECASE

    matches = list()
    for regex in regexes:
        matches.extend(re.findall(regex, strng, re_flags))

    if matches:
        sorted_by_longest_match = sorted(
            matches, key=lambda x: len(x), reverse=True
        )
        return sorted_by_longest_match[0]

    return None
