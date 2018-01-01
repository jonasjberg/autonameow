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

from util import sanity


def extract_digits(string):
    """
    Extracts and returns digits from a Unicode string, as a Unicode string.
    """
    sanity.check_internal_string(string)

    digits = ''.join(c for c in string if c.isdigit())
    return digits if digits.strip() else ''


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
    assert firstline >= 1, 'Argument first_line is < 1'
    assert lastline >= 1, 'Argument last_line is < 1'

    firstline -= 1

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
