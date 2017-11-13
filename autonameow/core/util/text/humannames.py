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

from core.util import sanity
from thirdparty import nameparser


RE_AUTHOR_ET_AL = re.compile(
    r'[\[\(\{]?et.al\.?[\]\)\}]?', re.IGNORECASE
)

IGNORED_AUTHOR_WORDS = frozenset([
    '...',
])


def strip_author_et_al(string):
    return RE_AUTHOR_ET_AL.sub('', string)


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
    sanity.check_internal_string(full_name)

    for ignored_word in IGNORED_AUTHOR_WORDS:
        full_name = full_name.replace(ignored_word, '')

    full_name = strip_author_et_al(full_name)

    full_name = full_name.strip()
    full_name = full_name.rstrip(',')
    full_name = full_name.lstrip(',')

    # Return names already in the output format as-is.
    if re.match(r'[\w-]+ (\w\.)+$', full_name):
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
        try:
            return string[0]
        except IndexError:
            return ''

    initials = [_to_initial(f) for f in first_list]
    initials += [_to_initial(m) for m in _human_name.middle_list]
    _initials = '{0}{1}'.format('.'.join(initials), '.')

    last_name = _human_name.last.replace(' ', '')
    return '{} {}'.format(last_name, _initials).strip()


def format_names(list_of_full_names, formatter):
    assert callable(formatter), 'Argument "formatter" must be callable'

    _formatted_authors = [formatter(a) for a in list_of_full_names]
    return sorted(_formatted_authors, key=str.lower)


def format_names_lastname_initials(list_of_full_names):
    return format_names(list_of_full_names, format_name_lastname_initials)
