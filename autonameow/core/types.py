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

from core import util


class BaseType(object):
    """
    Base class for all custom types. Provides type coercion and known defaults.
    Does not store values -- intended to act as filters.
    """

    # NOTE(jonas): Why revert to "str"? Assume BaseType won't be instantiated?
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = str

    def __call__(self, raw_value=None):
        if raw_value is None:
            return self.null

        parsed = self._parse(raw_value)
        return parsed if parsed else self.null

    @property
    def null(self):
        if not self.primitive_type:
            raise NotImplementedError('Must be implemented by subclass')
        else:
            return self.primitive_type()

    @classmethod
    def normalize(cls, value):
        """
        Processes the given value to a form suitable for serialization/storage.

        Args:
            value: The value to normalize.

        Returns:
            A "normalized" version of the given value in this class type if
            the value can be normalized, otherwise the class "null" value.
        """
        if value is None:
            return cls.null
        else:
            # TODO: Implement or make sure that inheriting classes does ..
            return value

    @classmethod
    def _parse(cls, raw_value):
        if not cls.primitive_type:
            raise NotImplementedError('Must be implemented by subclass')
        else:
            try:
                value = cls.primitive_type(raw_value)
            except (ValueError, TypeError):
                return cls.null
            else:
                return value

    def __repr__(self):
        return self.__class__.__name__

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)


class Path(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = str

    def __str__(self):
        return util.displayable_path(self.value)


class Boolean(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = bool


class Integer(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = int


class Float(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = float


class String(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = str


class TimeDate(BaseType):
    # TODO: Think long and hard about this before proceeding..
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = None

    @property
    def null(self):
        # TODO: [TD0050] Figure out how to represent null for datetime objects.
        return 'INVALID DATE'

    @classmethod
    def _parse(cls, raw_value):
        date_formats = ['%Y-%m-%dT%H:%M:%S.%f',  # %f: Microseconds
                        '%Y-%m-%d %H:%M:%S %z']  # %z: UTC offset

        for date_format in date_formats:
            try:
                dt = datetime.strptime(raw_value, date_format)
            except (ValueError, TypeError):
                return cls.null
            else:
                return dt


class ExifToolTimeDate(TimeDate):
    primitive_type = None

    @classmethod
    def _parse(cls, raw_value):
        try:
            dt = datetime.strptime(raw_value, '%Y-%m-%d %H:%M:%S+%z')
        except (ValueError, TypeError):
            return cls.null
        else:
            return dt


AW_PATH = Path()
AW_INTEGER = Integer()
AW_FLOAT = Float()
AW_STRING = String()
AW_TIMEDATE = TimeDate()
AW_EXIFTOOLTIMEDATE = ExifToolTimeDate()
