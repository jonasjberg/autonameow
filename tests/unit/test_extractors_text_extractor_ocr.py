# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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

from unittest import skipIf, TestCase

try:
    import PIL
except ImportError:
    PIL_IS_NOT_AVAILABLE = True, 'Missing required module "PIL"'
else:
    PIL_IS_NOT_AVAILABLE = False, ''

import unit.utils as uu
from extractors import ExtractorError
from extractors.text.extractor_ocr import pil_read_image
from extractors.text.extractor_ocr import TesseractOCRTextExtractor
from unit.case_extractors_text import CaseTextExtractorBasics
from unit.case_extractors_text import CaseTextExtractorOutputTypes


UNMET_DEPENDENCIES = (
    not TesseractOCRTextExtractor.dependencies_satisfied(),
    'Extractor dependencies not satisfied'
)

SAMPLEFILE_A = uu.samplefile_abspath('2007-04-23_12-comments.png')


class TestPrerequisites(TestCase):
    def test_samplefile_a_exists(self):
        self.assertTrue(uu.file_exists(SAMPLEFILE_A))


@skipIf(*UNMET_DEPENDENCIES)
class TestTesseractOCRTextExtractor(CaseTextExtractorBasics, TestCase):
    EXTRACTOR_CLASS = TesseractOCRTextExtractor
    EXTRACTOR_NAME = 'TesseractOCRTextExtractor'


@skipIf(*UNMET_DEPENDENCIES)
class TestTesseractOCRTextExtractorOutputTypes(CaseTextExtractorOutputTypes,
                                               TestCase):
    EXTRACTOR_CLASS = TesseractOCRTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_from_filepath(SAMPLEFILE_A)


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


@skipIf(*UNMET_DEPENDENCIES)
class TestTesseractOCRTextExtractorWithImageFile(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None
        cls.SAMPLEFILE_IMAGE = uu.fileobject_from_samplefile('2007-04-23_12-comments.png')
        cls.SAMPLEFILE_IMAGE_TEXT = 'Apr 23, 2007 - 12 Comments'

        cls.e = TesseractOCRTextExtractor()
        # Disable the cache
        cls.e.cache = None

    def test__extract_text_returns_expected_type(self):
        actual = self.e._extract_text(self.SAMPLEFILE_IMAGE)
        self.assertTrue(uu.is_internalstring(actual))

    def test__extract_text_returns_expected_text(self):
        actual = self.e._extract_text(self.SAMPLEFILE_IMAGE)
        self.assertIn(self.SAMPLEFILE_IMAGE_TEXT, actual)


@skipIf(*PIL_IS_NOT_AVAILABLE)
class TestTesseractWrapper(TestCase):
    SAMPLEFILE = uu.samplefile_abspath('2007-04-23_12-comments.png')

    def test_pil_read_image_returns_pil_image_for_valid_images(self):
        # Tests both Unicode or bytestring file names, even though the
        # intended primary caller 'TesseractOCRTextExtractor' uses bytestrings.
        for _image_file in [self.SAMPLEFILE,
                            uu.normpath(self.SAMPLEFILE)]:
            actual = pil_read_image(_image_file)
            self.assertIsInstance(actual, PIL.Image.Image)

    def test_pil_read_image_raises_expected_exception_for_invalid_images(self):
        _samplefiles = [
            '/foo/bar/baz',
            '',
            ' ',
            uu.samplefile_abspath('empty'),
            uu.samplefile_abspath('magic_txt.txt')
        ]
        # TODO: Fix ResourceWarning: unclosed file <_io.BufferedReader
        #           name='<SNIP>/tests/samplefiles/empty'>
        #           actual = tesseractocr.pil_read_image(_samplefile)
        for samplefile in _samplefiles:
            with self.assertRaises(ExtractorError):
                _ = pil_read_image(samplefile)
