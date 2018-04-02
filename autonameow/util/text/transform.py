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

import html
import re
import unicodedata
import urllib

try:
    from unidecode import unidecode
except ImportError:
    unidecode = None


__all__ = [
    'collapse_whitespace',
    'extract_digits',
    'html_unescape',
    'indent',
    'batch_regex_replace',
    'normalize_unicode',
    'normalize_whitespace',
    'simplify_unicode',
    'remove_blacklisted_lines',
    'remove_blacklisted_re_lines',
    'remove_nonbreaking_spaces',
    'remove_zerowidth_spaces',
    'strip_ansiescape',
    'strip_single_space_lines',
    'truncate_text',
    'urldecode'
]


# Attempt at matching ANSI escape sequences. Likely incomplete.
RE_ANSI_ESCAPE = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -\/]*[@-~]')

# Matches whitespace that repeats at least once, except newlines.
# I.E. a single space is NOT matched but two consecutive spaces is.
#
# Inverting the following classes solves the problem of matching whitespace
# Unicode characters included in the '\s' class but NOT newlines,
# which is also included in '\s'.
#
#   \S   Any character which is not a Unicode whitespace character.
#   \r   ASCII Carriage Return (CR)
#   \n   ASCII ASCII Linefeed (LF)
#
RE_REPEATED_WHITESPACE_EXCEPT_NEWLINE = re.compile(r'[^\S\r\n]{2,}')

# Like above but matches any number of whitespace characters.
RE_WHITESPACE_EXCEPT_NEWLINE = re.compile(r'[^\S\r\n]+')


def collapse_whitespace(text):
    """
    Replaces all repeating whitespace except newlines with a single space.

    Does not remove leading or trailing whitespace.
    Does not change linefeeds or carriage returns.
    Handles Unicode whitespace characters.

    NOTE: Assumes type-checks is handled elsewhere.
          "Empty" values like None, [], {}, etc. are passed through as-is.

    Args:
        text (str): Unicode text to transform.

    Returns:
        str: Transformed text as a Unicode string.

    Raises:
        AssertionError: Given text is not an instance of 'str'.
    """
    if not text:
        return text

    assert isinstance(text, str)
    collapsed = re.sub(RE_REPEATED_WHITESPACE_EXCEPT_NEWLINE, ' ', text)
    return collapsed


RE_SINGLE_SPACE_LINES = re.compile(r'^ $', re.MULTILINE)


def strip_single_space_lines(text):
    """
    Like 'str.strip()' but restricted to lines that only contain a single space.

    Args:
        text (str): Unicode text to transform.

    Returns:
        str: The given text with any lines containing only a single space
             replaced by an empty line.

    Raises:
        AssertionError: Given text is not an instance of 'str'.
    """
    if not text:
        return text

    assert isinstance(text, str)
    return re.sub(RE_SINGLE_SPACE_LINES, '', text)


def normalize_whitespace(text):
    """
    Replaces all whitespace except newlines with a single space.

    Does not remove leading or trailing whitespace.
    Does not change linefeeds or carriage returns.
    Handles Unicode whitespace characters.

    NOTE: Assumes type-checks is handled elsewhere.
          "Empty" values like None, [], {}, etc. are passed through as-is.

    Args:
        text (str): Unicode text to transform.

    Returns:
        str: The given text with all whitespace replaced with a single space.

    Raises:
        AssertionError: Given text is not an instance of 'str'.
    """
    if not text:
        return text

    assert isinstance(text, str)
    normalized = re.sub(RE_WHITESPACE_EXCEPT_NEWLINE, ' ', text)
    return normalized


DEFAULT_INDENT_AMOUNT = 4
DEFAULT_INDENT_PADCHAR = ' '


def indent(text, columns=None, padchar=None):
    """
    Indents (multi-line) text by a specified amount.

    Shifts text right by a given "amount" (default: DEFAULT_INDENT_AMOUNT)
    using the character "ch" for padding (default: DEFAULT_INDENT_PADCHAR).

    Args:
        text (str): Single or multi-line text to indent.
        columns (int)(optional): Padding character ('ch') multiple.
        padchar (str)(optional): Character to use for padding.

    Returns:
        str: An indented version of the given text as a Unicode str.

    Raises:
        AssertionError: Any argument has an unexpected type or value.
    """
    assert isinstance(text, str)

    if columns is None:
        columns = DEFAULT_INDENT_AMOUNT
    assert isinstance(columns, int) and columns > 0

    if padchar is None:
        padchar = DEFAULT_INDENT_PADCHAR
    assert isinstance(padchar, str)

    padding = columns * padchar
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
    if not text:
        return text

    assert isinstance(text, str)
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

    # Normalization Form KC (NFKC)
    # Compatibility Decomposition, followed by Canonical Composition.
    # http://unicode.org/reports/tr15/
    NORMALIZATION_FORM = 'NFKC'
    normalized = unicodedata.normalize(NORMALIZATION_FORM, text)
    return normalized


def simplify_unicode(text):
    """
    Strips accents or diacritics from Unicode text.

    Based on this post:  https://stackoverflow.com/a/17069876
    """
    if not text:
        return text

    assert isinstance(text, str)
    if unidecode:
        return _strip_accents_unidecode(text)
    return _strip_accents_homerolled(text)


def _strip_accents_homerolled(string):
    nkfd_form = unicodedata.normalize('NFKD', string)
    return ''.join([c for c in nkfd_form if not unicodedata.combining(c)])


def _strip_accents_unidecode(string):
    assert unidecode, 'Missing required module "unidecode"'
    return unidecode(string)


def remove_nonbreaking_spaces(text):
    return text.replace('\u00A0', ' ')


def remove_zerowidth_spaces(text):
    return text.replace('\u200B', '')


def strip_ansiescape(string):
    assert isinstance(string, str)
    stripped = re.sub(RE_ANSI_ESCAPE, '', string)
    return stripped


def truncate_text(text, maxlen=500, append_info=False):
    assert isinstance(text, str)
    assert isinstance(maxlen, int)

    if len(text) <= maxlen:
        return text

    truncated = text[0:maxlen]
    if not append_info:
        return truncated
    return truncated + '  ({}/{} characters)'.format(maxlen, len(text))


def urldecode(string):
    return urllib.parse.unquote(string)


def html_unescape(string):
    return html.unescape(string)


def batch_regex_replace(regex_replacement_tuples, string):
    if not string:
        return string

    assert isinstance(string, str)

    matches = list()
    for regex, replacement in regex_replacement_tuples:
        match = re.search(regex, string)
        if match:
            matches.append((regex, replacement))

    sorted_by_longest_replacement = sorted(
        matches, key=lambda x: len(x[1]), reverse=True
    )
    for regex, replacement in sorted_by_longest_replacement:
        string = re.sub(regex, replacement, string)

    return string


def remove_blacklisted_lines(text, blacklist):
    """
    Removes any text lines that matches any line in 'blacklist'.

    Blacklisted lines should not contain any line separators.

    Args:
        text: The text to process as a Unicode string.
        blacklist: List of Unicode strings to ignore.

    Returns:
        The given text with any lines matching those in 'blacklist' removed,
        as a Unicode string.
    """
    out = []

    blacklisted_lines = set(blacklist)
    for line in text.splitlines(keepends=True):
        if not any(line.strip() == bad_line for bad_line in blacklisted_lines):
            out.append(line)

    return ''.join(out)


def remove_blacklisted_re_lines(text, compiled_regexes):
    """
    Removes any text lines that matches any regular expression in 'blacklist'.

    Any line separators are removed from each line before evaluating
    the regular expressions.

    Args:
        text: The text to process as a Unicode string.
        compiled_regexes: Regular expressions matching lines to blacklist.

    Returns:
        The given text with any lines matching any of the given regular
        expressions removed, as a Unicode string.
    """
    regexes = set(compiled_regexes)
    out = []
    for line in text.splitlines(keepends=True):
        stripped_line = line.strip()
        if any(regex.match(stripped_line) for regex in regexes):
            continue
        out.append(line)

    return ''.join(out)


def extract_digits(string):
    """
    Extracts and returns digits from a Unicode string, as a Unicode string.
    """
    assert isinstance(string, str)

    digits = ''.join(c for c in string if c.isdigit())
    return digits if digits.strip() else ''
