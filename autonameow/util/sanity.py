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


def check_internal_bytestring(value):
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


def check_internal_string(value):
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


def check_isinstance(thing, expected_type):
    """
    Checks that a given "thing" is an instance of "expected_type".

    Args:
        thing: The object to test.
        expected_type: Expected type of the passed in "thing".

    Raises:
        AssertionError: Given "thing" is not an instance of "expected_type".
    """
    if not __debug__:
        return
    assert isinstance(thing, expected_type), (
        'Expected type {!s}.  Got {!s} ({!s})'.format(expected_type,
                                                      type(thing), thing)
    )
