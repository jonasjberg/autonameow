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
import unit_utils as uu


unmet_dependencies = not JpeginfoMetadataExtractor.check_dependencies()
dependency_error = 'Extractor dependencies not satisfied'


class TestJpeginfoMetadataExtractor(unittest.TestCase):
    def setUp(self):
        self.e = JpeginfoMetadataExtractor()

    def test_extractor_class_is_available(self):
        self.assertIsNotNone(JpeginfoMetadataExtractor)

    def test_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_specifies_handles_mime_types(self):
        self.assertIsNotNone(self.e.HANDLES_MIME_TYPES)
        self.assertTrue(isinstance(self.e.HANDLES_MIME_TYPES, list))

    def test_method_str_returns_expected(self):
        self.assertEqual(str(self.e), 'JpeginfoMetadataExtractor')


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestJpeginfoMetadataExtractorWithImageA(unittest.TestCase):
    def setUp(self):
        self.e = JpeginfoMetadataExtractor()
        self.test_file = uu.abspath_testfile('magic_jpg.jpg')
        self.test_fileobject = uu.fileobject_testfile('magic_jpg.jpg')
        self.actual_get_metadata = self.e._get_metadata(self.test_file)
        self.actual_execute = self.e.execute(self.test_fileobject)

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

    def test_method_execute_returns_expected_type(self):
        self.assertTrue(isinstance(self.actual_execute, dict))


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestJpeginfoMetadataExtractorWithImageB(unittest.TestCase):
    def setUp(self):
        self.test_fileobject = uu.fileobject_testfile('magic_jpg.jpg')
        self.e = JpeginfoMetadataExtractor()
        self.actual_call = self.e(self.test_fileobject)
        self.actual_execute = self.e.execute(self.test_fileobject)

    def test_call_returns_expected_type(self):
        self.assertTrue(isinstance(self.actual_call, dict))

    def test_call_returns_expected_contents(self):
        actual_health = self.actual_execute['health'].value
        self.assertEqual(actual_health, 1.0)
        self.assertTrue(isinstance(actual_health, float))

        actual_is_jpeg = self.actual_execute['is_jpeg'].value
        self.assertEqual(actual_is_jpeg, True)
        self.assertTrue(isinstance(actual_is_jpeg, bool))
