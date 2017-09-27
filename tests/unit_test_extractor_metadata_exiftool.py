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
from extractors import ExtractorError
from extractors.metadata import ExiftoolMetadataExtractor
from extractors.metadata.exiftool import _get_exiftool_data

import unit_utils as uu


unmet_dependencies = not ExiftoolMetadataExtractor.check_dependencies()
dependency_error = 'Extractor dependencies not satisfied'


temp_file = uu.make_temporary_file()


class TestExiftoolMetadataExtractor(unittest.TestCase):
    def setUp(self):
        self.e = ExiftoolMetadataExtractor()

    def test_exiftool_metadata_extractor_class_is_available(self):
        self.assertIsNotNone(ExiftoolMetadataExtractor)

    def test_exiftool_metadata_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_specifies_handles_mime_types(self):
        self.assertIsNotNone(self.e.HANDLES_MIME_TYPES)
        self.assertTrue(isinstance(self.e.HANDLES_MIME_TYPES, list))

    def test_method_str_returns_expected(self):
        self.assertEqual(str(self.e), 'ExiftoolMetadataExtractor')

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test__get_metadata_returns_something(self):
        self.assertIsNotNone(self.e._get_metadata(temp_file))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test__get_metadata_returns_expected_type(self):
        self.assertTrue(isinstance(self.e._get_metadata(temp_file), dict))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test__get_metadata_raises_expected_exceptions(self):
        with self.assertRaises(ExtractorError):
            e = ExiftoolMetadataExtractor()
            e._get_metadata(None)

        with self.assertRaises(ExtractorError):
            f = ExiftoolMetadataExtractor()
            f._get_metadata('not_a_file_surely')

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_get_exiftool_data_returns_something(self):
        self.assertIsNotNone(_get_exiftool_data(temp_file))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_get_exiftool_data_returns_expected_type(self):
        self.assertTrue(isinstance(_get_exiftool_data(temp_file), dict))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_get_exiftool_data_raises_expected_exception(self):
        with self.assertRaises(ExtractorError):
            e = ExiftoolMetadataExtractor()
            _get_exiftool_data(None)

        with self.assertRaises(ExtractorError):
            f = ExiftoolMetadataExtractor()
            _get_exiftool_data('not_a_file_surely')

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_returns_something(self):
        self.assertIsNotNone(self.e.execute(temp_file))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_returns_expected_type(self):
        self.assertTrue(isinstance(self.e.execute(temp_file), dict))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_all_result_contains_file_size(self):
        actual = self.e.execute(temp_file)
        self.assertTrue('File:FileSize' in actual)


class TestExiftoolMetadataExtractorWithImage(unittest.TestCase):
    def _to_datetime(self, value):
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

    def setUp(self):
        self.test_file = util.normpath(uu.abspath_testfile('smulan.jpg'))
        self.e = ExiftoolMetadataExtractor()

        self.EXPECT_FIELD_VALUE = [
            ('EXIF:CreateDate', self._to_datetime('2010-01-31 16:12:51')),
            ('EXIF:DateTimeOriginal', self._to_datetime('2010-01-31 16:12:51')),
            ('EXIF:ExifImageHeight', 1944),
            ('EXIF:ExifImageWidth', 2592)
        ]

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_returns_something(self):
        self.assertIsNotNone(self.e.execute(self.test_file))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_returns_expected_type(self):
        self.assertTrue(isinstance(self.e.execute(self.test_file), dict))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_all_result_contains_expected_fields(self):
        actual = self.e.execute(self.test_file)
        for field, _ in self.EXPECT_FIELD_VALUE:
            self.assertTrue(field in actual)

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_all_result_contains_expected_values(self):
        actual_result = self.e.execute(self.test_file)
        for field, value in self.EXPECT_FIELD_VALUE:
            actual = actual_result.get(field)
            self.assertEqual(actual.value, value)
