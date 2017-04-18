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
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   autonameow is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with autonameow.  If not, see <http://www.gnu.org/licenses/>.

from unidecode import unidecode


def sanitize_text(text):
    """
    Sanitizes text of unknown origin, encoding and content.
    :param text: text to process
    :return: sanitized text
    """
    if text is None or text.strip() is None:
        return False

    # TODO: Make sure this below is OK.
    try:
        text = unidecode(text)
    except UnicodeDecodeError:
        pass

    # Collapse whitespace.
    # '\xa0' is non-breaking space in Latin1 (ISO 8859-1), also chr(160).
    text = text.replace('\xa0', ' ')
    # pdf_text = " ".join(pdf_text.replace("\xa0", " ").strip().split())

    # text = text.decode('unicode-escape')
    # text = unicode(text, 'UTF-8')
    return text


def extract_digits(string):
    """
    Extracts digits from text string.
    :param string: string to extract digits from
    :return: digits in string or None if string contains no digits
    """
    digits = ''
    for char in string:
        if char.isdigit():
            digits += char

    return digits if digits.strip() else None
