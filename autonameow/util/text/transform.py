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
import unicodedata

from util import sanity


__all__ = [
    'collapse_whitespace',
    'indent',
    'normalize_unicode',
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


# \u002D Hyphen-minus
# \u05BE Hebrew punctuation MAQAF
# \u2010 Hyphen
# \u2011 Non-breaking hyphen
# \u2012 figure dash
# \u2013 en dash
# \u2014 em dash
# \u2015 horizontal bar
# \u2043 Hyphen bullet
# \u30FB Katakana middle dot
RE_UNICODE_DASHES_HYPHENS = re.compile(
    '[\u002d\u05be\u2010\u2011\u2012\u2013\u2014\u2015\u2043\u30fb]'
)

# \u002D Hyphen-minus
# \u207B Superscript minus
# \u2212 Minus
# \uFF0D Full-width Hyphen-minus
RE_UNICODE_MINUSES = re.compile(
    '[\u002d\u207b\u2212\uff0d]'
)

# \u0305 Combining overline
# \u203E Overline
RE_UNICODE_OVERLINES = re.compile(
    '[\u0305\u203e]'
)

# \u06D4 Arabic full stop
# \u2024 One dot leader
# \uFF0E Fullwidth full stop
RE_UNICODE_PERIODS = re.compile(
    '[\u06d4\u2024\uff0e]'
)

# \u002B Plus
# \u207A Superscript plus
# \uFF0B Full-width Plus
RE_UNICODE_PLUSES = re.compile(
    '[\u002b\u207a\uff0b]'
)

# \u002F Solidus
# \u2044 Fraction slash
# \u2215 Division slash
RE_UNICODE_SLASHES = re.compile(
    '[\u002f\u2044\u2215]'
)

# \u007E Tilde
# \u02DC Small tilde
# \u2053 Swung dash
# \u223C Tilde operator
# \u223D Reversed tilde
# \u223F Sine wave
# \u301C Wave dash
# \uFF5E Full-width tilde
RE_UNICODE_TILDES = re.compile(
    '[\u007e\u02dc\u2053\u223c\u223d\u223f\u301c\uff5e]'
)

# \u0027 Apostrophe
# \u055A Armenian apostrophe
# \u2019 Right single quotation mark
# \uA78B Latin capital letter saltillo
# \uA78C Latin small letter saltillo
# \uFF07 Fullwidth apostrophe
RE_UNICODE_APOSTROPHES = re.compile(
    '[\u0027\u055a\u2019\ua78b\ua78c\uff07]'
)

# \u0027 Apostrophe
# \u2018 Left single quotation mark
# \u2019 Right single quotation mark
# \u201A Single low-9 quotation mark
# \u201B Single high-reversed-9 quotation mark
RE_UNICODE_SINGLE_QUOTES = re.compile(
    '[\u0027\u2018\u2019\u201a\u201b]'
)

# \u0022 Quotation mark
# \u201C Left double quotation mark
# \u201D Right double quotation mark
# \u201E Double low-9 quotation mark
# \u201F Double high-reversed-9 quotation mark
RE_UNICODE_DOUBLE_QUOTES = re.compile(
    '[\u0022\u201c\u201d\u201e\u201f]'
)


def normalize_unicode(text):
    # Normalization Form KC (NFKC)
    # Compatibility Decomposition, followed by Canonical Composition.
    # http://unicode.org/reports/tr15/
    NORMALIZATION_FORM = 'NFKC'

    if not isinstance(text, str):
        raise TypeError('Expected "text" to be a Unicode str')

    text = re.sub(RE_UNICODE_DASHES_HYPHENS, '-', text)
    text = re.sub(RE_UNICODE_MINUSES, '-', text)
    text = re.sub(RE_UNICODE_OVERLINES, '-', text)
    text = re.sub(RE_UNICODE_PERIODS, '.', text)
    text = re.sub(RE_UNICODE_PLUSES, '+', text)
    text = re.sub(RE_UNICODE_SLASHES, '/', text)
    text = re.sub(RE_UNICODE_TILDES, '~', text)
    text = re.sub(RE_UNICODE_APOSTROPHES, "'", text)
    text = re.sub(RE_UNICODE_SINGLE_QUOTES, "'", text)
    text = re.sub(RE_UNICODE_DOUBLE_QUOTES, '"', text)

    return unicodedata.normalize(NORMALIZATION_FORM, text)


def remove_nonbreaking_spaces(text):
    return text.replace('\xa0', ' ')


def strip_ansiescape(string):
    stripped = re.sub(RE_ANSI_ESCAPE, '', string)
    return stripped
