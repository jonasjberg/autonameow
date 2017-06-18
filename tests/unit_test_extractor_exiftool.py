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

from core.exceptions import ExtractorError
from extractors.metadata import ExiftoolMetadataExtractor
from unit_utils import (
    make_temporary_file,
    abspath_testfile
)

E = ExiftoolMetadataExtractor(make_temporary_file())


class TestExiftoolMetadataExtractor(TestCase):
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

    def test__get_raw_metadata_returns_something(self):
        self.assertIsNotNone(self.e._get_raw_metadata())

    def test__get_raw_metadata_returns_expected_type(self):
        self.assertTrue(isinstance(self.e._get_raw_metadata(), dict))

    def test__get_raw_metadata_raises_expected_exceptions(self):
        with self.assertRaises(ExtractorError):
            e = ExiftoolMetadataExtractor(None)
            e._get_raw_metadata()
            f = ExiftoolMetadataExtractor('not_a_file_surely')
            f._get_raw_metadata()

    def test_get_exiftool_data_returns_something(self):
        self.assertIsNotNone(self.e.get_exiftool_data())

    def test_get_exiftool_data_returns_expected_type(self):
        self.assertTrue(isinstance(self.e.get_exiftool_data(), dict))

    def test_get_exiftool_data_raises_expected_exceptions(self):
        with self.assertRaises((AttributeError, ValueError, TypeError)):
            e = ExiftoolMetadataExtractor(None)
            e.get_exiftool_data()
            f = ExiftoolMetadataExtractor('not_a_file_surely')
            f.get_exiftool_data()

    def test_method_query_returns_something(self):
        self.assertIsNotNone(self.e.query())

    def test_method_query_returns_expected_type(self):
        self.assertTrue(isinstance(self.e.query(), dict))

    def test_method_query_all_result_contains_file_size(self):
        actual = self.e.query()
        self.assertTrue('File:FileSize' in actual)

    def test_method_query_file_size_returns_expected(self):
        actual = self.e.query('File:FileSize')
        self.assertEqual(actual, 0)

    def test_method_query_result_file_size_is_zero(self):
        self.assertEqual(self.e.query('File:FileSize'), 0)


class TestExiftoolMetadataExtractorWithImage(TestCase):
    def setUp(self):
        image = abspath_testfile('smulan.jpg')
        self.e = ExiftoolMetadataExtractor(image)

        self.EXPECT_FIELD_VALUE = [
            ('EXIF:CreateDate', '2010:01:31 16:12:51'),
            ('EXIF:DateTimeOriginal', '2010:01:31 16:12:51'),
            ('EXIF:ExifImageHeight', 1944),
            ('EXIF:ExifImageWidth', 2592)
        ]

    def test_method_query_returns_something(self):
        self.assertIsNotNone(self.e.query())

    def test_method_query_returns_expected_type(self):
        self.assertTrue(isinstance(self.e.query(), dict))

    def test_method_query_all_result_contains_expected_fields(self):
        actual = self.e.query()
        for field, _ in self.EXPECT_FIELD_VALUE:
            self.assertTrue(field in actual)

    def test_method_query_all_result_contains_expected_values(self):
        actual = self.e.query()
        for field, value in self.EXPECT_FIELD_VALUE:
            self.assertEqual(actual.get(field), value)

    def test_method_query_field_returns_expected_value(self):
        for field, value in self.EXPECT_FIELD_VALUE:
            actual = self.e.query(field)
            self.assertEqual(actual, value)
