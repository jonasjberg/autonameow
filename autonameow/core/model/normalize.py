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

import re

from util.text import (
    html_unescape,
    normalize_unicode,
    strip_edited_by
)


RE_NOT_LETTER_NUMBER_WHITESPACE = re.compile(r'[^\w\d\s]')

TITLE_REPLACEMENTS = {
    '&': 'and',
}


def _collapse_whitespace(string):
    while '  ' in string:
        string = string.replace('  ', ' ')
    return string


def normalize_full_title(string):
    if string is None:
        return ''

    title = normalize_unicode(string)
    title = html_unescape(title)
    title = title.lower()

    # Replace potentially valuable characters before the next step.
    for _find, _replace in TITLE_REPLACEMENTS.items():
        title = title.replace(_find, _replace)

    title = RE_NOT_LETTER_NUMBER_WHITESPACE.sub('', title)
    title = _collapse_whitespace(title)
    title = title.strip()
    return title


def normalize_full_human_name(string):
    if string is None:
        return ''

    name = normalize_unicode(string)
    name = name.lower()
    name = RE_NOT_LETTER_NUMBER_WHITESPACE.sub('', name)
    name = _collapse_whitespace(name)
    name = strip_edited_by(name)
    name = name.strip()

    return name
