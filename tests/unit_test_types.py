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
    exceptions,
    util
)

import unit_utils as uu


class TestBaseType(TestCase):
    def setUp(self):
        self.base_type = types.BaseType()

    def test_null(self):
        self.assertEqual(self.base_type(None), self.base_type.null)

    def test_normalize(self):
        self.assertEqual(self.base_type.normalize(None), self.base_type.null)
        self.assertEqual(self.base_type.normalize('foo'), 'foo')

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
        self.assertEqual(types.AW_BOOLEAN(None),
                         types.AW_BOOLEAN.null)
        self.assertNotEqual(types.AW_BOOLEAN(None), 'NONE',
                            'BaseType default "null" must be overridden')

    def test_normalize(self):
        self.assertEqual(types.AW_BOOLEAN.normalize(True), True)
        self.assertEqual(types.AW_BOOLEAN.normalize(False), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(-1), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(0), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(1), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(-1.0), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(0.0), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(1.0), False)
        self.assertEqual(types.AW_BOOLEAN.normalize('true'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize('True'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize('yes'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize('Yes'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize('no'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize('No'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize('false'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize('False'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(b'true'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(b'True'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(b'yes'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(b'Yes'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(b'no'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(b'No'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(b'false'), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(b'False'), False)

    def test_call_with_none(self):
        self.assertEqual(types.AW_BOOLEAN(None), False)

    def test_call_with_coercible_data(self):
        self.assertEqual(types.AW_BOOLEAN(True), True)
        self.assertEqual(types.AW_BOOLEAN(False), False)
        self.assertEqual(types.AW_BOOLEAN('true'), True)
        self.assertEqual(types.AW_BOOLEAN('True'), True)
        self.assertEqual(types.AW_BOOLEAN('True'), True)
        self.assertEqual(types.AW_BOOLEAN('yes'), True)
        self.assertEqual(types.AW_BOOLEAN('Yes'), True)
        self.assertEqual(types.AW_BOOLEAN('no'), False)
        self.assertEqual(types.AW_BOOLEAN('No'), False)
        self.assertEqual(types.AW_BOOLEAN('false'), False)
        self.assertEqual(types.AW_BOOLEAN('False'), False)
        self.assertEqual(types.AW_BOOLEAN(b'true'), True)
        self.assertEqual(types.AW_BOOLEAN(b'True'), True)
        self.assertEqual(types.AW_BOOLEAN(b'True'), True)
        self.assertEqual(types.AW_BOOLEAN(b'yes'), True)
        self.assertEqual(types.AW_BOOLEAN(b'Yes'), True)
        self.assertEqual(types.AW_BOOLEAN(b'no'), False)
        self.assertEqual(types.AW_BOOLEAN(b'No'), False)
        self.assertEqual(types.AW_BOOLEAN(b'false'), False)
        self.assertEqual(types.AW_BOOLEAN(b'False'), False)

    def test_call_with_noncoercible_data(self):
        def _assert_raises(input_data):
            with self.assertRaises(exceptions.AWTypeError):
                types.AW_BOOLEAN(input_data)

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
        self.assertIsNotNone(types.AW_BOOLEAN.format)
        self.assertEqual(types.AW_BOOLEAN.format(None), 'False')
        self.assertEqual(types.AW_BOOLEAN.format(False), 'False')
        self.assertEqual(types.AW_BOOLEAN.format(True), 'True')
        self.assertEqual(types.AW_BOOLEAN.format('false'), 'False')
        self.assertEqual(types.AW_BOOLEAN.format('true'), 'True')
        self.assertEqual(types.AW_BOOLEAN.format('None'), 'False')
        self.assertEqual(types.AW_BOOLEAN.format('False'), 'False')
        self.assertEqual(types.AW_BOOLEAN.format('True'), 'True')
        self.assertEqual(types.AW_BOOLEAN.format(b'false'), 'False')
        self.assertEqual(types.AW_BOOLEAN.format(b'true'), 'True')
        self.assertEqual(types.AW_BOOLEAN.format(b'None'), 'False')
        self.assertEqual(types.AW_BOOLEAN.format(b'False'), 'False')
        self.assertEqual(types.AW_BOOLEAN.format(b'True'), 'True')


class TestTypeInteger(TestCase):
    def test_wraps_expected_primitive(self):
        self.assertEqual(type(types.AW_INTEGER(None)), int)

    def test_null(self):
        self.assertEqual(types.AW_INTEGER(None), types.AW_INTEGER.null)
        self.assertNotEqual(types.AW_INTEGER(None), 'NONE',
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
        self.assertEqual(types.AW_INTEGER(None), 0)
        self.assertEqual(types.AW_INTEGER(-1), -1)
        self.assertEqual(types.AW_INTEGER(0), 0)
        self.assertEqual(types.AW_INTEGER(1), 1)
        self.assertEqual(types.AW_INTEGER(-1), -1)
        self.assertEqual(types.AW_INTEGER(-1.5), -1)
        self.assertEqual(types.AW_INTEGER(-1.0), -1)
        self.assertEqual(types.AW_INTEGER(1.0), 1)
        self.assertEqual(types.AW_INTEGER(1.5), 1)
        self.assertEqual(types.AW_INTEGER('0'), 0)
        self.assertEqual(types.AW_INTEGER('1'), 1)
        self.assertEqual(types.AW_INTEGER('-1'), -1)
        self.assertEqual(types.AW_INTEGER('-1.5'), -1)
        self.assertEqual(types.AW_INTEGER('-1.0'), -1)
        self.assertEqual(types.AW_INTEGER('1.0'), 1)
        self.assertEqual(types.AW_INTEGER('1.5'), 1)

    def test_call_with_noncoercible_data(self):
        def _assert_raises(input_data):
            with self.assertRaises(exceptions.AWTypeError):
                types.AW_INTEGER(input_data)

        _assert_raises([])
        _assert_raises([1, 2])
        _assert_raises(['a', 'b'])
        _assert_raises('')
        _assert_raises(' ')
        _assert_raises('foo')

    def test_format(self):
        # TODO: Add additional tests.
        self.assertIsNotNone(types.AW_INTEGER.format)

    def test_format_noncoercible_data(self):
        def _assert_raises(input_data):
            with self.assertRaises(exceptions.AWTypeError):
                types.AW_INTEGER.format(input_data)

        _assert_raises(None)


class TestTypeFloat(TestCase):
    def test_wraps_expected_primitive(self):
        self.assertEqual(type(types.AW_FLOAT(None)), float)

    def test_null(self):
        self.assertEqual(types.AW_FLOAT(None), types.AW_FLOAT.null)
        self.assertNotEqual(types.AW_FLOAT(None), 'NONE',
                            'BaseType default "null" must be overridden')

    def test_normalize(self):
        self.assertEqual(types.AW_FLOAT.normalize(-1), -1)
        self.assertEqual(types.AW_FLOAT.normalize(0), 0)
        self.assertEqual(types.AW_FLOAT.normalize(1), 1)

    def test_call_with_none(self):
        self.assertEqual(types.AW_FLOAT(None), types.AW_FLOAT.null)

    def test_call_with_coercible_data(self):
        self.assertEqual(types.AW_FLOAT(None), 0.0)
        self.assertEqual(types.AW_FLOAT(-1), -1.0)
        self.assertEqual(types.AW_FLOAT(0), 0.0)
        self.assertEqual(types.AW_FLOAT(1), 1.0)
        self.assertEqual(types.AW_FLOAT(-1.5), -1.5)
        self.assertEqual(types.AW_FLOAT(-1.0), -1.0)
        self.assertEqual(types.AW_FLOAT(1.0), 1.0)
        self.assertEqual(types.AW_FLOAT(1.5), 1.5)
        self.assertEqual(types.AW_FLOAT('-1.5'), -1.5)
        self.assertEqual(types.AW_FLOAT('-1.0'), -1.0)
        self.assertEqual(types.AW_FLOAT('-1'), -1.0)
        self.assertEqual(types.AW_FLOAT('0'), 0.0)
        self.assertEqual(types.AW_FLOAT('1'), 1.0)
        self.assertEqual(types.AW_FLOAT('1.5'), 1.5)

    def test_call_with_noncoercible_data(self):
        def _assert_raises(input_data):
            with self.assertRaises(exceptions.AWTypeError):
                types.AW_FLOAT(input_data)

        _assert_raises('foo')
        _assert_raises(datetime.now())

    def test_format(self):
        # TODO: Add additional tests.
        self.assertIsNotNone(types.AW_FLOAT.format)
        self.assertEqual(types.AW_FLOAT.format(None), '0.0')


class TestTypeTimeDate(TestCase):
    def test_wraps_expected_primitive(self):
        with self.assertRaises(exceptions.AWTypeError):
            self.assertEqual(type(types.AW_TIMEDATE(None)), str)

    def test_null(self):
        self.assertEqual(types.AW_TIMEDATE.null, 'INVALID DATE')

        with self.assertRaises(exceptions.AWTypeError):
            self.assertNotEqual(types.AW_TIMEDATE(None), 'NONE',
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
        with self.assertRaises(exceptions.AWTypeError):
            self.assertEqual(types.AW_TIMEDATE(None), types.AW_TIMEDATE.null)

    def test_call_with_coercible_data(self):
        expected = datetime.strptime('2017-07-12T20:50:15', '%Y-%m-%dT%H:%M:%S')
        self.assertEqual(types.AW_TIMEDATE(expected), expected)
        self.assertEqual(types.AW_TIMEDATE('2017-07-12T20:50:15'), expected)
        # TODO: Add testing additional input data.

    def test_call_with_noncoercible_data(self):
        def _assert_raises(input_data):
            with self.assertRaises(exceptions.AWTypeError):
                types.AW_TIMEDATE(input_data)

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


class TestTypeExiftoolTimeDate(TestCase):
    def test_wraps_expected_primitive(self):
        with self.assertRaises(exceptions.AWTypeError):
            self.assertEqual(type(types.AW_EXIFTOOLTIMEDATE(None)), str)

    def test_null(self):
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE.null, 'INVALID DATE')

        with self.assertRaises(exceptions.AWTypeError):
            self.assertNotEqual(types.AW_EXIFTOOLTIMEDATE(None), 'NONE',
                                'BaseType default "null" must be overridden')

    def test_call_with_none(self):
        with self.assertRaises(exceptions.AWTypeError):
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
        def _assert_raises(input_data):
            with self.assertRaises(exceptions.AWTypeError):
                types.AW_EXIFTOOLTIMEDATE(input_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises('foo')
        _assert_raises([])
        _assert_raises([''])
        _assert_raises([None])

    def test_call_with_valid_exiftool_string_returns_expected_type(self):
        actual = types.AW_EXIFTOOLTIMEDATE('2017-07-12 20:50:15+0200')
        self.assertTrue(isinstance(actual, datetime))

    def test_format(self):
        # TODO: Add additional tests.
        self.assertIsNotNone(types.AW_EXIFTOOLTIMEDATE.format)


class TestTypePyPDFTimeDate(TestCase):
    def test_wraps_expected_primitive(self):
        with self.assertRaises(exceptions.AWTypeError):
            self.assertEqual(type(types.AW_PYPDFTIMEDATE(None)), str)

    def test_null(self):
        self.assertEqual(types.AW_PYPDFTIMEDATE.null, 'INVALID DATE')

        with self.assertRaises(exceptions.AWTypeError):
            self.assertNotEqual(types.AW_PYPDFTIMEDATE(None), 'NONE',
                                'BaseType default "null" must be overridden')

    def test_call_with_none(self):
        with self.assertRaises(exceptions.AWTypeError):
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

    def test_call_with_noncoercible_data(self):
        with self.assertRaises(exceptions.AWTypeError):
            types.AW_PYPDFTIMEDATE(None)
            types.AW_PYPDFTIMEDATE('')
            types.AW_PYPDFTIMEDATE('foo')
            types.AW_PYPDFTIMEDATE([])
            types.AW_PYPDFTIMEDATE([''])
            types.AW_PYPDFTIMEDATE([None])

    def test_call_with_valid_pypdf_string_returns_expected_type(self):
        actual = types.AW_PYPDFTIMEDATE("D:20160111124132+00'00'")
        self.assertTrue(isinstance(actual, datetime))

    def test_format(self):
        # TODO: Add additional tests.
        self.assertIsNotNone(types.AW_PYPDFTIMEDATE.format)


class TestTypePath(TestCase):
    def test_wraps_expected_primitive(self):
        with self.assertRaises(exceptions.AWTypeError):
            self.assertEqual(type(types.AW_PATH(None)), None)

    def test_null(self):
        with self.assertRaises(exceptions.AWTypeError):
            self.assertEqual(types.AW_PATH(None), 'INVALID PATH')

        with self.assertRaises(exceptions.AWTypeError):
            self.assertEqual(types.AW_PATH(None), types.AW_PATH.null)

        with self.assertRaises(exceptions.AWTypeError):
            self.assertNotEqual(types.AW_PATH(None), 'NONE',
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
        with self.assertRaises(exceptions.AWTypeError):
            types.AW_PATH.normalize('')

    def test_call_with_coercible_data(self):
        self.assertEqual(types.AW_PATH('/tmp'), b'/tmp')
        self.assertEqual(types.AW_PATH('/tmp/foo'), b'/tmp/foo')
        self.assertEqual(types.AW_PATH('/tmp/foo.bar'), b'/tmp/foo.bar')
        self.assertEqual(types.AW_PATH('~'), b'~')
        self.assertEqual(types.AW_PATH('~/foo'), b'~/foo')
        self.assertEqual(types.AW_PATH('~/foo.bar'), b'~/foo.bar')
        self.assertEqual(types.AW_PATH(b'/tmp'), b'/tmp')
        self.assertEqual(types.AW_PATH(b'/tmp/foo'), b'/tmp/foo')
        self.assertEqual(types.AW_PATH(b'/tmp/foo.bar'), b'/tmp/foo.bar')
        self.assertEqual(types.AW_PATH(b'~'), b'~')
        self.assertEqual(types.AW_PATH(b'~/foo'), b'~/foo')
        self.assertEqual(types.AW_PATH(b'~/foo.bar'), b'~/foo.bar')

    def test_call_with_noncoercible_data(self):
        def _assert_raises(input_data):
            with self.assertRaises(exceptions.AWTypeError):
                types.AW_PATH(input_data)

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

        self.assertNotEqual(types.AW_PATHCOMPONENT(None), 'NONE',
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
        self.assertEqual(types.AW_PATHCOMPONENT.normalize('/'), b'/')
        self.assertEqual(types.AW_PATHCOMPONENT.normalize('/foo'), b'/foo')
        self.assertEqual(types.AW_PATHCOMPONENT.normalize('/foo/'), b'/foo')
        self.assertEqual(types.AW_PATHCOMPONENT.normalize('foo'), b'foo')
        self.assertEqual(types.AW_PATHCOMPONENT.normalize('a.pdf'), b'a.pdf')

    def test_normalize_invalid_value(self):
        with self.assertRaises(exceptions.AWTypeError):
            types.AW_PATHCOMPONENT.normalize('')

    def test_call_with_coercible_data(self):
        self.assertEqual(types.AW_PATHCOMPONENT(''), b'')
        self.assertEqual(types.AW_PATHCOMPONENT(None), b'')
        self.assertEqual(types.AW_PATHCOMPONENT('/tmp'), b'/tmp')
        self.assertEqual(types.AW_PATHCOMPONENT('/tmp/foo'), b'/tmp/foo')
        self.assertEqual(types.AW_PATHCOMPONENT('/tmp/f.e'), b'/tmp/f.e')
        self.assertEqual(types.AW_PATHCOMPONENT(b'/tmp'), b'/tmp')
        self.assertEqual(types.AW_PATHCOMPONENT(b'/tmp/foo'), b'/tmp/foo')
        self.assertEqual(types.AW_PATHCOMPONENT(b'/tmp/f.e'), b'/tmp/f.e')

    def test_call_with_coercible_data_including_user_home(self):
        self.assertEqual(types.AW_PATHCOMPONENT(b'~'), b'~')
        self.assertEqual(types.AW_PATHCOMPONENT(b'~/foo'), b'~/foo')
        self.assertEqual(types.AW_PATHCOMPONENT(b'~/foo.bar'), b'~/foo.bar')
        self.assertEqual(types.AW_PATHCOMPONENT('~'), b'~')
        self.assertEqual(types.AW_PATHCOMPONENT('~/foo'), b'~/foo')
        self.assertEqual(types.AW_PATHCOMPONENT('~/foo.bar'), b'~/foo.bar')

    def test_call_with_noncoercible_data(self):
        def _assert_raises(input_data):
            with self.assertRaises(exceptions.AWTypeError):
                types.AW_PATHCOMPONENT(input_data)

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

        self.assertNotEqual(types.AW_STRING(None), 'NONE',
                            'BaseType default "null" must be overridden')

    def test_normalize(self):
        self.assertEqual(types.AW_STRING.normalize(None), '')
        self.assertEqual(types.AW_STRING.normalize(''), '')
        self.assertEqual(types.AW_STRING.normalize(' '), '')
        self.assertEqual(types.AW_STRING.normalize('  '), '')
        self.assertEqual(types.AW_STRING.normalize('foo'), 'foo')
        self.assertEqual(types.AW_STRING.normalize('foo '), 'foo')
        self.assertEqual(types.AW_STRING.normalize(' foo'), 'foo')
        self.assertEqual(types.AW_STRING.normalize(' foo '), 'foo')
        self.assertEqual(types.AW_STRING.normalize('f foo '), 'f foo')
        self.assertEqual(types.AW_STRING.normalize(b'foo'), 'foo')
        self.assertEqual(types.AW_STRING.normalize(b'foo '), 'foo')
        self.assertEqual(types.AW_STRING.normalize(b' foo '), 'foo')
        self.assertEqual(types.AW_STRING.normalize(b'f foo '), 'f foo')

    def test_call_with_none(self):
        self.assertEqual(types.AW_STRING(None), types.AW_STRING.null)

    def test_call_with_coercible_data(self):
        self.assertEqual(types.AW_STRING(-1), '-1')
        self.assertEqual(types.AW_STRING(0), '0')
        self.assertEqual(types.AW_STRING(1), '1')
        self.assertEqual(types.AW_STRING(-1.5), '-1.5')
        self.assertEqual(types.AW_STRING(-1.0), '-1.0')
        self.assertEqual(types.AW_STRING(1.0), '1.0')
        self.assertEqual(types.AW_STRING(1.5), '1.5')
        self.assertEqual(types.AW_STRING('-1'), '-1')
        self.assertEqual(types.AW_STRING('-1.0'), '-1.0')
        self.assertEqual(types.AW_STRING('0'), '0')
        self.assertEqual(types.AW_STRING('1'), '1')
        self.assertEqual(types.AW_STRING('foo'), 'foo')
        self.assertEqual(types.AW_STRING(None), '')
        self.assertEqual(types.AW_STRING(False), 'False')
        self.assertEqual(types.AW_STRING(True), 'True')

    def test_call_with_noncoercible_data(self):
        with self.assertRaises(exceptions.AWTypeError):
            types.AW_STRING(datetime.now())

    def test_coerce_with_coercible_data(self):
        self.assertEqual(types.AW_STRING.coerce(-1), '-1')
        self.assertEqual(types.AW_STRING.coerce(0), '0')
        self.assertEqual(types.AW_STRING.coerce(1), '1')
        self.assertEqual(types.AW_STRING.coerce(-1.5), '-1.5')
        self.assertEqual(types.AW_STRING.coerce(-1.0), '-1.0')
        self.assertEqual(types.AW_STRING.coerce(1.0), '1.0')
        self.assertEqual(types.AW_STRING.coerce(1.5), '1.5')
        self.assertEqual(types.AW_STRING.coerce('-1'), '-1')
        self.assertEqual(types.AW_STRING.coerce('-1.0'), '-1.0')
        self.assertEqual(types.AW_STRING.coerce('0'), '0')
        self.assertEqual(types.AW_STRING.coerce('1'), '1')
        self.assertEqual(types.AW_STRING.coerce('foo'), 'foo')
        self.assertEqual(types.AW_STRING.coerce(None), '')
        self.assertEqual(types.AW_STRING.coerce(False), 'False')
        self.assertEqual(types.AW_STRING.coerce(True), 'True')

    def test_format(self):
        # TODO: Add additional tests.
        self.assertIsNotNone(types.AW_STRING.format)


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
