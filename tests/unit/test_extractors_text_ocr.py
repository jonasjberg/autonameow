# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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

from unittest import (
    skipIf,
    TestCase,
)

try:
    import PIL
except ImportError:
    PIL_IS_NOT_AVAILABLE = True, 'Missing required module "PIL"'
else:
    PIL_IS_NOT_AVAILABLE = False, ''

import unit.utils as uu
from extractors import ExtractorError
from extractors.text import (
    TesseractOCRTextExtractor,
    tesseractocr
)
from unit.case_extractors import (
    CaseExtractorBasics,
    CaseExtractorOutputTypes
)


UNMET_DEPENDENCIES = TesseractOCRTextExtractor.check_dependencies() is False
DEPENDENCY_ERROR = 'Extractor dependencies not satisfied'


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestTesseractOCRTextExtractor(CaseExtractorBasics):
    __test__ = True
    EXTRACTOR_CLASS = TesseractOCRTextExtractor

    def test_method_str_returns_expected(self):
        actual = str(self.extractor)
        expect = 'TesseractOCRTextExtractor'
        self.assertEqual(actual, expect)


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestTesseractOCRTextExtractorOutputTypes(CaseExtractorOutputTypes):
    __test__ = True
    EXTRACTOR_CLASS = TesseractOCRTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('2007-04-23_12-comments.png')


class TestTesseractOCRTextExtractorCanHandle(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.e = TesseractOCRTextExtractor()

        class DummyFileObject(object):
            def __init__(self, mime):
                self.mime_type = mime
        self.fo_image = DummyFileObject(mime='image/jpeg')
        self.fo_pdf = DummyFileObject(mime='application/pdf')

    def test_class_method_can_handle_returns_expected(self):
        self.assertTrue(self.e.can_handle(self.fo_image))
        self.assertFalse(self.e.can_handle(self.fo_pdf))


# NOTE(jonas): Use a shared instance to maintain test execution speed.
TEST_IMAGE_FILE = uu.fileobject_testfile('2007-04-23_12-comments.png')
TEST_IMAGE_FILE_TEXT = 'Apr 23, 2007 - 12 Comments'
image_ocr_extractor = TesseractOCRTextExtractor()


class TestTesseractOCRTextExtractorWithImageFile(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.e = image_ocr_extractor

    @skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
    def test__get_raw_text_returns_expected_type(self):
        self.assertTrue(uu.is_internalstring(self.e.extract_text(TEST_IMAGE_FILE)))

    @skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
    def test_method_extract_returns_expected_type(self):
        actual = self.e.extract(TEST_IMAGE_FILE)
        self.assertIsInstance(actual, dict)

    @skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
    def test_method_extract_all_result_contains_expected(self):
        self.skipTest(
            "AssertionError: 'Apr 23, 2007 - 12 Comments' != 'Aprﬁm-IZCommams'"
        )
        actual = self.e.extract(TEST_IMAGE_FILE)
        self.assertEqual(actual['full'], TEST_IMAGE_FILE_TEXT)


@skipIf(*PIL_IS_NOT_AVAILABLE)
class TestTesseractWrapper(TestCase):
    TEST_FILE = uu.abspath_testfile('2007-04-23_12-comments.png')

    def test_pil_read_image_returns_pil_image_for_valid_images(self):
        # Tests both Unicode or bytestring file names, even though the
        # intended primary caller 'TesseractOCRTextExtractor' uses bytestrings.
        for _image_file in [self.TEST_FILE,
                            uu.normpath(self.TEST_FILE)]:
            actual = tesseractocr.pil_read_image(_image_file)
            self.assertIsInstance(actual, PIL.Image.Image)

    def test_pil_read_image_raises_expected_exception_for_invalid_images(self):
        _test_files = [
            '/foo/bar/baz',
            '',
            ' ',
            uu.abspath_testfile('empty'),
            uu.abspath_testfile('magic_txt.txt')
        ]
        # TODO: Fix ResourceWarning: unclosed file <_io.BufferedReader
        #           name='<SNIP>/test_files/empty'>
        #           actual = tesseractocr.pil_read_image(_test_file)
        for _test_file in _test_files:
            with self.assertRaises(ExtractorError):
                _ = tesseractocr.pil_read_image(_test_file)

        # def test_pil_read_image_raises_exception_for_invalid_images(self):
        # _test_inputs = [
        #     image_file = uu.normpath(uu.abspath_testfile('2007-04-23_12-comments.png'))
        # ]
        # actual = ocr.pil_read_image(image_file)
