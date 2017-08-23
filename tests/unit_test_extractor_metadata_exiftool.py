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

from core import util
from core.exceptions import ExtractorError
from extractors.metadata_exiftool import ExiftoolMetadataExtractor
import unit_utils as uu


temporary_file = uu.make_temporary_file()
E = ExiftoolMetadataExtractor(temporary_file)

unmet_dependencies = ExiftoolMetadataExtractor.check_dependencies() is False
dependency_error = 'Extractor dependencies not satisfied'


class TestExiftoolMetadataExtractor(unittest.TestCase):
    def setUp(self):
        self.e = E

    def test_exiftool_metadata_extractor_class_is_available(self):
        self.assertIsNotNone(ExiftoolMetadataExtractor)

    def test_exiftool_metadata_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_specifies_handles_mime_types(self):
        self.assertIsNotNone(self.e.handles_mime_types)
        self.assertTrue(isinstance(self.e.handles_mime_types, list))

    def test_method_str_returns_expected(self):
        self.assertEqual(str(self.e), 'ExiftoolMetadataExtractor')

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test__get_raw_metadata_returns_something(self):
        self.assertIsNotNone(self.e._get_raw_metadata())

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test__get_raw_metadata_returns_expected_type(self):
        self.assertTrue(isinstance(self.e._get_raw_metadata(), dict))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test__get_raw_metadata_raises_expected_exceptions(self):
        with self.assertRaises(ExtractorError):
            e = ExiftoolMetadataExtractor(None)
            e._get_raw_metadata()
            f = ExiftoolMetadataExtractor('not_a_file_surely')
            f._get_raw_metadata()

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_get_exiftool_data_returns_something(self):
        self.assertIsNotNone(self.e._get_exiftool_data())

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_get_exiftool_data_returns_expected_type(self):
        self.assertTrue(isinstance(self.e._get_exiftool_data(), dict))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_get_exiftool_data_raises_expected_exception(self):
        with self.assertRaises(ExtractorError):
            e = ExiftoolMetadataExtractor(None)
            e._get_exiftool_data()
            f = ExiftoolMetadataExtractor('not_a_file_surely')
            f._get_exiftool_data()

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_returns_something(self):
        self.assertIsNotNone(self.e.execute())

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_returns_expected_type(self):
        self.assertTrue(isinstance(self.e.execute(), dict))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_all_result_contains_file_size(self):
        actual = self.e.execute()
        self.assertTrue('File:FileSize' in actual)

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_file_size_returns_expected(self):
        actual = self.e.execute(field='File:FileSize')
        self.assertEqual(actual, 0)


class TestExiftoolMetadataExtractorWithImage(unittest.TestCase):
    def _to_datetime(self, value):
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

    def setUp(self):
        image = util.normpath(uu.abspath_testfile('smulan.jpg'))
        self.e = ExiftoolMetadataExtractor(image)

        self.EXPECT_FIELD_VALUE = [
            ('EXIF:CreateDate', self._to_datetime('2010-01-31 16:12:51')),
            ('EXIF:DateTimeOriginal', self._to_datetime('2010-01-31 16:12:51')),
            ('EXIF:ExifImageHeight', 1944),
            ('EXIF:ExifImageWidth', 2592)
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
