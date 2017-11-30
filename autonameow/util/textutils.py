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


def remove_nonbreaking_spaces(text):
    return text.replace('\xa0', ' ')


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


def truncate_text(text, number_chars=500):
    msg = '  (.. TRUNCATED to {}/{} characters)'.format(number_chars, len(text))

    if len(text) <= number_chars:
        return text
    return text[0:number_chars] + msg


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
