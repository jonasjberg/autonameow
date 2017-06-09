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
from extractors.metadata import (
    MetadataExtractor,
    ExiftoolMetadataExtractor
)
from unit_utils import make_temporary_file


class TestMetadataExtractor(TestCase):
    def setUp(self):
        self.e = MetadataExtractor(make_temporary_file())

    def test_metadata_extractor_class_is_available(self):
        self.assertIsNotNone(MetadataExtractor)

    def test_metadata_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_method__get_raw_metadata_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e._get_raw_metadata()

    def test_query_returns_false_without__get_raw_metadata_implemented(self):
        self.assertFalse(self.e.query())
        self.assertFalse(self.e.query(field='some_field'))


class TestExiftoolMetadataExtractor(TestCase):
    def setUp(self):
        self.e = ExiftoolMetadataExtractor(make_temporary_file())

    def test_exiftool_metadata_extractor_class_is_available(self):
        self.assertIsNotNone(ExiftoolMetadataExtractor)

    def test_exiftool_metadata_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

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
