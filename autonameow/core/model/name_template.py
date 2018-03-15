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


# TODO: [TD0180] Add abstraction for file name composed of placeholder fields.


class NameTemplate(object):
    def __init__(self, format_string):
        assert isinstance(format_string, str)
        self._format_string = format_string


def format_string_placeholders(format_string):
    """
    Gets the format string placeholder fields from a text string.

    The text "{foo} mjao baz {bar}" would return ['foo', 'bar'].

    Args:
        format_string: Format string to get placeholders from.

    Returns:
        Any format string placeholder fields as a list of unicode strings.
    """
    if not isinstance(format_string, str):
        raise TypeError('Expected "format_string" to be of type str')
    if not format_string.strip():
        return []

    return re.findall(r'{(\w+)}', format_string)
