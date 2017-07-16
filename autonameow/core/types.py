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

import re

from core import (
    util,
    exceptions
)


class BaseType(object):
    """
    Base class for all custom types. Provides type coercion and known defaults.
    Does not store values -- intended to act as filters.
    """
    # Underlying primitive type.
    # NOTE(jonas): Why revert to "str"? Assume BaseType won't be instantiated?
    primitive_type = str

    # Default "None" value to fall back to.
    null = None

    # Types that can be coerced with the "parse" method.
    coercible_types = (str,)

    # Types that are "equivalent", does not require coercion.
    equivalent_types = (str,)

    def __call__(self, raw_value=None):
        if raw_value is None:
            return self._null()
        elif self.test(raw_value):
            # Pass through if type is "equivalent" without coercion.
            return raw_value
        elif isinstance(raw_value, self.coercible_types):
            # Type can be coerced, test after coercion to make sure.
            value = self.coerce(raw_value)
            if self.test(value):
                return value

        raise exceptions.AWTypeError(
            'Unable to coerce "{!s}" into {!r}'.format(raw_value, self)
        )

    def _null(self):
        return self.null

    def test(self, value):
        return isinstance(value, self.equivalent_types)

    def normalize(self, value):
        """
        Processes the given value to a form suitable for serialization/storage.

        Args:
            value: The value to normalize.

        Returns:
            A "normalized" version of the given value in this class type if
            the value can be normalized, otherwise the class "null" value.
        """
        if value is None:
            return self._null()
        else:
            # TODO: Implement or make sure that inheriting classes does ..
            return value

    def coerce(self, raw_value):
        return raw_value

    def format(self, value, formatter=None):
        if value is None:
            value = self._null()
        if value is None:
            # Case where 'self.null' is None.
            value = ''
        if isinstance(value, bytes):
            value = value.decode('utf-8', 'ignore')

        parsed = self.coerce(value)
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
    coercible_types = (str, bytes)
    equivalent_types = ()

    # TODO: Figure out how to represent null for Paths.
    null = None

    def __call__(self, raw_value=None):
        if raw_value and isinstance(raw_value, self.coercible_types):
            # Type can be coerced, test after coercion to make sure.
            value = self.coerce(raw_value)
            return value
        else:
            raise exceptions.AWTypeError(
                'Unable to coerce "{!s}" into {!r}'.format(raw_value, self)
            )

    def coerce(self, raw_value):
        try:
            value = util.normpath(raw_value)
        except (ValueError, TypeError):
            return self._null()
        else:
            return value

    def format(self, value, formatter=None):
        parsed = self.coerce(value)
        return util.displayable_path(parsed)


class Boolean(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = bool
    coercible_types = (str, bytes)
    equivalent_types = (bool,)
    null = False

    @staticmethod
    def string_to_bool(string_value):
        value = string_value.lower().strip()
        if value in ('yes', 'true'):
            return True
        elif value in ('no', 'false'):
            return False
        else:
            return False

    def coerce(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return bool(value)
        elif isinstance(value, str):
            return self.string_to_bool(value)
        elif isinstance(value, bytes):
            decoded = util.decode_(value)
            return self.string_to_bool(decoded)
        else:
            return False

    def normalize(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return bool(value)
        else:
            return False


class Integer(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = int
    coercible_types = (str, float)
    equivalent_types = (int,)
    null = 0

    @classmethod
    def coerce(cls, value):
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
    coercible_types = (str, int)
    equivalent_types = (float,)
    null = 0.0

    def coerce(self, value):
        try:
            parsed = float(value)
        except (TypeError, ValueError):
            return self._null()
        else:
            return parsed

    def format(self, value, formatter=None):
        if not formatter:
            return '{0:.1f}'.format(value or self._null())
        else:
            return formatter.format(value or self._null())


class String(BaseType):
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = str
    coercible_types = (str, bytes, int, float)
    equivalent_types = (str,)
    null = ''

    def coerce(self, value):
        if isinstance(value, bytes):
            try:
                decoded = util.decode_(value)
            except Exception:
                return self._null()
            else:
                return decoded
        if isinstance(value, (int, float)):
            return str(value)


class TimeDate(BaseType):
    # TODO: Think long and hard about this before proceeding..
    # TODO: [TD0002] Research requirements and implement custom type system.
    primitive_type = None
    coercible_types = (str, bytes, int, float)
    equivalent_types = (str, datetime)

    # TODO: [TD0050] Figure out how to represent null for datetime objects.
    null = 'INVALID DATE'

    def __call__(self, raw_value=None):
        if not raw_value:
            return self._null()
        elif isinstance(raw_value, (list, tuple)):
            return self._null()

        parsed = self.coerce(raw_value)
        return parsed if parsed else self._null()

    def coerce(self, raw_value):
        if isinstance(raw_value, datetime):
            return raw_value
        try:
            dt = try_parse_full_datetime(raw_value)
        except ValueError as e:
            return self._null()
        else:
            return dt

    def normalize(self, value):
        if not value:
            return self._null()
        try:
            parsed = self.coerce(value)
            if isinstance(parsed, datetime):
                return parsed.replace(microsecond=0)
            else:
                return self._null()
        except (TypeError, ValueError):
            return self._null()


class ExifToolTimeDate(TimeDate):
    primitive_type = None

    def coerce(self, raw_value):
        if isinstance(raw_value, datetime):
            return raw_value

        if re.match(r'.*\+\d\d:\d\d$', raw_value):
            raw_value = re.sub(r'\+(\d\d):(\d\d)$', r'+\1\2', raw_value)
        try:
            # TODO: Fix matching dates with timezone. Below is not working.
            dt = datetime.strptime(raw_value, '%Y:%m:%d %H:%M:%S%z')
        except (ValueError, TypeError) as e:
            try:
                dt = try_parse_full_datetime(raw_value)
            except ValueError:
                return self._null()
            else:
                return dt
        else:
            return dt


def try_parse_full_datetime(string):
    _error_msg = 'Unable parse to datetime: "{!s}"'

    if not string:
        raise ValueError(_error_msg.format(string))
    if not isinstance(string, str):
        raise ValueError(_error_msg.format(string))

    string = re.sub(
        r'(\d{4})[:-](\d{2})[:-](\d{2})[T ](\d{2})[:-](\d{2})[:-](\d{2})',
        r'\1-\2-\3 \4:\5:\6',
        string
    )

    date_formats = ['%Y-%m-%d %H:%M:%S',
                    '%Y-%m-%d %H:%M:%S.%f',  # %f: Microseconds
                    '%Y-%m-%d %H:%M:%S %z',  # %z: UTC offset
                    '%Y-%m-%d %H:%M:%S%z']

    for date_format in date_formats:
        try:
            dt = datetime.strptime(string, date_format)
        except (ValueError, TypeError):
            continue
        else:
            return dt

    raise ValueError(_error_msg.format(string))


def try_wrap(value):
    wrapper = PRIMITIVE_AW_TYPE_MAP.get(type(value), False)
    if wrapper:
        return wrapper(value)
    else:
        return None


# Singletons for actual use.
AW_BOOLEAN = Boolean()
AW_PATH = Path()
AW_INTEGER = Integer()
AW_FLOAT = Float()
AW_STRING = String()
AW_TIMEDATE = TimeDate()
AW_EXIFTOOLTIMEDATE = ExifToolTimeDate()


PRIMITIVE_AW_TYPE_MAP = {
    bool: AW_BOOLEAN,
    datetime: AW_TIMEDATE,
    int: AW_INTEGER,
    float: AW_FLOAT,
    str: AW_STRING,
    bytes: AW_STRING
}
