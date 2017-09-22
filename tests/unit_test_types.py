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

import os
from unittest import TestCase
from datetime import datetime

from core import (
    types,
    util,
)
from core import constants as C

import unit_utils as uu


class TestBaseType(TestCase):
    def setUp(self):
        self.base_type = types.BaseType()

    def test_null(self):
        self.assertEqual(self.base_type(None), self.base_type.null)

    def test_normalize(self):
        with self.assertRaises(NotImplementedError):
            self.base_type.normalize(None)

    def test_base_type_call(self):
        self.assertEqual(self.base_type('foo'), 'foo')
        self.assertEqual(self.base_type(None), 'NULL')

    def test_inheriting_classes_must_implement_format(self):
        with self.assertRaises(NotImplementedError):
            self.base_type.format(None)

    def test_testing_equivalency(self):
        self.assertTrue(self.base_type.test('foo'))
        self.assertFalse(self.base_type.test(b'foo'))
        self.assertFalse(self.base_type.test(False))
        self.assertFalse(self.base_type.test(1))


class TestTypeBoolean(TestCase):
    def test_coerces_expected_primitive(self):
        self.assertEqual(type(types.AW_BOOLEAN(None)), bool)

    def test_null(self):
        self.assertEqual(types.AW_BOOLEAN(None), types.AW_BOOLEAN.null)
        self.assertNotEqual(types.AW_BOOLEAN(None), 'NULL',
                            'BaseType default "null" must be overridden')

    def test_normalize(self):
        def _assert_normalizes(test_data, expected):
            self.assertEqual(types.AW_BOOLEAN.normalize(test_data), expected)

        _assert_normalizes(True, True)
        _assert_normalizes(False, False)
        _assert_normalizes(-1, False)
        _assert_normalizes(0, False)
        _assert_normalizes(1, False)
        _assert_normalizes(-1.0, False)
        _assert_normalizes(0.0, False)
        _assert_normalizes(1.0, False)
        _assert_normalizes('true', False)
        _assert_normalizes('True', False)
        _assert_normalizes('yes', False)
        _assert_normalizes('Yes', False)
        _assert_normalizes('no', False)
        _assert_normalizes('No', False)
        _assert_normalizes('false', False)
        _assert_normalizes('False', False)
        _assert_normalizes(b'true', False)
        _assert_normalizes(b'True', False)
        _assert_normalizes(b'yes', False)
        _assert_normalizes(b'Yes', False)
        _assert_normalizes(b'no', False)
        _assert_normalizes(b'No', False)
        _assert_normalizes(b'false', False)
        _assert_normalizes(b'False', False)

    def test_call_with_none(self):
        self.assertEqual(types.AW_BOOLEAN(None), False)

    def test_call_with_coercible_data(self):
        def _assert_returns(test_data, expected):
            self.assertEqual(types.AW_BOOLEAN(test_data), expected)

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
        _assert_returns(b'true', True)
        _assert_returns(b'True', True)
        _assert_returns(b'True', True)
        _assert_returns(b'yes', True)
        _assert_returns(b'Yes', True)
        _assert_returns(b'no', False)
        _assert_returns(b'No', False)
        _assert_returns(b'false', False)
        _assert_returns(b'False', False)

    def test_call_with_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_BOOLEAN(test_data)

        _assert_raises(-1)
        _assert_raises(0)
        _assert_raises(1)
        _assert_raises(-1.5)
        _assert_raises(-1.0)
        _assert_raises(-0.05)
        _assert_raises(-0.0)
        _assert_raises(1.0)
        _assert_raises(1.0001)
        _assert_raises(1.5)

        self.assertEqual(types.AW_BOOLEAN('foo'), types.AW_BOOLEAN.null)
        self.assertEqual(types.AW_BOOLEAN(None), types.AW_BOOLEAN.null)

    def test_format(self):
        def _assert_formats(test_data, expected):
            self.assertEqual(types.AW_BOOLEAN.format(test_data), expected)

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
        self.assertEqual(type(types.AW_INTEGER(None)), int)

    def test_null(self):
        self.assertEqual(types.AW_INTEGER(None), types.AW_INTEGER.null)
        self.assertNotEqual(types.AW_INTEGER(None), 'NULL',
                            'BaseType default "null" must be overridden')

    def test_normalize(self):
        self.assertEqual(types.AW_INTEGER.normalize(None),
                         types.AW_INTEGER.null)
        self.assertEqual(types.AW_INTEGER.normalize(-1), -1)
        self.assertEqual(types.AW_INTEGER.normalize(0), 0)
        self.assertEqual(types.AW_INTEGER.normalize(1), 1)

    def test_call_with_none(self):
        self.assertEqual(types.AW_INTEGER(None), 0)

    def test_call_with_coercible_data(self):
        def _assert_returns(test_data, expected):
            self.assertEqual(types.AW_INTEGER(test_data), expected)

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
            self.assertEqual(types.AW_INTEGER.format(test_data), expected)

        _assert_formats(1, '1')
        _assert_formats('1', '1')
        _assert_formats(b'1', '1')

    def test_format_valid_data_with_format_string(self):
        def _assert_formats(test_data, format_string, expected):
            self.assertEqual(
                types.AW_INTEGER.format(test_data, format_string=format_string),
                expected
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
        self.assertEqual(type(types.AW_FLOAT(None)), float)

    def test_null(self):
        self.assertEqual(types.AW_FLOAT(None), types.AW_FLOAT.null)
        self.assertNotEqual(types.AW_FLOAT(None), 'NULL',
                            'BaseType default "null" must be overridden')

    def test_normalize(self):
        self.assertEqual(types.AW_FLOAT.normalize(-1), -1)
        self.assertEqual(types.AW_FLOAT.normalize(0), 0)
        self.assertEqual(types.AW_FLOAT.normalize(1), 1)

    def test_call_with_none(self):
        self.assertEqual(types.AW_FLOAT(None), types.AW_FLOAT.null)

    def test_call_with_coercible_data(self):
        def _assert_returns(test_data, expected):
            self.assertEqual(types.AW_FLOAT(test_data), expected)

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

    def test_call_with_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_FLOAT(test_data)

        _assert_raises('foo')
        _assert_raises(datetime.now())

    def test_format_valid_data(self):
        def _assert_formats(test_data, expected):
            self.assertEqual(types.AW_FLOAT.format(test_data), expected)

        _assert_formats(None, '0.0')
        _assert_formats(1, '1.0')
        _assert_formats(20, '20.0')

    def test_format_valid_data_with_format_string(self):
        def _assert_formats(test_data, format_string, expected):
            self.assertEqual(
                types.AW_FLOAT.format(test_data, format_string=format_string),
                expected
            )

        _assert_formats(None, '{0:.1f}', '0.0')
        _assert_formats(1, '{0:.1f}', '1.0')
        _assert_formats(2, '{0:.2f}', '2.00')
        _assert_formats(33, '{0:.3f}', '33.000')
        _assert_formats(None, 'x', 'x')
        _assert_formats(1, 'x', 'x')
        _assert_formats(2, 'x', 'x')
        _assert_formats(33, 'x', 'x')

    def test_format_raises_exception_for_invalid_format_strings(self):
        def _assert_raises(test_data, format_string):
            with self.assertRaises(types.AWTypeError):
                types.AW_FLOAT.format(test_data, format_string=format_string)

        _assert_raises(1.0, None)
        _assert_raises(1.0, [])
        _assert_raises(1.0, '')
        _assert_raises(1.0, b'')
        _assert_raises(1.0, b'x')


class TestTypeTimeDate(TestCase):
    def test_coerces_expected_primitive(self):
        with self.assertRaises(types.AWTypeError):
            self.assertEqual(type(types.AW_TIMEDATE(None)), str)

    def test_null(self):
        self.assertEqual(types.AW_TIMEDATE.null, 'INVALID DATE')

        with self.assertRaises(types.AWTypeError):
            self.assertNotEqual(types.AW_TIMEDATE(None), 'NULL',
                                'BaseType default "null" must be overridden')

    def test_normalize(self):
        expected = datetime.strptime('2017-07-12T20:50:15',
                                     '%Y-%m-%dT%H:%M:%S')
        self.assertEqual(
            types.AW_TIMEDATE.normalize('2017-07-12T20:50:15.641659'), expected
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
            self.assertEqual(types.AW_TIMEDATE(None), types.AW_TIMEDATE.null)

    def test_call_with_coercible_data(self):
        expected = datetime.strptime('2017-07-12T20:50:15', '%Y-%m-%dT%H:%M:%S')
        self.assertEqual(types.AW_TIMEDATE(expected), expected)
        self.assertEqual(types.AW_TIMEDATE('2017-07-12T20:50:15'), expected)
        self.assertEqual(types.AW_TIMEDATE('2017-07-12T205015'), expected)
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
            self.assertEqual(types.AW_TIMEDATE.format(test_data), expected)

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
            self.assertEqual(type(types.AW_DATE(None)), datetime)

    def test_null(self):
        self.assertEqual(types.AW_DATE.null, 'INVALID DATE')

        with self.assertRaises(types.AWTypeError):
            self.assertNotEqual(types.AW_DATE(None), 'NULL',
                                'BaseType default "null" must be overridden')

    def test_normalize(self):
        def _assert_equal(test_data, expected):
            actual = types.AW_DATE.normalize(test_data)
            self.assertEqual(actual, expected)
            self.assertTrue(isinstance(actual, datetime))

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
        self.assertEqual(types.AW_DATE(expected), expected)
        self.assertEqual(types.AW_DATE('2017-07-12'), expected)
        self.assertEqual(types.AW_DATE('2017:07:12'), expected)
        self.assertEqual(types.AW_DATE('2017_07_12'), expected)
        self.assertEqual(types.AW_DATE('2017 07 12'), expected)
        self.assertEqual(types.AW_DATE(b'2017-07-12'), expected)
        self.assertEqual(types.AW_DATE(b'2017:07:12'), expected)
        self.assertEqual(types.AW_DATE(b'2017_07_12'), expected)
        self.assertEqual(types.AW_DATE(b'2017 07 12'), expected)

    def test_call_with_coercible_data_year_month(self):
        expected = datetime.strptime('2017-07', '%Y-%m')
        self.assertEqual(types.AW_DATE(expected), expected)
        self.assertEqual(types.AW_DATE('2017-07'), expected)
        self.assertEqual(types.AW_DATE('2017:07'), expected)
        self.assertEqual(types.AW_DATE('2017_07'), expected)
        self.assertEqual(types.AW_DATE(b'2017-07'), expected)
        self.assertEqual(types.AW_DATE(b'2017:07'), expected)
        self.assertEqual(types.AW_DATE(b'2017_07'), expected)

    def test_call_with_coercible_data_year(self):
        expected = datetime.strptime('2017', '%Y')
        self.assertEqual(types.AW_DATE(expected), expected)
        self.assertEqual(types.AW_DATE('2017'), expected)
        self.assertEqual(types.AW_DATE(b'2017'), expected)
        self.assertEqual(types.AW_DATE(2017), expected)

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
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE.null, 'INVALID DATE')

        with self.assertRaises(types.AWTypeError):
            self.assertNotEqual(types.AW_EXIFTOOLTIMEDATE(None), 'NULL',
                                'BaseType default "null" must be overridden')

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

    def test_call_with_valid_exiftool_string_returns_expected_type(self):
        actual = types.AW_EXIFTOOLTIMEDATE('2017-07-12 20:50:15+0200')
        self.assertTrue(isinstance(actual, datetime))

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


class TestTypePyPDFTimeDate(TestCase):
    def test_coerces_expected_primitive(self):
        with self.assertRaises(types.AWTypeError):
            self.assertEqual(type(types.AW_PYPDFTIMEDATE(None)), str)

    def test_null(self):
        self.assertEqual(types.AW_PYPDFTIMEDATE.null, 'INVALID DATE')

        with self.assertRaises(types.AWTypeError):
            self.assertNotEqual(types.AW_PYPDFTIMEDATE(None), 'NULL',
                                'BaseType default "null" must be overridden')

    def test_call_with_none(self):
        with self.assertRaises(types.AWTypeError):
            self.assertEqual(types.AW_PYPDFTIMEDATE(None),
                             types.AW_PYPDFTIMEDATE.null)

    def test_call_with_coercible_data(self):
        expected = datetime.strptime('2012-12-25T23:52:37+0530',
                                     '%Y-%m-%dT%H:%M:%S%z')
        self.assertEqual(types.AW_PYPDFTIMEDATE(expected), expected,
                         'datetime objects should be passed through as-is')
        self.assertEqual(types.AW_PYPDFTIMEDATE("D:20121225235237 +05'30'"),
                         expected)

    def test_call_with_coercible_data_2(self):
        expected = datetime.strptime('2016-01-11T12:41:32+0000',
                                     '%Y-%m-%dT%H:%M:%S%z')
        self.assertEqual(types.AW_PYPDFTIMEDATE(expected), expected,
                         'datetime objects should be passed through as-is')
        self.assertEqual(types.AW_PYPDFTIMEDATE("D:20160111124132+00'00'"),
                         expected)

    def test_call_with_coercible_data_no_time(self):
        expected = uu.str_to_datetime('2005-10-23 000000')
        self.assertEqual(types.AW_PYPDFTIMEDATE('D:20051023'), expected)

    def test_call_with_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_PYPDFTIMEDATE(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises('foo')
        _assert_raises([])
        _assert_raises([''])
        _assert_raises([None])

    def test_call_with_valid_pypdf_string_returns_expected_type(self):
        actual = types.AW_PYPDFTIMEDATE("D:20160111124132+00'00'")
        self.assertTrue(isinstance(actual, datetime))

    def test_format(self):
        # TODO: Add additional tests.
        self.skipTest('TODO: Add additional tests ..')


class TestTypePath(TestCase):
    def test_coerces_expected_primitive(self):
        with self.assertRaises(types.AWTypeError):
            self.assertEqual(type(types.AW_PATH(None)), None)

    def test_null(self):
        with self.assertRaises(types.AWTypeError):
            self.assertEqual(types.AW_PATH(None), 'INVALID PATH')

        with self.assertRaises(types.AWTypeError):
            self.assertEqual(types.AW_PATH(None), types.AW_PATH.null)

        with self.assertRaises(types.AWTypeError):
            self.assertNotEqual(types.AW_PATH(None), 'NULL',
                                'BaseType default "null" must be overridden')

    def test_normalize(self):
        user_home = os.path.expanduser('~')
        self.assertEqual(types.AW_PATH.normalize('~'),
                         util.encode_(user_home))
        self.assertEqual(types.AW_PATH.normalize('~/'),
                         util.encode_(user_home))

        expected = os.path.normpath(os.path.join(user_home, 'foo'))
        self.assertEqual(types.AW_PATH.normalize('~/foo'),
                         util.encode_(expected))

    def test_normalize_invalid_value(self):
        with self.assertRaises(types.AWTypeError):
            types.AW_PATH.normalize('')

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
        # TODO: Add additional tests.
        self.skipTest('TODO: Add additional tests ..')


class TestTypePathComponent(TestCase):
    def test_coerces_expected_primitive(self):
        self.assertEqual(type(types.AW_PATHCOMPONENT(None)), bytes)

    def test_null(self):
        self.assertEqual(types.AW_PATHCOMPONENT(None), b'')
        self.assertEqual(types.AW_PATHCOMPONENT(None),
                         types.AW_PATHCOMPONENT.null)

        self.assertNotEqual(types.AW_PATHCOMPONENT(None), 'NULL',
                            'BaseType default "null" must be overridden')

    def test_normalize_path_with_user_home(self):
        user_home = os.path.expanduser('~')
        self.assertEqual(types.AW_PATHCOMPONENT.normalize('~'),
                         util.encode_(user_home))
        self.assertEqual(types.AW_PATHCOMPONENT.normalize('~/'),
                         util.encode_(user_home))

        expected = os.path.normpath(os.path.join(user_home, 'foo'))
        self.assertEqual(types.AW_PATHCOMPONENT.normalize('~/foo'),
                         util.encode_(expected))

    def test_normalize_path_components(self):
        def _assert_normalizes(test_data, expected):
            self.assertEqual(types.AW_PATHCOMPONENT.normalize(test_data),
                             expected)

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
            self.assertEqual(types.AW_PATHCOMPONENT(test_data), expected)

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
            self.assertEqual(types.AW_PATHCOMPONENT(test_data), expected)

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
        # TODO: Add additional tests.
        self.skipTest('TODO: Add additional tests ..')


class TestTypeString(TestCase):
    def test_coerces_expected_primitive(self):
        self.assertEqual(type(types.AW_STRING(None)), str)

    def test_null(self):
        self.assertEqual(types.AW_STRING.null, '')

        self.assertNotEqual(types.AW_STRING(None), 'NULL',
                            'BaseType default "null" must be overridden')

    def test_normalize(self):
        def _assert_normalizes(test_data, expected):
            self.assertEqual(types.AW_STRING.normalize(test_data), expected)

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
        self.assertEqual(types.AW_STRING(None), types.AW_STRING.null)

    def test_call_with_coercible_data(self):
        def _assert_returns(test_data, expected):
            self.assertEqual(types.AW_STRING(test_data), expected)

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
            self.assertEqual(types.AW_STRING.format(test_data), expected)

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
    def test_coerces_expected_primitive(self):
        self.assertEqual(type(types.AW_MIMETYPE(None)), str)

    def test_null(self):
        self.assertEqual(types.AW_MIMETYPE.null, C.MAGIC_TYPE_UNKNOWN)
        self.assertNotEqual(types.AW_MIMETYPE(None), 'NULL',
                            'BaseType default "null" must be overridden')

    def test_normalize(self):
        def _assert_normalizes(test_data, expected):
            self.assertEqual(types.AW_MIMETYPE.normalize(test_data), expected)

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
        self.assertEqual(types.AW_MIMETYPE(None), types.AW_MIMETYPE.null)

    def test_call_with_coercible_data(self):
        def _assert_coerces(test_data, expected):
            self.assertEqual(types.AW_MIMETYPE(test_data), expected)

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

    def test_call_with_noncoercible_data(self):
        def _assert_uncoercible(test_data):
            self.assertEqual(types.AW_MIMETYPE(test_data),
                             types.AW_MIMETYPE.null)

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
            self.assertEqual(types.AW_MIMETYPE.format(test_data), expected)

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


class TestTryCoerce(TestCase):
    def test_try_coerce_none(self):
        self.assertIsNone(types.try_coerce(None))

    def test_try_coerce_list(self):
        # TODO: [TD0084] Add handling collections to type coercion classes.
        self.assertIsNone(types.try_coerce([]))
        self.assertIsNone(types.try_coerce(['foo', 'bar']))
        self.assertIsNone(types.try_coerce([1, 2]))

    def test_try_coerce_primitive_bool(self):
        self.assertEqual(types.try_coerce(False), False)
        self.assertEqual(types.try_coerce(True), True)
        self.assertTrue(isinstance(types.try_coerce(False), bool))
        self.assertTrue(isinstance(types.try_coerce(True), bool))

    def test_try_coerce_primitive_int(self):
        self.assertEqual(types.try_coerce(1), 1)
        self.assertEqual(types.try_coerce(0), 0)
        self.assertTrue(isinstance(types.try_coerce(1), int))
        self.assertTrue(isinstance(types.try_coerce(0), int))

    def test_try_coerce_primitive_float(self):
        self.assertEqual(types.try_coerce(1.0), 1.0)
        self.assertEqual(types.try_coerce(0.0), 0.0)
        self.assertTrue(isinstance(types.try_coerce(1.0), float))
        self.assertTrue(isinstance(types.try_coerce(0.0), float))

    def test_try_coerce_primitive_str(self):
        self.assertEqual(types.try_coerce('foo'), 'foo')
        self.assertEqual(types.try_coerce(''), '')
        self.assertTrue(isinstance(types.try_coerce('foo'), str))
        self.assertTrue(isinstance(types.try_coerce(''), str))

    def test_try_coerce_primitive_bytes(self):
        self.assertEqual(types.try_coerce(b'foo'), 'foo')
        self.assertEqual(types.try_coerce(b''), '')
        self.assertTrue(isinstance(types.try_coerce(b'foo'), str))
        self.assertTrue(isinstance(types.try_coerce(b''), str))

    def test_try_coerce_datetime(self):
        dt = datetime.now()
        self.assertEqual(types.try_coerce(dt), dt)
        self.assertTrue(isinstance(types.try_coerce(dt), datetime))
        self.assertTrue(isinstance(types.try_coerce(datetime.now()), datetime))


class TestTryParseDate(TestCase):
    def test_parses_valid_date(self):
        expected = datetime.strptime('2017-09-14', '%Y-%m-%d')

        def _assert_match(test_data):
            actual = types.try_parse_date(test_data)
            self.assertEqual(actual, expected)
            self.assertTrue(isinstance(actual, datetime))

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
        self.assertEqual(actual, expected)
        self.assertTrue(isinstance(actual, datetime))

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
            self.assertEqual(actual.group(1), '2017')
            self.assertEqual(actual.group(2), '09')
            self.assertEqual(actual.group(3), '14')

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
            self.assertEqual(actual.group(1), '16')
            self.assertEqual(actual.group(2), '33')
            self.assertEqual(actual.group(3), '59')

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
            self.assertEqual(actual.group(1), '2017')
            self.assertEqual(actual.group(2), '09')
            self.assertEqual(actual.group(3), '14')
            self.assertEqual(actual.group(4), '16')
            self.assertEqual(actual.group(5), '33')
            self.assertEqual(actual.group(6), '59')

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
            self.assertEqual(actual.group(1), '2017')
            self.assertEqual(actual.group(2), '07')
            self.assertEqual(actual.group(3), '12')
            self.assertEqual(actual.group(4), '20')
            self.assertEqual(actual.group(5), '50')
            self.assertEqual(actual.group(6), '15')
            self.assertEqual(actual.group(7), '641659')

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
            self.assertEqual(actual, expected)

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
            self.assertEqual(actual, expected)

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
            self.assertEqual(actual, expected)

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
            self.assertEqual(actual, expected)

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
