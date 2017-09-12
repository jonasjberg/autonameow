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
    constants,
    types,
    util,
)

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
    def test_wraps_expected_primitive(self):
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
    def test_wraps_expected_primitive(self):
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

    def test_format(self):
        def _assert_formats(test_data, expected):
            self.assertEqual(types.AW_INTEGER.format(test_data), expected)

        _assert_formats(1, '1')
        _assert_formats('1', '1')
        _assert_formats(b'1', '1')

    def test_format_noncoercible_data(self):
        def _assert_raises(test_data):
            with self.assertRaises(types.AWTypeError):
                types.AW_INTEGER.format(test_data)

        _assert_raises('x')


class TestTypeFloat(TestCase):
    def test_wraps_expected_primitive(self):
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

    def test_format(self):
        # TODO: Add additional tests.
        self.assertIsNotNone(types.AW_FLOAT.format)
        self.assertEqual(types.AW_FLOAT.format(None), '0.0')


class TestTypeTimeDate(TestCase):
    def test_wraps_expected_primitive(self):
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

    def test_format(self):
        # TODO: Add additional tests.
        self.assertIsNotNone(types.AW_TIMEDATE.format)


class TestTypeDate(TestCase):
    def test_wraps_expected_primitive(self):
        with self.assertRaises(types.AWTypeError):
            self.assertEqual(type(types.AW_DATE(None)), datetime)

    def test_null(self):
        self.assertEqual(types.AW_DATE.null, 'INVALID DATE')

        with self.assertRaises(types.AWTypeError):
            self.assertNotEqual(types.AW_DATE(None), 'NULL',
                                'BaseType default "null" must be overridden')

    def test_normalize(self):
        self.skipTest('TODO: Add tests for the "Date" type wrapper')

    def test_call_with_none(self):
        with self.assertRaises(types.AWTypeError):
            types.AW_DATE(None)

    def test_call_with_coercible_data_year_month_day(self):
        expected = datetime.strptime('2017-07-12', '%Y-%m-%d')
        self.assertEqual(types.AW_DATE(expected), expected)
        self.assertEqual(types.AW_DATE('2017-07-12'), expected)
        self.assertEqual(types.AW_DATE(b'2017-07-12'), expected)

    def test_call_with_coercible_data_year_month(self):
        expected = datetime.strptime('2017-07', '%Y-%m')
        self.assertEqual(types.AW_DATE(expected), expected)
        self.assertEqual(types.AW_DATE('2017-07'), expected)
        self.assertEqual(types.AW_DATE(b'2017-07'), expected)

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

    def test_format(self):
        # TODO: Add additional tests.
        self.assertIsNotNone(types.AW_DATE.format)


class TestTypeExiftoolTimeDate(TestCase):
    def test_wraps_expected_primitive(self):
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

    def test_format(self):
        # TODO: Add additional tests.
        self.assertIsNotNone(types.AW_EXIFTOOLTIMEDATE.format)


class TestTypePyPDFTimeDate(TestCase):
    def test_wraps_expected_primitive(self):
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
        self.assertIsNotNone(types.AW_PYPDFTIMEDATE.format)


class TestTypePath(TestCase):
    def test_wraps_expected_primitive(self):
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
        self.assertIsNotNone(types.AW_PATH.format)


class TestTypePathComponent(TestCase):
    def test_wraps_expected_primitive(self):
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
        self.assertIsNotNone(types.AW_PATHCOMPONENT.format)


class TestTypeString(TestCase):
    def test_wraps_expected_primitive(self):
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

    def test_coerce_with_coercible_data(self):
        def _assert_coerces(test_data, expected):
            self.assertEqual(types.AW_STRING.coerce(test_data), expected)

        _assert_coerces('', '')
        _assert_coerces(' ', ' ')
        _assert_coerces(b'', '')
        _assert_coerces(b' ', ' ')
        _assert_coerces(-1, '-1')
        _assert_coerces(0, '0')
        _assert_coerces(1, '1')
        _assert_coerces(-1.5, '-1.5')
        _assert_coerces(-1.0, '-1.0')
        _assert_coerces(1.0, '1.0')
        _assert_coerces(1.5, '1.5')
        _assert_coerces('-1', '-1')
        _assert_coerces('-1.0', '-1.0')
        _assert_coerces('0', '0')
        _assert_coerces('1', '1')
        _assert_coerces('foo', 'foo')
        _assert_coerces(None, '')
        _assert_coerces(False, 'False')
        _assert_coerces(True, 'True')

    def test_format(self):
        # TODO: Add additional tests.
        self.assertIsNotNone(types.AW_STRING.format)


class TestTypeMimeType(TestCase):
    def test_wraps_expected_primitive(self):
        self.assertEqual(type(types.AW_MIMETYPE(None)), str)

    def test_null(self):
        self.assertEqual(types.AW_MIMETYPE.null, constants.MAGIC_TYPE_UNKNOWN)
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

            # TODO: [TD0083] Return "NULL" or raise 'AWTypeError'..?
            # with self.assertRaises(exceptions.AWTypeError):
            #     types.AW_MIMETYPE(test_data)

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


class TestTryWrap(TestCase):
    def test_try_wrap_primitive_bool(self):
        self.assertEqual(types.try_wrap(False), False)
        self.assertEqual(types.try_wrap(True), True)
        self.assertTrue(isinstance(types.try_wrap(False), bool))
        self.assertTrue(isinstance(types.try_wrap(True), bool))

    def test_try_wrap_primitive_int(self):
        self.assertEqual(types.try_wrap(1), 1)
        self.assertEqual(types.try_wrap(0), 0)
        self.assertTrue(isinstance(types.try_wrap(1), int))
        self.assertTrue(isinstance(types.try_wrap(0), int))

    def test_try_wrap_primitive_float(self):
        self.assertEqual(types.try_wrap(1.0), 1.0)
        self.assertEqual(types.try_wrap(0.0), 0.0)
        self.assertTrue(isinstance(types.try_wrap(1.0), float))
        self.assertTrue(isinstance(types.try_wrap(0.0), float))

    def test_try_wrap_primitive_str(self):
        self.assertEqual(types.try_wrap('foo'), 'foo')
        self.assertEqual(types.try_wrap(''), '')
        self.assertTrue(isinstance(types.try_wrap('foo'), str))
        self.assertTrue(isinstance(types.try_wrap(''), str))

    def test_try_wrap_primitive_bytes(self):
        self.assertEqual(types.try_wrap(b'foo'), 'foo')
        self.assertEqual(types.try_wrap(b''), '')
        self.assertTrue(isinstance(types.try_wrap(b'foo'), str))
        self.assertTrue(isinstance(types.try_wrap(b''), str))

    def test_try_wrap_datetime(self):
        dt = datetime.now()
        self.assertEqual(types.try_wrap(dt), dt)
        self.assertTrue(isinstance(types.try_wrap(dt), datetime))
        self.assertTrue(isinstance(types.try_wrap(datetime.now()), datetime))
