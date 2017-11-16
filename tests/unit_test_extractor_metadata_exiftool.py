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

from extractors import ExtractorError
from extractors.metadata import ExiftoolMetadataExtractor
from extractors.metadata.exiftool import (
    _get_exiftool_data,
    is_bad_metadata
)

import unit_utils as uu
import unit_utils_constants as uuconst
from unit_utils_extractors import (
    TestCaseExtractorBasics,
    TestCaseExtractorOutputTypes
)


unmet_dependencies = not ExiftoolMetadataExtractor.check_dependencies()
dependency_error = 'Extractor dependencies not satisfied'


temp_fileobject = uu.get_mock_fileobject()
temp_file = uu.make_temporary_file()


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestExiftoolMetadataExtractorOutputTypes(TestCaseExtractorOutputTypes):
    EXTRACTOR_CLASS = ExiftoolMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('magic_jpg.jpg')


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestExiftoolMetadataExtractor(TestCaseExtractorBasics):
    EXTRACTOR_CLASS = ExiftoolMetadataExtractor

    def test_method_str_returns_expected(self):
        actual = str(self.extractor)
        expect = 'ExiftoolMetadataExtractor'
        self.assertEqual(actual, expect)


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestExiftoolMetadataExtractorInternals(unittest.TestCase):
    def setUp(self):
        self.test_file = uu.fileobject_testfile('smulan.jpg')
        self.e = ExiftoolMetadataExtractor()

    def test__get_metadata_returns_something(self):
        self.assertIsNotNone(self.e._get_metadata(temp_file))

    def test__get_metadata_returns_expected_type(self):
        self.assertTrue(isinstance(self.e._get_metadata(temp_file), dict))

    def test__get_metadata_raises_expected_exceptions(self):
        with self.assertRaises(ExtractorError):
            e = ExiftoolMetadataExtractor()
            e._get_metadata(None)

        with self.assertRaises(ExtractorError):
            f = ExiftoolMetadataExtractor()
            f._get_metadata(uuconst.ASSUMED_NONEXISTENT_BASENAME)

    def test_get_exiftool_data_returns_something(self):
        self.assertIsNotNone(_get_exiftool_data(temp_file))

    def test_get_exiftool_data_returns_expected_type(self):
        self.assertTrue(isinstance(_get_exiftool_data(temp_file), dict))

    def test_get_exiftool_data_raises_expected_exception(self):
        with self.assertRaises(ExtractorError):
            _ = ExiftoolMetadataExtractor()
            _get_exiftool_data(None)

        with self.assertRaises(ExtractorError):
            _ = ExiftoolMetadataExtractor()
            _get_exiftool_data(uuconst.ASSUMED_NONEXISTENT_BASENAME)

    def test_method_extract_returns_something(self):
        self.assertIsNotNone(self.e.extract(temp_fileobject))

    def test_method_extract_all_result_contains_filename(self):
        actual = self.e.extract(temp_fileobject)
        self.assertIn('File:FileName', actual)


class TestExiftoolMetadataExtractorWithImage(unittest.TestCase):
    def _to_datetime(self, value):
        return datetime.strptime(value, '%Y-%m-%d %H:%M:%S')

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def setUp(self):
        self.test_file = uu.fileobject_testfile('smulan.jpg')
        self.e = ExiftoolMetadataExtractor()

        self.EXPECT_FIELD_VALUE = [
            ('EXIF:CreateDate', self._to_datetime('2010-01-31 16:12:51')),
            ('EXIF:DateTimeOriginal', self._to_datetime('2010-01-31 16:12:51')),
            ('EXIF:ExifImageHeight', 1944),
            ('EXIF:ExifImageWidth', 2592)
        ]

        self.actual = self.e.extract(self.test_file)

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_extract_returns_something(self):
        self.assertIsNotNone(self.actual)

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_extract_returns_expected_type(self):
        _actual_extracted = self.actual
        self.assertTrue(isinstance(_actual_extracted, dict))
        for meowuri, datadict in _actual_extracted.items():
            self.assertTrue(isinstance(datadict, dict))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_extract_all_result_contains_expected_fields(self):
        for field, _ in self.EXPECT_FIELD_VALUE:
            self.assertIn(field, self.actual)

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_extract_all_result_contains_expected_values(self):
        for field, expected in self.EXPECT_FIELD_VALUE:
            _actual_datadict = self.actual.get(field)
            _actual_value = _actual_datadict.get('value')
            self.assertEqual(_actual_value, expected)


class TestIsBadMetadata(unittest.TestCase):
    def test_good_tags_values_return_true(self):
        def _aT(tag, value):
            actual = is_bad_metadata(tag, value)
            self.assertFalse(actual)
            self.assertTrue(isinstance(actual, bool))

        _aT('File:FileName', 'gmail.pdf')
        _aT('File:FileSize', 2702410)
        _aT('File:FileModifyDate', '2016:08:28 10:36:30+02:00')
        _aT('File:FileType', 'PDF')
        _aT('XMP:Date', [1918, '2009:08:20'])
        _aT('XMP:Subject', ['Non-Fiction', 'Human Science', 'Philosophy',
                            'Religion', 'Science and Technics', 'Science'])

    def test_bad_tags_values_return_false(self):
        def _aF(tag, value):
            actual = is_bad_metadata(tag, value)
            self.assertTrue(actual)
            self.assertTrue(isinstance(actual, bool))

        _aF('PDF:Subject', 'Subject')
        _aF('PDF:Author', 'Author')
        _aF('PDF:Title', 'Title')
        _aF('XMP:Author', 'Author')
        _aF('XMP:Creator', 'Author')
        _aF('XMP:Creator', 'Creator')
        _aF('XMP:Description', 'Subject')
        _aF('XMP:Description', 'Description')
        _aF('XMP:Subject', 'Subject')
        _aF('XMP:Title', 'Title')
        _aF('XMP:Subject', ['Subject'])
        _aF('XMP:Subject', ['Science', 'Subject'])
        _aF('XMP:Subject', ['Title', 'Subject'])
