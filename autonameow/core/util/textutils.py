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

try:
    import chardet
except (ImportError, ModuleNotFoundError):
    chardet = None

from core import util


def extract_digits(string):
    """
    Extracts digits from text string.
    :param string: string to extract digits from
    :return: digits in string or None if string contains no digits
    """
    # TODO: [TD0004] Enforce encoding boundary for extracted data.
    string = util.decode_(string)
    digits = ''
    for char in string:
        if char.isdigit():
            digits += char

    return digits if digits.strip() else None


def remove_nonbreaking_spaces(text):
    return text.replace('\xa0', ' ')


def indent(text, amount=4, ch=' '):
    """
    Indents (multi-line) text by a specified amount.

    Shifts text right by a given "amount" (default: 4) using the character
    "ch" for padding (defaults to ' ').

    Based on this post; https://stackoverflow.com/a/8348914/7802196

    Args:
        text: Single or multi-line text to indent, as a Unicode str.
        amount: Optional padding character ('ch') multiple, as an integer.
        ch: Optional character to use for padding.

    Returns:
        An indented version of the given text as an Unicode str.
    """
    assert isinstance(text, str)
    assert isinstance(amount, int) and amount > 0
    assert isinstance(ch, str)

    padding = amount * ch
    return ''.join(padding + line for line in text.splitlines(True))


def autodetect_decode(string):
    """
    Try to decode a string with an unknown encoding to a Unicode str.

    Args:
        string: The string to decode.

    Returns:
        The given string decoded to an "internal" Unicode string.
    Raises:
        ValueError: The autodetection and/or decoding was unsuccessful.
    """
    if isinstance(string, str):
        return string

    if chardet is None:
        raise ValueError('Required module "chardet" is not available!')

    # chardet "expects a bytes object, not a unicode object".
    assert(isinstance(string, bytes))

    detected_encoding = chardet.detect(string)
    if detected_encoding and 'encoding' in detected_encoding:
        try:
            string = string.decode(detected_encoding['encoding'])
        except ValueError:
            raise ValueError('Unable to autodetect encoding and decode string')

    return string


def extract_lines(text, first_line, last_line):
    """
    Extracts a range of text lines from a Unicode string.

    The line boundaries are a superset of "universal newlines" as defined here;
        https://docs.python.org/3/library/stdtypes.html#str.splitlines

    Any trailing newlines are trimmed.

    Args:
        text: Text to extract lines from, as a Unicode string.
        first_line: First line to include, as a non-negative integer.
        last_line: Last line to include, as a non-negative integer.

    Returns:
        Lines between 'first_line' and 'last_line' from the given 'text'.
    """
    if text is None:
        raise ValueError('Got None argument "text"')
    if not isinstance(text, str):
        raise TypeError('Expected argument "text" to be a Unicode str')

    assert(first_line >= 0)
    assert(last_line >= 0)

    #if text.endswith('\n'):
    #    add_trailing_newline = True
    #else:
    #    add_trailing_newline = False

    lines = text.splitlines(keepends=True)
    if last_line > len(lines):
        last_line = len(lines)

    if first_line > last_line:
        first_line = last_line

    extracted = lines[first_line:last_line]
    extracted = ''.join(extracted)

    #if last_line == len(lines) and add_trailing_newline:
    #    extracted += '\n'

    return extracted
