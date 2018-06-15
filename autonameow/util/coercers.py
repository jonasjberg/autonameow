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

"""
Custom data types, used internally by autonameow.
Coerces incoming data with unreliable or unknown types to primitives.
Provides "NULL" values and additional type-specific functionality.

Use by passing data through the singletons defined at the bottom of this file.
The values are "passed through" the type classes and returned as primitive or
standard library types (E.G. "datetime").
These classes are meant to be used as "filters" for coercing values to known
types --- they are shared and should not retain any kind of state.

The coercion is more "generous" than the default Python casting. The coercion
was originally intended to be used primarily by data extractors to tame
incoming "raw" data. Making the coercion very flexible at the risk of
unintended type casting and very unpredictable behaviour due to having to
learn this arbitrary type-coercion system, MADE SENSE for this use-case.

However, functionality provided by these classes have expanded and multiple
parts of autonameow now use these types in various ways. The exact workings
of the coercion _IS_ relevant for some of the usages..
The best way to get a grip on what these classes are doing is to look at the
tests in 'tests/unit/test_util_coercers.py'.

Note that the behaviours of for instance 'format()' and 'normalize()' vary
a lot between classes.

# TODO: [cleanup] This should probably be cleaned up at some point ..
"""

import os
import re
from datetime import datetime

import util.text as textutils
from core import constants as C
from core import exceptions
from util import encoding as enc
from util import mimemagic
from util import sanity


class AWTypeError(exceptions.AutonameowException):
    """Failure to coerce a value with one of the type coercers."""


class BaseNullValue(object):
    AS_STRING = '(NULL BaseNullValue)'

    def __bool__(self):
        return False

    def __str__(self):
        return self.AS_STRING

    def __eq__(self, other):
        if other is None:
            return False
        if isinstance(other, self.__class__):
            return True
        if other == self.__class__:
            return True
        if isinstance(other, bool) and other is False:
            return True
        return False

    def __hash__(self):
        return hash(self.__class__)


class _NullMIMEType(BaseNullValue):
    # Default MIME type string used if the MIME type detection fails.
    AS_STRING = '(UNKNOWN MIME-TYPE)'


class BaseCoercer(object):
    """
    Base class for all type coercers with shared functionality.
    Does *not* store values or any kind of state -- intended to act as filters.
    """
    # Default "None" value to fall back to.
    NULL = BaseNullValue()

    # Types that can be coerced with the 'coerce' method.
    COERCIBLE_TYPES = (str,)

    # Used by the 'equivalent' method to check if types are "equivalent".
    EQUIVALENT_TYPES = (str, )

    def __call__(self, value=None):
        if value is None:
            return self.null()
        elif self.equivalent(value):
            # Pass through if type is "equivalent" without coercion.
            return value
        elif self.coercible(value):
            # Type can be coerced, check after coercion to make sure.
            value = self.coerce(value)
            if self.equivalent(value):
                return value

        return self._fail_coercion(value)

    def null(self):
        return self.NULL

    def equivalent(self, value):
        return isinstance(value, self.EQUIVALENT_TYPES)

    def coercible(self, value):
        return isinstance(value, self.COERCIBLE_TYPES)

    def coerce(self, value):
        """
        Coerces values whose types are included in 'COERCIBLE_TYPES'.

        If the value is not part of the specific class 'COERCIBLE_TYPES',
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


class _Path(BaseCoercer):
    COERCIBLE_TYPES = (str, bytes)

    # Always force coercion so that all incoming data is properly normalized.
    EQUIVALENT_TYPES = ()

    # Make sure to never return "null" -- raise a 'AWTypeError' exception.
    NULL = 'INVALID PATH'

    def __call__(self, value=None):
        # Overrides the 'BaseType' __call__ method as to not perform the test
        # after the the value coercion. This is because the path could be a
        # byte string and still not be properly normalized.
        if value is not None and self.coercible(value):
            if value.strip() is not None:
                value = self.coerce(value)
                return value

        return self._fail_coercion(value)

    def coerce(self, value):
        if value:
            with exceptions.ignored(ValueError, TypeError):
                return enc.bytestring_path(value)

        return self._fail_coercion(value)

    def normalize(self, value):
        value = self.__call__(value)
        if value:
            return enc.normpath(value)

        return self._fail_normalization(value)

    def format(self, value, **kwargs):
        _normalized = self.normalize(value)
        return enc.displayable_path(_normalized)


class _PathComponent(BaseCoercer):
    COERCIBLE_TYPES = (str, bytes)
    EQUIVALENT_TYPES = (bytes, )
    NULL = b''

    def coerce(self, value):
        try:
            return enc.bytestring_path(value)
        except (ValueError, TypeError):
            return self._fail_coercion(value)

    def normalize(self, value):
        value = self.__call__(value)
        if value:
            # Expand user home directory if present.
            return os.path.normpath(
                os.path.expanduser(enc.syspath(value))
            )

        return self._fail_normalization(value)

    def format(self, value, **kwargs):
        _coerced = self.__call__(value)
        return enc.displayable_path(_coerced)


class _Boolean(BaseCoercer):
    COERCIBLE_TYPES = (bytes, str, int, float, object)
    EQUIVALENT_TYPES = (bool, )
    NULL = False

    STR_TRUE = frozenset('positive true yes on enable enabled active'.split())
    STR_FALSE = frozenset(
        'negative false no off disable disabled inactive passive'.split()
    )

    def string_to_bool(self, string_value):
        value = string_value.lower().strip()
        if value in self.STR_TRUE:
            return True
        if value in self.STR_FALSE:
            return False
        return None

    @staticmethod
    def bool_to_string(bool_value):
        return 'True' if bool_value else 'False'

    def coerce(self, value):
        if value is None:
            return self.null()

        bool_as_str = None
        with exceptions.ignored(AWTypeError):
            bool_as_str = AW_STRING(value)

        if bool_as_str:
            str_as_bool = self.string_to_bool(bool_as_str)
            if str_as_bool is not None:
                return str_as_bool

        with exceptions.ignored(AWTypeError):
            return bool(AW_FLOAT(value) > 0)

        if hasattr(value, '__bool__'):
            try:
                return bool(value)
            except (AttributeError, LookupError, NotImplementedError,
                    TypeError, ValueError):
                return self._fail_coercion(value)

        return self.null()

    def normalize(self, value):
        return self.__call__(value)

    def format(self, value, **kwargs):
        value = self.__call__(value)
        return self.bool_to_string(value)


class _Integer(BaseCoercer):
    COERCIBLE_TYPES = (bytes, str, float)
    EQUIVALENT_TYPES = (int, )
    NULL = 0

    def coerce(self, value):
        # If casting to int directly fails, try first converting to float,
        # then from float to int. Casting string to int handles "1.5" but
        # "-1.5" fails. The two step approach fixes the negative numbers.
        with exceptions.ignored(ValueError, TypeError):
            return int(value)

        with exceptions.ignored(ValueError, TypeError):
            return int(float(value))

        return self._fail_coercion(value)

    def normalize(self, value):
        return self.__call__(value)

    def format(self, value, **kwargs):
        value = self.__call__(value)

        if 'format_string' not in kwargs:
            return '{}'.format(value or self.null())

        format_string = kwargs.get('format_string')
        if format_string:
            if not isinstance(format_string, str):
                raise AWTypeError('Expected "format_string" to be Unicode str')

            with exceptions.ignored(TypeError):
                return format_string.format(value)

        raise AWTypeError(
            'Invalid "format_string": "{!s}"'.format(format_string)
        )


class _Float(BaseCoercer):
    COERCIBLE_TYPES = (bytes, str, int)
    EQUIVALENT_TYPES = (float, )
    NULL = 0.0

    def coerce(self, value):
        try:
            return float(value)
        except (ValueError, TypeError):
            return self._fail_coercion(value)

    def normalize(self, value):
        return self.__call__(value)

    def bounded(self, value, low=None, high=None):
        _value = self.__call__(value)

        if low is not None:
            low = float(low)
        if high is not None:
            high = float(high)

        if None not in (low, high):
            if low > high:
                raise ValueError('Expected "low" < "high"')

        if low is not None and _value <= low:
            return low
        elif high is not None and _value >= high:
            return high
        return _value

    def format(self, value, **kwargs):
        value = self.__call__(value)

        if 'format_string' not in kwargs:
            return '{0:.1f}'.format(value or self.null())

        format_string = kwargs.get('format_string')
        if format_string:
            if not isinstance(format_string, str):
                raise AWTypeError('Expected "format_string" to be Unicode str')

            with exceptions.ignored(TypeError):
                return format_string.format(value)

        raise AWTypeError(
            'Invalid "format_string": "{!s}"'.format(format_string)
        )


class _String(BaseCoercer):
    COERCIBLE_TYPES = (str, bytes, int, float, bool)
    EQUIVALENT_TYPES = (str, )
    NULL = ''

    def coerce(self, value):
        if value is None:
            return self.null()

        if isinstance(value, bytes):
            try:
                return enc.decode_(value)
            except Exception:
                return self.null()

        if self.coercible(value):
            with exceptions.ignored(ValueError, TypeError):
                return str(value)

        return self._fail_coercion(value)

    def normalize(self, value):
        return self.__call__(value).strip()

    def format(self, value, **kwargs):
        value = self.__call__(value)
        return value


class _MimeType(BaseCoercer):
    COERCIBLE_TYPES = (str, bytes)
    EQUIVALENT_TYPES = ()
    NULL = _NullMIMEType()

    def __call__(self, value=None):
        # Overrides the 'BaseType' __call__ method as to not perform the test
        # after the the value coercion. A valid MIME-type can not be determined
        # by looking at the primitive type alone.
        if value is not None and self.coercible(value):
            if value.strip():
                value = self.coerce(value)
                return value
        return self.null()

    def coerce(self, value):
        string_value = AW_STRING(value)
        string_value = string_value.lstrip('.').strip().lower()

        if string_value:
            _ext = mimemagic.get_extension(string_value)
            if _ext is not None:
                # The value is a MIME-type.
                # Note that an empty string is considered a valid extension.
                return string_value

            _mime = mimemagic.get_mimetype(string_value)
            if _mime:
                # The value is an extension. Return mapped MIME-type.
                return _mime

        return self.null()

    def normalize(self, value):
        return self.__call__(value)

    def format(self, value, **kwargs):
        value = self.__call__(value)

        if value == self.null():
            return str(self.null())

        formatted = mimemagic.get_extension(value)
        return formatted if formatted is not None else self.null()


class _Date(BaseCoercer):
    COERCIBLE_TYPES = (str, bytes, int, float)
    EQUIVALENT_TYPES = (datetime, )

    # Make sure to never return "null" -- raise a 'AWTypeError' exception.
    NULL = 'INVALID DATE'

    # TODO: [TD0054] Represent datetime as UTC within autonameow.

    # Override parent 'null' method to force returning only valid 'datetime'
    # instances. Otherwise, raise an exception to be handled by the caller.
    def null(self):
        raise AWTypeError(
            '"{!r}" got incoercible data'.format(self)
        )

    def coerce(self, value):
        try:
            string_value = AW_STRING(value)
        except AWTypeError as e:
            return self._fail_coercion(value, msg=e)

        string_value = string_value.strip()
        if not string_value:
            return self._fail_coercion(value, msg='string is empty or whitespace')

        try:
            return try_parse_date(string_value)
        except ValueError as e:
            self._fail_coercion(value, msg=e)

    def normalize(self, value):
        value = self.__call__(value)
        if isinstance(value, datetime):
            return value.replace(microsecond=0)

        return self._fail_normalization(value)

    def format(self, value, **kwargs):
        value = self.__call__(value)

        format_string = kwargs.get('format_string')
        if format_string is None:
            format_string = C.DEFAULT_DATETIME_FORMAT_DATE
            if not isinstance(format_string, str):
                raise AWTypeError('Expected "format_string" to be Unicode str')

            with exceptions.ignored(TypeError):
                return datetime.strftime(value, format_string)

        raise AWTypeError(
            'Invalid "format_string": "{!s}"'.format(format_string)
        )


class _TimeDate(BaseCoercer):
    COERCIBLE_TYPES = (str, bytes, int, float)
    EQUIVALENT_TYPES = (datetime, )

    # Make sure to never return "null" -- raise a 'AWTypeError' exception.
    NULL = 'INVALID DATE'

    # TODO: [TD0054] Represent datetime as UTC within autonameow.

    # Override parent 'null' method to force returning only valid 'datetime'
    # instances. Otherwise, raise an exception to be handled by the caller.
    def null(self):
        raise AWTypeError(
            '"{!r}" got incoercible data'.format(self)
        )

    def coerce(self, value):
        try:
            string_value = AW_STRING(value)
        except AWTypeError as e:
            return self._fail_coercion(value, msg=e)

        string_value = string_value.strip()
        if not string_value:
            return self._fail_coercion(value, msg='string is empty or whitespace')

        try:
            dt = try_parse_datetime(string_value)
        except ValueError as e:
            return self._fail_coercion(value, msg=e)
        else:
            # TODO: [TD0054] Represent datetime as UTC within autonameow.
            from util.dateandtime import timezone_aware_to_naive
            naive_dt = timezone_aware_to_naive(dt)

            # TODO: [cleanup] Really OK to just drop the microseconds?
            return naive_dt.replace(microsecond=0)

    def normalize(self, value):
        value = self.__call__(value)
        if isinstance(value, datetime):
            return value.replace(microsecond=0)

        return self._fail_normalization(value)

    def format(self, value, **kwargs):
        value = self.__call__(value)

        format_string = kwargs.get('format_string')
        if format_string is None:
            format_string = C.DEFAULT_DATETIME_FORMAT_DATETIME
            if not isinstance(format_string, str):
                raise AWTypeError('Expected "format_string" to be Unicode str')

            with exceptions.ignored(TypeError):
                return datetime.strftime(value, format_string)

        raise AWTypeError(
            'Invalid "format_string": "{!s}"'.format(format_string)
        )


class _ExifToolTimeDate(_TimeDate):
    def coerce(self, value):
        try:
            string_value = AW_STRING(value)
        except AWTypeError as e:
            return self._fail_coercion(value, msg=e)

        string_value = string_value.strip()
        if not string_value:
            return self._fail_coercion(value, msg='string is empty or whitespace')

        if re.match(r'.*0000:00:00 00:00:00.*', string_value):
            return self._fail_coercion(value, msg='date and time is all zeroes')

        last_exception = None
        try:
            return try_parse_datetime(string_value)
        except ValueError as e:
            last_exception = e
        try:
            return try_parse_date(string_value)
        except ValueError as e:
            last_exception = e

        return self._fail_coercion(value, msg=last_exception)


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
RE_LOOSE_DATETIME_US_TZ = re.compile(
    _pat_loose_date + _pat_datetime_sep + _pat_loose_time + _pat_microseconds
    + _pat_timezone
)


def normalize_date(string):
    match = RE_LOOSE_DATE.search(string)
    if not match:
        return None

    normalized = re.sub(RE_LOOSE_DATE, r'\1-\2-\3', string)
    return normalized


def normalize_datetime_with_microseconds_and_timezone(string):
    match = RE_LOOSE_DATETIME_US_TZ.search(string)
    if not match:
        return None

    normalized = re.sub(RE_LOOSE_DATETIME_US_TZ, r'\1-\2-\3T\4:\5:\6.\7 \8\9\10', string)
    return normalized.replace(' ', '')


def normalize_datetime_with_timezone(string):
    match = RE_LOOSE_DATETIME_TZ.search(string)
    if not match:
        return None

    normalized = re.sub(RE_LOOSE_DATETIME_TZ, r'\1-\2-\3T\4:\5:\6 \7\8\9', string)
    return normalized.replace(' ', '')


def normalize_datetime(string):
    match = RE_LOOSE_DATETIME.search(string)
    if not match:
        return None

    normalized = re.sub(RE_LOOSE_DATETIME, r'\1-\2-\3T\4:\5:\6', string)
    return normalized.replace(' ', '')


def normalize_datetime_with_microseconds(string):
    match = RE_LOOSE_DATETIME_US.search(string)
    if not match:
        return None

    normalized = re.sub(RE_LOOSE_DATETIME_US, r'\1-\2-\3T\4:\5:\6.\7', string)
    return normalized


def try_parse_datetime(s):
    """
    Attempt to parse get a 'datetime' object from a Unicode string.

    Tries various patterns in turn and returns the first successfully
    parsed 'datetime' object.
    If the string cannot be parsed, a 'ValueError' exception is raised.

    Args:
        s (str): Unicode string to parse.

    Returns:
        The given string parsed into an instance of 'datetime'.

    Raises:
        ValueError: The given string could not be parsed.
        AssertionError: The given string is not a Unicode string.
    """
    assert isinstance(s, str)

    # Handle "malformed" (?) dates produced by "Mac OS X 10.11.5 Quartz PDFContext".
    if s.endswith('Z'):
        s = s[:-1]

    for normalization_func, strptime_pattern in [
        (normalize_datetime_with_microseconds_and_timezone, '%Y-%m-%dT%H:%M:%S.%f%z'),
        (normalize_datetime_with_timezone, '%Y-%m-%dT%H:%M:%S%z'),
        (normalize_datetime_with_microseconds, '%Y-%m-%dT%H:%M:%S.%f'),
        (normalize_datetime, '%Y-%m-%dT%H:%M:%S'),
    ]:
        normalized_s = normalization_func(s)
        if normalized_s:
            assert isinstance(normalized_s, str)
            with exceptions.ignored(ValueError):
                return datetime.strptime(normalized_s, strptime_pattern)

    raise ValueError('Unable to parse datetime from string "{!s}"'.format(s))


def try_parse_date(s):
    """
    Attempt to parse get a 'datetime' object from a Unicode string.

    First attempts to parse a "normalized" version of string.
    If this fails, the second approach is a brute force method that
    also assumes that the date is a variation of the form "YYYY-mm-dd".
    If the string cannot be parsed, a 'ValueError' exception is raised.

    Args:
        s (str): Unicode string to parse.

    Returns:
        The given string parsed into an instance of 'datetime',
        without any time-information.

    Raises:
        ValueError: The given string could not be parsed.
        AssertionError: The given string is not a Unicode string.
    """
    assert isinstance(s, str)

    match = normalize_date(s)
    if match:
        with exceptions.ignored(ValueError, TypeError):
            return datetime.strptime(match, '%Y-%m-%d')

    # Alternative, brute force method. Extract digits.
    # Assumes year, month, day is in ISO-date-like order.
    digits = textutils.extract_digits(s)
    if digits:
        assert isinstance(digits, str)

        # TODO: [hack] This is not good ..
        MATCH_PATTERNS = [('%Y%m%d', 8),
                          ('%Y%m', 6),
                          ('%Y', 4)]
        from util.dateandtime import parse_datetime_from_start_to_char_n_patterns
        match = parse_datetime_from_start_to_char_n_patterns(digits, MATCH_PATTERNS)
        if match:
            return match

    raise ValueError('Unable to parse date from string "{!s}"'.format(s))


def force_string(raw_value):
    # Silently fetch single value from list.
    if isinstance(raw_value, list) and len(raw_value) == 1:
        raw_value = raw_value[0]

    try:
        str_value = AW_STRING(raw_value)
    except AWTypeError:
        return AW_STRING.null()
    else:
        return str_value


def force_stringlist(raw_values):
    if not raw_values:
        return [AW_STRING.null()]

    try:
        str_list = listof(AW_STRING)(raw_values)
    except AWTypeError:
        return [AW_STRING.null()]
    else:
        return str_list


class MultipleTypes(object):
    """
    For defining coercion of lists of a specific type.

    Do not call directly! Use the 'listof()' function.
    Coercing a list of values:

        coerced_list = coercers.listof(coercers.AW_STRING)(raw_list)

    Formatting a list of values:

        formatted_list = coercers.listof(coercers.AW_STRING).format(raw_list)
    """
    def __init__(self, coercer):
        sanity.check_isinstance(coercer, BaseCoercer)
        self.coercer = coercer

    def __call__(self, value):
        if value is None:
            return [self.coercer.null()]

        if not isinstance(value, list):
            value = [value]

        out = list()
        for v in value:
            _coerced = self.coercer(v)
            if _coerced is None:
                continue

            out.append(_coerced)

        return out

    def format(self, value):
        if value is None:
            return [self.coercer.null()]

        if not isinstance(value, list):
            value = [value]

        out = list()
        for v in value:
            _formatted = self.coercer.format(v)
            if _formatted is None:
                continue

            out.append(_formatted)

        return out

    def __contains__(self, item):
        if isinstance(item, BaseCoercer):
            return item == self.coercer
        return False

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return self.coercer == other.coercer
        return False


def listof(coercer):
    return MultipleTypes(coercer)


# Singletons for actual use.
AW_BOOLEAN = _Boolean()
AW_DATE = _Date()
AW_PATH = _Path()
AW_PATHCOMPONENT = _PathComponent()
AW_INTEGER = _Integer()
AW_FLOAT = _Float()
AW_STRING = _String()
AW_MIMETYPE = _MimeType()
AW_TIMEDATE = _TimeDate()
AW_EXIFTOOLTIMEDATE = _ExifToolTimeDate()

NULL_AW_MIMETYPE = _NullMIMEType()


# This is not clearly defined otherwise.
BUILTIN_REGEX_TYPE = type(re.compile(''))
