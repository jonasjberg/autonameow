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
    if not strng:
        return strng
    assert isinstance(strng, str)

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
