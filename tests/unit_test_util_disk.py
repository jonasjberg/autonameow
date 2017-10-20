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

from core.exceptions import EncodingBoundaryViolation
from core.util.disk import compare_basenames


class TestCompareBasenames(TestCase):
    def test_compare_basenames_is_defined(self):
        self.assertIsNotNone(compare_basenames)

    def test_compare_basenames_raises_exceptions_given_invalid_input(self):
        def _raises(exception_, a, b):
            with self.assertRaises(exception_):
                compare_basenames(a, b)

        _raises(ValueError, None, None)
        _raises(ValueError, None, None)
        _raises(ValueError, None, [])
        _raises(ValueError, [], None)
        _raises(EncodingBoundaryViolation, 1, 2)
        _raises(EncodingBoundaryViolation, [], [])
        _raises(EncodingBoundaryViolation, object(), object())
        _raises(EncodingBoundaryViolation, 'a', 'b')
        _raises(EncodingBoundaryViolation, 'a', [])
        _raises(EncodingBoundaryViolation, '', '')
        _raises(EncodingBoundaryViolation, '', ' ')
        _raises(EncodingBoundaryViolation, '_', '')
        _raises(EncodingBoundaryViolation, 'a', 2)
        _raises(EncodingBoundaryViolation, 1, 'b')
        _raises(EncodingBoundaryViolation, 'a', b'a')
        _raises(EncodingBoundaryViolation, b'a', 'a')

    def test_comparing_equal_basenames_returns_true(self):
        def _assert_true(first, second):
            self.assertTrue(compare_basenames(first, second))
            self.assertTrue(
                isinstance(compare_basenames(first, second), bool)
            )

        _assert_true(b'', b'')
        _assert_true(b' ', b' ')
        _assert_true(b'a', b'a')
        _assert_true(b'foo', b'foo')
        _assert_true(b'_', b'_')
        _assert_true('å'.encode('utf-8'), 'å'.encode('utf-8'))
        _assert_true('ö'.encode('utf-8'), 'ö'.encode('utf-8'))
        _assert_true('A_ö'.encode('utf-8'), 'A_ö'.encode('utf-8'))
        _assert_true(b'__', b'__')

    def test_comparing_unequal_basenames_returns_false(self):
        def _assert_false(first, second):
            self.assertFalse(compare_basenames(first, second))
            self.assertTrue(
                isinstance(compare_basenames(first, second), bool)
            )

        _assert_false(b' ', b'y')
        _assert_false(b'x', b'y')
        _assert_false(b'foo_', b'foo')
        _assert_false('ä'.encode('utf-8'), b'a')
        _assert_false('Ä'.encode('utf-8'), b'A')
        _assert_false('Ä'.encode('utf-8'), 'A'.encode('utf-8'))

        # Looks identical but the second string contains character '\xc2\xa0'
        # between the last timestamp digit and 'W' instead of a simple space.
        _assert_false(
            '2017-08-14T015051 Working on autonameow -- dev projects.png'.encode('utf-8'),
            '2017-08-14T015051 Working on autonameow -- dev projects.png'.encode('utf-8')
        )
