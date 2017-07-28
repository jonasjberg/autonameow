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

Requirements:
* Simplify configuration parsing
* Confine data extractor results data to types
* Allow type-specific processing of data extractor data
"""


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
    null = 'NULL'

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
    primitive_type = str
    coercible_types = (str, bytes)

    # Always force coercion so that all incoming data is properly normalized.
    equivalent_types = ()

    # Make sure to never return "null" -- raise a 'AWTypeError' exception.
    null = 'INVALID PATH'

    def __call__(self, raw_value=None):
        # Overrides the 'BaseType' __call__ method as to not perform the test
        # after the the value coercion. This is because the path could be a
        # byte string and still not be properly normalized.
        if (raw_value is not None
                and isinstance(raw_value, self.coercible_types)):
            if raw_value.strip() is not None:
                value = self.coerce(raw_value)
                return value
        raise exceptions.AWTypeError(
            'Unable to coerce "{!s}" into {!r}'.format(raw_value, self)
        )

    def normalize(self, value):
        coerced = self.coerce(value)
        if coerced:
            return util.normpath(coerced)
        raise exceptions.AWTypeError(
            'Unable to normalize "{!s}" into {!r}'.format(value, self)
        )

    def coerce(self, raw_value):
        if raw_value is None:
            return self._null()

        try:
            value = util.bytestring_path(raw_value)
        except (ValueError, TypeError):
            return self._null()
        else:
            return value

    def format(self, value, formatter=None):
        parsed = self.coerce(value)
        return util.displayable_path(parsed)


class Boolean(BaseType):
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
    primitive_type = None
    coercible_types = (str, bytes, int, float)
    equivalent_types = (str, datetime)

    # Make sure to never return "null" -- raise a 'AWTypeError' exception.
    null = 'INVALID DATE'

    # TODO: [TD0054] Represent datetime as UTC within autonameow.

    def __call__(self, raw_value=None):
        # Overrides the 'BaseType' __call__ method as to never return 'null'.
        if raw_value and not isinstance(raw_value, (list, tuple)):
            parsed = self.coerce(raw_value)
            if parsed:
                return parsed

        raise exceptions.AWTypeError(
            'Unable to coerce "{!s}" into {!r}'.format(raw_value, self)
        )

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


class PyPDFTimeDate(TimeDate):
    primitive_type = None

    def coerce(self, raw_value):
        if not raw_value:
            raise ValueError('Got empty/None string from PyPDF')
        if isinstance(raw_value, datetime):
            return raw_value

        if "'" in raw_value:
            raw_value = raw_value.replace("'", '')

        # Expected date format:           D:20121225235237 +05'30'
        #                                   ^____________^ ^_____^
        # Regex search matches two groups:        #1         #2
        re_datetime_tz = re.compile(r'D:(\d{14}) ?(\+\d{2}\'?\d{2}\'?)')
        re_match_tz = re_datetime_tz.search(raw_value)
        if re_match_tz:
            datetime_str = re_match_tz.group(1)
            timezone_str = re_match_tz.group(2)
            timezone_str = timezone_str.replace("'", "")

            try:
                # With timezone ('%z')
                return datetime.strptime(str(datetime_str + timezone_str),
                                         '%Y%m%d%H%M%S%z')
            except ValueError:
                pass
            try:
                # Without timezone
                return datetime.strptime(datetime_str, '%Y%m%d%H%M%S')
            except ValueError:
                pass

        # Try matching another pattern.
        re_datetime_no_tz = re.compile(r'D:(\d{14})')
        re_match = re_datetime_no_tz.search(raw_value)
        if re_match:
            try:
                return datetime.strptime(re_match.group(1), '%Y%m%d%H%M%S')
            except ValueError:
                pass

        raise ValueError


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
AW_PYPDFTIMEDATE = PyPDFTimeDate()


PRIMITIVE_AW_TYPE_MAP = {
    bool: AW_BOOLEAN,
    datetime: AW_TIMEDATE,
    int: AW_INTEGER,
    float: AW_FLOAT,
    str: AW_STRING,
    bytes: AW_STRING
}
