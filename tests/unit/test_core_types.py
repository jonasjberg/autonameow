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
from datetime import (
    datetime,
    timedelta,
    timezone
)

import unit.utils as uu
from core import types


USER_HOME = os.path.expanduser('~')


class CaseCoercers(object):
    def test_overrides_basetype_default_null_value(self):
        try:
            actual = self.COERCER(None)
        except types.AWTypeError:
            # Some coercer raise an exception instead of returning "null".
            pass
        else:
            self.assertNotEqual(
                actual, types.BaseNullValue,
                'BaseType default "null" value must be overridden'
            )

    def test_normalizes_coercible_or_equivalent_values(self):
        for given, expect in self.TESTDATA_NORMALIZE:
            with self.subTest(expected=expect, given=given):
                actual = self.COERCER.normalize(given)
                self.assertEqual(expect, actual)

    def test_coerces_coercible_or_equivalent_values(self):
        for given, expect in self.TESTDATA_COERCE:
            with self.subTest(expected=expect, given=given):
                actual = self.COERCER(given)
                self.assertEqual(expect, actual)

    def test_formats_coercible_or_equivalent_values(self):
        for given, expect in self.TESTDATA_FORMAT:
            with self.subTest(expected=expect, given=given):
                actual = self.COERCER.format(given)
                self.assertEqual(expect, actual)

    def test_raises_exception_given_incoercible_values(self):
        for given in self.TESTDATA_COERCE_FAIL:
            with self.subTest(given=given):
                with self.assertRaises(types.AWTypeError):
                    _ = self.COERCER(given)


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
            _ = self.base_type.normalize(None)

    def test_base_type_call(self):
        self.assertEqual('foo', self.base_type('foo'))
        self.assertEqual(types.BaseNullValue(), self.base_type(None))

    def test_inheriting_classes_must_implement_format(self):
        with self.assertRaises(NotImplementedError):
            _ = self.base_type.format(None)

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


class TestTypeBoolean(TestCase, CaseCoercers):
    @classmethod
    def setUpClass(cls):
        cls.COERCER = types.AW_BOOLEAN
        cls.TESTDATA_NORMALIZE = [
            (True, True),
            (False, False),
            (-1, False),
            (0, False),
            (1, True),
            (-1.5, False),
            (-1.0001, False),
            (-1.0, False),
            (-0.05, False),
            (-0.0, False),
            (0.0, False),
            (0.05, True),
            (1.0, True),
            (1.0001, True),
            (1.5, True),
            ('true', True),
            ('True', True),
            ('yes', True),
            ('Yes', True),
            ('no', False),
            ('No', False),
            ('false', False),
            ('False', False),
            (b'true', True),
            (b'True', True),
            (b'yes', True),
            (b'Yes', True),
            (b'no', False),
            (b'No', False),
            (b'false', False),
            (b'False', False),
        ]
        cls.TESTDATA_COERCE = [
            (None, False),
            (True, True),
            (False, False),
            ('true', True),
            ('True', True),
            ('True', True),
            ('yes', True),
            ('Yes', True),
            ('no', False),
            ('No', False),
            ('false', False),
            ('False', False),
            ('positive', True),
            ('on', True),
            ('enable', True),
            ('enabled', True),
            ('active', True),
            (b'true', True),
            (b'True', True),
            (b'True', True),
            (b'yes', True),
            (b'Yes', True),
            (b'no', False),
            (b'No', False),
            (b'false', False),
            (b'False', False),
            (b'negative', False),
            (b'off', False),
            (b'disable', False),
            (b'disabled', False),
            (b'inactive', False),
            (-1, False),
            (0, False),
            (1, True),
            (-1.5, False),
            (-1.0001, False),
            (-1.0, False),
            (-0.05, False),
            (-0.0, False),
            (0.0, False),
            (0.05, True),
            (1.0, True),
            (1.0001, True),
            (1.5, True),
            ('foo', types.AW_BOOLEAN.NULL),
            (None, types.AW_BOOLEAN.NULL),
        ]

        class _NoBool(object):
            def __raise(self):
                raise ValueError

            def __bool__(self):
                return self.__raise()

        cls.TESTDATA_COERCE_FAIL = [
            _NoBool(),
        ]

        cls.TESTDATA_FORMAT = [
            (None, 'False'),
            (False, 'False'),
            (True, 'True'),
            ('false', 'False'),
            ('true', 'True'),
            ('None', 'False'),
            ('False', 'False'),
            ('True', 'True'),
            (b'false', 'False'),
            (b'true', 'True'),
            (b'None', 'False'),
            (b'False', 'False'),
            (b'True', 'True'),
        ]

        class _AlwaysTrue(object):
            def __bool__(self):
                return True

        class _AlwaysFalse(object):
            def __bool__(self):
                return False

        cls.TESTDATA_COERCE.extend([
            (_AlwaysTrue(), True),
            (_AlwaysFalse(), False),
            (uu.str_to_datetime('2017-09-25 100951'), False),
        ])

    def test_coerces_expected_primitive(self):
        self.assertEqual(bool, type(types.AW_BOOLEAN(None)))
        self.assertIsInstance(types.AW_BOOLEAN(None), bool)

    def test_null(self):
        self.assertEqual(types.AW_BOOLEAN.NULL, types.AW_BOOLEAN(None))


class TestTypeInteger(TestCase, CaseCoercers):
    @classmethod
    def setUpClass(cls):
        cls.COERCER = types.AW_INTEGER
        cls.TESTDATA_NORMALIZE = [
            (None, types.AW_INTEGER.NULL),
            (-1, -1),
            (0, 0),
            (1, 1),
        ]
        cls.TESTDATA_COERCE = [
            (None, 0),
            (-1, -1),
            (0, 0),
            (1, 1),
            (-1, -1),
            (-1.5, -1),
            (-1.0, -1),
            (1.0, 1),
            (1.5, 1),
            ('0', 0),
            ('1', 1),
            ('-1', -1),
            ('-1.5', -1),
            ('-1.0', -1),
            ('1.0', 1),
            ('1.5', 1),
        ]
        cls.TESTDATA_COERCE_FAIL = [
            [],
            [1, 2],
            ['a', 'b'],
            '',
            ' ',
            'foo',
        ]
        cls.TESTDATA_FORMAT = [
            (1, '1'),
            ('1', '1'),
            (b'1', '1'),
        ]

    def test_coerces_expected_primitive(self):
        self.assertEqual(int, type(types.AW_INTEGER(None)))
        self.assertIsInstance(types.AW_INTEGER(None), int)

    def test_null(self):
        self.assertEqual(types.AW_INTEGER.NULL, types.AW_INTEGER(None))

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
                _ = types.AW_INTEGER.format(test_data, format_string=format_string)

        _assert_raises(1, None)
        _assert_raises(1, [])
        _assert_raises(1, '')
        _assert_raises(1, b'')
        _assert_raises(1, b'x')


class TestTypeFloat(TestCase, CaseCoercers):
    @classmethod
    def setUpClass(cls):
        cls.COERCER = types.AW_FLOAT
        cls.TESTDATA_NORMALIZE = [
            (None, types.AW_FLOAT.NULL),
            (-1, -1),
            (0, 0),
            (1, 1),
        ]
        cls.TESTDATA_COERCE = [
            (None, 0.0),
            (-1, -1.0),
            (0, 0.0),
            (1, 1.0),
            (-1.5, -1.5),
            (-1.0, -1.0),
            (1.0, 1.0),
            (1.5, 1.5),
            ('-1.5', -1.5),
            ('-1.0', -1.0),
            ('-1', -1.0),
            ('0', 0.0),
            ('1', 1.0),
            ('1.5', 1.5),
            (b'-1.5', -1.5),
            (b'-1.0', -1.0),
            (b'-1', -1.0),
            (b'0', 0.0),
            (b'1', 1.0),
            (b'1.5', 1.5),
        ]
        cls.TESTDATA_COERCE_FAIL = [
            'foo',
            datetime.now(),
        ]
        cls.TESTDATA_FORMAT = [
            (None, '0.0'),
            (1, '1.0'),
            (20, '20.0'),
            ('1', '1.0'),
            ('20', '20.0'),
            (b'1', '1.0'),
            (b'20', '20.0'),
        ]

    def test_coerces_expected_primitive(self):
        self.assertEqual(float, type(types.AW_FLOAT(None)))
        self.assertIsInstance(types.AW_FLOAT(None), float)

    def test_null(self):
        self.assertEqual(types.AW_FLOAT.NULL, types.AW_FLOAT(None))

    def test_call_with_none(self):
        self.assertEqual(types.AW_FLOAT.NULL, types.AW_FLOAT(None))

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
                _ = types.AW_FLOAT.format(test_data, format_string=format_string)

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


class TestTypeTimeDate(TestCase, CaseCoercers):
    @classmethod
    def setUpClass(cls):
        cls.COERCER = types.AW_TIMEDATE
        cls.TESTDATA_NORMALIZE = [
            ('2017-07-12T20:50:15.641659', datetime(2017, 7, 12, 20, 50, 15)),
        ]

        expect = datetime(2017, 7, 12, 20, 50, 15)
        cls.TESTDATA_COERCE = [
            (expect, expect),
            ('2017-07-12T20:50:15', expect),
            ('2017-07-12T20-50-15', expect),
            ('2017-07-12T20_50_15', expect),
            ('2017-07-12T205015', expect),
            ('2017-07-12_20:50:15', expect),
            ('2017-07-12_20-50-15', expect),
            ('2017-07-12_20_50_15', expect),
            ('2017-07-12_205015', expect),
            ('2017-07-12-20:50:15', expect),
            ('2017-07-12-20-50-15', expect),
            ('2017-07-12-20_50_15', expect),
            ('2017-07-12-205015', expect),

            # TODO: [cleanup] Really OK to just drop the microseconds?
            ('2017-07-12T20:50:15.613051', expect),

            # TODO: [TD0054] Represent datetime as UTC within autonameow.
            ('2017-07-12T20:50:15.613051+00:00', expect),  # PandocMetadataExtractor

            # TODO: Handle things like 'Thu Aug 31 11:51:57 2017 +0200'
            # TODO: Add testing additional input data.
        ]
        cls.TESTDATA_COERCE_FAIL = [
            None,
            '',
            'foo',
            [],
            [''],
            [None],
        ]
        cls.TESTDATA_FORMAT = [
            ('2017:02:03 10:20:30', '2017-02-03T102030'),
            ('2017-02-03 10:20:30', '2017-02-03T102030'),
            ('2015:03:03 12:25:56-08:00', '2015-03-03T122556'),
        ]

    def test_null(self):
        self.assertEqual('INVALID DATE', types.AW_TIMEDATE.NULL)
        with self.assertRaises(types.AWTypeError):
            _ = types.AW_TIMEDATE(None)

    def test_compare_normalized(self):
        with_usecs = types.AW_TIMEDATE.normalize('2017-07-12T20:50:15.641659')
        without_usecs = types.AW_TIMEDATE.normalize('2017-07-12T20:50:15')
        self.assertEqual(with_usecs, without_usecs)

        another_day = types.AW_TIMEDATE.normalize('2017-07-11T20:50:15')
        self.assertNotEqual(with_usecs, another_day)
        self.assertNotEqual(without_usecs, another_day)

    def test_call_with_none(self):
        with self.assertRaises(types.AWTypeError):
            _ = types.AW_TIMEDATE(None)

    def test_format_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                _ = types.AW_TIMEDATE.format(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises('foo')
        _assert_raises([])
        _assert_raises([''])
        _assert_raises([None])


class TestTypeDate(TestCase, CaseCoercers):
    @classmethod
    def setUpClass(cls):
        cls.COERCER = types.AW_DATE
        expected = datetime(2017, 7, 12, 0, 0, 0)
        cls.TESTDATA_NORMALIZE = [
            (expected, expected),
            ('2017-07-12', expected),
            ('2017 07 12', expected),
            ('2017_07_12', expected),
            ('2017:07:12', expected),
            ('20170712', expected),
        ]

        expected_YMD = datetime(2017, 7, 12, 0, 0, 0)
        expected_YM = datetime.strptime('2017-07', '%Y-%m')
        expected_Y = datetime.strptime('2017', '%Y')
        cls.TESTDATA_COERCE = [
            # Year, month, day
            (expected_YMD, expected_YMD),
            ('2017-07-12', expected_YMD),
            ('2017:07:12', expected_YMD),
            ('2017_07_12', expected_YMD),
            ('2017 07 12', expected_YMD),
            (b'2017-07-12', expected_YMD),
            (b'2017:07:12', expected_YMD),
            (b'2017_07_12', expected_YMD),
            (b'2017 07 12', expected_YMD),

            # Year, month
            (expected_YM, expected_YM),
            ('2017-07', expected_YM),
            ('2017:07', expected_YM),
            ('2017_07', expected_YM),
            (b'2017-07', expected_YM),
            (b'2017:07', expected_YM),
            (b'2017_07', expected_YM),

            # Year
            (expected_Y, expected_Y),
            ('2017', expected_Y),
            (b'2017', expected_Y),
            (2017, expected_Y),
        ]
        cls.TESTDATA_COERCE_FAIL = [
            None,
            '',
            'foo',
            [],
            [''],
            [None],
        ]
        cls.TESTDATA_FORMAT = [
            ('2017:02:03', '2017-02-03'),
            ('2017-02-03', '2017-02-03'),
            ('2015:03:03', '2015-03-03'),
        ]

    def test_null(self):
        self.assertEqual('INVALID DATE', types.AW_DATE.NULL)

    def test_call_with_none(self):
        with self.assertRaises(types.AWTypeError):
            _ = types.AW_DATE(None)

    def test_format_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                _ = types.AW_DATE.format(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises('foo')
        _assert_raises([])
        _assert_raises([''])
        _assert_raises([None])
        _assert_raises('0000:00:00')
        _assert_raises('1234:56:78')


class TestTypeExiftoolTimeDate(TestCase, CaseCoercers):
    @classmethod
    def setUpClass(cls):
        cls.COERCER = types.AW_EXIFTOOLTIMEDATE
        cls.TESTDATA_NORMALIZE = [
        ]

        def _as_datetime(string):
            return datetime.strptime(string, '%Y-%m-%dT%H:%M:%S%z')

        expected_a = _as_datetime('2017-07-12T20:50:15+0200')
        expected_b = _as_datetime('2008-09-12T04:40:52-0400')
        expected_c = _as_datetime('2015-03-03T12:25:56-0800')

        cls.TESTDATA_COERCE = [
            # Most common exiftool format
            (expected_a, expected_a),
            ('2017-07-12 20:50:15+0200', expected_a),

            # Messy timezone
            (expected_b, expected_b),
            ('2008:09:12 04:40:52-04:00', expected_b),

            # Negative timezone
            (expected_c, expected_c),
            ('2015:03:03 12:25:56-08:00', expected_c),

            # Malformed date with trialing z
            ('2017:07:12 20:50:15Z', uu.str_to_datetime('2017-07-12 205015')),
        ]
        cls.TESTDATA_COERCE_FAIL = [
            None,
            '',
            'foo',
            [],
            [''],
            [None],
            '0000:00:00 00:00:00',
            '0000:00:00 00:00:00Z',
            '1234:56:78 90:00:00',
            [1918, '2009:08:20'],
            ['1918', '2009:08:20'],
        ]
        cls.TESTDATA_FORMAT = [
            ('2017:02:03 10:20:30', '2017-02-03T102030'),
            ('2017-02-03 10:20:30', '2017-02-03T102030'),
            ('2015:03:03 12:25:56-08:00', '2015-03-03T122556'),
        ]

    def test_null(self):
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE.NULL, 'INVALID DATE')

    def test_call_with_null(self):
        with self.assertRaises(types.AWTypeError):
            _ = types.AW_EXIFTOOLTIMEDATE(None)

    def test_call_with_valid_exiftool_string_returns_expected_type(self):
        actual = types.AW_EXIFTOOLTIMEDATE('2017-07-12 20:50:15+0200')
        self.assertIsInstance(actual, datetime)

    def test_format_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                _ = types.AW_EXIFTOOLTIMEDATE.format(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises('foo')
        _assert_raises([])
        _assert_raises([''])
        _assert_raises([None])
        _assert_raises('0000:00:00 00:00:00')
        _assert_raises('0000:00:00 00:00:00Z')
        _assert_raises('1234:56:78 90:00:00')


class TestTypePath(TestCase, CaseCoercers):
    @classmethod
    def setUpClass(cls):
        cls.COERCER = types.AW_PATH

        relative_home_foo = uu.normpath(os.path.join(os.path.curdir, 'home/foo'))
        cls.TESTDATA_NORMALIZE = [
            # Expands tilde to user home directory
            ('~', uu.encode(USER_HOME)),
            ('~/', uu.encode(USER_HOME)),
            ('~/foo', uu.normpath(os.path.join(USER_HOME, 'foo'))),

            # Collapses repeating path separators
            ('/home/foo', b'/home/foo'),
            ('/home//foo', b'/home/foo'),
            ('///home/foo', b'/home/foo'),
            ('////home/foo', b'/home/foo'),
            ('////home//foo', b'/home/foo'),
            ('////home////foo', b'/home/foo'),
            ('//home//foo', b'//home/foo'),

            # Normalizes relative path
            ('home/foo', relative_home_foo),
            ('home//foo', relative_home_foo),
            ('home///foo', relative_home_foo),
        ]
        cls.TESTDATA_COERCE = [
            ('/tmp', b'/tmp'),
            ('/tmp/foo', b'/tmp/foo'),
            ('/tmp/foo.bar', b'/tmp/foo.bar'),
            ('~', b'~'),
            ('~/foo', b'~/foo'),
            ('~/foo.bar', b'~/foo.bar'),
            (b'/tmp', b'/tmp'),
            (b'/tmp/foo', b'/tmp/foo'),
            (b'/tmp/foo.bar', b'/tmp/foo.bar'),
            (b'~', b'~'),
            (b'~/foo', b'~/foo'),
            (b'~/foo.bar', b'~/foo.bar'),
        ]
        cls.TESTDATA_COERCE_FAIL = [
            None,
            0,
            '',
            datetime.now(),
        ]
        cls.TESTDATA_FORMAT = [
            (b'/tmp', '/tmp'),
            (b'/tmp/foo', '/tmp/foo'),
            (b'/tmp/foo.bar', '/tmp/foo.bar'),
            (b'~', USER_HOME),
            (b'~/foo', os.path.join(USER_HOME, 'foo')),
            (b'~/foo.bar', os.path.join(USER_HOME, 'foo.bar')),
        ]

    def test_call_with_null(self):
        with self.assertRaises(types.AWTypeError):
            _ = types.AW_PATH(None)

    def test_normalize_invalid_value(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                _ = types.AW_PATH.normalize(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises(b'')


class TestTypePathComponent(TestCase, CaseCoercers):
    @classmethod
    def setUpClass(cls):
        cls.COERCER = types.AW_PATHCOMPONENT

        relative_home_foo = uu.normpath(os.path.join(os.path.curdir, 'home/foo'))
        cls.TESTDATA_NORMALIZE = [
            # Path with user home
            ('~', uu.encode(USER_HOME)),
            ('~/', uu.encode(USER_HOME)),
            ('~/foo', uu.normpath(os.path.join(USER_HOME, 'foo'))),

            # Normalizes path components
            ('/', b'/'),
            ('/foo', b'/foo'),
            ('/foo/', b'/foo'),
            ('foo/', b'foo'),
            ('foo', b'foo'),
            ('a.pdf', b'a.pdf'),
        ]
        cls.TESTDATA_COERCE = [
            ('', b''),
            (None, b''),
            ('/tmp', b'/tmp'),
            ('/tmp/foo', b'/tmp/foo'),
            ('/tmp/f.e', b'/tmp/f.e'),
            (b'/tmp', b'/tmp'),
            (b'/tmp/foo', b'/tmp/foo'),
            (b'/tmp/f.e', b'/tmp/f.e'),

            ('a', b'a'),
            ('a.b', b'a.b'),
            ('a.b.c', b'a.b.c'),
            (b'a', b'a'),
            (b'a.b', b'a.b'),
            (b'a.b.c', b'a.b.c'),
            ('extractor.filesystem.xplat', b'extractor.filesystem.xplat'),
            (b'extractor.filesystem.xplat', b'extractor.filesystem.xplat'),
            ('extractor.text.common', b'extractor.text.common'),
            (b'extractor.text.common', b'extractor.text.common'),

            # With tilde user home
            (b'~', b'~'),
            (b'~/foo', b'~/foo'),
            (b'~/foo.bar', b'~/foo.bar'),
            ('~', b'~'),
            ('~/foo', b'~/foo'),
            ('~/foo.bar', b'~/foo.bar'),
        ]
        cls.TESTDATA_COERCE_FAIL = [
            0,
            datetime.now(),
        ]
        cls.TESTDATA_FORMAT = [
            ('', ''),
            (None, ''),
            (b'/tmp', '/tmp'),
            (b'/tmp/foo', '/tmp/foo'),
            (b'/tmp/foo.bar', '/tmp/foo.bar'),
            ('/tmp', '/tmp'),
            ('/tmp/foo', '/tmp/foo'),
            ('/tmp/foo.bar', '/tmp/foo.bar'),
            (b'~', '~'),
            (b'~/foo', '~/foo'),
            (b'~/foo.bar', '~/foo.bar'),
            ('~', '~'),
            ('~/foo', '~/foo'),
            ('~/foo.bar', '~/foo.bar'),
        ]

    def test_coerces_expected_primitive(self):
        self.assertEqual(bytes, type(types.AW_PATHCOMPONENT(None)))
        self.assertIsInstance(types.AW_PATHCOMPONENT(None), bytes)

    def test_null(self):
        self.assertEqual(types.AW_PATHCOMPONENT(None), b'')
        self.assertEqual(types.AW_PATHCOMPONENT(None),
                         types.AW_PATHCOMPONENT.NULL)

    def test_normalize_invalid_value(self):
        with self.assertRaises(types.AWTypeError):
            _ = types.AW_PATHCOMPONENT.normalize('')


class TestTypeString(TestCase, CaseCoercers):
    @classmethod
    def setUpClass(cls):
        cls.COERCER = types.AW_STRING
        cls.TESTDATA_NORMALIZE = [
            (None, ''),
            ('', ''),
            (' ', ''),
            ('  ', ''),
            (b'', ''),
            (b' ', ''),
            (b'  ', ''),
            (-1, '-1'),
            (0, '0'),
            (1, '1'),
            (-1.5, '-1.5'),
            (-1.0, '-1.0'),
            (1.0, '1.0'),
            (1.5, '1.5'),
            ('foo', 'foo'),
            ('foo ', 'foo'),
            (' foo', 'foo'),
            (' foo ', 'foo'),
            ('f foo ', 'f foo'),
            (b'foo', 'foo'),
            (b'foo ', 'foo'),
            (b' foo', 'foo'),
            (b' foo ', 'foo'),
            (b'f foo ', 'f foo'),
            (None, ''),
            (False, 'False'),
            (True, 'True'),
        ]
        cls.TESTDATA_COERCE = [
            ('', ''),
            (' ', ' '),
            (b'', ''),
            (b' ', ' '),
            (-1, '-1'),
            (0, '0'),
            (1, '1'),
            (-1.5, '-1.5'),
            (-1.0, '-1.0'),
            (1.0, '1.0'),
            (1.5, '1.5'),
            ('-1', '-1'),
            ('-1.0', '-1.0'),
            ('0', '0'),
            ('1', '1'),
            ('foo', 'foo'),
            (None, ''),
            (False, 'False'),
            (True, 'True'),
        ]
        cls.TESTDATA_COERCE_FAIL = [
            datetime.now(),
        ]
        cls.TESTDATA_FORMAT = [
            ('', ''),
            (' ', ' '),
            (b'', ''),
            (b' ', ' '),
            (-1, '-1'),
            (0, '0'),
            (1, '1'),
            (-1.5, '-1.5'),
            (-1.0, '-1.0'),
            (1.0, '1.0'),
            (1.5, '1.5'),
            ('-1', '-1'),
            ('-1.0', '-1.0'),
            ('0', '0'),
            ('1', '1'),
            ('foo', 'foo'),
            (None, ''),
            (False, 'False'),
            (True, 'True'),
        ]

    def test_coerces_expected_primitive(self):
        self.assertEqual(str, type(types.AW_STRING(None)))
        self.assertIsInstance(types.AW_STRING(None), str)

    def test_null(self):
        self.assertEqual('', types.AW_STRING.NULL)

    def test_call_with_none(self):
        self.assertEqual(types.AW_STRING.NULL, types.AW_STRING(None))


class TestTypeMimeType(TestCase, CaseCoercers):
    @classmethod
    def setUpClass(cls):
        cls.COERCER = types.AW_MIMETYPE
        cls.TESTDATA_NORMALIZE = [
            ('asm', 'text/x-asm'),
            ('gz', 'application/gzip'),
            ('pdf', 'application/pdf'),
            ('.pdf', 'application/pdf'),
            ('PDF', 'application/pdf'),
            ('.PDF', 'application/pdf'),
            ('application/pdf', 'application/pdf'),
            ('APPLICATION/pdf', 'application/pdf'),
            ('application/PDF', 'application/pdf'),
            ('APPLICATION/PDF', 'application/pdf'),
            (b'pdf', 'application/pdf'),
            (b'.pdf', 'application/pdf'),
            (b'PDF', 'application/pdf'),
            (b'.PDF', 'application/pdf'),
            (b'application/pdf', 'application/pdf'),
            (b'APPLICATION/pdf', 'application/pdf'),
            (b'application/PDF', 'application/pdf'),
            (b'APPLICATION/PDF', 'application/pdf'),
            ('epub', 'application/epub+zip'),
            ('.epub', 'application/epub+zip'),
            ('EPUB', 'application/epub+zip'),
            ('.EPUB', 'application/epub+zip'),
            ('application/epub+zip', 'application/epub+zip'),
            ('APPLICATION/epub+zip', 'application/epub+zip'),
            ('application/EPUB+ZIP', 'application/epub+zip'),
            ('APPLICATION/EPUB+ZIP', 'application/epub+zip'),
            (b'epub', 'application/epub+zip'),
            (b'.epub', 'application/epub+zip'),
            (b'EPUB', 'application/epub+zip'),
            (b'.EPUB', 'application/epub+zip'),
            (b'application/epub+zip', 'application/epub+zip'),
            (b'APPLICATION/epub+zip', 'application/epub+zip'),
            (b'application/EPUB+ZIP', 'application/epub+zip'),
            (b'APPLICATION/EPUB+ZIP', 'application/epub+zip'),
        ]

        null = types.AW_MIMETYPE.NULL
        cls.TESTDATA_COERCE = [
            ('pdf', 'application/pdf'),
            ('.pdf', 'application/pdf'),
            ('PDF', 'application/pdf'),
            ('.PDF', 'application/pdf'),
            ('application/pdf', 'application/pdf'),
            ('APPLICATION/pdf', 'application/pdf'),
            ('application/PDF', 'application/pdf'),
            ('APPLICATION/PDF', 'application/pdf'),
            (b'pdf', 'application/pdf'),
            (b'.pdf', 'application/pdf'),
            (b'PDF', 'application/pdf'),
            (b'.PDF', 'application/pdf'),
            (b'application/pdf', 'application/pdf'),
            (b'APPLICATION/pdf', 'application/pdf'),
            (b'application/PDF', 'application/pdf'),
            (b'APPLICATION/PDF', 'application/pdf'),
            ('jpg', 'image/jpeg'),
            ('.jpg', 'image/jpeg'),
            ('JPG', 'image/jpeg'),
            ('.JPG', 'image/jpeg'),
            ('.JPEG', 'image/jpeg'),
            ('image/jpeg', 'image/jpeg'),
            (b'jpg', 'image/jpeg'),
            (b'.jpg', 'image/jpeg'),
            (b'JPG', 'image/jpeg'),
            (b'.JPG', 'image/jpeg'),
            (b'image/jpeg', 'image/jpeg'),
            ('application/epub+zip', 'application/epub+zip'),
            ('application/x-lzma', 'application/x-lzma'),
            ('application/gzip', 'application/gzip'),
            ('asm', 'text/x-asm'),
            ('gz', 'application/gzip'),
            ('lzma', 'application/x-lzma'),
            ('mov', 'video/quicktime'),
            ('mp4', 'video/mp4'),
            ('rar', 'application/rar'),
            ('rtf', 'text/rtf'),
            ('sh', 'text/x-shellscript'),
            ('tar.gz', 'application/gzip'),
            ('tar.lzma', 'application/x-lzma'),
            ('txt', 'text/plain'),
            ('inode/x-empty', 'inode/x-empty'),

            # incoercible
            (None, null),
            (False, null),
            (True, null),
            ('', null),
            (' ', null),
            ('foo', null),
            (-1, null),
            (1, null),
            ('application/foo+bar', null),
            ('foo/epub+zip', null),
        ]
        cls.TESTDATA_COERCE_FAIL = [
        ]

        _unknown = types.NULL_AW_MIMETYPE.AS_STRING
        cls.TESTDATA_FORMAT = [
            (None, _unknown),
            ('', _unknown),
            ('this is not a MIME-type', _unknown),
            (1, _unknown),
            (False, _unknown),
            (True, _unknown),
            ([], _unknown),
            ({}, _unknown),
            ('JPG', 'jpg'),
            ('image/jpeg', 'jpg'),
            ('pdf', 'pdf'),
            ('.pdf', 'pdf'),
            ('PDF', 'pdf'),
            ('.PDF', 'pdf'),
            ('application/pdf', 'pdf'),
            ('APPLICATION/pdf', 'pdf'),
            ('application/PDF', 'pdf'),
            ('APPLICATION/PDF', 'pdf'),
            (b'pdf', 'pdf'),
            (b'.pdf', 'pdf'),
            (b'PDF', 'pdf'),
            (b'.PDF', 'pdf'),
            (b'application/pdf', 'pdf'),
            (b'APPLICATION/pdf', 'pdf'),
            (b'application/PDF', 'pdf'),
            (b'APPLICATION/PDF', 'pdf'),
            ('jpg', 'jpg'),
            ('.jpg', 'jpg'),
            ('JPG', 'jpg'),
            ('.JPG', 'jpg'),
            ('.JPEG', 'jpg'),
            ('image/jpeg', 'jpg'),
            (b'jpg', 'jpg'),
            (b'.jpg', 'jpg'),
            (b'JPG', 'jpg'),
            (b'.JPG', 'jpg'),
            (b'image/jpeg', 'jpg'),
            ('epub', 'epub'),
            ('.epub', 'epub'),
            ('EPUB', 'epub'),
            ('.EPUB', 'epub'),
            ('application/epub+zip', 'epub'),
            (b'epub', 'epub'),
            (b'.epub', 'epub'),
            (b'EPUB', 'epub'),
            (b'.EPUB', 'epub'),
            (b'application/epub+zip', 'epub'),
            ('text/plain', 'txt'),
            ('inode/x-empty', ''),
        ]

    def test_null(self):
        self.assertEqual(types.AW_MIMETYPE.NULL, types.NullMIMEType())

        self.assertFalse(types.AW_MIMETYPE.NULL)
        self.assertFalse(types.AW_MIMETYPE.null())

    def test_boolean_evaluation(self):
        actual = types.AW_MIMETYPE('this is an unknown MIME-type ..')
        self.assertFalse(actual)


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
        expected = datetime(2017, 9, 14, 0, 0, 0)

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
        _assert_match('2017-09-14T05:22:31.613051+00:00')

    def test_invalid_dates_raises_valueerror(self):
        def _assert_raises(test_data):
            with self.assertRaises(ValueError):
                _ = types.try_parse_date(test_data)

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

    def test_parses_valid_datetime_with_timezone_and_microseconds(self):
        expected = datetime(
            2017, 7, 20, 5, 22, 31, 613051, tzinfo=timezone.utc
        )
        self._assert_equal('2017 07 20 05 22 31.613051+00:00', expected)
        self._assert_equal('2017-07-20 05 22 31.613051+00:00', expected)
        self._assert_equal('2017-07-20 05:22:31.613051+00:00', expected)
        self._assert_equal('2017-07-20T05:22:31.613051+00:00', expected)
        self._assert_equal('2017 07 20 05 22 31.613051+0000', expected)
        self._assert_equal('2017-07-20 05 22 31.613051+0000', expected)
        self._assert_equal('2017-07-20 05:22:31.613051+0000', expected)
        self._assert_equal('2017-07-20T05:22:31.613051+0000', expected)


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


class TestRegexLooseDateTimeMicrosecondsAndTimezone(TestCase):
    def test_matches_yyyy_mm_dd_hh_mm_ss_us_tz(self):
        def _assert_matches(test_data):
            actual = types.RE_LOOSE_DATETIME_US_TZ.match(test_data)
            self.assertIsNotNone(actual)
            self.assertEqual('2017', actual.group(1))
            self.assertEqual('07', actual.group(2))
            self.assertEqual('12', actual.group(3))
            self.assertEqual('20', actual.group(4))
            self.assertEqual('50', actual.group(5))
            self.assertEqual('15', actual.group(6))
            self.assertEqual('641659', actual.group(7))

        _assert_matches('2017-07-12T20:50:15.641659+00:00')
        _assert_matches('2017-07-12 20:50:15.641659+00:00')
        _assert_matches('2017:07:12 20:50:15.641659+00:00')
        _assert_matches('2017_07_12 20:50:15.641659+00:00')
        _assert_matches('2017_07_12 20-50-15.641659+00:00')
        _assert_matches('2017_07_12 20_50_15.641659+00:00')
        _assert_matches('2017_07_12 20_50_15 641659+00:00')
        _assert_matches('2017_07_12 20_50_15_641659+00:00')
        _assert_matches('2017 07 12 20 50 15 641659+00:00')

    def test_does_not_match_non_yyyy_mm_dd_us(self):
        def _assert_no_match(test_data):
            actual = types.RE_LOOSE_DATETIME_US_TZ.match(test_data)
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


class TestNormalizeDatetimeWithMicrosecondsAndTimeZone(TestCase):
    def test_matches_expected(self):
        expected = '2017-07-12T20:50:15.613051+0200'

        def _assert_match(test_data):
            actual = types.normalize_datetime_with_microseconds_and_timezone(test_data)
            self.assertIsNotNone(actual)
            self.assertEqual(expected, actual)

        _assert_match(expected)
        _assert_match('2017 07 12 20 50 15.613051+0200')
        _assert_match('2017 07 12 20 50 15.613051+0200')
        _assert_match('2017-07-12 20:50:15.613051+0200')
        _assert_match('2017:07:12 20:50:15.613051+0200')
        _assert_match('2017-07-12T20:50:15.613051+0200')
        _assert_match('2017 07 12 20 50 15.613051+02:00')
        _assert_match('2017 07 12 20 50 15.613051+02:00')
        _assert_match('2017-07-12 20:50:15.613051+02:00')
        _assert_match('2017:07:12 20:50:15.613051+02:00')
        _assert_match('2017-07-12T20:50:15.613051+02:00')


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
            _ = types.AW_STRING(datetime.now())

        with self.assertRaises(types.AWTypeError):
            _ = types.AW_STRING([datetime.now()])

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
            _ = types.AW_INTEGER('')

        with self.assertRaises(types.AWTypeError):
            _ = types.AW_INTEGER('foo')

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
