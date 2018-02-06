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

import os
from unittest import TestCase
from datetime import datetime

import unit.utils as uu
from core import types


USER_HOME = os.path.expanduser('~')


class TestBaseType(TestCase):
    def setUp(self):
        self.base_type = types.BaseType()

    def test_null(self):
        self.assertEqual(self.base_type.NULL, self.base_type(None))
        self.assertEqual(self.base_type.NULL, types.BaseNullValue())
        self.assertFalse(self.base_type.NULL)
        self.assertFalse(self.base_type.null())

    def test_normalize(self):
        with self.assertRaises(NotImplementedError):
            self.base_type.normalize(None)

    def test_base_type_call(self):
        self.assertEqual('foo', self.base_type('foo'))
        self.assertEqual(types.BaseNullValue(), self.base_type(None))

    def test_inheriting_classes_must_implement_format(self):
        with self.assertRaises(NotImplementedError):
            self.base_type.format(None)

    def test_testing_equivalency(self):
        self.assertTrue(self.base_type.equivalent('foo'))
        self.assertFalse(self.base_type.equivalent(b'foo'))
        self.assertFalse(self.base_type.equivalent(False))
        self.assertFalse(self.base_type.equivalent(1))


class TestBaseNullValue(TestCase):
    def setUp(self):
        self.bn = types.BaseNullValue()

    def test_boolean_evaluation_returns_false(self):
        self.assertFalse(self.bn)
        self.assertEqual(False, self.bn)
        self.assertFalse(bool(self.bn))
        self.assertEqual(False, bool(self.bn))
        self.assertTrue(not self.bn)
        self.assertTrue(not bool(self.bn))
        self.assertEqual(True, not self.bn)
        self.assertEqual(True, not bool(self.bn))

    def test_comparison(self):
        def _is_equal(expected, value):
            actual = self.bn == value
            self.assertEqual(expected, actual)
            self.assertTrue(bool(expected) == bool(actual))
            self.assertIsInstance(actual, bool)

        _is_equal(True, value=False)
        _is_equal(True, value=self.bn)
        _is_equal(True, value=types.BaseNullValue())
        _is_equal(True, value=types.BaseNullValue)
        _is_equal(False, value=None)
        _is_equal(False, value=True)
        _is_equal(False, value=1)
        _is_equal(False, value=[])
        _is_equal(False, value={})
        _is_equal(False, value=object)
        _is_equal(False, value=object())
        _is_equal(False, value='foo')

    def test___str__(self):
        expected = '(NULL BaseType value)'
        self.assertEqual(expected, str(self.bn))

    def test___hash__(self):
        actual = hash(self.bn)
        self.assertIsNotNone(actual)

    def test_hashable_for_set_membership(self):
        a = types.BaseNullValue()
        b = types.BaseNullValue()

        container = set()
        container.add(a)
        self.assertEqual(len(container), 1)
        self.assertIn(a, container)
        self.assertIn(b, container)

        container.add(b)
        self.assertEqual(len(container), 1)
        self.assertIn(a, container)
        self.assertIn(b, container)


class TestNullMIMEType(TestCase):
    def setUp(self):
        self.nm = types.NullMIMEType()

    def test_boolean_evaluation_returns_false(self):
        self.assertFalse(self.nm)
        self.assertEqual(False, self.nm)
        self.assertFalse(bool(self.nm))
        self.assertEqual(False, bool(self.nm))
        self.assertTrue(not self.nm)
        self.assertTrue(not bool(self.nm))
        self.assertEqual(True, not self.nm)
        self.assertEqual(True, not bool(self.nm))

    def test_comparison(self):
        def _is_equal(expected, value):
            actual = self.nm == value
            self.assertEqual(expected, actual)
            self.assertTrue(bool(expected) == bool(actual))
            self.assertIsInstance(actual, bool)

        _is_equal(True, value=False)
        _is_equal(True, value=self.nm)
        _is_equal(True, value=types.NullMIMEType())
        _is_equal(True, value=types.NullMIMEType)
        _is_equal(False, value=types.BaseNullValue())
        _is_equal(False, value=types.BaseNullValue())
        _is_equal(False, value=None)
        _is_equal(False, value=True)
        _is_equal(False, value=1)
        _is_equal(False, value=[])
        _is_equal(False, value={})
        _is_equal(False, value=object)
        _is_equal(False, value=object())
        _is_equal(False, value='foo')

    def test___str__(self):
        expected = types.NullMIMEType.AS_STRING
        self.assertEqual(expected, str(self.nm))

    def test___hash__(self):
        actual = hash(self.nm)
        self.assertIsNotNone(actual)

    def test_hashable_for_set_membership(self):
        a = types.NullMIMEType()
        b = types.NullMIMEType()

        container = set()
        container.add(a)
        self.assertEqual(len(container), 1)
        self.assertIn(a, container)
        self.assertIn(b, container)

        container.add(b)
        self.assertEqual(len(container), 1)
        self.assertIn(a, container)
        self.assertIn(b, container)


class TestTypeBoolean(TestCase):
    def test_coerces_expected_primitive(self):
        self.assertEqual(bool, type(types.AW_BOOLEAN(None)))

    def test_null(self):
        self.assertEqual(types.AW_BOOLEAN.NULL, types.AW_BOOLEAN(None))
        self.assertNotEqual(types.BaseNullValue, types.AW_BOOLEAN(None),
                            'BaseType default "null" must be overridden')

    def test_normalize(self):
        def _assert_normalizes(test_data, expected):
            self.assertEqual(expected, types.AW_BOOLEAN.normalize(test_data))

        _assert_normalizes(True, True)
        _assert_normalizes(False, False)
        _assert_normalizes(-1, False)
        _assert_normalizes(0, False)
        _assert_normalizes(1, True)
        _assert_normalizes(-1.5, False)
        _assert_normalizes(-1.0001, False)
        _assert_normalizes(-1.0, False)
        _assert_normalizes(-0.05, False)
        _assert_normalizes(-0.0, False)
        _assert_normalizes(0.0, False)
        _assert_normalizes(0.05, True)
        _assert_normalizes(1.0, True)
        _assert_normalizes(1.0001, True)
        _assert_normalizes(1.5, True)
        _assert_normalizes('true', True)
        _assert_normalizes('True', True)
        _assert_normalizes('yes', True)
        _assert_normalizes('Yes', True)
        _assert_normalizes('no', False)
        _assert_normalizes('No', False)
        _assert_normalizes('false', False)
        _assert_normalizes('False', False)
        _assert_normalizes(b'true', True)
        _assert_normalizes(b'True', True)
        _assert_normalizes(b'yes', True)
        _assert_normalizes(b'Yes', True)
        _assert_normalizes(b'no', False)
        _assert_normalizes(b'No', False)
        _assert_normalizes(b'false', False)
        _assert_normalizes(b'False', False)

    def test_call_with_none(self):
        self.assertEqual(False, types.AW_BOOLEAN(None))

    def test_call_with_coercible_data(self):
        def _assert_returns(test_data, expected):
            self.assertEqual(expected, types.AW_BOOLEAN(test_data))

        _assert_returns(True, True)
        _assert_returns(False, False)
        _assert_returns('true', True)
        _assert_returns('True', True)
        _assert_returns('True', True)
        _assert_returns('yes', True)
        _assert_returns('Yes', True)
        _assert_returns('no', False)
        _assert_returns('No', False)
        _assert_returns('false', False)
        _assert_returns('False', False)
        _assert_returns('positive', True)
        _assert_returns('on', True)
        _assert_returns('enable', True)
        _assert_returns('enabled', True)
        _assert_returns('active', True)
        _assert_returns(b'true', True)
        _assert_returns(b'True', True)
        _assert_returns(b'True', True)
        _assert_returns(b'yes', True)
        _assert_returns(b'Yes', True)
        _assert_returns(b'no', False)
        _assert_returns(b'No', False)
        _assert_returns(b'false', False)
        _assert_returns(b'False', False)
        _assert_returns(b'negative', False)
        _assert_returns(b'off', False)
        _assert_returns(b'disable', False)
        _assert_returns(b'disabled', False)
        _assert_returns(b'inactive', False)
        _assert_returns(-1, False)
        _assert_returns(0, False)
        _assert_returns(1, True)
        _assert_returns(-1.5, False)
        _assert_returns(-1.0001, False)
        _assert_returns(-1.0, False)
        _assert_returns(-0.05, False)
        _assert_returns(-0.0, False)
        _assert_returns(0.0, False)
        _assert_returns(0.05, True)
        _assert_returns(1.0, True)
        _assert_returns(1.0001, True)
        _assert_returns(1.5, True)

        class _AlwaysTrue(object):
            def __bool__(self):
                return True

        _assert_returns(_AlwaysTrue(), True)
        _at = _AlwaysTrue()
        _assert_returns(_at, True)

        class _AlwaysFalse(object):
            def __bool__(self):
                return False

        _assert_returns(_AlwaysFalse(), False)
        _af = _AlwaysFalse()
        _assert_returns(_af, False)

        _datetime_object = uu.str_to_datetime('2017-09-25 100951')
        _assert_returns(_datetime_object, False)

    def test_call_with_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_BOOLEAN(test_data)

        self.assertEqual(types.AW_BOOLEAN.NULL, types.AW_BOOLEAN('foo'))
        self.assertEqual(types.AW_BOOLEAN.NULL, types.AW_BOOLEAN(None))

        class _NoBool(object):
            def __raise(self):
                raise ValueError

            def __bool__(self):
                return self.__raise()

        _assert_raises(_NoBool())

    def test_format(self):
        def _assert_formats(test_data, expected):
            self.assertEqual(expected, types.AW_BOOLEAN.format(test_data))

        _assert_formats(None, 'False')
        _assert_formats(False, 'False')
        _assert_formats(True, 'True')
        _assert_formats('false', 'False')
        _assert_formats('true', 'True')
        _assert_formats('None', 'False')
        _assert_formats('False', 'False')
        _assert_formats('True', 'True')
        _assert_formats(b'false', 'False')
        _assert_formats(b'true', 'True')
        _assert_formats(b'None', 'False')
        _assert_formats(b'False', 'False')
        _assert_formats(b'True', 'True')


class TestTypeInteger(TestCase):
    def test_coerces_expected_primitive(self):
        self.assertEqual(int, type(types.AW_INTEGER(None)))

    def test_null(self):
        self.assertEqual(types.AW_INTEGER.NULL, types.AW_INTEGER(None))
        self.assertNotEqual(types.AW_INTEGER(None), types.BaseNullValue,
                            'BaseType default "null" must be overridden')

    def test_normalize(self):
        self.assertEqual(types.AW_INTEGER.NULL,
                         types.AW_INTEGER.normalize(None))
        self.assertEqual(-1, types.AW_INTEGER.normalize(-1))
        self.assertEqual(0, types.AW_INTEGER.normalize(0))
        self.assertEqual(1, types.AW_INTEGER.normalize(1))

    def test_call_with_none(self):
        self.assertEqual(0, types.AW_INTEGER(None))

    def test_call_with_coercible_data(self):
        def _assert_returns(test_data, expected):
            self.assertEqual(expected, types.AW_INTEGER(test_data))

        _assert_returns(None, 0)
        _assert_returns(-1, -1)
        _assert_returns(0, 0)
        _assert_returns(1, 1)
        _assert_returns(-1, -1)
        _assert_returns(-1.5, -1)
        _assert_returns(-1.0, -1)
        _assert_returns(1.0, 1)
        _assert_returns(1.5, 1)
        _assert_returns('0', 0)
        _assert_returns('1', 1)
        _assert_returns('-1', -1)
        _assert_returns('-1.5', -1)
        _assert_returns('-1.0', -1)
        _assert_returns('1.0', 1)
        _assert_returns('1.5', 1)

    def test_call_with_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_INTEGER(test_data)

        _assert_raises([])
        _assert_raises([1, 2])
        _assert_raises(['a', 'b'])
        _assert_raises('')
        _assert_raises(' ')
        _assert_raises('foo')

    def test_format_valid_data(self):
        def _assert_formats(test_data, expected):
            self.assertEqual(expected, types.AW_INTEGER.format(test_data))

        _assert_formats(1, '1')
        _assert_formats('1', '1')
        _assert_formats(b'1', '1')

    def test_format_valid_data_with_format_string(self):
        def _assert_formats(test_data, format_string, expected):
            self.assertEqual(
                expected,
                types.AW_INTEGER.format(test_data, format_string=format_string)
            )

        _assert_formats(None, '{:01d}', '0')
        _assert_formats(1, '{:02d}', '01')
        _assert_formats(2, '{:03d}', '002')
        _assert_formats(33, '{:04d}', '0033')
        _assert_formats(None, 'x', 'x')
        _assert_formats(1, 'x', 'x')
        _assert_formats(2, 'x', 'x')
        _assert_formats(33, 'x', 'x')

    def test_format_raises_exception_for_invalid_format_strings(self):
        def _assert_raises(test_data, format_string):
            with self.assertRaises(types.AWTypeError):
                types.AW_INTEGER.format(test_data, format_string=format_string)

        _assert_raises(1, None)
        _assert_raises(1, [])
        _assert_raises(1, '')
        _assert_raises(1, b'')
        _assert_raises(1, b'x')


class TestTypeFloat(TestCase):
    def test_coerces_expected_primitive(self):
        self.assertEqual(float, type(types.AW_FLOAT(None)))

    def test_null(self):
        self.assertEqual(types.AW_FLOAT.NULL, types.AW_FLOAT(None))
        self.assertNotEqual(types.AW_FLOAT(None), types.BaseNullValue,
                            'BaseType default "null" must be overridden')

    def test_normalize(self):
        self.assertEqual(-1, types.AW_FLOAT.normalize(-1))
        self.assertEqual(0, types.AW_FLOAT.normalize(0))
        self.assertEqual(1, types.AW_FLOAT.normalize(1))

    def test_call_with_none(self):
        self.assertEqual(types.AW_FLOAT.NULL, types.AW_FLOAT(None))

    def test_call_with_coercible_data(self):
        def _assert_returns(test_data, expected):
            self.assertEqual(expected, types.AW_FLOAT(test_data))

        _assert_returns(None, 0.0)
        _assert_returns(-1, -1.0)
        _assert_returns(0, 0.0)
        _assert_returns(1, 1.0)
        _assert_returns(-1.5, -1.5)
        _assert_returns(-1.0, -1.0)
        _assert_returns(1.0, 1.0)
        _assert_returns(1.5, 1.5)
        _assert_returns('-1.5', -1.5)
        _assert_returns('-1.0', -1.0)
        _assert_returns('-1', -1.0)
        _assert_returns('0', 0.0)
        _assert_returns('1', 1.0)
        _assert_returns('1.5', 1.5)
        _assert_returns(b'-1.5', -1.5)
        _assert_returns(b'-1.0', -1.0)
        _assert_returns(b'-1', -1.0)
        _assert_returns(b'0', 0.0)
        _assert_returns(b'1', 1.0)
        _assert_returns(b'1.5', 1.5)

    def test_call_with_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_FLOAT(test_data)

        _assert_raises('foo')
        _assert_raises(datetime.now())

    def test_format_valid_data(self):
        def _assert_formats(test_data, expected):
            self.assertEqual(expected, types.AW_FLOAT.format(test_data))

        _assert_formats(None, '0.0')
        _assert_formats(1, '1.0')
        _assert_formats(20, '20.0')
        _assert_formats('1', '1.0')
        _assert_formats('20', '20.0')
        _assert_formats(b'1', '1.0')
        _assert_formats(b'20', '20.0')

    def test_format_valid_data_with_format_string(self):
        def _assert_formats(test_data, format_string, expected):
            self.assertEqual(
                expected,
                types.AW_FLOAT.format(test_data, format_string=format_string)
            )

        _assert_formats(None, '{0:.1f}', '0.0')
        _assert_formats(1, '{0:.1f}', '1.0')
        _assert_formats(2, '{0:.2f}', '2.00')
        _assert_formats(33, '{0:.3f}', '33.000')
        _assert_formats('1', '{0:.1f}', '1.0')
        _assert_formats('2', '{0:.2f}', '2.00')
        _assert_formats('33', '{0:.3f}', '33.000')
        _assert_formats(b'1', '{0:.1f}', '1.0')
        _assert_formats(b'2', '{0:.2f}', '2.00')
        _assert_formats(b'33', '{0:.3f}', '33.000')
        _assert_formats(None, 'x', 'x')
        _assert_formats(1, 'x', 'x')
        _assert_formats(2, 'x', 'x')
        _assert_formats(33, 'x', 'x')
        _assert_formats('1', 'x', 'x')
        _assert_formats('2', 'x', 'x')
        _assert_formats('33', 'x', 'x')
        _assert_formats(b'1', 'x', 'x')
        _assert_formats(b'2', 'x', 'x')
        _assert_formats(b'33', 'x', 'x')

    def test_format_raises_exception_for_invalid_format_strings(self):
        def _assert_raises(test_data, format_string):
            with self.assertRaises(types.AWTypeError):
                types.AW_FLOAT.format(test_data, format_string=format_string)

        _assert_raises(1.0, None)
        _assert_raises(1.0, [])
        _assert_raises(1.0, '')
        _assert_raises(1.0, b'')
        _assert_raises(1.0, b'x')

    def test_bounded_low(self):
        def _aE(test_input, low, expected):
            actual = types.AW_FLOAT.bounded(test_input, low=low)
            self.assertEqual(expected, actual)

        _aE(10.0,    0, 10.0)
        _aE(1.0,     0,  1.0)
        _aE(-0.0001, 0,  0.0)
        _aE(-1.0,    0,  0.0)
        _aE(-10.0,   0,  0.0)

        _aE(10.0,    1, 10.0)
        _aE(1.0,     1,  1.0)
        _aE(-0.0001, 1,  1.0)
        _aE(-1.0,    1,  1.0)
        _aE(-10.0,   1,  1.0)

        _aE(10.0,    2, 10.0)
        _aE(1.0,     2,  2.0)
        _aE(-0.0001, 2,  2.0)
        _aE(-1.0,    2,  2.0)
        _aE(-10.0,   2,  2.0)

    def test_bounded_high(self):
        def _aE(test_input, high, expected):
            actual = types.AW_FLOAT.bounded(test_input, high=high)
            self.assertEqual(expected, actual)

        _aE(10.0,    0,   0.0)
        _aE(1.0,     0,   0.0)
        _aE(-0.001,  0,  -0.001)
        _aE(-1.0,    0,  -1.0)
        _aE(-10.0,   0, -10.0)

        _aE(10.0,    1,   1.0)
        _aE(1.0,     1,   1.0)
        _aE(-0.0001, 1,  -0.0001)
        _aE(-1.0,    1,  -1.0)
        _aE(-10.0,   1, -10.0)

        _aE(10.0,    2,   2.0)
        _aE(1.0,     2,   1.0)
        _aE(-0.0001, 2,  -0.0001)
        _aE(-1.0,    2,  -1.0)
        _aE(-10.0,   2, -10.0)

    def test_bounded_low_and_high(self):
        def _aE(test_input, low, high, expected):
            actual = types.AW_FLOAT.bounded(test_input, low=low, high=high)
            self.assertEqual(expected, actual)

        _aE(10.0,    0,  0,  0.0)
        _aE(1.0,     0,  0,  0.0)
        _aE(-0.0001, 0,  0,  0.0)
        _aE(-1.0,    0,  0,  0.0)
        _aE(-10.0,   0,  0,  0.0)
        _aE(10.0,    0,  1,  1.0)
        _aE(1.0,     0,  1,  1.0)
        _aE(-0.0001, 0,  1,  0.0)
        _aE(-1.0,    0,  1,  0.0)
        _aE(-10.0,   0,  1,  0.0)
        _aE(10.0,    0,  2,  2.0)
        _aE(1.0,     0,  2,  1.0)
        _aE(-0.0001, 0,  2,  0.0)
        _aE(-1.0,    0,  2,  0.0)
        _aE(-10.0,   0,  2,  0.0)
        _aE(10.0,    0, 10, 10.0)
        _aE(1.0,     0, 10,  1.0)
        _aE(-0.0001, 0, 10,  0.0)
        _aE(-1.0,    0, 10,  0.0)
        _aE(-10.0,   0, 10,  0.0)
        _aE(10.0,    1,  1,  1.0)
        _aE(1.0,     1,  1,  1.0)
        _aE(-0.0001, 1,  1,  1.0)
        _aE(-1.0,    1,  1,  1.0)
        _aE(-10.0,   1,  1,  1.0)
        _aE(10.0,    1,  2,  2.0)
        _aE(1.0,     1,  2,  1.0)
        _aE(-0.0001, 1,  2,  1.0)
        _aE(-1.0,    1,  2,  1.0)
        _aE(-10.0,   1,  2,  1.0)
        _aE(10.0,    1, 10, 10.0)
        _aE(1.0,     1, 10,  1.0)
        _aE(-0.0001, 1, 10,  1.0)
        _aE(-1.0,    1, 10,  1.0)
        _aE(-10.0,   1, 10,  1.0)
        _aE(10.0,    2,  2,  2.0)
        _aE(1.0,     2,  2,  2.0)
        _aE(-0.0001, 2,  2,  2.0)
        _aE(-1.0,    2,  2,  2.0)
        _aE(-10.0,   2,  2,  2.0)
        _aE(10.0,    2, 10, 10.0)
        _aE(1.0,     2, 10,  2.0)
        _aE(-0.0001, 2, 10,  2.0)
        _aE(-1.0,    2, 10,  2.0)
        _aE(-10.0,   2, 10,  2.0)
        _aE(1.01,   0.0, 1.0,  1.0)


class TestTypeTimeDate(TestCase):
    def test_coerces_expected_primitive(self):
        with self.assertRaises(types.AWTypeError):
            self.assertEqual(str, type(types.AW_TIMEDATE(None)))

    def test_null(self):
        self.assertEqual('INVALID DATE', types.AW_TIMEDATE.NULL)
        with self.assertRaises(types.AWTypeError):
            self.assertNotEqual(types.AW_TIMEDATE(None), 'NULL',
                                'BaseType default "null" must be overridden')

    def test_normalize(self):
        expected = datetime.strptime('2017-07-12T20:50:15',
                                     '%Y-%m-%dT%H:%M:%S')
        self.assertEqual(
            expected,
            types.AW_TIMEDATE.normalize('2017-07-12T20:50:15.641659')
        )

    def test_compare_normalized(self):
        with_usecs = types.AW_TIMEDATE.normalize('2017-07-12T20:50:15.641659')
        without_usecs = types.AW_TIMEDATE.normalize('2017-07-12T20:50:15')
        self.assertEqual(with_usecs, without_usecs)

        another_day = types.AW_TIMEDATE.normalize('2017-07-11T20:50:15')
        self.assertNotEqual(with_usecs, another_day)
        self.assertNotEqual(without_usecs, another_day)

    def test_call_with_none(self):
        with self.assertRaises(types.AWTypeError):
            self.assertEqual(types.AW_TIMEDATE.NULL, types.AW_TIMEDATE(None))

    def test_call_with_coercible_data(self):
        expected = datetime.strptime('2017-07-12T20:50:15', '%Y-%m-%dT%H:%M:%S')

        def _ok(test_input):
            actual = types.AW_TIMEDATE(test_input)
            self.assertEqual(expected, actual)

        _ok(expected)
        _ok('2017-07-12T20:50:15')
        _ok('2017-07-12T20-50-15')
        _ok('2017-07-12T20_50_15')
        _ok('2017-07-12T205015')
        _ok('2017-07-12_20:50:15')
        _ok('2017-07-12_20-50-15')
        _ok('2017-07-12_20_50_15')
        _ok('2017-07-12_205015')
        _ok('2017-07-12-20:50:15')
        _ok('2017-07-12-20-50-15')
        _ok('2017-07-12-20_50_15')
        _ok('2017-07-12-205015')

        # TODO: Handle things like 'Thu Aug 31 11:51:57 2017 +0200'
        # TODO: Add testing additional input data.

    def test_call_with_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_TIMEDATE(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises('foo')
        _assert_raises([])
        _assert_raises([''])
        _assert_raises([None])
        # TODO: Add testing additional input data.

    def test_format_coercible_data(self):
        def _assert_formats(test_data, expected):
            self.assertEqual(expected, types.AW_TIMEDATE.format(test_data))

        _assert_formats('2017:02:03 10:20:30', '2017-02-03T102030')
        _assert_formats('2017-02-03 10:20:30', '2017-02-03T102030')
        _assert_formats('2015:03:03 12:25:56-08:00', '2015-03-03T122556')

    def test_format_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_TIMEDATE.format(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises('foo')
        _assert_raises([])
        _assert_raises([''])
        _assert_raises([None])


class TestTypeDate(TestCase):
    def test_coerces_expected_primitive(self):
        with self.assertRaises(types.AWTypeError):
            self.assertEqual(datetime, type(types.AW_DATE(None)))

    def test_null(self):
        self.assertEqual('INVALID DATE', types.AW_DATE.NULL)

        with self.assertRaises(types.AWTypeError):
            self.assertNotEqual(types.AW_DATE(None), types.BaseNullValue,
                                'BaseType default "null" must be overridden')

    def test_normalize(self):
        def _assert_equal(test_data, expect):
            actual = types.AW_DATE.normalize(test_data)
            self.assertEqual(expect, actual)
            self.assertIsInstance(actual, datetime)

        expected = datetime.strptime('2017-07-12', '%Y-%m-%d')
        _assert_equal('2017-07-12', expected)
        _assert_equal('2017 07 12', expected)
        _assert_equal('2017_07_12', expected)
        _assert_equal('2017:07:12', expected)
        _assert_equal('20170712', expected)

    def test_call_with_none(self):
        with self.assertRaises(types.AWTypeError):
            types.AW_DATE(None)

    def test_call_with_coercible_data_year_month_day(self):
        expected = datetime.strptime('2017-07-12', '%Y-%m-%d')

        def _check(given):
            actual = types.AW_DATE(given)
            self.assertEqual(expected, actual)

        _check(expected)
        _check('2017-07-12')
        _check('2017:07:12')
        _check('2017_07_12')
        _check('2017 07 12')
        _check(b'2017-07-12')
        _check(b'2017:07:12')
        _check(b'2017_07_12')
        _check(b'2017 07 12')

    def test_call_with_coercible_data_year_month(self):
        expected = datetime.strptime('2017-07', '%Y-%m')

        def _check(given):
            actual = types.AW_DATE(given)
            self.assertEqual(expected, actual)

        _check(expected)
        _check('2017-07')
        _check('2017:07')
        _check('2017_07')
        _check(b'2017-07')
        _check(b'2017:07')
        _check(b'2017_07')

    def test_call_with_coercible_data_year(self):
        expected = datetime.strptime('2017', '%Y')

        def _check(given):
            actual = types.AW_DATE(given)
            self.assertEqual(expected, actual)

        _check(expected)
        _check('2017')
        _check(b'2017')
        _check(2017)

    def test_call_with_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_DATE(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises('foo')
        _assert_raises([])
        _assert_raises([''])
        _assert_raises([None])
        # TODO: Add testing additional input data.

    def test_format_coercible_data(self):
        def _assert_formats(test_data, expected):
            self.assertEqual(types.AW_DATE.format(test_data),
                             expected)

        _assert_formats('2017:02:03', '2017-02-03')
        _assert_formats('2017-02-03', '2017-02-03')
        _assert_formats('2015:03:03', '2015-03-03')

    def test_format_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_DATE.format(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises('foo')
        _assert_raises([])
        _assert_raises([''])
        _assert_raises([None])
        _assert_raises('0000:00:00')
        _assert_raises('1234:56:78')


class TestTypeExiftoolTimeDate(TestCase):
    def test_coerces_expected_primitive(self):
        with self.assertRaises(types.AWTypeError):
            self.assertEqual(type(types.AW_EXIFTOOLTIMEDATE(None)), str)

    def test_null(self):
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE.NULL, 'INVALID DATE')

        with self.assertRaises(types.AWTypeError):
            self.assertNotEqual(
                types.AW_EXIFTOOLTIMEDATE(None), types.BaseNullValue,
                'BaseType default "null" must be overridden'
            )

    def test_call_with_none(self):
        with self.assertRaises(types.AWTypeError):
            self.assertEqual(types.AW_EXIFTOOLTIMEDATE(None),
                             types.AW_EXIFTOOLTIMEDATE.null)

    def test_call_with_coercible_data(self):
        expected = datetime.strptime('2017-07-12T20:50:15+0200',
                                     '%Y-%m-%dT%H:%M:%S%z')
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE(expected), expected)
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE('2017-07-12 20:50:15+0200'),
                         expected)

    def test_call_with_coercible_data_messy_timezone(self):
        expected = datetime.strptime('2008-09-12T04:40:52-0400',
                                     '%Y-%m-%dT%H:%M:%S%z')
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE('2008:09:12 04:40:52-04:00'),
                         expected)

    def test_call_with_coercible_data_negative_timezone(self):
        expected = datetime.strptime('2015-03-03T12:25:56-0800',
                                     '%Y-%m-%dT%H:%M:%S%z')
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE('2015:03:03 12:25:56-08:00'),
                         expected)

    def test_call_with_malformed_date_trailing_z(self):
        actual = types.AW_EXIFTOOLTIMEDATE('2017:07:12 20:50:15Z')
        expected = uu.str_to_datetime('2017-07-12 205015')
        self.assertEqual(actual, expected)

    def test_call_with_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_EXIFTOOLTIMEDATE(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises('foo')
        _assert_raises([])
        _assert_raises([''])
        _assert_raises([None])
        _assert_raises('0000:00:00 00:00:00')
        _assert_raises('0000:00:00 00:00:00Z')
        _assert_raises('1234:56:78 90:00:00')
        _assert_raises([1918, '2009:08:20'])
        _assert_raises(['1918', '2009:08:20'])

    def test_call_with_valid_exiftool_string_returns_expected_type(self):
        actual = types.AW_EXIFTOOLTIMEDATE('2017-07-12 20:50:15+0200')
        self.assertIsInstance(actual, datetime)

    def test_format_coercible_data(self):
        def _assert_formats(test_data, expected):
            self.assertEqual(types.AW_EXIFTOOLTIMEDATE.format(test_data),
                             expected)

        _assert_formats('2017:02:03 10:20:30', '2017-02-03T102030')
        _assert_formats('2017-02-03 10:20:30', '2017-02-03T102030')
        _assert_formats('2015:03:03 12:25:56-08:00', '2015-03-03T122556')

    def test_format_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_EXIFTOOLTIMEDATE.format(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises('foo')
        _assert_raises([])
        _assert_raises([''])
        _assert_raises([None])
        _assert_raises('0000:00:00 00:00:00')
        _assert_raises('0000:00:00 00:00:00Z')
        _assert_raises('1234:56:78 90:00:00')


class TestTypePath(TestCase):
    def test_coerces_expected_primitive(self):
        with self.assertRaises(types.AWTypeError):
            self.assertEqual(type(types.AW_PATH(None)), None)

    def test_null(self):
        with self.assertRaises(types.AWTypeError):
            self.assertEqual(types.AW_PATH(None), 'INVALID PATH')

        with self.assertRaises(types.AWTypeError):
            self.assertEqual(types.AW_PATH(None), types.AW_PATH.NULL)

        with self.assertRaises(types.AWTypeError):
            self.assertNotEqual(types.AW_PATH(None), types.BaseNullValue,
                                'BaseType default "null" must be overridden')

    def test_normalize_expands_tilde_to_user_home(self):
        self.assertEqual(uu.encode(USER_HOME), types.AW_PATH.normalize('~'))
        self.assertEqual(uu.encode(USER_HOME), types.AW_PATH.normalize('~/'))

        expected = os.path.normpath(os.path.join(USER_HOME, 'foo'))
        self.assertEqual(uu.encode(expected), types.AW_PATH.normalize('~/foo'))

    def test_normalize_collapses_repeating_path_separators(self):
        def _assert_normalizes(given, expect):
            actual = types.AW_PATH.normalize(given)
            self.assertEqual(expect, actual)

        _assert_normalizes(given='/home/foo', expect=b'/home/foo')
        _assert_normalizes(given='/home//foo', expect=b'/home/foo')
        _assert_normalizes(given='///home/foo', expect=b'/home/foo')
        _assert_normalizes(given='////home/foo', expect=b'/home/foo')
        _assert_normalizes(given='////home//foo', expect=b'/home/foo')
        _assert_normalizes(given='////home////foo', expect=b'/home/foo')

        _assert_normalizes(given='//home//foo', expect=b'//home/foo')

    def test_normalize_relative_path(self):
        _this_dir = os.path.curdir
        expect = uu.normpath(os.path.join(_this_dir, 'home/foo'))
        self.assertEqual(expect, types.AW_PATH.normalize('home/foo'))
        self.assertEqual(expect, types.AW_PATH.normalize('home//foo'))
        self.assertEqual(expect, types.AW_PATH.normalize('home///foo'))

    def test_normalize_invalid_value(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                _ = types.AW_PATH.normalize(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises(b'')

    def test_call_with_coercible_data(self):
        def _assert_returns(test_data, expected):
            self.assertEqual(types.AW_PATH(test_data), expected)

        _assert_returns('/tmp', b'/tmp')
        _assert_returns('/tmp/foo', b'/tmp/foo')
        _assert_returns('/tmp/foo.bar', b'/tmp/foo.bar')
        _assert_returns('~', b'~')
        _assert_returns('~/foo', b'~/foo')
        _assert_returns('~/foo.bar', b'~/foo.bar')
        _assert_returns(b'/tmp', b'/tmp')
        _assert_returns(b'/tmp/foo', b'/tmp/foo')
        _assert_returns(b'/tmp/foo.bar', b'/tmp/foo.bar')
        _assert_returns(b'~', b'~')
        _assert_returns(b'~/foo', b'~/foo')
        _assert_returns(b'~/foo.bar', b'~/foo.bar')

    def test_call_with_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_PATH(test_data)

        _assert_raises(datetime.now())
        _assert_raises(0)
        _assert_raises(None)
        _assert_raises('')

    def test_format(self):
        def _assert_formats(test_data, expected):
            self.assertEqual(types.AW_PATH.format(test_data), expected)

        _assert_formats(b'/tmp', '/tmp')
        _assert_formats(b'/tmp/foo', '/tmp/foo')
        _assert_formats(b'/tmp/foo.bar', '/tmp/foo.bar')
        _assert_formats(b'~', USER_HOME)
        _assert_formats(b'~/foo', os.path.join(USER_HOME, 'foo'))
        _assert_formats(b'~/foo.bar', os.path.join(USER_HOME, 'foo.bar'))


class TestTypePathComponent(TestCase):
    def test_coerces_expected_primitive(self):
        self.assertEqual(type(types.AW_PATHCOMPONENT(None)), bytes)

    def test_null(self):
        self.assertEqual(types.AW_PATHCOMPONENT(None), b'')
        self.assertEqual(types.AW_PATHCOMPONENT(None),
                         types.AW_PATHCOMPONENT.NULL)

        self.assertNotEqual(types.AW_PATHCOMPONENT(None), types.BaseNullValue,
                            'BaseType default "null" must be overridden')

    def test_normalize_path_with_user_home(self):
        expected = uu.encode(USER_HOME)
        self.assertEqual(expected, types.AW_PATHCOMPONENT.normalize('~'))
        self.assertEqual(expected, types.AW_PATHCOMPONENT.normalize('~/'))

        expected = uu.encode(os.path.normpath(os.path.join(USER_HOME, 'foo')))
        self.assertEqual(expected, types.AW_PATHCOMPONENT.normalize('~/foo'))

    def test_normalize_path_components(self):
        def _assert_normalizes(test_data, expected):
            self.assertEqual(expected,
                             types.AW_PATHCOMPONENT.normalize(test_data))

        _assert_normalizes('/', b'/')
        _assert_normalizes('/foo', b'/foo')
        _assert_normalizes('/foo/', b'/foo')
        _assert_normalizes('foo/', b'foo')
        _assert_normalizes('foo', b'foo')
        _assert_normalizes('a.pdf', b'a.pdf')

    def test_normalize_invalid_value(self):
        with self.assertRaises(types.AWTypeError):
            types.AW_PATHCOMPONENT.normalize('')

    def test_call_with_coercible_data(self):
        def _assert_returns(test_data, expected):
            self.assertEqual(expected, types.AW_PATHCOMPONENT(test_data))

        _assert_returns('', b'')
        _assert_returns(None, b'')
        _assert_returns('/tmp', b'/tmp')
        _assert_returns('/tmp/foo', b'/tmp/foo')
        _assert_returns('/tmp/f.e', b'/tmp/f.e')
        _assert_returns(b'/tmp', b'/tmp')
        _assert_returns(b'/tmp/foo', b'/tmp/foo')
        _assert_returns(b'/tmp/f.e', b'/tmp/f.e')

    def test_call_with_coercible_data_including_user_home(self):
        def _assert_returns(test_data, expected):
            self.assertEqual(expected, types.AW_PATHCOMPONENT(test_data))

        _assert_returns(b'~', b'~')
        _assert_returns(b'~/foo', b'~/foo')
        _assert_returns(b'~/foo.bar', b'~/foo.bar')
        _assert_returns('~', b'~')
        _assert_returns('~/foo', b'~/foo')
        _assert_returns('~/foo.bar', b'~/foo.bar')

    def test_call_with_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_PATHCOMPONENT(test_data)

        _assert_raises(0)
        _assert_raises(datetime.now())

    def test_format(self):
        def _assert_formats(test_data, expected):
            actual = types.AW_PATHCOMPONENT.format(test_data)
            self.assertEqual(expected, actual)

        _assert_formats('', '')
        _assert_formats(None, '')
        _assert_formats(b'/tmp', '/tmp')
        _assert_formats(b'/tmp/foo', '/tmp/foo')
        _assert_formats(b'/tmp/foo.bar', '/tmp/foo.bar')
        _assert_formats('/tmp', '/tmp')
        _assert_formats('/tmp/foo', '/tmp/foo')
        _assert_formats('/tmp/foo.bar', '/tmp/foo.bar')
        _assert_formats(b'~', '~')
        _assert_formats(b'~/foo', '~/foo')
        _assert_formats(b'~/foo.bar', '~/foo.bar')
        _assert_formats('~', '~')
        _assert_formats('~/foo', '~/foo')
        _assert_formats('~/foo.bar', '~/foo.bar')


class TestTypeString(TestCase):
    def test_coerces_expected_primitive(self):
        self.assertEqual(str, type(types.AW_STRING(None)))

    def test_null(self):
        self.assertEqual('', types.AW_STRING.NULL)

        self.assertNotEqual(types.AW_STRING(None), types.BaseNullValue,
                            'BaseType default "null" must be overridden')

    def test_normalize(self):
        def _assert_normalizes(test_data, expected):
            self.assertEqual(expected, types.AW_STRING.normalize(test_data))

        _assert_normalizes(None, '')
        _assert_normalizes('', '')
        _assert_normalizes(' ', '')
        _assert_normalizes('  ', '')
        _assert_normalizes(b'', '')
        _assert_normalizes(b' ', '')
        _assert_normalizes(b'  ', '')
        _assert_normalizes(-1, '-1')
        _assert_normalizes(0, '0')
        _assert_normalizes(1, '1')
        _assert_normalizes(-1.5, '-1.5')
        _assert_normalizes(-1.0, '-1.0')
        _assert_normalizes(1.0, '1.0')
        _assert_normalizes(1.5, '1.5')
        _assert_normalizes('foo', 'foo')
        _assert_normalizes('foo ', 'foo')
        _assert_normalizes(' foo', 'foo')
        _assert_normalizes(' foo ', 'foo')
        _assert_normalizes('f foo ', 'f foo')
        _assert_normalizes(b'foo', 'foo')
        _assert_normalizes(b'foo ', 'foo')
        _assert_normalizes(b' foo', 'foo')
        _assert_normalizes(b' foo ', 'foo')
        _assert_normalizes(b'f foo ', 'f foo')
        _assert_normalizes(None, '')
        _assert_normalizes(False, 'False')
        _assert_normalizes(True, 'True')

    def test_call_with_none(self):
        self.assertEqual(types.AW_STRING.NULL, types.AW_STRING(None))

    def test_call_with_coercible_data(self):
        def _assert_returns(test_data, expected):
            self.assertEqual(expected, types.AW_STRING(test_data))

        _assert_returns('', '')
        _assert_returns(' ', ' ')
        _assert_returns(b'', '')
        _assert_returns(b' ', ' ')
        _assert_returns(-1, '-1')
        _assert_returns(0, '0')
        _assert_returns(1, '1')
        _assert_returns(-1.5, '-1.5')
        _assert_returns(-1.0, '-1.0')
        _assert_returns(1.0, '1.0')
        _assert_returns(1.5, '1.5')
        _assert_returns('-1', '-1')
        _assert_returns('-1.0', '-1.0')
        _assert_returns('0', '0')
        _assert_returns('1', '1')
        _assert_returns('foo', 'foo')
        _assert_returns(None, '')
        _assert_returns(False, 'False')
        _assert_returns(True, 'True')

    def test_call_with_noncoercible_data(self):
        with self.assertRaises(types.AWTypeError):
            types.AW_STRING(datetime.now())

    def test_format(self):
        def _assert_formats(test_data, expected):
            self.assertEqual(expected, types.AW_STRING.format(test_data))

        _assert_formats('', '')
        _assert_formats(' ', ' ')
        _assert_formats(b'', '')
        _assert_formats(b' ', ' ')
        _assert_formats(-1, '-1')
        _assert_formats(0, '0')
        _assert_formats(1, '1')
        _assert_formats(-1.5, '-1.5')
        _assert_formats(-1.0, '-1.0')
        _assert_formats(1.0, '1.0')
        _assert_formats(1.5, '1.5')
        _assert_formats('-1', '-1')
        _assert_formats('-1.0', '-1.0')
        _assert_formats('0', '0')
        _assert_formats('1', '1')
        _assert_formats('foo', 'foo')
        _assert_formats(None, '')
        _assert_formats(False, 'False')
        _assert_formats(True, 'True')


class TestTypeMimeType(TestCase):
    def test_null(self):
        self.assertEqual(types.AW_MIMETYPE.NULL, types.NullMIMEType())
        self.assertNotEqual(types.BaseNullValue, types.AW_MIMETYPE(None),
                            'BaseType default "null" must be overridden')

        self.assertFalse(types.AW_MIMETYPE.NULL)
        self.assertFalse(types.AW_MIMETYPE.null())

    def test_normalize(self):
        def _assert_normalizes(test_data, expected):
            self.assertEqual(expected, types.AW_MIMETYPE.normalize(test_data))

        _assert_normalizes('asm', 'text/x-asm')
        _assert_normalizes('gz', 'application/gzip')
        _assert_normalizes('pdf', 'application/pdf')
        _assert_normalizes('.pdf', 'application/pdf')
        _assert_normalizes('PDF', 'application/pdf')
        _assert_normalizes('.PDF', 'application/pdf')
        _assert_normalizes('application/pdf', 'application/pdf')
        _assert_normalizes('APPLICATION/pdf', 'application/pdf')
        _assert_normalizes('application/PDF', 'application/pdf')
        _assert_normalizes('APPLICATION/PDF', 'application/pdf')
        _assert_normalizes(b'pdf', 'application/pdf')
        _assert_normalizes(b'.pdf', 'application/pdf')
        _assert_normalizes(b'PDF', 'application/pdf')
        _assert_normalizes(b'.PDF', 'application/pdf')
        _assert_normalizes(b'application/pdf', 'application/pdf')
        _assert_normalizes(b'APPLICATION/pdf', 'application/pdf')
        _assert_normalizes(b'application/PDF', 'application/pdf')
        _assert_normalizes(b'APPLICATION/PDF', 'application/pdf')
        _assert_normalizes('epub', 'application/epub+zip')
        _assert_normalizes('.epub', 'application/epub+zip')
        _assert_normalizes('EPUB', 'application/epub+zip')
        _assert_normalizes('.EPUB', 'application/epub+zip')
        _assert_normalizes('application/epub+zip', 'application/epub+zip')
        _assert_normalizes('APPLICATION/epub+zip', 'application/epub+zip')
        _assert_normalizes('application/EPUB+ZIP', 'application/epub+zip')
        _assert_normalizes('APPLICATION/EPUB+ZIP', 'application/epub+zip')
        _assert_normalizes(b'epub', 'application/epub+zip')
        _assert_normalizes(b'.epub', 'application/epub+zip')
        _assert_normalizes(b'EPUB', 'application/epub+zip')
        _assert_normalizes(b'.EPUB', 'application/epub+zip')
        _assert_normalizes(b'application/epub+zip', 'application/epub+zip')
        _assert_normalizes(b'APPLICATION/epub+zip', 'application/epub+zip')
        _assert_normalizes(b'application/EPUB+ZIP', 'application/epub+zip')
        _assert_normalizes(b'APPLICATION/EPUB+ZIP', 'application/epub+zip')

    def test_call_with_none(self):
        self.assertEqual(types.AW_MIMETYPE(None), types.AW_MIMETYPE.NULL)

    def test_call_with_coercible_data(self):
        def _assert_coerces(test_data, expected):
            self.assertEqual(expected, types.AW_MIMETYPE(test_data))

        _assert_coerces('pdf', 'application/pdf')
        _assert_coerces('.pdf', 'application/pdf')
        _assert_coerces('PDF', 'application/pdf')
        _assert_coerces('.PDF', 'application/pdf')
        _assert_coerces('application/pdf', 'application/pdf')
        _assert_coerces('APPLICATION/pdf', 'application/pdf')
        _assert_coerces('application/PDF', 'application/pdf')
        _assert_coerces('APPLICATION/PDF', 'application/pdf')
        _assert_coerces(b'pdf', 'application/pdf')
        _assert_coerces(b'.pdf', 'application/pdf')
        _assert_coerces(b'PDF', 'application/pdf')
        _assert_coerces(b'.PDF', 'application/pdf')
        _assert_coerces(b'application/pdf', 'application/pdf')
        _assert_coerces(b'APPLICATION/pdf', 'application/pdf')
        _assert_coerces(b'application/PDF', 'application/pdf')
        _assert_coerces(b'APPLICATION/PDF', 'application/pdf')
        _assert_coerces('jpg', 'image/jpeg')
        _assert_coerces('.jpg', 'image/jpeg')
        _assert_coerces('JPG', 'image/jpeg')
        _assert_coerces('.JPG', 'image/jpeg')
        _assert_coerces('.JPEG', 'image/jpeg')
        _assert_coerces('image/jpeg', 'image/jpeg')
        _assert_coerces(b'jpg', 'image/jpeg')
        _assert_coerces(b'.jpg', 'image/jpeg')
        _assert_coerces(b'JPG', 'image/jpeg')
        _assert_coerces(b'.JPG', 'image/jpeg')
        _assert_coerces(b'image/jpeg', 'image/jpeg')
        _assert_coerces('application/epub+zip', 'application/epub+zip')
        _assert_coerces('application/x-lzma', 'application/x-lzma')
        _assert_coerces('application/gzip', 'application/gzip')
        _assert_coerces('asm', 'text/x-asm')
        _assert_coerces('gz', 'application/gzip')
        _assert_coerces('lzma', 'application/x-lzma')
        _assert_coerces('mov', 'video/quicktime')
        _assert_coerces('mp4', 'video/mp4')
        _assert_coerces('rar', 'application/rar')
        _assert_coerces('rtf', 'text/rtf')
        _assert_coerces('sh', 'text/x-shellscript')
        _assert_coerces('tar.gz', 'application/gzip')
        _assert_coerces('tar.lzma', 'application/x-lzma')
        _assert_coerces('txt', 'text/plain')
        _assert_coerces('inode/x-empty', 'inode/x-empty')

    def test_call_with_noncoercible_data(self):
        def _assert_uncoercible(test_data):
            self.assertEqual(types.AW_MIMETYPE.NULL,
                             types.AW_MIMETYPE(test_data))

        _assert_uncoercible(None)
        _assert_uncoercible(False)
        _assert_uncoercible(True)
        _assert_uncoercible('')
        _assert_uncoercible(' ')
        _assert_uncoercible('foo')
        _assert_uncoercible(-1)
        _assert_uncoercible(1)
        _assert_uncoercible('application/foo+bar')
        _assert_uncoercible('foo/epub+zip')

    def test_format(self):
        def _assert_formats(test_data, expected):
            self.assertEqual(expected, types.AW_MIMETYPE.format(test_data))

        _unknown = types.NULL_AW_MIMETYPE.AS_STRING

        _assert_formats(None, _unknown)
        _assert_formats('', _unknown)
        _assert_formats('this is not a MIME-type', _unknown)
        _assert_formats(1, _unknown)
        _assert_formats(False, _unknown)
        _assert_formats(True, _unknown)
        _assert_formats([], _unknown)
        _assert_formats({}, _unknown)
        _assert_formats('JPG', 'jpg')
        _assert_formats('image/jpeg', 'jpg')
        _assert_formats('pdf', 'pdf')
        _assert_formats('.pdf', 'pdf')
        _assert_formats('PDF', 'pdf')
        _assert_formats('.PDF', 'pdf')
        _assert_formats('application/pdf', 'pdf')
        _assert_formats('APPLICATION/pdf', 'pdf')
        _assert_formats('application/PDF', 'pdf')
        _assert_formats('APPLICATION/PDF', 'pdf')
        _assert_formats(b'pdf', 'pdf')
        _assert_formats(b'.pdf', 'pdf')
        _assert_formats(b'PDF', 'pdf')
        _assert_formats(b'.PDF', 'pdf')
        _assert_formats(b'application/pdf', 'pdf')
        _assert_formats(b'APPLICATION/pdf', 'pdf')
        _assert_formats(b'application/PDF', 'pdf')
        _assert_formats(b'APPLICATION/PDF', 'pdf')
        _assert_formats('jpg', 'jpg')
        _assert_formats('.jpg', 'jpg')
        _assert_formats('JPG', 'jpg')
        _assert_formats('.JPG', 'jpg')
        _assert_formats('.JPEG', 'jpg')
        _assert_formats('image/jpeg', 'jpg')
        _assert_formats(b'jpg', 'jpg')
        _assert_formats(b'.jpg', 'jpg')
        _assert_formats(b'JPG', 'jpg')
        _assert_formats(b'.JPG', 'jpg')
        _assert_formats(b'image/jpeg', 'jpg')
        _assert_formats('epub', 'epub')
        _assert_formats('.epub', 'epub')
        _assert_formats('EPUB', 'epub')
        _assert_formats('.EPUB', 'epub')
        _assert_formats('application/epub+zip', 'epub')
        _assert_formats(b'epub', 'epub')
        _assert_formats(b'.epub', 'epub')
        _assert_formats(b'EPUB', 'epub')
        _assert_formats(b'.EPUB', 'epub')
        _assert_formats(b'application/epub+zip', 'epub')
        _assert_formats('text/plain', 'txt')
        _assert_formats('inode/x-empty', '')

    def test_boolean_evaluation(self):
        actual = types.AW_MIMETYPE('this is an unknown MIME-type ..')
        self.assertFalse(actual)


class TestTryCoerce(TestCase):
    def _test(self, given, expect, type_):
        actual = types.try_coerce(given)
        self.assertEqual(expect, actual)

        if isinstance(actual, list):
            for a in actual:
                self.assertIsInstance(a, type_)
        else:
            self.assertIsInstance(actual, type_)

    def test_try_coerce_none(self):
        self.assertIsNone(types.try_coerce(None))

    def test_try_coerce_primitive_bool(self):
        self._test(given=False, expect=False, type_=bool)
        self._test(given=True, expect=True, type_=bool)

    def test_try_coerce_primitive_int(self):
        self._test(given=1, expect=1, type_=int)
        self._test(given=0, expect=0, type_=int)

    def test_try_coerce_primitive_float(self):
        self._test(given=1.0, expect=1.0, type_=float)
        self._test(given=0.0, expect=0.0, type_=float)

    def test_try_coerce_primitive_str(self):
        self._test(given='foo', expect='foo', type_=str)
        self._test(given='', expect='', type_=str)

    def test_try_coerce_primitive_bytes(self):
        self._test(given=b'foo', expect='foo', type_=str)
        self._test(given=b'', expect='', type_=str)

    def test_try_coerce_datetime(self):
        dt = datetime.now()
        self._test(given=dt, expect=dt, type_=datetime)

    def test_try_coerce_list_primitive_bool(self):
        self._test(given=[False], expect=[False], type_=bool)
        self._test(given=[True, False], expect=[True, False], type_=bool)

    def test_try_coerce_list_mixed_primitives_to_bool(self):
        self._test(given=[True, 'False'], expect=[True, False], type_=bool)
        self._test(given=[True, 1.5, b'c'], expect=[True, True, False],
                   type_=bool)
        self._test(given=[True, 'False', b'True', 'true'],
                   expect=[True, False, True, True], type_=bool)

    def test_try_coerce_list_primitive_str(self):
        self._test(given=['foo'], expect=['foo'], type_=str)
        self._test(given=['foo', 'bar'], expect=['foo', 'bar'], type_=str)

    def test_try_coerce_list_mixed_primitives_to_str(self):
        self._test(given=['foo', 1], expect=['foo', '1'], type_=str)
        self._test(given=['a', 1.5, b'c'], expect=['a', '1.5', 'c'], type_=str)

    def test_try_coerce_list_primitive_int(self):
        self._test(given=[1], expect=[1], type_=int)
        self._test(given=[1, 2], expect=[1, 2], type_=int)

    def test_try_coerce_list_mixed_primitives_to_int(self):
        self._test(given=[1, 2.5], expect=[1, 2], type_=int)
        self._test(given=[1, 2.5, b'3'], expect=[1, 2, 3], type_=int)
        self._test(given=[1, '2', b'3'], expect=[1, 2, 3], type_=int)

    def test_try_coerce_list_primitive_float(self):
        self._test(given=[1.0], expect=[1.0], type_=float)
        self._test(given=[1.0, 2.0], expect=[1.0, 2.0], type_=float)

    def test_try_coerce_list_mixed_primitives_to_float(self):
        self._test(given=[1.0, 2], expect=[1.0, 2.0], type_=float)
        self._test(given=[1.0, 2.5, b'3'], expect=[1.0, 2.5, 3.0], type_=float)
        self._test(given=[1.0, '2', b'3'], expect=[1.0, 2.0, 3.0], type_=float)


class TestCoercerFor(TestCase):
    def _check(self, test_input, expected):
        assert isinstance(expected, types.BaseType)
        actual = types.coercer_for(test_input)
        self.assertEqual(expected, actual)

    def test_none(self):
        actual = types.coercer_for(None)
        self.assertIsNone(actual)

    def test_empty_empty(self):
        actual = types.coercer_for([])
        self.assertIsNone(actual)

    def test_bytes(self):
        self._check(b'foo', types.AW_STRING)
        self._check(b'', types.AW_STRING)
        self._check([b''], types.AW_STRING)
        self._check([b'', 1], types.AW_STRING)
        self._check((b'', ), types.AW_STRING)
        self._check((b'', 1), types.AW_STRING)
        self._check({b'a': b''}, types.AW_STRING)
        self._check({b'a': b'1', b'b': b'2'}, types.AW_STRING)

    def test_string(self):
        self._check('foo', types.AW_STRING)
        self._check('', types.AW_STRING)
        self._check([''], types.AW_STRING)
        self._check(['', 1], types.AW_STRING)
        self._check(('', ), types.AW_STRING)
        self._check(('', 1), types.AW_STRING)
        self._check({'a': ''}, types.AW_STRING)
        self._check({'a': '1', 'b': '2'}, types.AW_STRING)

    def test_integer(self):
        self._check(1, types.AW_INTEGER)
        self._check(-1, types.AW_INTEGER)
        self._check([1], types.AW_INTEGER)
        self._check([1, 'foo'], types.AW_INTEGER)
        self._check((1, ), types.AW_INTEGER)
        self._check((1, 'foo'), types.AW_INTEGER)
        self._check({'a': 1}, types.AW_INTEGER)
        self._check({'a': 1, 'b': 2}, types.AW_INTEGER)

    def test_boolean(self):
        self._check(False, types.AW_BOOLEAN)
        self._check(True, types.AW_BOOLEAN)
        self._check([True], types.AW_BOOLEAN)
        self._check([True, 'foo'], types.AW_BOOLEAN)
        self._check((True, ), types.AW_BOOLEAN)
        self._check((True, 'foo'), types.AW_BOOLEAN)
        self._check({'a': True}, types.AW_BOOLEAN)
        self._check({'a': True, 'b': False}, types.AW_BOOLEAN)

    def test_float(self):
        self._check(1.0, types.AW_FLOAT)
        self._check(-1.0, types.AW_FLOAT)
        self._check([-1.0], types.AW_FLOAT)
        self._check([-1.0, 'foo'], types.AW_FLOAT)
        self._check((-1.0, ), types.AW_FLOAT)
        self._check((-1.0, 'foo'), types.AW_FLOAT)
        self._check({'a': -1.0}, types.AW_FLOAT)
        self._check({'a': -1.0, 'b': 2.0}, types.AW_FLOAT)


class TestForceString(TestCase):
    def test_returns_strings(self):
        def _aS(test_input):
            actual = types.force_string(test_input)
            self.assertIsInstance(actual, str)

        _aS(1)
        _aS(1.0)
        _aS('')
        _aS(' ')
        _aS(b'')
        _aS(b' ')
        _aS('foo')
        _aS(b'foo')
        _aS([])
        _aS([''])
        _aS(['foo'])
        _aS({})
        _aS(None)

    def test_returns_expected_value(self):
        def _aE(test_input, expected):
            actual = types.force_string(test_input)
            self.assertEqual(expected, actual)

        _aE(1, '1')
        _aE(1.0, '1.0')
        _aE('', '')
        _aE(' ', ' ')
        _aE(b'', '')
        _aE(b' ', ' ')
        _aE('foo', 'foo')
        _aE(b'foo', 'foo')
        _aE([], '')
        _aE([''], '')
        _aE(['foo'], 'foo')
        _aE({}, '')
        _aE(None, '')


class TestForceStringList(TestCase):
    GIVEN_EXPECT = [
        (1, ['1']),
        (1.0, ['1.0']),
        ('', ['']),
        (b'', ['']),
        ('foo', ['foo']),
        (b'foo', ['foo']),
        ([], ['']),
        ({}, ['']),
        (None, ['']),
        ([1], ['1']),
        ([1.0], ['1.0']),
        ([''], ['']),
        ([b''], ['']),
        (['foo'], ['foo']),
        ([b'foo'], ['foo']),
        ([[]], ['']),
        ([{}], ['']),
        ([None], ['']),
        ([None, ''], ['', '']),
        ([None, 'foo'], ['', 'foo']),
        ([None, None], ['', '']),
        ([None, None, 'foo'], ['', '', 'foo'])
    ]

    def test_returns_list_of_strings(self):
        for given, _ in self.GIVEN_EXPECT:
            with self.subTest(given):
                actual = types.force_stringlist(given)
                self.assertIsInstance(actual, list)
                for a in actual:
                    self.assertIsInstance(a, str)

    def test_returns_expected_values(self):
        for given, expect in self.GIVEN_EXPECT:
            with self.subTest(given):
                actual = types.force_stringlist(given)
                self.assertEqual(expect, actual)


class TestTryParseDate(TestCase):
    def test_parses_valid_date(self):
        expected = datetime.strptime('2017-09-14', '%Y-%m-%d')

        def _assert_match(test_data):
            actual = types.try_parse_date(test_data)
            self.assertEqual(expected, actual)
            self.assertIsInstance(actual, datetime)

        _assert_match('2017 09 14')
        _assert_match('2017-09-14')
        _assert_match('2017:09:14')
        _assert_match('20170914')
        _assert_match('2017-0914')
        _assert_match('201709-14')
        _assert_match('2017-09-14')
        _assert_match('2017:0914')
        _assert_match('201709:14')
        _assert_match('2017:09:14')
        _assert_match('2017_0914')
        _assert_match('201709_14')
        _assert_match('2017_09_14')
        _assert_match('2017 0914')
        _assert_match('201709 14')
        _assert_match('2017 09 14')

    def test_invalid_dates_raises_valueerror(self):
        def _assert_raises(test_data):
            with self.assertRaises(ValueError):
                types.try_parse_date(test_data)

        _assert_raises(None)
        _assert_raises([])
        _assert_raises({})
        _assert_raises(1)
        _assert_raises(1.0)
        _assert_raises('')
        _assert_raises(' ')
        _assert_raises('foo')
        _assert_raises('1')
        _assert_raises(b'')
        _assert_raises(b' ')
        _assert_raises(b'foo')
        _assert_raises(b'1')


class TestTryParseDateTime(TestCase):
    def _assert_equal(self, test_data, expected):
        actual = types.try_parse_datetime(test_data)
        self.assertEqual(expected, actual)
        self.assertIsInstance(actual, datetime)

    def test_parses_valid_datetime(self):
        expected = uu.str_to_datetime('2017-07-12 205015')
        self._assert_equal('2017-07-12T20:50:15', expected)
        self._assert_equal('2017-07-12 20:50:15', expected)
        self._assert_equal('2017:07:12 20:50:15', expected)
        self._assert_equal('2017_07_12 20:50:15', expected)
        self._assert_equal('2017_07_12 20-50-15', expected)

    def test_parses_valid_datetime_with_microseconds(self):
        expected = datetime.strptime('2017-07-12T20:50:15.641659',
                                     '%Y-%m-%dT%H:%M:%S.%f')
        self._assert_equal('2017-07-12T20:50:15.641659', expected)
        self._assert_equal('2017-07-12_20:50:15.641659', expected)
        self._assert_equal('2017-07-12_205015 641659', expected)
        self._assert_equal('2017-07-12 205015 641659', expected)

    def test_parses_valid_datetime_with_timezone(self):
        expected = datetime.strptime('2017-07-12T20:50:15+0200',
                                     '%Y-%m-%dT%H:%M:%S%z')

        self._assert_equal('2017 07 12 20 50 15+0200', expected)
        self._assert_equal('2017-07-12 20:50:15+0200', expected)
        self._assert_equal('2017:07:12 20:50:15+0200', expected)
        self._assert_equal('2017-07-12T20:50:15+0200', expected)


class TestRegexLooseDate(TestCase):
    def test_matches_yyyy_mm_dd(self):
        def _assert_matches(test_data):
            actual = types.RE_LOOSE_DATE.match(test_data)
            self.assertIsNotNone(actual)
            self.assertEqual('2017', actual.group(1))
            self.assertEqual('09', actual.group(2))
            self.assertEqual('14', actual.group(3))

        _assert_matches('20170914')
        _assert_matches('2017-0914')
        _assert_matches('201709-14')
        _assert_matches('2017-09-14')
        _assert_matches('2017:0914')
        _assert_matches('201709:14')
        _assert_matches('2017:09:14')
        _assert_matches('2017_0914')
        _assert_matches('201709_14')
        _assert_matches('2017_09_14')
        _assert_matches('2017 0914')
        _assert_matches('201709 14')
        _assert_matches('2017 09 14')

    def test_does_not_match_non_yyyy_mm_dd(self):
        def _assert_no_match(test_data):
            actual = types.RE_LOOSE_DATE.match(test_data)
            self.assertIsNone(actual)

        _assert_no_match('')
        _assert_no_match(' ')
        _assert_no_match('foo')
        _assert_no_match('2017')
        _assert_no_match('201709')
        _assert_no_match('2017091')

        for test_string in ['20170914', '2017-09-14', '2017:09:14']:
            for n in range(1, len(test_string)):
                # Successively strip the right-most characters.
                _partial = test_string[:-n]
                _assert_no_match(_partial)


class TestRegexLooseTime(TestCase):
    def test_matches_hh_mm_ss(self):
        def _assert_matches(test_data):
            actual = types.RE_LOOSE_TIME.match(test_data)
            self.assertIsNotNone(actual)
            self.assertEqual('16', actual.group(1))
            self.assertEqual('33', actual.group(2))
            self.assertEqual('59', actual.group(3))

        _assert_matches('163359')
        _assert_matches('16-3359')
        _assert_matches('1633-59')
        _assert_matches('16-33-59')
        _assert_matches('16:3359')
        _assert_matches('1633:59')
        _assert_matches('16:33:59')
        _assert_matches('16_3359')
        _assert_matches('1633_59')
        _assert_matches('16_33_59')
        _assert_matches('16 3359')
        _assert_matches('1633 59')
        _assert_matches('16 33 59')

    def test_does_not_match_non_hh_mm_ss(self):
        def _assert_no_match(test_data):
            actual = types.RE_LOOSE_DATE.match(test_data)
            self.assertIsNone(actual)

        _assert_no_match('')
        _assert_no_match(' ')
        _assert_no_match('foo')
        _assert_no_match('16')
        _assert_no_match('1633')
        _assert_no_match('16335')

        for test_string in ['163359', '16-33-59', '16:33:59']:
            for n in range(1, len(test_string)):
                # Successively strip the right-most characters.
                _partial = test_string[:-n]
                _assert_no_match(_partial)


class TestRegexLooseDateTime(TestCase):
    def test_matches_yyyy_mm_dd_hh_mm_ss(self):
        def _assert_matches(test_data):
            actual = types.RE_LOOSE_DATETIME.match(test_data)
            self.assertIsNotNone(actual)
            self.assertEqual('2017', actual.group(1))
            self.assertEqual('09', actual.group(2))
            self.assertEqual('14', actual.group(3))
            self.assertEqual('16', actual.group(4))
            self.assertEqual('33', actual.group(5))
            self.assertEqual('59', actual.group(6))

        _assert_matches('20170914163359')
        _assert_matches('2017-091416-3359')
        _assert_matches('201709-141633-59')
        _assert_matches('2017-09-1416-33-59')
        _assert_matches('2017:091416:3359')
        _assert_matches('201709:141633:59')
        _assert_matches('2017:09:1416:33:59')
        _assert_matches('2017_091416_3359')
        _assert_matches('201709_141633_59')
        _assert_matches('2017_09_1416_33_59')
        _assert_matches('2017 09 1416 3359')
        _assert_matches('2017 09141633 59')
        _assert_matches('201709 1416 33 59')

    def test_does_not_match_non_yyyy_mm_dd(self):
        def _assert_no_match(test_data):
            actual = types.RE_LOOSE_DATETIME.match(test_data)
            self.assertIsNone(actual)

        _assert_no_match('')
        _assert_no_match(' ')
        _assert_no_match('foo')
        _assert_no_match('16')
        _assert_no_match('1633')
        _assert_no_match('16335')

        for test_string in ['20170914163359', '2017-09-14 16-33-59',
                            '2017-09-14T16:33:59']:
            for n in range(1, len(test_string)):
                # Successively strip the right-most characters.
                _partial = test_string[:-n]
                _assert_no_match(_partial)


class TestRegexLooseDateTimeMicroseconds(TestCase):
    def test_matches_yyyy_mm_dd_hh_mm_ss_us(self):
        def _assert_matches(test_data):
            actual = types.RE_LOOSE_DATETIME_US.match(test_data)
            self.assertIsNotNone(actual)
            self.assertEqual('2017', actual.group(1))
            self.assertEqual('07', actual.group(2))
            self.assertEqual('12', actual.group(3))
            self.assertEqual('20', actual.group(4))
            self.assertEqual('50', actual.group(5))
            self.assertEqual('15', actual.group(6))
            self.assertEqual('641659', actual.group(7))

        _assert_matches('2017-07-12T20:50:15.641659')
        _assert_matches('2017-07-12 20:50:15.641659')
        _assert_matches('2017:07:12 20:50:15.641659')
        _assert_matches('2017_07_12 20:50:15.641659')
        _assert_matches('2017_07_12 20-50-15.641659')
        _assert_matches('2017_07_12 20_50_15.641659')
        _assert_matches('2017_07_12 20_50_15 641659')
        _assert_matches('2017_07_12 20_50_15_641659')
        _assert_matches('2017 07 12 20 50 15 641659')

    def test_does_not_match_non_yyyy_mm_dd_us(self):
        def _assert_no_match(test_data):
            actual = types.RE_LOOSE_DATETIME_US.match(test_data)
            self.assertIsNone(actual)

        _assert_no_match('')
        _assert_no_match(' ')
        _assert_no_match('foo')
        _assert_no_match('16')
        _assert_no_match('2017-07-12T20:50:15')
        _assert_no_match('2017-07-12T20:50:15.')
        _assert_no_match('2017-07-12T20:50:15.1')
        _assert_no_match('2017-07-12T20:50:15.12')
        _assert_no_match('2017-07-12T20:50:15.123')
        _assert_no_match('2017-07-12T20:50:15.1234')
        _assert_no_match('2017-07-12T20:50:15.12345')


class TestNormalizeDate(TestCase):
    def test_matches_expected(self):
        expected = '2017-09-14'

        def _assert_match(test_data):
            actual = types.normalize_date(test_data)
            self.assertIsNotNone(actual)
            self.assertEqual(expected, actual)

        _assert_match(expected)
        _assert_match('2017 09 14')
        _assert_match('2017-09-14')
        _assert_match('2017:09:14')
        _assert_match('20170914')
        _assert_match('2017-0914')
        _assert_match('201709-14')
        _assert_match('2017-09-14')
        _assert_match('2017:0914')
        _assert_match('201709:14')
        _assert_match('2017:09:14')
        _assert_match('2017_0914')
        _assert_match('201709_14')
        _assert_match('2017_09_14')
        _assert_match('2017 0914')
        _assert_match('201709 14')
        _assert_match('2017 09 14')

        # TODO: Handle other date formats?
        # _assert_match('14.09.2017 3')
        # _assert_match('14092017')


class TestNormalizeDatetimeWithTimeZone(TestCase):
    def test_matches_expected(self):
        expected = '2017-07-12T20:50:15+0200'

        def _assert_match(test_data):
            actual = types.normalize_datetime_with_timezone(test_data)
            self.assertIsNotNone(actual)
            self.assertEqual(expected, actual)

        _assert_match(expected)
        _assert_match('2017 07 12 20 50 15+0200')
        _assert_match('2017-07-12 20:50:15+0200')
        _assert_match('2017:07:12 20:50:15+0200')
        _assert_match('2017-07-12T20:50:15+0200')


class TestNormalizeDatetime(TestCase):
    def test_matches_expected(self):
        expected = '2017-07-12T20:50:15'

        def _assert_match(test_data):
            actual = types.normalize_datetime(test_data)
            self.assertIsNotNone(actual)
            self.assertEqual(expected, actual)

        _assert_match(expected)
        _assert_match('2017 07 12 20 50 15')
        _assert_match('2017-07-12 20:50:15')
        _assert_match('2017:07:12 20:50:15')
        _assert_match('2017-07-12T20:50:15')

        # TODO: Add handling more difficult patterns here?
        # _assert_match('2017-07-12-kl.-20.50.15')
        # _assert_match('07-12-2017 20-50-15 1XZx')


class TestNormalizeDatetimeWithMicroseconds(TestCase):
    def test_matches_expected(self):
        expected = '2017-07-12T20:50:15.641659'

        def _assert_match(test_data):
            actual = types.normalize_datetime_with_microseconds(test_data)
            self.assertIsNotNone(actual)
            self.assertEqual(expected, actual)

        _assert_match(expected)
        _assert_match('2017-07-12T20:50:15.641659')
        _assert_match('2017-07-12 20:50:15.641659')
        _assert_match('2017:07:12 20:50:15.641659')
        _assert_match('2017_07_12 20:50:15.641659')
        _assert_match('2017_07_12 20-50-15.641659')
        _assert_match('2017_07_12 20_50_15.641659')
        _assert_match('2017_07_12 20_50_15 641659')
        _assert_match('2017_07_12 20_50_15_641659')
        _assert_match('2017 07 12 20 50 15 641659')

        # TODO: Add handling more difficult patterns here?
        # _assert_match('12_7_2017_20_50_15_641659')


class TestMultipleTypes(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.coercer_klasses = types.BaseType.__subclasses__()

        # Instantiate to simulate passing the "AW_*" singletons.
        cls.coercer_singletons = [k() for k in cls.coercer_klasses]

    def test_setup(self):
        # Sanity checking ..
        self.assertTrue(all(issubclass(k, types.BaseType)
                        for k in self.coercer_klasses))
        self.assertTrue(all(uu.is_class_instance(k)
                            for k in self.coercer_singletons))

    def test_raises_exception_if_not_instantiated_with_basetype_subclass(self):
        with self.assertRaises(AssertionError):
            _ = types.MultipleTypes(object())

    def test_raises_exception_if_instantiated_with_none(self):
        with self.assertRaises(AssertionError):
            _ = types.MultipleTypes(None)

    def test_instantiate_with_basetype_subclasses(self):
        for coercer in self.coercer_singletons:
            mt = types.MultipleTypes(coercer)
            self.assertIsNotNone(mt)
            self.assertTrue(uu.is_class_instance(mt))

    def test_call_with_none(self):
        for coercer in self.coercer_singletons:
            mt = types.MultipleTypes(coercer)

            if isinstance(coercer, (types.Date, types.TimeDate)):
                # Skip coercers that do not allow failures and raises
                # AWTypeError instead of returning the type-specific "null".
                # TODO: Using coercers "correctly" is becoming too difficult!
                with self.assertRaises(types.AWTypeError):
                    _ = mt(None)
            else:
                actual = mt(None)
                expect = [coercer.null()]
                self.assertEqual(
                    expect, actual,
                    'Expect coercion of None to return the "type-specific null"'
                )

    def test_call_with_string_value_coercable_by_all_but_timedate(self):
        for coercer in self.coercer_singletons:
            mt = types.MultipleTypes(coercer)

            if isinstance(coercer, types.TimeDate):
                # Skip coercers that do not allow failures.
                # TODO: Using coercers "correctly" is becoming too difficult!
                with self.assertRaises(types.AWTypeError):
                    _ = mt('2018')
            else:
                actual = mt('2018')
                self.assertIsNotNone(actual)
                self.assertIsInstance(actual, list)
                self.assertIsNotNone(actual[0])
                self.assertEqual(1, len(actual))


class TestListofComparison(TestCase):
    def test_expect_coercer_klass_in_multipletypes(self):
        list_of_string_coercer = types.listof(types.AW_STRING)
        self.assertIn(types.AW_STRING, list_of_string_coercer)

        list_of_int_coercer = types.listof(types.AW_INTEGER)
        self.assertIn(types.AW_INTEGER, list_of_int_coercer)

    def test_expect_coercer_klass_not_in_multipletypes(self):
        list_of_string_coercer = types.listof(types.AW_STRING)
        self.assertNotIn(types.AW_INTEGER, list_of_string_coercer)

        list_of_int_coercer = types.listof(types.AW_INTEGER)
        self.assertNotIn(types.AW_STRING, list_of_int_coercer)


class TestListofStrings(TestCase):
    def test_call_with_coercible_data(self):
        def _assert_returns(test_data, expected):
            actual = types.listof(types.AW_STRING)(test_data)
            self.assertEqual(expected, actual)

        _assert_returns([''], [''])
        _assert_returns([' '], [' '])
        _assert_returns([b''], [''])
        _assert_returns([b' '], [' '])
        _assert_returns([-1], ['-1'])
        _assert_returns([0], ['0'])
        _assert_returns([1], ['1'])
        _assert_returns([-1.5], ['-1.5'])
        _assert_returns([-1.0], ['-1.0'])
        _assert_returns([1.0], ['1.0'])
        _assert_returns([1.5], ['1.5'])
        _assert_returns(['-1'], ['-1'])
        _assert_returns(['-1.0'], ['-1.0'])
        _assert_returns(['0'], ['0'])
        _assert_returns(['1'], ['1'])
        _assert_returns(['foo'], ['foo'])
        _assert_returns([None], [''])
        _assert_returns([False], ['False'])
        _assert_returns([True], ['True'])

    def test_call_with_noncoercible_data(self):
        with self.assertRaises(types.AWTypeError):
            types.AW_STRING(datetime.now())

        with self.assertRaises(types.AWTypeError):
            types.AW_STRING([datetime.now()])

    def test_listof_string_passthrough(self):
        _coercer = types.listof(types.AW_STRING)
        self.assertTrue(callable(_coercer))

        actual = _coercer(['a', 'b'])
        expect = ['a', 'b']
        self.assertEqual(expect, actual)

    def test_listof_string_passthrough_direct_call(self):
        actual = types.listof(types.AW_STRING)(['a', 'b'])
        expect = ['a', 'b']
        self.assertEqual(expect, actual)

    def test_listof_string_bytes(self):
        _coercer = types.listof(types.AW_STRING)
        self.assertTrue(callable(_coercer))

        actual = _coercer([b'a', b'b'])
        expect = ['a', 'b']
        self.assertEqual(expect, actual)

    def test_listof_string_bytes_direct_call(self):
        actual = types.listof(types.AW_STRING)([b'a', b'b'])
        expect = ['a', 'b']
        self.assertEqual(expect, actual)


class TestListofStringsFormat(TestCase):
    def test_format_coercible_data(self):
        def _assert_formats(test_data, expected):
            actual = types.listof(types.AW_STRING).format(test_data)
            self.assertEqual(expected, actual)

        _assert_formats([''], [''])
        _assert_formats([' '], [' '])
        _assert_formats([b''], [''])
        _assert_formats([b' '], [' '])
        _assert_formats([-1], ['-1'])
        _assert_formats([0], ['0'])
        _assert_formats([1], ['1'])
        _assert_formats([-1.5], ['-1.5'])
        _assert_formats([-1.0], ['-1.0'])
        _assert_formats([1.0], ['1.0'])
        _assert_formats([1.5], ['1.5'])
        _assert_formats(['-1'], ['-1'])
        _assert_formats(['-1.0'], ['-1.0'])
        _assert_formats(['0'], ['0'])
        _assert_formats(['1'], ['1'])
        _assert_formats(['foo'], ['foo'])
        _assert_formats([None], [''])
        _assert_formats([False], ['False'])
        _assert_formats([True], ['True'])

        _assert_formats('', [''])
        _assert_formats(' ', [' '])
        _assert_formats(b'', [''])
        _assert_formats(b' ', [' '])
        _assert_formats(-1, ['-1'])
        _assert_formats(0, ['0'])
        _assert_formats(1, ['1'])
        _assert_formats(-1.5, ['-1.5'])
        _assert_formats(-1.0, ['-1.0'])
        _assert_formats(1.0, ['1.0'])
        _assert_formats(1.5, ['1.5'])
        _assert_formats('-1', ['-1'])
        _assert_formats('-1.0', ['-1.0'])
        _assert_formats('0', ['0'])
        _assert_formats('1', ['1'])
        _assert_formats('foo', ['foo'])
        _assert_formats(None, [''])
        _assert_formats(False, ['False'])
        _assert_formats(True, ['True'])


class TestListofIntegers(TestCase):
    def test_call_with_coercible_data(self):
        def _assert_returns(test_data, expected):
            actual = types.listof(types.AW_INTEGER)(test_data)
            self.assertEqual(expected, actual)

        _assert_returns([None], [0])
        _assert_returns([-1], [-1])
        _assert_returns([0], [0])
        _assert_returns([1], [1])
        _assert_returns([-1.5], [-1])
        _assert_returns([-1.0], [-1])
        _assert_returns([1.0], [1])
        _assert_returns([1.5], [1])
        _assert_returns(['-1'], [-1])
        _assert_returns(['-1.0'], [-1])
        _assert_returns(['0'], [0])
        _assert_returns(['1'], [1])

        _assert_returns(None, [0])
        _assert_returns(-1, [-1])
        _assert_returns(0, [0])
        _assert_returns(1, [1])
        _assert_returns(-1, [-1])
        _assert_returns('0', [0])
        _assert_returns('1', [1])
        _assert_returns('-1', [-1])
        _assert_returns('-1.5', [-1])
        _assert_returns('-1.0', [-1])
        _assert_returns('1.0', [1])
        _assert_returns('1.5', [1])

    def test_call_with_noncoercible_data(self):
        with self.assertRaises(types.AWTypeError):
            types.AW_INTEGER('')

        with self.assertRaises(types.AWTypeError):
            types.AW_INTEGER('foo')

    def test_listof_integer_passthrough(self):
        _coercer = types.listof(types.AW_INTEGER)
        self.assertTrue(callable(_coercer))

        actual = _coercer([1, 2])
        expect = [1, 2]
        self.assertEqual(expect, actual)

    def test_listof_integer_passthrough_direct_call(self):
        actual = types.listof(types.AW_INTEGER)([1, 2])
        expect = [1, 2]
        self.assertEqual(expect, actual)

    def test_listof_string_floats_direct_call(self):
        actual = types.listof(types.AW_INTEGER)([1.0, 2.0])
        expect = [1, 2]
        self.assertEqual(expect, actual)
