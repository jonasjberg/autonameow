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
from functools import lru_cache

from util import coercers
from util.text.transform import collapse_whitespace


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


def ordinal_indicator(number):
    """
    Returns the "ordinal indicator" suffix for a given cardinal number.

    E.G. returns 'st' given the number 1, which could be used to make '1st'.

    Args:
        number: Cardinal number as a type that can be converted to type int.

    Returns:
        The ordinal suffix for the given number as a Unicode string.

    Raises:
        ValueError: The given number could not be converted to type int.
    """
    number = abs(int(number))
    if number % 100 in (11, 12, 13):
        return 'th'

    return {
        1: 'st',
        2: 'nd',
        3: 'rd',
    }.get(number % 10, 'th')


def ordinalize(number):
    """
    Returns the ordinal string version of a given cardinal number.

    E.G. returns '1st' given the number 1.

    Args:
        number: Cardinal number as a type that can be converted to type int.

    Returns:
        The given number as a Unicode string ordinal.

    Raises:
        ValueError: The given number could not be converted to type int.
    """
    return '{!s}{!s}'.format(number, ordinal_indicator(number))


@lru_cache()
def compiled_ordinal_regexes():
    re_ordinals = dict()
    for number, regexp in enumerate(_ORDINAL_NUMBER_PATTERNS, start=1):
        compiled_regex = re.compile(regexp, re.IGNORECASE)
        re_ordinals[number] = compiled_regex
    return re_ordinals


@lru_cache()
def compiled_ordinal_edition_regexes():
    re_ordinal_edition = dict()
    for number, regexp in enumerate(_ORDINAL_NUMBER_PATTERNS, start=1):
        ordinal_edition_pattern = regexp + r' ?(edition|ed\.?|e)'
        compiled_regex = re.compile(ordinal_edition_pattern, re.IGNORECASE)
        re_ordinal_edition[number] = compiled_regex
    return re_ordinal_edition


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


_re_copyright_symbol_text_combos = r'({SYM}{SEP}{TXT}|{TXT}{SEP}{SYM}|{SYM}{SEP})'.format(
    SYM=r'\(c\)',
    TXT=r'copyright',
    SEP=' ?',
)
_re_copyright_year = r'(?P<year>\d{4})'
_re_copyright_years = r'(?P<year_range>\d{4}[- ,]+\d{4})'

# Like '\w' but without numbers (Unicode letters): '[^\W\d]'
_re_copyright_name = r'(?P<name>[^\W\d]+[\D\.]+)'

RE_COPYRIGHT_NOTICE_A = re.compile(
    r'{symbol_text_combos} ?({year}|{years})[, ]+?{name}'.format(
        symbol_text_combos=_re_copyright_symbol_text_combos,
        year=_re_copyright_year,
        years=_re_copyright_years,
        name=_re_copyright_name
    ), re.IGNORECASE
)
RE_COPYRIGHT_NOTICE_B = re.compile(
    r'{symbol_text_combos} ?{name}[, ]+?({year}|{years})'.format(
        symbol_text_combos=_re_copyright_symbol_text_combos,
        year=_re_copyright_year,
        years=_re_copyright_years,
        name=_re_copyright_name
    ), re.IGNORECASE
)


def find_publisher_in_copyright_notice(strng):
    assert isinstance(strng, str)

    text = collapse_whitespace(strng)
    text = text.replace(',', ' ')
    text = text.replace('©', '(c)')
    text = text.strip()
    if not text:
        return None

    matches = RE_COPYRIGHT_NOTICE_A.search(text)
    if not matches:
        matches = RE_COPYRIGHT_NOTICE_B.search(text)
        if not matches:
            return None

    match = matches.group('name')
    return match.strip()
