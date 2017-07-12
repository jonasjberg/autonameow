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

from datetime import datetime


class BaseType(object):
    """
    Base class for all custom types. Provides type coercion and known defaults.
    """

    # NOTE(jonas): Why revert to "str"? Assume BaseType won't be instantiated?
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = str

    # def __init__(self, raw_value):
    #     self._value = self._parse(raw_value)

    @classmethod
    def __call__(cls, raw_value=None):
        if raw_value is None:
            return cls.null

        parsed = cls._parse(raw_value)
        return parsed if parsed else cls.null

    @property
    def null(self):
        return self.primitive_type(None)

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

    @classmethod
    def _parse(cls, raw_value):
        if not cls.primitive_type:
            raise NotImplementedError('Must be implemented by inheriting class')
        else:
            try:
                value = cls.primitive_type(raw_value)
            except ValueError:
                return cls.null
            else:
                return value

    def __repr__(self):
        return self.__class__.__name__

    # def __eq__(self, other):
    #     return (isinstance(other, self.__class__)
    #             and self.__dict__ == other.__dict__)

    def __ne__(self, other):
        return not self.__eq__(other)


class Boolean(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = bool


class Integer(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = int


class Float(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = float


class TimeDate(BaseType):
    # TODO: Think long and hard about this before proceeding..
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = None

    def _parse(self, raw_value):
        try:
            dt = datetime.strptime(raw_value, '%Y-%m-%dT%H:%M:%S.%f')
        except (ValueError, TypeError):
            return self.null
        else:
            return dt

    def __call__(self, raw_value):
        self._value = self._parse(raw_value)
        return self._value

    def __repr__(self):
        return self._value

    def __str__(self):
        return self._value.isoformat()
