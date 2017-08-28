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

import unit_utils as uu
from core import util
from extractors.text import ImageOCRTextExtractor

unmet_dependencies = ImageOCRTextExtractor.check_dependencies() is False
dependency_error = 'Extractor dependencies not satisfied'


class TestImageOCRTextExtractor(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.e = ImageOCRTextExtractor(uu.make_temporary_file())

        class DummyFileObject(object):
            def __init__(self, mime):
                self.mime_type = mime
        self.fo_image = DummyFileObject(mime='image/jpeg')
        self.fo_pdf = DummyFileObject(mime='application/pdf')

    def test_class_method_can_handle_is_defined(self):
        self.assertIsNotNone(self.e.can_handle)

    def test_class_method_can_handle_returns_expected(self):
        self.assertTrue(self.e.can_handle(self.fo_image))
        self.assertFalse(self.e.can_handle(self.fo_pdf))


class TestImageOCRTextExtractorWithEmptyFile(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.e = ImageOCRTextExtractor(uu.make_temporary_file())

    def test_extractor_class_is_available(self):
        self.assertIsNotNone(ImageOCRTextExtractor)

    def test_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_specifies_handles_mime_types(self):
        self.assertIsNotNone(self.e.handles_mime_types)
        self.assertTrue(isinstance(self.e.handles_mime_types, list))

    def test_method_str_returns_expected(self):
        self.assertEqual(str(self.e), 'ImageOCRTextExtractor')


# NOTE(jonas): Use a shared instance to maintain test execution speed.
image_file = util.normpath(uu.abspath_testfile('2007-04-23_12-comments.png'))
image_ocr_extractor = ImageOCRTextExtractor(image_file)


class TestImageOCRTextExtractorWithImageFile(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.EXPECT_TEXT = 'Apr 23, 2007 - 12 Comments'

        self.e = image_ocr_extractor

    def test_extractor_class_is_available(self):
        self.assertIsNotNone(ImageOCRTextExtractor)

    def test_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test__get_raw_text_returns_expected_type(self):
        self.assertTrue(isinstance(self.e._get_raw_text(), str))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_returns_expected_type(self):
        self.assertTrue(isinstance(self.e.execute(), str))

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_all_result_contains_expected(self):
        self.skipTest(
            "AssertionError: 'Apr 23, 2007 - 12 Comments' != 'Aprﬁm-IZCommams'")
        actual = self.e.execute()
        self.assertEqual(self.EXPECT_TEXT, actual)

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_arbitrary_field_result_contains_expected(self):
        self.skipTest(
            "AssertionError: 'Apr 23, 2007 - 12 Comments' != 'Aprﬁm-IZCommams'")
        actual = self.e.execute(field='dummy_field')
        self.assertEqual(self.EXPECT_TEXT, actual)
