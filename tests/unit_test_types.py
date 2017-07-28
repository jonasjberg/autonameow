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


class TestTypeBoolean(TestCase):
    def test_wraps_expected_primitive(self):
        self.assertEqual(type(types.AW_BOOLEAN(None)), bool)

    def test_null(self):
        self.assertEqual(types.AW_BOOLEAN(None),
                         types.AW_BOOLEAN.null)

    def test_normalize(self):
        self.assertEqual(types.AW_BOOLEAN.normalize(True), True)
        self.assertEqual(types.AW_BOOLEAN.normalize(False), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(-1), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(0), False)
        self.assertEqual(types.AW_BOOLEAN.normalize(1), False)
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
        with self.assertRaises(exceptions.AWTypeError):
            self.assertEqual(types.AW_BOOLEAN(-1), False)
            self.assertEqual(types.AW_BOOLEAN(0), False)
            self.assertEqual(types.AW_BOOLEAN(1), False)

        self.assertEqual(types.AW_BOOLEAN('foo'), types.AW_BOOLEAN.null)
        self.assertEqual(types.AW_BOOLEAN(None), types.AW_BOOLEAN.null)

    def test_format(self):
        self.assertIsNotNone(types.AW_BOOLEAN.format)
        self.assertEqual(types.AW_BOOLEAN.format(False), 'False')
        self.assertEqual(types.AW_BOOLEAN.format(True), 'True')
        self.assertEqual(types.AW_BOOLEAN.format('false'), 'False')
        self.assertEqual(types.AW_BOOLEAN.format('true'), 'True')
        self.assertEqual(types.AW_BOOLEAN.format('False'), 'False')
        self.assertEqual(types.AW_BOOLEAN.format('True'), 'True')
        self.assertEqual(types.AW_BOOLEAN.format(b'false'), 'False')
        self.assertEqual(types.AW_BOOLEAN.format(b'true'), 'True')
        self.assertEqual(types.AW_BOOLEAN.format(b'False'), 'False')
        self.assertEqual(types.AW_BOOLEAN.format(b'True'), 'True')


class TestTypeInteger(TestCase):
    def test_wraps_expected_primitive(self):
        self.assertEqual(type(types.AW_INTEGER(None)), int)

    def test_null(self):
        self.assertEqual(types.AW_INTEGER(None), types.AW_INTEGER.null)

    def test_normalize(self):
        # self.assertEqual(types.AW_INTEGER.normalize(None),
        #                  types.AW_INTEGER.null)
        self.assertEqual(types.AW_INTEGER.normalize(-1), -1)
        self.assertEqual(types.AW_INTEGER.normalize(0), 0)
        self.assertEqual(types.AW_INTEGER.normalize(1), 1)

    def test_call_with_none(self):
        self.assertEqual(types.AW_INTEGER(None), 0)

    def test_call_with_coercible_data(self):
        self.assertEqual(types.AW_INTEGER(-1), -1)
        self.assertEqual(types.AW_INTEGER(0), 0)
        self.assertEqual(types.AW_INTEGER(1), 1)
        self.assertEqual(types.AW_INTEGER(-1.5), -1)
        self.assertEqual(types.AW_INTEGER(-1.0), -1)
        self.assertEqual(types.AW_INTEGER(1.0), 1)
        self.assertEqual(types.AW_INTEGER(1.5), 1)
        self.assertEqual(types.AW_INTEGER('-1'), -1)
        self.assertEqual(types.AW_INTEGER('1'), 1)

    def test_call_with_noncoercible_data(self):
        self.assertEqual(types.AW_INTEGER(None), types.AW_INTEGER.null)
        self.assertEqual(types.AW_INTEGER('foo'), types.AW_INTEGER.null)

        with self.assertRaises(exceptions.AWTypeError):
            self.assertEqual(types.AW_INTEGER([]),
                             types.AW_INTEGER.null)
            self.assertEqual(types.AW_INTEGER([1, 2]),
                             types.AW_INTEGER.null)
            self.assertEqual(types.AW_INTEGER(['a', 'b']),
                             types.AW_INTEGER.null)

        # TODO: Fix 'cls.null' returning "property object at 0x*" (?).
        self.assertEqual(types.AW_INTEGER('-1.5'), 0)
        self.assertEqual(types.AW_INTEGER('1.0'), 0)
        self.assertEqual(types.AW_INTEGER('1.5'), 0)


class TestTypeFloat(TestCase):
    def test_wraps_expected_primitive(self):
        self.assertEqual(type(types.AW_FLOAT(None)), float)

    def test_null(self):
        self.assertEqual(types.AW_FLOAT(None), types.AW_FLOAT.null)

    def test_normalize(self):
        self.assertEqual(types.AW_FLOAT.normalize(-1), -1)
        self.assertEqual(types.AW_FLOAT.normalize(0), 0)
        self.assertEqual(types.AW_FLOAT.normalize(1), 1)

    def test_call_with_none(self):
        self.assertEqual(types.AW_FLOAT(None), types.AW_FLOAT.null)

    def test_call_with_coercible_data(self):
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
        self.assertEqual(types.AW_FLOAT('foo'), 0.0)
        self.assertEqual(types.AW_FLOAT(None), 0.0)

        with self.assertRaises(exceptions.AWTypeError):
            self.assertEqual(types.AW_FLOAT(datetime.now()), 0.0)


class TestTypeTimeDate(TestCase):
    def test_wraps_expected_primitive(self):
        # TODO: [TD0050] Figure out how to represent null for datetime objects.
        self.assertEqual(type(types.AW_TIMEDATE(None)), str)

    def test_null(self):
        # TODO: [TD0050] Figure out how to represent null for datetime objects.
        self.assertEqual(types.AW_TIMEDATE(None), 'INVALID DATE')

    def test_normalize(self):
        prior = datetime.strptime('2017-07-12T20:50:15.641659',
                                  '%Y-%m-%dT%H:%M:%S.%f')
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
        self.assertEqual(types.AW_TIMEDATE(None), types.AW_TIMEDATE.null)

    def test_call_with_coercible_data(self):
        expected = datetime.strptime('2017-07-12T20:50:15', '%Y-%m-%dT%H:%M:%S')
        self.assertEqual(types.AW_TIMEDATE(expected), expected)
        self.assertEqual(types.AW_TIMEDATE('2017-07-12T20:50:15'), expected)

    def test_call_with_noncoercible_data(self):
        self.assertEqual(types.AW_TIMEDATE(None), types.AW_TIMEDATE.null)
        self.assertEqual(types.AW_TIMEDATE(''), types.AW_TIMEDATE.null)
        self.assertEqual(types.AW_TIMEDATE([]), types.AW_TIMEDATE.null)
        self.assertEqual(types.AW_TIMEDATE(['']), types.AW_TIMEDATE.null)
        self.assertEqual(types.AW_TIMEDATE([None]), types.AW_TIMEDATE.null)


class TestTypeExiftoolTimeDate(TestCase):
    def test_wraps_expected_primitive(self):
        # TODO: [TD0050] Figure out how to represent null for datetime objects.
        self.assertEqual(type(types.AW_EXIFTOOLTIMEDATE(None)), str)

    def test_null(self):
        # TODO: [TD0050] Figure out how to represent null for datetime objects.
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE(None), 'INVALID DATE')

    def test_call_with_none(self):
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE(None),
                         types.AW_EXIFTOOLTIMEDATE.null)

    def test_call_with_coercible_data(self):
        expected = datetime.strptime('2017-07-12T20:50:15+0200',
                                     '%Y-%m-%dT%H:%M:%S%z')
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE(expected), expected)
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE('2017-07-12 20:50:15+0200'),
                         expected)

    def test_call_with_noncoercible_data(self):
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE(None),
                         types.AW_TIMEDATE.null)
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE(''),
                         types.AW_TIMEDATE.null)
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE([]),
                         types.AW_TIMEDATE.null)
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE(['']),
                         types.AW_TIMEDATE.null)
        self.assertEqual(types.AW_EXIFTOOLTIMEDATE([None]),
                         types.AW_TIMEDATE.null)

    def test_call_with_valid_exiftool_string_returns_expected_type(self):
        actual = types.AW_EXIFTOOLTIMEDATE('2017-07-12 20:50:15+0200')
        self.assertTrue(isinstance(actual, datetime))


class TestTypePyPDFTimeDate(TestCase):
    def test_wraps_expected_primitive(self):
        # TODO: [TD0050] Figure out how to represent null for datetime objects.
        self.assertEqual(type(types.AW_PYPDFTIMEDATE(None)), str)

    def test_null(self):
        # TODO: [TD0050] Figure out how to represent null for datetime objects.
        self.assertEqual(types.AW_PYPDFTIMEDATE(None), 'INVALID DATE')

    def test_call_with_none(self):
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
        self.assertEqual(types.AW_PYPDFTIMEDATE(None),
                         types.AW_TIMEDATE.null)
        self.assertEqual(types.AW_PYPDFTIMEDATE(''),
                         types.AW_TIMEDATE.null)
        self.assertEqual(types.AW_PYPDFTIMEDATE([]),
                         types.AW_TIMEDATE.null)
        self.assertEqual(types.AW_PYPDFTIMEDATE(['']),
                         types.AW_TIMEDATE.null)
        self.assertEqual(types.AW_PYPDFTIMEDATE([None]),
                         types.AW_TIMEDATE.null)

    def test_call_with_valid_pypdf_string_returns_expected_type(self):
        actual = types.AW_PYPDFTIMEDATE("D:20160111124132+00'00'")
        self.assertTrue(isinstance(actual, datetime))


class TestTypePath(TestCase):
    def test_wraps_expected_primitive(self):
        with self.assertRaises(exceptions.AWTypeError):
            self.assertEqual(type(types.AW_PATH(None)), None)

    def test_normalize(self):
        self.skipTest('TODO: ..')
        self.assertEqual(types.AW_PATH.normalize('~/temp'), '/Users/USER/temp')

    def test_call_with_none(self):
        with self.assertRaises(exceptions.AWTypeError):
            self.assertEqual(types.AW_PATH(None), types.AW_PATH.null)

    def test_call_with_coercible_data(self):
        self.assertEqual(types.AW_PATH('/tmp'), b'/tmp')

    def test_call_with_noncoercible_data(self):
        with self.assertRaises(exceptions.AWTypeError):
            types.AW_PATH(datetime.now())
            types.AW_PATH(0)
            types.AW_PATH(None)


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
