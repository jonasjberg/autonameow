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

try:
    import chardet
except ImportError:
    chardet = None

from core.util import sanity
from thirdparty import nameparser


def extract_digits(string):
    """
    Extracts and returns digits from a Unicode string, as a Unicode string.
    """
    sanity.check_internal_string(string)

    digits = ''
    for char in string:
        if char.isdigit():
            digits += char

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
        If 'text' is a Unicode str; lines between 'first_line' and 'last_line'.
        None if 'text' is None.
    Raises:
        EncodingBoundaryViolation: Argument 'text' is not a Unicode string.
        AWAssertionError: Either 'first_line' or 'last_line' is negative.
    """
    if text is None:
        return text

    sanity.check_internal_string(text)
    sanity.check(first_line >= 0, 'Argument first_line is negative')
    sanity.check(last_line >= 0, 'Argument last_line is negative')

    lines = text.splitlines(keepends=True)
    if last_line > len(lines):
        last_line = len(lines)

    if first_line > last_line:
        first_line = last_line

    extracted = lines[first_line:last_line]
    return ''.join(extracted)


IGNORED_AUTHOR_WORDS = frozenset([
    'van'
])


def parse_name(full_name):
    """
    Thin wrapper around 'nameparser'.

    Args:
        full_name: The name to parse as a Unicode string.

    Returns:
        The parsed name as an instance of the 'HumanName' class.
    """
    if nameparser:
        return nameparser.HumanName(full_name)
    return None


def format_name_lastname_initials(full_name):
    """
    Formats a full name to LAST_NAME, INITIALS..

    Example:  "Gibson Cat Sjöberg" is returned as "Sjöberg G.C."

    Args:
        full_name: The full name to format as a Unicode string.

    Returns:
        The specified name written as LAST_NAME, INITIAL, INITIAL..
    """
    words = full_name.split(' ')
    words = [w for w in words if w not in IGNORED_AUTHOR_WORDS]

    lastname = words.pop()
    if words:
        initials = [w[0] for w in words]
        _initials = '{0}{1}'.format('.'.join(initials), '.')
        return lastname + ' ' + _initials
    else:
        return lastname


def format_name_lastname_initials2(full_name):
    """
    Formats a full name to LAST_NAME, INITIALS..

    Example:  "Gibson Cat Sjöberg" is returned as "Sjöberg G.C."

    Args:
        full_name: The full name to format as a Unicode string.

    Returns:
        The specified name written as LAST_NAME, INITIAL, INITIAL..
    """
    sanity.check_internal_string(full_name)

    full_name = full_name.strip()

    # Return names already in the output format as-is.
    if re.match(r'[\w]+ (\w\.)+$', full_name):
        return full_name

    # Using the third-party 'nameparser' module.
    _human_name = parse_name(full_name)
    if not _human_name:
        return ''

    # Some first names are misinterpreted as titles.
    if _human_name.first == '':
        first_list = _human_name.title_list
    else:
        first_list = _human_name.first_list

    def _to_initial(string):
        string = string.strip('.')
        return string[0]

    initials = [_to_initial(f) for f in first_list]
    initials += [_to_initial(m) for m in _human_name.middle_list]
    _initials = '{0}{1}'.format('.'.join(initials), '.')

    last_name = _human_name.last.replace(' ', '')
    return '{} {}'.format(last_name, _initials)


def format_names_lastname_initials(list_of_full_names):
    _formatted_authors = [format_name_lastname_initials(a)
                          for a in list_of_full_names]
    return sorted(_formatted_authors, key=str.lower)


RE_UNICODE_DASHES = re.compile(
    '[\u2212\u2013\u2014\u05be\u2010\u2015\u30fb]'
)


def normalize_unicode(text):
    # Normalization Form KC (NFKC)
    # Compatibility Decomposition, followed by Canonical Composition.
    # http://unicode.org/reports/tr15/
    NORMALIZATION_FORM = 'NFKC'

    if not isinstance(text, str):
        raise TypeError('Expected "text" to be a Unicode str')

    text = re.sub(RE_UNICODE_DASHES, '-', text)

    return unicodedata.normalize(NORMALIZATION_FORM, text)
