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

"""
Custom data types, used internally by autonameow.
Wraps primitives to force safe defaults and extra functionality.
"""

# TODO: [TD0002] Research requirements and implement custom type system.

#   Requirements:
#   * Simplify configuration parsing
#   * Confine data extractor results data to types
#   * Allow type-specific processing of data extractor data


class BaseType(object):
    # NOTE(jonas): Why revert to "str"? Assume BaseType won't be instantiated?
    primitive_type = str

    @property
    def null(self):
        return self.primitive_type()

    def normalize(self, value):
        """
        Processes the given value to a form suitable for serialization/storage.

        Args:
            value: The value to normalize.

        Returns:
            A "normalized" version of the given value in this class type if the
            value can be normalized. Otherwise the class "null" value.
        """
        if value is None:
            return self.null
        else:
            # TODO: ..
            return value


class Integer(BaseType):
    primitive_type = int


class Float(BaseType):
    primitive_type = float


class TimeDate(BaseType):
    # TODO: Think long and hard about this before proceeding..
    primitive_type = None
