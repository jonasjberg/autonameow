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

Use by passing through the singletons defined at the bottom of this file.
The values are "passed through" the type classes and returned as primitive or
standard library types (E.G. "datetime").
These classes are meant to be used as "filters" for coercing values to known
types, they are shared and should not retain any kind of state.
"""

import os
import mimetypes
import re

from datetime import datetime

from core import (
    constants,
    exceptions,
    util
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
    coercible_types = (str, )

    # Types that are "equivalent", does not require coercion.
    equivalent_types = (str, )

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
        try:
            value = self.primitive_type(raw_value)
        except (ValueError, TypeError):
            raise exceptions.AWTypeError(
                'Coercion default failed for: "{!s}" to primitive'
                ' {!r}'.format(raw_value, self.primitive_type)
            )
        else:
            return value

    def format(self, value, formatter=None):
        raise NotImplementedError('Must be implemented by inheriting classes.')

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
        if raw_value:
            try:
                value = util.bytestring_path(raw_value)
            except (ValueError, TypeError):
                pass
            else:
                return value

        raise exceptions.AWTypeError(
            'Unable to coerce "{!s}" into {!r}'.format(raw_value, self)
        )

    def format(self, value, formatter=None):
        # TODO: [TD0060] Implement or remove the "formatter" argument.
        parsed = self.coerce(value)
        return util.displayable_path(parsed)


class PathComponent(BaseType):
    primitive_type = str
    coercible_types = (str, bytes)
    equivalent_types = (bytes, )
    null = b''

    def normalize(self, value):
        coerced = self.coerce(value)
        if coerced:
            # Expand user home directory if present.
            return os.path.normpath(os.path.expanduser(util.syspath(coerced)))
        raise exceptions.AWTypeError(
            'Unable to normalize "{!s}" into {!r}'.format(value, self)
        )

    def coerce(self, raw_value):
        try:
            value = util.bytestring_path(raw_value)
        except (ValueError, TypeError):
            raise exceptions.AWTypeError(
                'Unable to coerce "{!s}" into {!r}'.format(raw_value, self)
            )
        else:
            return value

    def format(self, value, formatter=None):
        # TODO: [TD0060] Implement or remove the "formatter" argument.
        parsed = self.coerce(value)
        return util.displayable_path(parsed)


class Boolean(BaseType):
    primitive_type = bool
    coercible_types = (str, bytes)
    equivalent_types = (bool, )
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
        if isinstance(value, bytes):
            value = util.decode_(value)
        if isinstance(value, str):
            return self.string_to_bool(value)
        else:
            return False

    def normalize(self, value):
        if value is None:
            return False
        if isinstance(value, bool):
            return bool(value)
        else:
            return False

    def format(self, value, formatter=None):
        # TODO: [TD0060] Implement or remove the "formatter" argument.
        value = self.__call__(value)
        return str(value)


class Integer(BaseType):
    primitive_type = int
    coercible_types = (str, float)
    equivalent_types = (int, )
    null = 0

    def coerce(self, value):
        # If casting to int directly fails, try first converting to float,
        # then from float to int. Casting string to int handles "1.5" but
        # "-1.5" fails. The two step approach fixes the negative numbers.
        try:
            return int(value)
        except (ValueError, TypeError):
            try:
                float_value = float(value)
            except (ValueError, TypeError):
                pass
            else:
                try:
                    return int(float_value)
                except (ValueError, TypeError):
                    pass

        raise exceptions.AWTypeError(
            'Coercion default failed for: "{!s}" to primitive'
            ' {!r}'.format(value, self.primitive_type)
        )

    def format(self, value, formatter=None):
        # TODO: [TD0060] Implement or remove the "formatter" argument.
        coerced = self.coerce(value)
        if not formatter:
            return '{}'.format(coerced)
        else:
            return formatter.format(coerced)


class Float(BaseType):
    primitive_type = float
    coercible_types = (str, int)
    equivalent_types = (float, )
    null = 0.0

    def format(self, value, formatter=None):
        # TODO: [TD0060] Implement or remove the "formatter" argument.
        if not formatter:
            return '{0:.1f}'.format(value or self._null())
        else:
            return formatter.format(value or self._null())


class String(BaseType):
    primitive_type = str
    coercible_types = (str, bytes, int, float, bool)
    try:
        from PyPDF2.generic import TextStringObject
        coercible_types = coercible_types + (TextStringObject, )
    except ImportError:
        pass

    equivalent_types = (str, )
    null = ''

    def coerce(self, value):
        if value is None:
            return self._null()

        if isinstance(value, bytes):
            try:
                decoded = util.decode_(value)
            except Exception:
                return self._null()
            else:
                return decoded
        if isinstance(value, self.coercible_types):
            try:
                value = self.primitive_type(value)
            except (ValueError, TypeError):
                raise exceptions.AWTypeError(
                    'Coercion default failed for: "{!s}" to primitive'
                    ' {!r}'.format(value, self.primitive_type)
                )
            else:
                return value
        return str(value)

    def normalize(self, value):
        return self.__call__(value).strip()


class MimeType(BaseType):
    primitive_type = str
    coercible_types = (str, bytes)
    equivalent_types = ()
    null = constants.MAGIC_TYPE_UNKNOWN

    MIME_TYPE_LOOKUP = {
        ext.lstrip('.'): mime for ext, mime in mimetypes.types_map.items()
    }
    KNOWN_EXTENSIONS = list(MIME_TYPE_LOOKUP.keys())
    KNOWN_MIME_TYPES = list(MIME_TYPE_LOOKUP.values())
    assert(len(KNOWN_EXTENSIONS) > 0)
    assert(len(KNOWN_MIME_TYPES) > 0)

    def __call__(self, raw_value=None):
        # Overrides the 'BaseType' __call__ method as to not perform the test
        # after the the value coercion. A valid MIME-type can not be determined
        # by looking at the primitive type alone.
        if (raw_value is not None
                and isinstance(raw_value, self.coercible_types)):
            if raw_value.strip() is not None:
                value = self.coerce(raw_value)
                return value
        return self._null()

    def coerce(self, raw_value):
        string_value = AW_STRING(raw_value)
        string_value = string_value.lstrip('.').strip().lower()

        if string_value:
            if string_value in self.KNOWN_MIME_TYPES:
                return string_value
            if string_value in self.KNOWN_EXTENSIONS:
                return self.MIME_TYPE_LOOKUP[string_value]

        # TODO: [TD0083] Return "NULL" or raise 'AWTypeError'..?
        # raise exceptions.AWTypeError(
        #     'Unable to coerce "{!s}" into {!r}'.format(raw_value, self)
        # )
        return self._null()

    def normalize(self, value):
        return self.__call__(value)


class TimeDate(BaseType):
    primitive_type = None
    coercible_types = (str, bytes, int, float)
    equivalent_types = (datetime, )

    # Make sure to never return "null" -- raise a 'AWTypeError' exception.
    null = 'INVALID DATE'

    # TODO: [TD0054] Represent datetime as UTC within autonameow.

    def coerce(self, raw_value):
        try:
            dt = try_parse_full_datetime(raw_value)
        except (TypeError, ValueError) as e:
            raise exceptions.AWTypeError(
                'Unable to coerce "{!s}" into {!r}: {!s}'.format(raw_value,
                                                                 self, e)
            )
        else:
            return dt

    def normalize(self, value):
        try:
            parsed = self.coerce(value)
            if isinstance(parsed, datetime):
                return parsed.replace(microsecond=0)
            else:
                return self._null()
        except (TypeError, ValueError):
            return self._null()

    # Override parent '_null' method to force returning only valid 'datetime'
    # instances. Otherwise, raise an exception to be handled by the caller.
    def _null(self):
        raise exceptions.AWTypeError(
            'Type wrapper "{!r}" should never EVER return null!'.format(self)
        )


class ExifToolTimeDate(TimeDate):
    def coerce(self, raw_value):
        if re.match(r'.*0000:00:00 00:00:00.*', raw_value):
            raise exceptions.AWTypeError(
                'Unable to coerce "{!s}" into {!r}'.format(raw_value, self)
            )

        # Remove any ':' in timezone as to match strptime pattern.
        if re.match(r'.*\+\d\d:\d\d$', raw_value):
            raw_value = re.sub(r'\+(\d\d):(\d\d)$', r'+\1\2', raw_value)
        elif re.match(r'.*-\d\d:\d\d$', raw_value):
            raw_value = re.sub(r'-(\d\d):(\d\d)$', r'-\1\2', raw_value)

        try:
            # TODO: Fix matching dates with timezone. Below is not working.
            dt = datetime.strptime(raw_value, '%Y:%m:%d %H:%M:%S%z')
            return dt
        except (ValueError, TypeError):
            try:
                dt = try_parse_full_datetime(raw_value)
                return dt
            except (TypeError, ValueError) as e:
                pass

        raise exceptions.AWTypeError(
            'Unable to coerce "{!s}" into {!r}'.format(raw_value, self)
        )


class PyPDFTimeDate(TimeDate):
    primitive_type = None

    def coerce(self, raw_value):
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

        raise exceptions.AWTypeError(
            'Unable to coerce "{!s}" into {!r}'.format(raw_value, self)
        )


def try_parse_full_datetime(string):
    _error_msg = 'Unable to parse full datetime from: "{!s}"'.format(string)

    if not string:
        raise ValueError(_error_msg)
    if not isinstance(string, str):
        raise ValueError(_error_msg)

    string = re.sub(
        r'(\d{4})[:-](\d{2})[:-](\d{2})[T ](\d{2})[:-]?(\d{2})[:-]?(\d{2})',
        r'\1-\2-\3 \4:\5:\6',
        string
    )

    # Handles malformed dates produced by "Mac OS X 10.11.5 Quartz PDFContext".
    if string.endswith('Z'):
        string = string[:-1]

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

    raise ValueError(_error_msg)


def try_wrap(value):
    wrapper = PRIMITIVE_AW_TYPE_MAP.get(type(value))
    if wrapper:
        return wrapper(value)
    else:
        return None


# Singletons for actual use.
AW_BOOLEAN = Boolean()
AW_PATH = Path()
AW_PATHCOMPONENT = PathComponent()
AW_INTEGER = Integer()
AW_FLOAT = Float()
AW_STRING = String()
AW_MIMETYPE = MimeType()
AW_TIMEDATE = TimeDate()
AW_EXIFTOOLTIMEDATE = ExifToolTimeDate()
AW_PYPDFTIMEDATE = PyPDFTimeDate()


# NOTE: Wrapping paths (potentially bytes) with this automatic type
#       detection would coerce them to Unicode strings when we actually
#       want to do path coercion with one the "AW_Path"-types ..
PRIMITIVE_AW_TYPE_MAP = {
    bool: AW_BOOLEAN,
    datetime: AW_TIMEDATE,
    int: AW_INTEGER,
    float: AW_FLOAT,
    str: AW_STRING,
    bytes: AW_STRING
}
