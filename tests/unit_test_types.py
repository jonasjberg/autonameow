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
from datetime import datetime

from core import types


class TestBaseType(TestCase):
    def test_null(self):
        self.skipTest('TODO: ..')
        self.assertEqual(types.BaseType(''), types.BaseType.null)

    def test_normalize(self):
        self.skipTest('TODO: ..')
        self.assertEqual(self.t.null, self.t.normalize(None))
        self.assertEqual('foo', self.t.normalize('foo'))


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

    def test_call_with_none(self):
        self.assertEqual(types.AW_BOOLEAN(None), False)

    def test_call_with_coercible_data(self):
        self.assertEqual(types.AW_BOOLEAN(True), True)
        self.assertEqual(types.AW_BOOLEAN(False), False)
        self.assertEqual(types.AW_BOOLEAN(-1), False)
        self.assertEqual(types.AW_BOOLEAN(0), False)
        self.assertEqual(types.AW_BOOLEAN(1), False)
        self.assertEqual(types.AW_BOOLEAN('true'), True)
        self.assertEqual(types.AW_BOOLEAN('True'), True)
        self.assertEqual(types.AW_BOOLEAN('yes'), True)
        self.assertEqual(types.AW_BOOLEAN('Yes'), True)
        self.assertEqual(types.AW_BOOLEAN('no'), False)
        self.assertEqual(types.AW_BOOLEAN('No'), False)
        self.assertEqual(types.AW_BOOLEAN('false'), False)
        self.assertEqual(types.AW_BOOLEAN('False'), False)

    def test_call_with_noncoercible_data(self):
        self.assertEqual(types.AW_BOOLEAN('foo'), types.AW_BOOLEAN.null)
        self.assertEqual(types.AW_BOOLEAN(None), types.AW_BOOLEAN.null)


class TestTypeInteger(TestCase):
    def test_wraps_expected_primitive(self):
        self.assertEqual(type(types.AW_INTEGER(None)), int)

    def test_null(self):
        self.assertEqual(types.AW_INTEGER(None), 0)
        self.assertNotEqual(types.AW_INTEGER(None), None)
        self.assertNotEqual(types.AW_INTEGER(None), -1)

    def test_normalize(self):
        # self.assertEqual(types.AW_INTEGER.normalize(None),
        #                  types.AW_INTEGER.null)
        self.assertEqual(types.AW_INTEGER.normalize(-1), -1)
        self.assertEqual(types.AW_INTEGER.normalize(0), 0)
        self.assertEqual(types.AW_INTEGER.normalize(1), 1)

    def test_call_with_none(self):
        self.assertEqual(types.AW_INTEGER(None),
                         types.AW_INTEGER.null)

    def test_call_with_coercible_data(self):
        self.assertEqual(types.AW_INTEGER(-1), -1)
        # self.assertEqual(types.AW_INTEGER(-1), -1)

    def test_call_with_noncoercible_data(self):
        self.assertEqual(types.AW_INTEGER('foo'), types.AW_INTEGER.null)


class TestTypeFloat(TestCase):
    def test_wraps_expected_primitive(self):
        self.assertEqual(type(types.AW_FLOAT(None)), float)

    def test_null(self):
        # self.assertEqual(types.AW_FLOAT(None), types.AW_FLOAT.null)
        self.assertEqual(types.AW_FLOAT(None), 0)
        self.assertNotEqual(types.AW_FLOAT(None), None)
        self.assertNotEqual(types.AW_FLOAT(None), -1)

    def test_normalize(self):
        # self.assertEqual(types.AW_FLOAT.normalize(None), types.AW_FLOAT.null)
        self.assertEqual(types.AW_FLOAT.normalize(-1), -1)
        self.assertEqual(types.AW_FLOAT.normalize(0), 0)
        self.assertEqual(types.AW_FLOAT.normalize(1), 1)

    def test_call_with_none(self):
        self.assertEqual(types.AW_FLOAT(None),
                         types.AW_FLOAT.null)

    def test_call_with_coercible_data(self):
        self.fail('TODO')

    def test_call_with_noncoercible_data(self):
        self.fail('TODO')


class TestTypeTimeDate(TestCase):
    def test_wraps_expected_primitive(self):
        # TODO: [TD0050] Figure out how to represent null for datetime objects.
        self.assertEqual(type(types.AW_TIMEDATE(None)), str)

    def test_null(self):
        # TODO: [TD0050] Figure out how to represent null for datetime objects.
        self.assertEqual(types.AW_TIMEDATE(None), 'INVALID DATE')

    def test_normalize(self):
        self.fail('TODO')

    def test_call_with_none(self):
        self.assertEqual(types.AW_TIMEDATE(None),
                         types.AW_TIMEDATE.null)

    def test_call_with_valid_iso_format_string_returns_expected_type(self):
        actual = types.AW_TIMEDATE('2017-07-12T20:50:15.641659')
        self.assertTrue(isinstance(actual, datetime))

    def test_call_with_coercible_data(self):
        self.fail('TODO')

    def test_call_with_noncoercible_data(self):
        self.fail('TODO')


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
        self.fail('TODO')

    def test_call_with_noncoercible_data(self):
        self.fail('TODO')

    def test_call_with_valid_exiftool_string_returns_expected_type(self):
        actual = types.AW_EXIFTOOLTIMEDATE('2017-07-12 20:50:15+0000')
        self.assertTrue(isinstance(actual, datetime))
