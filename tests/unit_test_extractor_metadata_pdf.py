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

import unittest
from datetime import datetime

import unit_utils as uu
from core import util
from extractors.metadata import PyPDFMetadataExtractor

unmet_dependencies = PyPDFMetadataExtractor.check_dependencies() is False
dependency_error = 'Extractor dependencies not satisfied'


class TestPDFMetadataExtractor(unittest.TestCase):
    def _to_datetime(self, value):
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S%z')

    def setUp(self):
        image = util.normpath(uu.abspath_testfile('gmail.pdf'))
        self.e = PyPDFMetadataExtractor(image)

        self.EXPECT_FIELD_VALUE = [
            ('CreationDate', self._to_datetime('2016-01-11 12:41:32+0000')),
            ('ModDate', self._to_datetime('2016-01-11 12:41:32+0000')),
            ('Creator', 'Chromium'),
            ('Producer', 'Skia/PDF'),
            ('NumberPages', 2),
            ('Encrypted', False)
        ]

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_returns_something(self):
        self.assertIsNotNone(self.e.execute())

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_returns_expected_type(self):
        self.assertTrue(isinstance(self.e.execute(), dict))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_all_result_contains_expected_fields(self):
        actual = self.e.execute()
        for field, _ in self.EXPECT_FIELD_VALUE:
            self.assertTrue(field in actual)

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_all_result_contains_expected_values(self):
        actual = self.e.execute()
        for field, value in self.EXPECT_FIELD_VALUE:
            self.assertEqual(actual.get(field), value)

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_field_returns_expected_value(self):
        for field, value in self.EXPECT_FIELD_VALUE:
            actual = self.e.execute(field=field)
            self.assertEqual(actual, value)
