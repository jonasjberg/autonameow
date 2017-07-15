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
    # Underlying primitive type. Used to define 'null' and coerce values.
    # NOTE(jonas): Why revert to "str"? Assume BaseType won't be instantiated?
    primitive_type = str

    def __call__(self, raw_value=None):
        if raw_value is None:
            return self.null

        parsed = self.parse(raw_value)
        return parsed if parsed else self.null

    @property
    def null(cls):
        if not cls.primitive_type:
            raise NotImplementedError('Class does not specify "primitive_type"'
                                      ' -- must override "parse"')
        else:
            return cls.primitive_type()

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
    def parse(cls, raw_value):
        if not cls.primitive_type:
            raise NotImplementedError('Class does not specify "primitive_type"'
                                      ' -- must override "parse"')
        else:
            try:
                value = cls.primitive_type(raw_value)
            except (ValueError, TypeError):
                return cls.null
            else:
                return value

    @classmethod
    def format(cls, value, formatter=None):
        if value is None:
            value = cls.null
        if value is None:
            # Case where 'self.null' is None.
            value = ''
        if isinstance(value, bytes):
            value = value.decode('utf-8', 'ignore')

        parsed = cls.parse(value)
        return str(parsed)

    def __repr__(self):
        return self.__class__.__name__

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)


class Path(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = str

    @property
    def null(self):
        # TODO: Figure out how to represent null for Paths.
        raise NotImplementedError('Got NULL path')
        return 'INVALID PATH'

    @classmethod
    def parse(cls, raw_value):
        try:
            value = util.normpath(raw_value)
        except (ValueError, TypeError):
            return cls.null
        else:
            return value

    @classmethod
    def format(cls, value, formatter=None):
        parsed = cls.parse(value)
        return util.displayable_path(parsed)


class Boolean(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = bool

    @staticmethod
    def string_to_bool(string_value):
        value = string_value.lower().strip()
        if value in ('yes', 'true'):
            return True
        elif value in ('no', 'false'):
            return False
        else:
            return False

    @classmethod
    def parse(cls, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return bool(value)
        elif isinstance(value, str):
            return cls.string_to_bool(value)
        else:
            return False

    @classmethod
    def normalize(cls, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return bool(value)
        else:
            return False


class Integer(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = int

    @classmethod
    def parse(cls, value):
        try:
            parsed = int(value)
        except (TypeError, ValueError):
            return 0
        else:
            return parsed

    @classmethod
    def format(cls, value, formatter=None):
        if not formatter:
            return '{}'.format(value or 0)
        else:
            return formatter.format(value or 0)


class Float(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = float

    @classmethod
    def parse(cls, value):
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return 0.0
        else:
            return parsed

    @classmethod
    def format(cls, value, formatter=None):
        if not formatter:
            return '{0:.1f}'.format(value or 0.0)
        else:
            return formatter.format(value or 0.0)


class String(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = str


class TimeDate(BaseType):
    # TODO: Think long and hard about this before proceeding..
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = None

    def __call__(self, raw_value=None):
        if not raw_value:
            return self.null
        elif isinstance(raw_value, (list, tuple)):
            return self.null

        parsed = self.parse(raw_value)
        return parsed if parsed else self.null

    @property
    def null(cls):
        # TODO: [TD0050] Figure out how to represent null for datetime objects.
        return 'INVALID DATE'

    @classmethod
    def parse(cls, raw_value):
        if not raw_value:
            return cls.null

        if isinstance(raw_value, datetime):
            return raw_value

        date_formats = ['%Y-%m-%dT%H:%M:%S',
                        '%Y-%m-%dT%H:%M:%S.%f',  # %f: Microseconds
                        '%Y-%m-%d %H:%M:%S %z']  # %z: UTC offset

        for date_format in date_formats:
            try:
                dt = datetime.strptime(raw_value, date_format)
            except (ValueError, TypeError):
                continue
            else:
                return dt

        return cls.null

    def normalize(cls, value):
        if not value:
            return cls.null
        try:
            parsed = cls.parse(value)
            if isinstance(parsed, datetime):
                return parsed.replace(microsecond=0)
            else:
                return cls.null
        except (TypeError, ValueError):
            return cls.null


class ExifToolTimeDate(TimeDate):
    primitive_type = None

    @classmethod
    def parse(cls, raw_value):
        try:
            dt = datetime.strptime(raw_value, '%Y-%m-%d %H:%M:%S+%z')
        except (ValueError, TypeError):
            return cls.null
        else:
            return dt


AW_BOOLEAN = Boolean()
AW_PATH = Path()
AW_INTEGER = Integer()
AW_FLOAT = Float()
AW_STRING = String()
AW_TIMEDATE = TimeDate()
AW_EXIFTOOLTIMEDATE = ExifToolTimeDate()
