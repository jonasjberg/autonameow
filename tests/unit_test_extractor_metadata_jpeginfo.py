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

from extractors import ExtractorError
from extractors.metadata import JpeginfoMetadataExtractor
from extractors.metadata.jpeginfo import _run_jpeginfo
from unit_utils_extractors import (
    TestCaseExtractorBasics,
    TestCaseExtractorOutputTypes
)
import unit_utils as uu


ALL_EXTRACTOR_FIELDS_TYPES = [
    ('health', float),
    ('is_jpeg', bool),
]

unmet_dependencies = not JpeginfoMetadataExtractor.check_dependencies()
dependency_error = 'Extractor dependencies not satisfied'


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestJpeginfoMetadataExtractorOutputTypes(TestCaseExtractorOutputTypes):
    EXTRACTOR_CLASS = JpeginfoMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('magic_jpg.jpg')


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestJpeginfoMetadataExtractor(TestCaseExtractorBasics):
    EXTRACTOR_CLASS = JpeginfoMetadataExtractor

    def test_method_str_returns_expected_value(self):
        actual = str(self.extractor)
        expect = 'JpeginfoMetadataExtractor'
        self.assertEqual(actual, expect)


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestJpeginfoMetadataExtractorWithImageA(unittest.TestCase):
    def setUp(self):
        self.e = JpeginfoMetadataExtractor()
        self.test_file = uu.abspath_testfile('magic_jpg.jpg')
        self.test_fileobject = uu.fileobject_testfile('magic_jpg.jpg')
        self.actual_get_metadata = self.e._get_metadata(self.test_file)
        self.actual_extract = self.e.extract(self.test_fileobject)

    def test__get_metadata_returns_expected_type(self):
        self.assertTrue(isinstance(self.actual_get_metadata, dict))

    def test__get_metadata_raises_expected_exceptions(self):
        with self.assertRaises(ExtractorError):
            e = JpeginfoMetadataExtractor()
            e._get_metadata(None)

        # with self.assertRaises(ExtractorError):
        #     f = JpeginfoMetadataExtractor()
        #     f._get_metadata('not_a_file_surely')

    def test__run_jpeginfo_returns_expected_type(self):
        actual = _run_jpeginfo(self.test_file)
        self.assertTrue(isinstance(actual, str))

    def test__run_jpeginfo_raises_expected_exception(self):
        with self.assertRaises(ExtractorError):
            _run_jpeginfo(None)

        # with self.assertRaises(ExtractorError):
        #     _run_jpeginfo('not_a_file_surely')

    def test_method_extract_returns_expected_type(self):
        self.assertTrue(isinstance(self.actual_extract, dict))


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestJpeginfoMetadataExtractorWithImageB(unittest.TestCase):
    def setUp(self):
        self.test_fileobject = uu.fileobject_testfile('magic_jpg.jpg')
        self.e = JpeginfoMetadataExtractor()
        self.actual = self.e.extract(self.test_fileobject)

    def test_returns_expected_values(self):
        _actual_health = self.actual['health']
        self.assertEqual(_actual_health, 1.0)
        self.assertTrue(isinstance(_actual_health, float))

        _actual_is_jpeg = self.actual['is_jpeg']
        self.assertEqual(_actual_is_jpeg, True)
        self.assertTrue(isinstance(_actual_is_jpeg, bool))


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestJpeginfoMetadataExtractorExtractTestFileJpeg(unittest.TestCase):
    def setUp(self):
        _fo = uu.fileobject_testfile('magic_jpg.jpg')
        _extractor_instance = JpeginfoMetadataExtractor()
        self.actual = _extractor_instance.extract(_fo)

    def test_extract_returns_expected_keys(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn(_field, self.actual)

    def test_extract_returns_expected_values(self):
        def _aE(field, expected):
            actual = self.actual.get(field)
            self.assertEqual(actual, expected)

        _aE('health', 1.0)
        _aE('is_jpeg', True)

    def test_extract_returns_expected_types(self):
        for _field, _type in ALL_EXTRACTOR_FIELDS_TYPES:
            actual = self.actual.get(_field)
            self.assertTrue(
                isinstance(actual, _type),
                'Expected "{!s}" ({!s}) to be of type "{!s}"'.format(
                    actual, type(actual), _type
                )
            )


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestJpeginfoMetadataExtractorMetainfo(unittest.TestCase):
    def setUp(self):
        _extractor_instance = JpeginfoMetadataExtractor()
        self.actual = _extractor_instance.metainfo()

    def test_metainfo_returns_expected_fields(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn(_field, self.actual)

    def test_metainfo_specifies_types_for_all_fields(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn('coercer', self.actual.get(_field, {}))

    def test_metainfo_multiple_is_bool_or_none(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            _field_lookup_entry = self.actual.get(_field, {})
            self.assertIn('multiple', _field_lookup_entry)

            actual = _field_lookup_entry.get('multiple')
            self.assertTrue(isinstance(actual, (bool, type(None))))
