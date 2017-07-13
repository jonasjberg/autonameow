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


class TestIntegerType(TestCase):
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


class TestIntegerTypeWrapsValidValues(TestCase):
    def __wrap_integer(self, value):
        return types.AW_INTEGER(value)

    def test_wraps_zero(self):
        wi = self.__wrap_integer(0)
        self.assertIsNotNone(wi)
        self.assertEqual(wi, 0)

    def test_wraps_positive_integers(self):
        wi = self.__wrap_integer(1)
        self.assertIsNotNone(wi)
        self.assertEqual(wi, 1)

    def test_wraps_negative_integers(self):
        wi = self.__wrap_integer(-1)
        self.assertIsNotNone(wi)
        self.assertEqual(wi, -1)


class TestFloatType(TestCase):
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


class TestTimeDateType(TestCase):
    def setUp(self):
        self.t = types.TimeDate()

    def test_null(self):
        self.fail('TODO')

    def test_normalize(self):
        self.fail('TODO')

    def test_call_with_none(self):
        self.t(None)

    def test_call_with_iso_format_string(self):
        self.t('2017-07-12T20:50:15.641659')

    def test_call_with_iso_format_string_sets_expected_value(self):
        isodate_str = '2017-07-12T20:50:15.641659'
        self.t(isodate_str)
        self.assertTrue(isinstance(self.t, types.TimeDate))
        self.assertEqual(str(self.t), isodate_str)


class TestTimeDateTypeParsing(TestCase):
    def test_parse_value_none(self):
        self.assertEqual(types.TimeDate(None), types.TimeDate.null)

    def test_parse_value_iso_format_string(self):
        isodate_str = '2017-07-12T20:50:15.641659'
        expected = datetime.strptime(isodate_str, '%Y-%m-%dT%H:%M:%S.%f')
        self.assertEqual(types.TimeDate(isodate_str), expected)
