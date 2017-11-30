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
from util.text.transform import collapse_whitespace


RE_EDITION = re.compile(
    r'([0-9])+\s?((st|nd|rd|th)\s?|(e|ed.?|edition))\b',
    re.IGNORECASE
)

# Like '\w' but without numbers (Unicode letters): '[^\W\d]'
_re_copyright_name = r'(?P<name>[^\W\d]+[\D\.]+)'
_re_copyright_symbol = r'(©|\(?[Cc]\)?)'
_re_copyright_text = r'[Cc]opyright'
_re_copyright_symbol_and_or_text = r'({CS}{SEP}{CT}|{CT}{SEP}{CS}|{CT}{SEP}|{CS}{SEP})'.format(CS=_re_copyright_symbol, CT=_re_copyright_text, SEP=' +?')
_re_copyright_year = r'(?P<year>\d{4})'
_re_copyright_years = r'(?P<year_range>\d{4}[- ]+\d{4})'

RE_COPYRIGHT_NOTICE_A = re.compile(
    '({copyright}? ?{symbol}|{symbol} ?{copyright}?) ?({year}|{years}) ?{name}'.format(
        copyright=_re_copyright_text,
        symbol=_re_copyright_symbol,
        year=_re_copyright_year,
        years=_re_copyright_years,
        name=_re_copyright_name
    ), re.IGNORECASE
)
RE_COPYRIGHT_NOTICE_B = re.compile(
    '({copyright}? ?{symbol}|{symbol} ?{copyright}?) ?{name}[,\ ]+?({year}|{years})'.format(
        copyright=_re_copyright_text,
        symbol=_re_copyright_symbol,
        year=_re_copyright_year,
        years=_re_copyright_years,
        name=_re_copyright_name
    ), re.IGNORECASE
)


# TODO: [TD0130] Implement general-purpose substring matching/extraction.


def find_edition(text):
    """
    Extract an "edition", like "1st Edition", from a Unicode text string.

    Args:
        text: Unicode string to search.

    Returns:
        Any found edition as an integer or None if no edition was found.
    """
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


def find_publisher_in_copyright_notice(string):
    text = collapse_whitespace(string)
    text = text.replace(',', ' ')
    text = text.strip()

    if 'copyright' not in text.lower():
        return None

    # endmarker = text.find('and/or')
    # if endmarker > 1:
    #     text = text[:endmarker]

    matches = RE_COPYRIGHT_NOTICE_A.search(text)
    if not matches:
        matches = RE_COPYRIGHT_NOTICE_B.search(text)
        if not matches:
            return None

    match = matches.group('name')

    return match.strip()
