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

from core import util
from extractors import ExtractorError
from extractors.text import (
    ImageOCRTextExtractor,
    ocr
)
import unit_utils as uu


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
TEST_IMAGE_FILE = util.normpath(
    uu.abspath_testfile('2007-04-23_12-comments.png')
)
TEST_IMAGE_FILE_TEXT = 'Apr 23, 2007 - 12 Comments'
image_ocr_extractor = ImageOCRTextExtractor(TEST_IMAGE_FILE)


class TestImageOCRTextExtractorWithImageFile(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
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
            "AssertionError: 'Apr 23, 2007 - 12 Comments' != 'Aprﬁm-IZCommams'"
        )
        actual = self.e.execute()
        self.assertEqual(TEST_IMAGE_FILE_TEXT, actual)

    @unittest.skipIf(unmet_dependencies, dependency_error)
    def test_method_execute_arbitrary_field_result_contains_expected(self):
        self.skipTest(
            "AssertionError: 'Apr 23, 2007 - 12 Comments' != 'Aprﬁm-IZCommams'"
        )
        actual = self.e.execute(field='dummy_field')
        self.assertEqual(TEST_IMAGE_FILE_TEXT, actual)


class TestTesseractWrapper(unittest.TestCase):
    TEST_FILE = uu.abspath_testfile('2007-04-23_12-comments.png')

    def test_pil_read_image_returns_pil_image_for_valid_images(self):
        import PIL

        # Tests both Unicode or bytestring file names, even though the
        # intended primary caller 'ImageOCRTextExtractor' uses bytestrings.
        for _image_file in [self.TEST_FILE,
                            util.normpath(self.TEST_FILE)]:
            actual = ocr.pil_read_image(_image_file)
            self.assertTrue(isinstance(actual, PIL.Image.Image))

    def test_pil_read_image_raises_expected_exception_for_invalid_images(self):
        _test_files = [
            '/foo/bar/baz',
            '',
            ' ',
            uu.abspath_testfile('empty'),
            uu.abspath_testfile('magic_txt.txt')
        ]
        for _test_file in _test_files:
            with self.assertRaises(ExtractorError):
                actual = ocr.pil_read_image(_test_file)


            #def test_pil_read_image_raises_exception_for_invalid_images(self):
        #_test_inputs = [
        #    image_file = util.normpath(uu.abspath_testfile('2007-04-23_12-comments.png'))
        #]
        #actual = ocr.pil_read_image(image_file)
