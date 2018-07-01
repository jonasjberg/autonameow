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

from util import coercers
from util.text.transform import collapse_whitespace


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
    r'({copyright}? ?{symbol}|{symbol} ?{copyright}?) ?{name}[, ]+?({year}|{years})'.format(
        copyright=_re_copyright_text,
        symbol=_re_copyright_symbol,
        year=_re_copyright_year,
        years=_re_copyright_years,
        name=_re_copyright_name
    ), re.IGNORECASE
)

RE_EDITION = re.compile(
    r'([0-9])+\s?(e\b|ed\.?|edition)',
    re.IGNORECASE
)

# TODO: [TD0130] Implement general-purpose substring matching/extraction.
_ORDINAL_NUMBER_PATTERNS = [
    r'(1st|first)',
    r'(2nd|second)',
    r'(3rd|third)',
    r'(4th|fourth)',
    r'(5th|fifth)',
    r'(6th|sixth)',
    r'(7th|seventh)',
    r'(8th|eighth)',
    r'(9th|ninth)',
    r'(10th|tenth)',
    r'(11th|eleventh)',
    r'(12th|twelfth)',
    r'(13th|thirteenth)',
    r'(14th|fourteenth)',
    r'(15th|fifteenth)',
    r'(16th|sixteenth)',
    r'(17th|seventeenth)',
    r'(18th|eighteenth)',
    r'(19th|nineteenth)',
    r'(20th|twentieth)',
    r'(21th|twenty-?first)',
    r'(22th|twenty-?second)',
    r'(23th|twenty-?third)',
    r'(24th|twenty-?fourth)',
    r'(25th|twenty-?fifth)',
    r'(26th|twenty-?sixth)',
    r'(27th|twenty-?seventh)',
    r'(28th|twenty-?eighth)',
    r'(29th|twenty-?ninth)',
    r'(30th|thirtieth)',
]


RE_ORDINALS = dict()


def compiled_ordinal_regexes():
    global RE_ORDINALS
    if not RE_ORDINALS:
        for number, regexp in enumerate(_ORDINAL_NUMBER_PATTERNS, start=1):
            compiled_regex = re.compile(regexp, re.IGNORECASE)
            RE_ORDINALS[number] = compiled_regex
    return RE_ORDINALS


RE_ORDINAL_EDITION = dict()


def compiled_ordinal_edition_regexes():
    global RE_ORDINAL_EDITION
    if not RE_ORDINAL_EDITION:
        for number, regexp in enumerate(_ORDINAL_NUMBER_PATTERNS, start=1):
            ordinal_edition_pattern = regexp + r' ?(edition|ed\.?|e)'
            compiled_regex = re.compile(ordinal_edition_pattern, re.IGNORECASE)
            RE_ORDINAL_EDITION[number] = compiled_regex
    return RE_ORDINAL_EDITION


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
        string (str): Text to search as a Unicode string.

    Returns:
        Any found edition and modified text as a (int, str) tuple.

    Raises:
        AssertionError: Given text is not an instance of 'str'.
    """
    # TODO: [TD0192] Detect and extract editions from titles
    if not string:
        return None, string

    assert isinstance(string, str)

    def _find_editions(ordinal_regexes):
        _matches = list()
        for number, regex in ordinal_regexes.items():
            m = regex.search(string)
            if m:
                _matches.append((number, regex))

        return _matches

    matches = _find_editions(compiled_ordinal_edition_regexes())
    if not matches:
        # Try again with less "specific" regexes.
        matches = _find_editions(compiled_ordinal_regexes())

    if matches:
        # Handle case where "25th" matches "5th" and returns 5.
        # Use the highest matched number.
        matches = sorted(matches, key=lambda x: x[0], reverse=True)
        match_to_use = matches[0]
        matched_number, matched_regex = match_to_use
        modified_text = re.sub(matched_regex, '', string)
        return matched_number, modified_text

    # Try a third approach.
    match = RE_EDITION.search(string)
    if match:
        ed = match.group(1)
        try:
            edition = coercers.AW_INTEGER(ed)
        except coercers.AWTypeError:
            pass
        else:
            modified_text = re.sub(RE_EDITION, '', string)
            return edition, modified_text

    return None, string


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
