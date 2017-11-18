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

from core import types
from util import textutils


RE_EDITION = re.compile(
    r'([0-9])+\s?((st|nd|rd|th)\s?|(e|ed.?|edition))\b',
    re.IGNORECASE
)


def find_edition(text):
    # TODO: [TD0118] Refactor and improve robustness.
    text = text.replace('_', ' ')
    text = text.replace('-', ' ')

    matches = []
    for _num, _re_pattern in textutils.compiled_ordinal_regexes().items():
        m = _re_pattern.search(text)
        if m:
            matches.append(_num)

    if matches:
        # Handle case where "25th" matches "5th" and returns 5.
        # Store all matches and return the highest matched number.
        matches = sorted(matches, reverse=True)
        return matches[0]

    match = RE_EDITION.search(text)
    if match:
        e = match.group(1)
        try:
            edition = types.AW_INTEGER(e)
            return edition
        except types.AWTypeError:
            pass

    return None
