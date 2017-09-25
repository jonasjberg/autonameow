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
Coerces incoming data with unreliable or unknown types to primitives.
Provides "NULL" values and additional type-specific functionality.

Use by passing data through the singletons defined at the bottom of this file.
The values are "passed through" the type classes and returned as primitive or
standard library types (E.G. "datetime").
These classes are meant to be used as "filters" for coercing values to known
types --- they are shared and should not retain any kind of state.
"""

import os
import mimetypes
import re

from datetime import datetime

from core import (
    exceptions,
    util
)
from core.util import (
    sanity,
    textutils
)
from core import constants as C

# TODO: [TD0084] Add handling collections to type coercion classes.

mimetypes.add_type('application/epub+zip', '.epub')


class AWTypeError(exceptions.AutonameowException):
    """Failure to coerce a value with one of the type coercers."""


class BaseType(object):
    """
    Base class for all custom types. Provides type coercion and known defaults.
    Does not store values -- intended to act as filters.
    """
    # Default "None" value to fall back to.
    NULL = 'NULL'

    # Types that can be coerced with the "coerce" method.
    COERCIBLE_TYPES = (str,)

    # Used by the "test" method to test if value types are "equivalent".
    EQUIVALENT_TYPES = (str, )

    def __call__(self, value=None):
        if value is None:
            return self._null()
        elif self.test(value):
            # Pass through if type is "equivalent" without coercion.
            return value
        elif isinstance(value, self.COERCIBLE_TYPES):
            # Type can be coerced, test after coercion to make sure.
            value = self.coerce(value)
            if self.test(value):
                return value

        self._fail_coercion(value)

    def _null(self):
        return self.NULL

    def test(self, value):
        return isinstance(value, self.EQUIVALENT_TYPES)

    def coerce(self, value):
        """
        Coerces values whose types are included in "COERCIBLE_TYPES".

        If the value is not part of the specific class "COERCIBLE_TYPES",
        the coercion fails and a class-specific "null" value is returned.

        Args:
            value: The value to coerce as any type, including None.

        Returns:
            A representation of the original value coerced to the type
            represented by the specific class, or the class "null" value if
            coercion fails.
        Raises:
            AWTypeError: The value could not be coerced.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def normalize(self, value):
        """
        Processes the given value to a form suitable for serialization/storage.

        Calling this method should be equivalent to calling 'coerce' followed
        by some processing that produces a "simplified" representation of
        the value.  Strings might be converted to lower-case, etc.

        Args:
            value: The value to coerce as any type, including None.

        Returns:
            A "normalized" version of the given value if the value can be
            coerced and normalized, or the class "null" value.
        Raises:
            AWTypeError: The value could not be coerced and/or normalized.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def format(self, value, **kwargs):
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def _fail_normalization(self, value, msg=None):
        error_msg = 'Unable to normalize "{!s}" into {!r}'.format(value, self)
        if msg is not None:
            error_msg = '{}; {!s}'.format(error_msg, msg)

        raise AWTypeError(error_msg)

    def _fail_coercion(self, value, msg=None):
        error_msg = 'Unable to coerce "{!s}" into {!r}'.format(value, self)
        if msg is not None:
            error_msg = '{}; {!s}'.format(error_msg, msg)

        raise AWTypeError(error_msg)

    def __repr__(self):
        return self.__class__.__name__

    def __eq__(self, other):
        return isinstance(other, self.__class__)

    def __ne__(self, other):
        return not self.__eq__(other)


class Path(BaseType):
    COERCIBLE_TYPES = (str, bytes)

    # Always force coercion so that all incoming data is properly normalized.
    EQUIVALENT_TYPES = ()

    # Make sure to never return "null" -- raise a 'AWTypeError' exception.
    NULL = 'INVALID PATH'

    def __call__(self, value=None):
        # Overrides the 'BaseType' __call__ method as to not perform the test
        # after the the value coercion. This is because the path could be a
        # byte string and still not be properly normalized.
        if (value is not None
                and isinstance(value, self.COERCIBLE_TYPES)):
            if value.strip() is not None:
                value = self.coerce(value)
                return value

        self._fail_coercion(value)

    def coerce(self, value):
        if value:
            try:
                return util.bytestring_path(value)
            except (ValueError, TypeError):
                pass

        self._fail_coercion(value)

    def normalize(self, value):
        value = self.__call__(value)
        if value:
            return util.normpath(value)

        self._fail_normalization(value)

    def format(self, value, **kwargs):
        parsed = self.__call__(value)
        return util.displayable_path(parsed)


class PathComponent(BaseType):
    COERCIBLE_TYPES = (str, bytes)
    EQUIVALENT_TYPES = (bytes, )
    NULL = b''

    def coerce(self, value):
        try:
            return util.bytestring_path(value)
        except (ValueError, TypeError):
            self._fail_coercion(value)

    def normalize(self, value):
        value = self.__call__(value)
        if value:
            # Expand user home directory if present.
            return os.path.normpath(os.path.expanduser(util.syspath(value)))

        self._fail_normalization(value)

    def format(self, value, **kwargs):
        value = self.__call__(value)
        return util.displayable_path(value)


class Boolean(BaseType):
    COERCIBLE_TYPES = (bytes, str, int, float, object)
    EQUIVALENT_TYPES = (bool, )
    NULL = False

    STR_TRUE = frozenset('positive true yes'.split())
    STR_FALSE = frozenset('negative false no'.split())

    def string_to_bool(self, string_value):
        value = string_value.lower().strip()
        if value in self.STR_TRUE:
            return True
        if value in self.STR_FALSE:
            return False

    @staticmethod
    def bool_to_string(bool_value):
        if bool_value:
            return 'True'
        else:
            return 'False'

    def coerce(self, value):
        if value is None:
            return self._null()

        try:
            string_value = AW_STRING(value)
        except AWTypeError:
            pass
        else:
            _maybe_bool = self.string_to_bool(string_value)
            if _maybe_bool is not None:
                return _maybe_bool

        try:
            float_value = AW_FLOAT(value)
        except AWTypeError:
            pass
        else:
            return bool(float_value > 0)

        if hasattr(value, '__bool__'):
            try:
                return bool(value)
            except (AttributeError, LookupError, NotImplementedError,
                    TypeError, ValueError):
                self._fail_coercion(value)

        return self._null()

    def normalize(self, value):
        return self.__call__(value)

    def format(self, value, **kwargs):
        value = self.__call__(value)
        return self.bool_to_string(value)


class Integer(BaseType):
    COERCIBLE_TYPES = (bytes, str, float)
    EQUIVALENT_TYPES = (int, )
    NULL = 0

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

        self._fail_coercion(value)

    def normalize(self, value):
        return self.__call__(value)

    def format(self, value, **kwargs):
        value = self.__call__(value)

        if 'format_string' not in kwargs:
            return '{}'.format(value or self._null())

        format_string = kwargs.get('format_string')
        if format_string:
            if not isinstance(format_string, str):
                raise AWTypeError('Expected "format_string" to be Unicode str')

            try:
                return format_string.format(value)
            except TypeError:
                pass

        raise AWTypeError(
            'Invalid "format_string": "{!s}"'.format(format_string)
        )


class Float(BaseType):
    COERCIBLE_TYPES = (bytes, str, int)
    EQUIVALENT_TYPES = (float, )
    NULL = 0.0

    def coerce(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            self._fail_coercion(value)

    def normalize(self, value):
        return self.__call__(value)

    def format(self, value, **kwargs):
        value = self.__call__(value)

        if 'format_string' not in kwargs:
            return '{0:.1f}'.format(value or self._null())

        format_string = kwargs.get('format_string')
        if format_string:
            if not isinstance(format_string, str):
                raise AWTypeError('Expected "format_string" to be Unicode str')

            try:
                return format_string.format(value)
            except TypeError:
                pass

        raise AWTypeError(
            'Invalid "format_string": "{!s}"'.format(format_string)
        )


class String(BaseType):
    COERCIBLE_TYPES = (str, bytes, int, float, bool)
    try:
        from PyPDF2.generic import TextStringObject
        COERCIBLE_TYPES = COERCIBLE_TYPES + (TextStringObject,)
    except ImportError:
        pass

    EQUIVALENT_TYPES = (str, )
    NULL = ''

    def coerce(self, value):
        if value is None:
            return self._null()

        if isinstance(value, bytes):
            try:
                return util.decode_(value)
            except Exception:
                return self._null()

        if isinstance(value, self.COERCIBLE_TYPES):
            try:
                return str(value)
            except (ValueError, TypeError):
                self._fail_coercion(value)

    def normalize(self, value):
        return self.__call__(value).strip()

    def format(self, value, **kwargs):
        value = self.__call__(value)
        return value


class MimeType(BaseType):
    COERCIBLE_TYPES = (str, bytes)
    EQUIVALENT_TYPES = ()
    NULL = C.MAGIC_TYPE_UNKNOWN

    try:
        MIME_TYPE_LOOKUP = {
            ext.lstrip('.'): mime for ext, mime in mimetypes.types_map.items()
        }
    except AttributeError:
        MIME_TYPE_LOOKUP = {}

    # TODO: Improve robustness of interfacing with 'mimetypes'.
    sanity.check(len(MIME_TYPE_LOOKUP) > 0,
                 'MIME_TYPE_LOOKUP is empty')

    # Any custom "extension to MIME-type"-mappings goes here.
    MIME_TYPE_LOOKUP['sh'] = 'text/x-shellscript'

    MIME_TYPE_LOOKUP_INV = {
        mime: ext for ext, mime in MIME_TYPE_LOOKUP.items()
    }

    # Override "MIME-type to extension"-mappings here.
    MIME_TYPE_LOOKUP_INV['text/plain'] = 'txt'
    MIME_TYPE_LOOKUP_INV['image/jpeg'] = 'jpg'

    KNOWN_EXTENSIONS = frozenset(MIME_TYPE_LOOKUP.keys())
    KNOWN_MIME_TYPES = frozenset(MIME_TYPE_LOOKUP.values())

    def __call__(self, value=None):
        # Overrides the 'BaseType' __call__ method as to not perform the test
        # after the the value coercion. A valid MIME-type can not be determined
        # by looking at the primitive type alone.
        if (value is not None
                and isinstance(value, self.COERCIBLE_TYPES)):
            if value.strip() is not None:
                value = self.coerce(value)
                return value
        return self._null()

    def coerce(self, value):
        string_value = AW_STRING(value)
        string_value = string_value.lstrip('.').strip().lower()

        if string_value:
            if string_value in self.KNOWN_MIME_TYPES:
                return string_value
            elif string_value in self.KNOWN_EXTENSIONS:
                return self.MIME_TYPE_LOOKUP[string_value]

        return self._null()

    def normalize(self, value):
        return self.__call__(value)

    def format(self, value, **kwargs):
        if value == C.MAGIC_TYPE_UNKNOWN:
            return ''

        value = self.__call__(value)
        formatted = self.MIME_TYPE_LOOKUP_INV.get(value)
        return formatted if formatted is not None else self._null()


class Date(BaseType):
    COERCIBLE_TYPES = (str, bytes, int, float)
    EQUIVALENT_TYPES = (datetime, )

    # Make sure to never return "null" -- raise a 'AWTypeError' exception.
    NULL = 'INVALID DATE'

    # TODO: [TD0054] Represent datetime as UTC within autonameow.

    # Override parent '_null' method to force returning only valid 'datetime'
    # instances. Otherwise, raise an exception to be handled by the caller.
    def _null(self):
        raise AWTypeError(
            '"{!r}" got incoercible data'.format(self)
        )

    def coerce(self, value):
        try:
            string_value = AW_STRING(value)
        except AWTypeError as e:
            self._fail_coercion(value, msg=e)
        else:
            try:
                return try_parse_date(string_value)
            except ValueError as e:
                self._fail_coercion(value, msg=e)

    def normalize(self, value):
        value = self.__call__(value)
        if isinstance(value, datetime):
            return value.replace(microsecond=0)

        self._fail_normalization(value)

    def format(self, value, **kwargs):
        value = self.__call__(value)

        format_string = kwargs.get('format_string')
        if format_string is None:
            format_string = C.DEFAULT_DATETIME_FORMAT_DATE
            if not isinstance(format_string, str):
                raise AWTypeError('Expected "format_string" to be Unicode str')

            try:
                return datetime.strftime(value, format_string)
            except TypeError:
                pass

        raise AWTypeError(
            'Invalid "format_string": "{!s}"'.format(format_string)
        )


class TimeDate(BaseType):
    COERCIBLE_TYPES = (str, bytes, int, float)
    EQUIVALENT_TYPES = (datetime, )

    # Make sure to never return "null" -- raise a 'AWTypeError' exception.
    NULL = 'INVALID DATE'

    # TODO: [TD0054] Represent datetime as UTC within autonameow.

    # Override parent '_null' method to force returning only valid 'datetime'
    # instances. Otherwise, raise an exception to be handled by the caller.
    def _null(self):
        raise AWTypeError(
            '"{!r}" got incoercible data'.format(self)
        )

    def coerce(self, value):
        try:
            return try_parse_datetime(value)
        except (TypeError, ValueError) as e:
            self._fail_coercion(value, msg=e)

    def normalize(self, value):
        value = self.__call__(value)
        if isinstance(value, datetime):
            return value.replace(microsecond=0)

        self._fail_normalization(value)

    def format(self, value, **kwargs):
        value = self.__call__(value)

        format_string = kwargs.get('format_string')
        if format_string is None:
            format_string = C.DEFAULT_DATETIME_FORMAT_DATETIME
            if not isinstance(format_string, str):
                raise AWTypeError('Expected "format_string" to be Unicode str')

            try:
                return datetime.strftime(value, format_string)
            except TypeError:
                pass

        raise AWTypeError(
            'Invalid "format_string": "{!s}"'.format(format_string)
        )


class ExifToolTimeDate(TimeDate):
    def coerce(self, value):
        if re.match(r'.*0000:00:00 00:00:00.*', value):
            self._fail_coercion(value)

        try:
            return try_parse_datetime(value)
        except ValueError:
            pass
        try:
            return try_parse_date(value)
        except ValueError:
            pass

        self._fail_coercion(value)


class PyPDFTimeDate(TimeDate):
    # Expected date/time format:      D:20121225235237 +05'30'
    #                                   ^____________^ ^_____^
    # Regex search matches two groups:        #1         #2
    RE_DATETIME_TZ = re.compile(r'D:(\d{14}) ?(\+\d{2}\'?\d{2}\'?)')

    # Date/time without timezone, alternate pattern:
    RE_DATETIME = re.compile(r'D:(\d{14})')

    # Only date, without timezone:
    RE_DATE = re.compile(r'D:(\d{8})')

    def coerce(self, value):
        value = value.replace("'", '')

        re_match_tz = self.RE_DATETIME_TZ.search(value)
        if re_match_tz:
            datetime_str = re_match_tz.group(1)
            timezone_str = re_match_tz.group(2)

            try:
                return datetime.strptime(str(datetime_str + timezone_str),
                                         '%Y%m%d%H%M%S%z')
            except ValueError:
                pass
            try:
                # Without timezone
                return datetime.strptime(datetime_str, '%Y%m%d%H%M%S')
            except ValueError:
                pass

        re_match = self.RE_DATETIME.search(value)
        if re_match:
            try:
                return datetime.strptime(re_match.group(1), '%Y%m%d%H%M%S')
            except ValueError:
                pass

        re_match = self.RE_DATE.search(value)
        if re_match:
            try:
                return datetime.strptime(re_match.group(1), '%Y%m%d')
            except ValueError:
                pass

        self._fail_coercion(value)


_pat_loose_date = '{year}{sep}{month}{sep}{day}'.format(
    year=r'(\d{4})', month=r'(\d{2})', day=r'(\d{2})', sep=r'[:_ \-]?'
)
_pat_loose_time = '{hour}{sep}{minute}{sep}{second}'.format(
    hour=r'(\d{2})', minute=r'(\d{2})', second=r'(\d{2})', sep=r'[:_ \-]?'
)
_pat_datetime_sep = r'[:_ tT\-]?'
_pat_timezone = r'([-+])?(\d{2}).?(\d{2})'
_pat_microseconds = r'[\._ ]?(\d{6})'

RE_LOOSE_TIME = re.compile(_pat_loose_time)
RE_LOOSE_DATE = re.compile(_pat_loose_date)
RE_LOOSE_DATETIME = re.compile(
    _pat_loose_date + _pat_datetime_sep + _pat_loose_time
)
RE_LOOSE_DATETIME_TZ = re.compile(
    _pat_loose_date + _pat_datetime_sep + _pat_loose_time + _pat_timezone
)
RE_LOOSE_DATETIME_US = re.compile(
    _pat_loose_date + _pat_datetime_sep + _pat_loose_time + _pat_microseconds
)


def normalize_date(string):
    match = RE_LOOSE_DATE.search(string)
    if match:
        _normalized = re.sub(RE_LOOSE_DATE, r'\1-\2-\3', string)
        return _normalized
    return None


def normalize_datetime_with_timezone(string):
    match = RE_LOOSE_DATETIME_TZ.search(string)
    if match:
        _normalized = re.sub(RE_LOOSE_DATETIME_TZ,
                             r'\1-\2-\3T\4:\5:\6 \7\8\9',
                             string)
        return _normalized.replace(' ', '')
    return None


def normalize_datetime(string):
    match = RE_LOOSE_DATETIME.search(string)
    if match:
        _normalized = re.sub(RE_LOOSE_DATETIME, r'\1-\2-\3T\4:\5:\6', string)
        return _normalized.replace(' ', '')
    return None


def normalize_datetime_with_microseconds(string):
    match = RE_LOOSE_DATETIME_US.search(string)
    if match:
        _normalized = re.sub(RE_LOOSE_DATETIME_US, r'\1-\2-\3T\4:\5:\6.\7',
                             string)
        return _normalized
    return None


def try_parse_datetime(string):
    _error_msg = 'Unable to parse datetime: "{!s}" ({})'.format(string,
                                                                type(string))

    if not string:
        raise ValueError(_error_msg)
    if not isinstance(string, str):
        raise ValueError(_error_msg)

    # Handles malformed dates produced by "Mac OS X 10.11.5 Quartz PDFContext".
    if string.endswith('Z'):
        string = string[:-1]

    match = normalize_datetime_with_timezone(string)
    if match:
        try:
            return datetime.strptime(match, '%Y-%m-%dT%H:%M:%S%z')
        except (ValueError, TypeError):
            pass

    match = normalize_datetime_with_microseconds(string)
    if match:
        try:
            return datetime.strptime(match, '%Y-%m-%dT%H:%M:%S.%f')
        except (ValueError, TypeError):
            pass

    match = normalize_datetime(string)
    if match:
        try:
            return datetime.strptime(match, '%Y-%m-%dT%H:%M:%S')
        except (ValueError, TypeError):
            pass

    raise ValueError(_error_msg)


def try_parse_date(string):
    _error_msg = 'Unable to parse date: "{!s}" ({})'.format(string,
                                                            type(string))

    if not string:
        raise ValueError(_error_msg)
    if not isinstance(string, str):
        raise ValueError(_error_msg)

    match = normalize_date(string)
    if match:
        try:
            return datetime.strptime(match, '%Y-%m-%d')
        except (ValueError, TypeError):
            pass

    # Alternative, bruteforce method. Extract digits.
    # Assumes year, month, day is in ISO-date-like order.
    digits = textutils.extract_digits(string)
    if digits:
        sanity.check_internal_string(digits)

        date_formats = ['%Y%m%d', '%Y%m', '%Y']
        for date_format in date_formats:
            try:
                return datetime.strptime(digits, date_format)
            except (ValueError, TypeError):
                pass

    raise ValueError(_error_msg)


def try_coerce(value):
    coercer = coercer_for(value)
    if coercer:
        try:
            return coercer(value)
        except AWTypeError:
            pass
    return None


def coercer_for(value):
    if value is None:
        return None
    return PRIMITIVE_AW_TYPE_MAP.get(type(value), None)


# Singletons for actual use.
AW_BOOLEAN = Boolean()
AW_DATE = Date()
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
