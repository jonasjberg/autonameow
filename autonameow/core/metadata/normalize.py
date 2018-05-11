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

from util.text import html_unescape
from util.text import normalize_unicode
from util.text import normalize_whitespace
from util.text import strip_edited_by


RE_NOT_LETTER_NUMBER_WHITESPACE = re.compile(r'[^\w\d\s]')

TITLE_REPLACEMENTS = {
    '&': 'and',
    '.epub': '',
    '.djvu': '',
}


def _strip_trailing_junk(s):
    return re.sub(r'[\s_-]+$', '', s)


def normalize_full_human_name(string):
    normalized_name = cleanup_full_human_name(string)
    return normalized_name.lower()


def cleanup_full_human_name(string):
    if not string:
        return ''

    assert isinstance(string, str)
    name = normalize_unicode(string)
    name = normalize_whitespace(name)
    name = strip_edited_by(name)
    name = RE_NOT_LETTER_NUMBER_WHITESPACE.sub('', name)
    name = name.strip()
    return name


def cleanup_full_title(string):
    if not string:
        return ''

    assert isinstance(string, str)
    title = normalize_unicode(string)
    title = html_unescape(title)
    title = normalize_whitespace(title)

    # Replace potentially valuable characters before the next step.
    for pattern, replacement in TITLE_REPLACEMENTS.items():
        title = title.replace(pattern, replacement)

    title = _strip_trailing_junk(title).strip()
    return title


def normalize_full_title(string):
    clean_title = cleanup_full_title(string)
    normalized_title = RE_NOT_LETTER_NUMBER_WHITESPACE.sub('', clean_title)
    return normalized_title.lower().strip()
