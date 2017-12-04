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
import urllib

try:
    import chardet
except ImportError:
    chardet = None

from util import sanity


def extract_digits(string):
    """
    Extracts and returns digits from a Unicode string, as a Unicode string.
    """
    sanity.check_internal_string(string)

    digits = ''.join(c for c in string if c.isdigit())
    return digits if digits.strip() else ''


def autodetect_decode(string):
    """
    Tries to decode a string with an unknown encoding to a Unicode str.

    Unicode strings are passed through as-is.

    Args:
        string: The string to decode as a Unicode str or a bytestring.

    Returns:
        The given string decoded to an ("internal") Unicode string.
    Raises:
        ValueError: Autodetection and/or decoding was unsuccessful because
                    the given string is None or not a string type,
                    or the "chardet" module is not available.
    """
    if isinstance(string, str):
        return string

    # Guard against chardet "expects a bytes object, not a unicode object".
    # Although this check probably only applies if given a non-string arg.
    if not isinstance(string, bytes):
        raise TypeError('Module "chardet" expects bytestrings')

    if string == b'':
        return ''

    if chardet is None:
        raise ValueError('Required module "chardet" is not available!')

    detected_encoding = chardet.detect(string)
    if detected_encoding and 'encoding' in detected_encoding:
        try:
            string = string.decode(detected_encoding['encoding'])
        except ValueError:
            raise ValueError('Unable to autodetect encoding and decode string')

    sanity.check_internal_string(string)
    return string


def extract_lines(text, firstline, lastline):
    """
    Extracts a range of text lines from a Unicode string.

    The line boundaries are a superset of "universal newlines" as defined here;
        https://docs.python.org/3/library/stdtypes.html#str.splitlines

    Any trailing newlines are trimmed.

    Args:
        text: Text to extract lines from, as a Unicode string.
        firstline: First line to include, as a non-negative integer.
        lastline: Last line to include, as a non-negative integer.

    Returns:
        If 'text' is a Unicode str; lines between 'first_line' and 'last_line'.
        None if 'text' is None.
    Raises:
        EncodingBoundaryViolation: Argument 'text' is not a Unicode string.
        AWAssertionError: Either 'first_line' or 'last_line' is negative.
    """
    if text is None:
        return text

    sanity.check_internal_string(text)
    assert firstline >= 0, 'Argument first_line is negative'
    assert lastline >= 0, 'Argument last_line is negative'

    lines = text.splitlines(keepends=True)
    if lastline > len(lines):
        lastline = len(lines)

    if firstline > lastline:
        firstline = lastline

    extracted = lines[firstline:lastline]
    return ''.join(extracted)


def extractlines_do(callback, text, fromline, toline):
    """
    Perform an action within certain lines of some given text.

    Args:
        callback: The callable to pass the extracted lines to.
        text: The Text to extract lines from, as a Unicode string.
        fromline: First line number of the text to be extracted, as an integer.
        toline: Last line number of the text to be extracted, as an integer.

    Returns:
        The result of calling "callback" with the contents in "text" between
        lines "fromline" and "toline".
    """
    assert callable(callback), 'Argument "callback" must be callable'
    assert isinstance(fromline, int), 'Expected "fromline" of type int'
    assert isinstance(toline, int), 'Expected "toline" of type int'

    lines = extract_lines(text, fromline, toline)
    return callback(lines)


__ordinal_number_patterns = [
    (1, r'1st|first'),             (2, r'2nd|second'),
    (3, r'3rd|third'),             (4, r'4th|fourth'),
    (5, r'5th|fifth'),             (6, r'6th|sixth'),
    (7, r'7th|seventh'),           (8, r'8th|eighth'),
    (9, r'9th|ninth'),             (10, r'10th|tenth'),
    (11, r'11th|eleventh'),        (12, r'12th|twelfth'),
    (13, r'13th|thirteenth'),      (14, r'14th|fourteenth'),
    (15, r'15th|fifteenth'),       (16, r'16th|sixteenth'),
    (17, r'17th|seventeenth'),     (18, r'18th|eighteenth'),
    (19, r'19th|nineteenth'),      (20, r'20th|twentieth'),
    (21, r'21th|twenty-?first'),   (22, r'22th|twenty-?second'),
    (23, r'23th|twenty-?third'),   (24, r'24th|twenty-?fourth'),
    (25, r'25th|twenty-?fifth'),   (26, r'26th|twenty-?sixth'),
    (27, r'27th|twenty-?seventh'), (28, r'28th|twenty-?eighth'),
    (29, r'29th|twenty-?ninth'),   (30, r'30th|thirtieth'),
]


RE_ORDINALS = {}


def compiled_ordinal_regexes():
    """
    Returns:
        Dictionary of compiled regular expressions keyed by positive integers,
        each storing patterns for matching ordinal strings of that number.
    """
    global RE_ORDINALS
    if not RE_ORDINALS:
        for _number, _patterns in __ordinal_number_patterns:
            RE_ORDINALS[_number] = re.compile(_patterns, re.IGNORECASE)
    return RE_ORDINALS


def urldecode(string):
    return urllib.parse.unquote(string)
