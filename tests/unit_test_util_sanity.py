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

from unittest import TestCase

from core.exceptions import (
    AWAssertionError,
    EncodingBoundaryViolation
)
from core.util import sanity


class TestSanityCheckInternalBytestring(TestCase):
    def test_check_passes(self):
        def _assert_valid(test_input):
            sanity.check_internal_bytestring(test_input)

        _assert_valid(b'')
        _assert_valid(b'foo')

    def test_raises_exception_for_non_bytes_values(self):
        def _assert_raises(test_input):
            with self.assertRaises(EncodingBoundaryViolation):
                sanity.check_internal_bytestring(test_input)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises('foo')


class TestSanityCheckInternalString(TestCase):
    def test_check_passes(self):
        def _assert_valid(test_input):
            sanity.check_internal_string(test_input)

        _assert_valid('')
        _assert_valid('foo')
        _assert_valid(b'foo'.decode('utf8'))

    def test_raises_exception_for_non_bytes_values(self):
        def _assert_raises(test_input):
            with self.assertRaises(EncodingBoundaryViolation):
                sanity.check_internal_string(test_input)

        _assert_raises(None)
        _assert_raises(b'')
        _assert_raises(b'foo')


class TestSanityCheckIsinstance(TestCase):
    def test_check_passes(self):
        def _assert_ok(test_input, expected):
            sanity.check_isinstance(test_input, expected)

        _assert_ok('', str)
        _assert_ok(1, int)
        _assert_ok(None, object)

        # Intended to prevent false positives. Probably a bad idea.
        _assert_ok(None, None)

    def test_assertion_failure_raises_exception(self):
        def _assert_raises(test_input, expected):
            with self.assertRaises(AWAssertionError):
                sanity.check_isinstance(test_input, expected)

        _assert_raises(str, str)
        _assert_raises(b'', str)
        _assert_raises(bytes, str)
        _assert_raises(None, str)

        _assert_raises(bytes, bytes)
        _assert_raises('', bytes)
        _assert_raises(str, bytes)
        _assert_raises(None, bytes)

        _assert_raises(float, float)
        _assert_raises(1, float)
        _assert_raises(int, float)
        _assert_raises(None, float)

        _assert_raises(int, int)
        _assert_raises(1.0, int)
        _assert_raises(float, int)
        _assert_raises(None, int)

        _assert_raises('', None)
        _assert_raises(str, None)
        _assert_raises(b'', None)
        _assert_raises(bytes, None)


class TestSanityCheck(TestCase):
    def test_check_passes(self):
        def _assert_ok(test_input, msg=None):
            if msg:
                sanity.check(test_input, msg)
            else:
                sanity.check(test_input, msg)

        _assert_ok(1 == 1)
        _assert_ok(1 == 1, 'Expr: 1 == 1')
        _assert_ok(True)
        _assert_ok(True, 'Expr: True')
        _assert_ok('a' == 'a' and 'a' != 'b')
        _assert_ok('a' == 'a' and 'a' != 'b', 'Expr: foo')

    def test_assertion_failure_raises_exception(self):
        def _assert_raises(test_input, msg=None):
            with self.assertRaises(AWAssertionError):
                if msg:
                    sanity.check(test_input, msg)
                else:
                    sanity.check(test_input, msg)

        _assert_raises(1 == 2)
        _assert_raises(1 == 2, 'Expr: 1 == 2')
        _assert_raises(False)
        _assert_raises(False, 'Expr: False')
        _assert_raises('a' == 'X' and 'a' != 'Z')
        _assert_raises('a' == 'X' and 'a' != 'Z', 'Expr: foo')
