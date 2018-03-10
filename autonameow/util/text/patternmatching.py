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

from core import types
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
    r'({copyright}? ?{symbol}|{symbol} ?{copyright}?) ?({year}|{years}) ?{name}'.format(
        copyright=_re_copyright_text,
        symbol=_re_copyright_symbol,
        year=_re_copyright_year,
        years=_re_copyright_years,
        name=_re_copyright_name
    ), re.IGNORECASE
)
RE_COPYRIGHT_NOTICE_B = re.compile(
    r'({copyright}? ?{symbol}|{symbol} ?{copyright}?) ?{name}[,\ ]+?({year}|{years})'.format(
        copyright=_re_copyright_text,
        symbol=_re_copyright_symbol,
        year=_re_copyright_year,
        years=_re_copyright_years,
        name=_re_copyright_name
    ), re.IGNORECASE
)


# TODO: [TD0130] Implement general-purpose substring matching/extraction.


_ORDINAL_NUMBER_PATTERNS = [
    (1, r'1st|first'),
    (2, r'2nd|second'),
    (3, r'3rd|third'),
    (4, r'4th|fourth'),
    (5, r'5th|fifth'),
    (6, r'6th|sixth'),
    (7, r'7th|seventh'),
    (8, r'8th|eighth'),
    (9, r'9th|ninth'),
    (10, r'10th|tenth'),
    (11, r'11th|eleventh'),
    (12, r'12th|twelfth'),
    (13, r'13th|thirteenth'),
    (14, r'14th|fourteenth'),
    (15, r'15th|fifteenth'),
    (16, r'16th|sixteenth'),
    (17, r'17th|seventeenth'),
    (18, r'18th|eighteenth'),
    (19, r'19th|nineteenth'),
    (20, r'20th|twentieth'),
    (21, r'21th|twenty-?first'),
    (22, r'22th|twenty-?second'),
    (23, r'23th|twenty-?third'),
    (24, r'24th|twenty-?fourth'),
    (25, r'25th|twenty-?fifth'),
    (26, r'26th|twenty-?sixth'),
    (27, r'27th|twenty-?seventh'),
    (28, r'28th|twenty-?eighth'),
    (29, r'29th|twenty-?ninth'),
    (30, r'30th|thirtieth'),
]


_ORDINAL_EDITION_NUMBER_PATTERNS = [
    (1, r'1st|first( Edition)?'),
    (2, r'2nd|second( Edition)?'),
    (3, r'3rd|third( Edition)?'),
    (4, r'4th|fourth( Edition)?'),
    (5, r'5th|fifth( Edition)?'),
    (6, r'6th|sixth( Edition)?'),
    (7, r'7th|seventh( Edition)?'),
    (8, r'8th|eighth( Edition)?'),
    (9, r'9th|ninth( Edition)?'),
    (10, r'10th|tenth( Edition)?'),
    (11, r'11th|eleventh( Edition)?'),
    (12, r'12th|twelfth( Edition)?'),
    (13, r'13th|thirteenth( Edition)?'),
    (14, r'14th|fourteenth( Edition)?'),
    (15, r'15th|fifteenth( Edition)?'),
    (16, r'16th|sixteenth( Edition)?'),
    (17, r'17th|seventeenth( Edition)?'),
    (18, r'18th|eighteenth( Edition)?'),
    (19, r'19th|nineteenth( Edition)?'),
    (20, r'20th|twentieth( Edition)?'),
    (21, r'21th|twenty-?first( Edition)?'),
    (22, r'22th|twenty-?second( Edition)?'),
    (23, r'23th|twenty-?third( Edition)?'),
    (24, r'24th|twenty-?fourth( Edition)?'),
    (25, r'25th|twenty-?fifth( Edition)?'),
    (26, r'26th|twenty-?sixth( Edition)?'),
    (27, r'27th|twenty-?seventh( Edition)?'),
    (28, r'28th|twenty-?eighth( Edition)?'),
    (29, r'29th|twenty-?ninth( Edition)?'),
    (30, r'30th|thirtieth( Edition)?'),
]


RE_ORDINALS = dict()


def compiled_ordinal_regexes():
    """
    Returns:
        Dictionary of compiled regular expressions keyed by positive integers,
        each storing patterns for matching ordinal strings of that number.
    """
    global RE_ORDINALS
    if not RE_ORDINALS:
        for number, regexp in _ORDINAL_NUMBER_PATTERNS:
            RE_ORDINALS[number] = re.compile(regexp, re.IGNORECASE)
    return RE_ORDINALS


RE_EDITION_ORDINALS = dict()


def compiled_ordinal_edition_regexes():
    global RE_EDITION_ORDINALS
    if not RE_EDITION_ORDINALS:
        for number, regexp in _ORDINAL_EDITION_NUMBER_PATTERNS:
            compiled_regex = re.compile(regexp, re.IGNORECASE)
            RE_EDITION_ORDINALS[number] = compiled_regex
    return RE_EDITION_ORDINALS


def find_and_extract_edition(string):
    """
    Extracts any "edition-like" substrings from a string.

    Searches the given text for any "edition-like" substrings and returns a
    tuple with the match as an integer and the given string *without* the match.

    Example:

        edition, modified_string = find_and_extract_edition('foo 1st bar')
        assert edition == 1
        assert modified_string == 'foo  bar'

    Args:
        string: Text to search as a Unicode string.

    Returns:
        Any found edition and modified text as a (int, str) tuple.
    """
    text = str(string)

    matches = []
    for number, regex in compiled_ordinal_edition_regexes().items():
        m = regex.search(text)
        if m:
            matches.append((number, regex))

    if matches:
        # Handle case where "25th" matches "5th" and returns 5.
        # Use the highest matched number.
        matches = sorted(matches, key=lambda x: x[0], reverse=True)
        match_to_use = matches[0]
        matched_number, matched_regex = match_to_use
        modified_text = re.sub(matched_regex, '', text)

        # Strip any extra trailing edition.
        # TODO: Handle this in the matched regex ..
        modified_text = re.sub(r' ?Edition', '', modified_text, re.IGNORECASE)

        return matched_number, modified_text

    _RE_EDITION = re.compile(
        r'([0-9])+\s?((st|nd|rd|th)\s?|(ed?\.?|edition))[\b]?',
        re.IGNORECASE
    )
    match = _RE_EDITION.search(text)
    if match:
        e = match.group(1)
        try:
            edition = types.AW_INTEGER(e)
        except types.AWTypeError:
            pass
        else:
            modified_text = re.sub(_RE_EDITION, '', text)
            return edition, modified_text

    return None, None


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
    for _num, _re_pattern in compiled_ordinal_regexes().items():
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
