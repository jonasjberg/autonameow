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

from util import sanity


__all__ = [
    'collapse_whitespace',
    'indent',
    'remove_nonbreaking_spaces',
    'strip_ansiescape'
]


# Attempt at matching ANSI escape sequences. Likely incomplete.
RE_ANSI_ESCAPE = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')

# Matches sequentially repeating whitespace, except newlines.
#
# Inverting the following classes solves the problem of matching whitespace
# Unicode characters included in the '\s' class but NOT newlines,
# which is also included in '\s'.
#
#   \S   Any character which is not a Unicode whitespace character.
#   \r   ASCII Carriage Return (CR)
#   \n   ASCII ASCII Linefeed (LF)
#
RE_WHITESPACE_EXCEPT_NEWLINE = re.compile(r'[^\S\r\n]{2,}')


def collapse_whitespace(string):
    """
    Replaces repeating whitespace, except newlines, with a single space.

    Does not remove leading or trailing whitespace.
    Does not change linefeeds or carriage returns.
    Handles Unicode whitespace characters.

    Args:
        string: Unicode String to transform.

    Returns:
        Transformed text as a Unicode string.
    """
    #  Assume type-checks is handled elsewhere. Pass through None, [], {}, etc.
    if not string:
        return string

    assert isinstance(string, str), (
        'Expected Unicode string. Got {!s} "{!s}"'.format(type(string), string)
    )

    collapsed = re.sub(RE_WHITESPACE_EXCEPT_NEWLINE, ' ', string)
    return collapsed


def indent(text, amount=None, ch=None):
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
    Raises:
        ValueError: Given 'text' is None or a optional argument is set to None.
    """
    DEFAULT_AMOUNT = 4
    DEFAULT_PADDING = ' '

    if amount is None:
        amount = DEFAULT_AMOUNT
    else:
        if not isinstance(amount, int):
            raise TypeError('Expected "amount" to be of type int')
        elif amount <= 0:
            raise ValueError('Expected "amount" to be greater than zero')

    if ch is None:
        ch = DEFAULT_PADDING

    if text is None:
        raise ValueError('Got None argument "text"')

    sanity.check_internal_string(text)
    sanity.check_internal_string(ch)

    padding = amount * ch
    return ''.join(padding + line for line in text.splitlines(True))


def remove_nonbreaking_spaces(text):
    return text.replace('\xa0', ' ')


def strip_ansiescape(string):
    stripped = re.sub(RE_ANSI_ESCAPE, '', string)
    return stripped
