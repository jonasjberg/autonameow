# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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

from core.namebuilder.fields import nametemplatefield_class_from_string


class NameTemplate(object):
    def __init__(self, format_string):
        assert isinstance(format_string, str)
        self._format_string = format_string

        self._str_placeholders = None
        self._placeholders = None

    @property
    def str_placeholders(self):
        if self._str_placeholders is None:
            self._str_placeholders = template_placeholder_substrings(self._format_string)
        return self._str_placeholders

    @property
    def placeholders(self):
        if self._placeholders is None:
            self._placeholders = [
                nametemplatefield_class_from_string(p) for p in self.str_placeholders
            ]
        return self._placeholders

    def __str__(self):
        return self._format_string


def template_placeholder_substrings(format_string):
    """
    Returns the format string placeholder fields from a text string.

    The text "{foo} mjao baz {bar}" would return ['foo', 'bar'].

    Args:
        format_string (str): Name template to search for placeholder substrings.

    Returns:
        Any name template placeholder fields as a list of Unicode strings.
    """
    assert isinstance(format_string, str)
    if not format_string.strip():
        return list()

    return re.findall(r'{(\w+)}', format_string)
