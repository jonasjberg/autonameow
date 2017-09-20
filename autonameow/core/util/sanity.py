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

from core import exceptions


def assert_internal_bytestring(value):
    """
    Checks that a given value is an "internal bytestring", I.E. bytes.

    Intended for sanity checking, in place of assertions.

    Args:
        value: The value to test.
    Raises:
        EncodingBoundaryViolation: The given value is not a bytestring.
    """
    if not isinstance(value, bytes):
        _msg = ('Assertion Failed - Expected an "internal" bytestring.'
                '  Got "{!s}" ("{!s}")'.format(type(value), value))
        raise exceptions.EncodingBoundaryViolation(_msg)


def assert_internal_string(value):
    """
    Checks that a given value is an "internal string", I.E. Unicode str.

    Intended for sanity checking, in place of assertions.

    Args:
        value: The value to test.
    Raises:
        EncodingBoundaryViolation: The given value is not a Unicode str.
    """
    if not isinstance(value, str):
        _msg = ('Assertion Failed - Expected a Unicode string.'
                '  Got "{!s}" ("{!s}")'.format(type(value), value))
        raise exceptions.EncodingBoundaryViolation(_msg)


def assert_isinstance(value, expected):
    """
    Checks that argument 'value' is an instance of argument 'expected'.
    Args:
        value: The value to test.
        expected: The expected type.
    Raises:
        AWAssertionError: The given value is not an instance of 'expected'.
    """
    if expected is None:
        # Intended to prevent false positives. Probably a bad idea.
        expected = type(None)

    if not isinstance(value, expected):
        raise exceptions.AWAssertionError(
            'Assertion Failed - Expected type "{!s}". Got type "{!s}"'.format(
                expected, type(value)
            )
        )


def assertthat(expression, msg=None):
    if msg is None:
        msg = 'Reason unknown'

    if not expression:
        raise exceptions.AWAssertionError(
            'Assertion Failed - "{!s}"'.format(msg)
        )
