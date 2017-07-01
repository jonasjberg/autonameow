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

from unidecode import unidecode

from core import util


def sanitize_text(text):
    """
    Sanitizes text of unknown origin, encoding and content.
    :param text: text to process
    :return: sanitized text
    """
    if text is None or text.strip() is None:
        return False

    # TODO: [TD0004] Handle text encoding properly.
    # TODO: [TD0044] Rework converting "raw data" to internal representations.

    # NOTE(jonas): This strips all umlauts from 'test_files/gmail.pdf" on Linux.
    # try:
    #     text = unidecode(text)
    # except UnicodeDecodeError:
    #     pass

    # Collapse whitespace.
    # '\xa0' is non-breaking space in Latin1 (ISO 8859-1), also chr(160).
    # text = text.replace('\xa0', ' ')

    # text = text.decode('unicode-escape')
    # text = unicode(text, 'UTF-8')

    # TODO: [TD0004] Enforce encoding boundary for extracted data.
    return util.encode_(text)


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
    Indents (multi-line) text a specified amount.

    Shift text right by the given "amount" (default 4) using the character
    "ch", which default to a space if left unspecified.

    Based on this post; https://stackoverflow.com/a/8348914/7802196

    Args:
        text: The text to indent. Single or multi-line.
        amount: Optional number of columns of indentation. Default: 4
        ch: Optional character to insert. Default: ' '

    Returns:
        An indented version of the given text.
    """
    padding = amount * ch
    return ''.join(padding + line for line in text.splitlines(True))