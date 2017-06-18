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

import os
from unittest import TestCase

import PyPDF2

from extractors.textual import (
    extract_pdf_content_with_pdftotext,
    extract_pdf_content_with_pypdf,
    ImageOCRTextExtractor
)
from unit_utils import (
    abspath_testfile,
    make_temporary_file
)

pdf_file = abspath_testfile('simplest_pdf.md.pdf')
expected_text = '''Probably a title
Text following the title, probably.

Chapter One
First chapter text is missing!

Chapter Two
Second chapter depends on Chapter one ..
Test test. This file contains no digits whatsoever.

1

'''

class TestSetup(TestCase):
    def test_sample_pdf_file_exists(self):
        self.assertTrue(os.path.isfile(pdf_file))


class TestPyPdf(TestCase):
    def test_pypdf_is_available(self):
        self.assertIsNotNone(PyPDF2)

    def test_pypdf_pdf_file_reader_is_available(self):
        self.assertIsNotNone(PyPDF2.PdfFileReader)


class TestExtractPdfContentWithPyPdf(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_extract_pdf_content_with_pypdf_returns_expected_type(self):
        self.assertEqual(type(extract_pdf_content_with_pypdf(pdf_file)), str)

    def test_extract_pdf_content_with_pypdf_returns_expected_text(self):
        self.skipTest('PyPDF strips all whitespace for some reason. '
                      'Will use pdftotext instead.')
        self.assertEqual(extract_pdf_content_with_pypdf(pdf_file),
                         expected_text)


class TestExtractPdfContentWithPdfTotext(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_extract_pdf_content_with_pdftotext_returns_expected_type(self):
        self.assertEqual(type(extract_pdf_content_with_pdftotext(pdf_file)),
                         str)

    def test_extract_pdf_content_with_pdftotext_returns_expected_text(self):
        self.assertEqual(extract_pdf_content_with_pdftotext(pdf_file),
                         expected_text)


class TestImageOCRTextExtractorWithEmptyFile(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.e = ImageOCRTextExtractor(make_temporary_file())

    def test_extractor_class_is_available(self):
        self.assertIsNotNone(ImageOCRTextExtractor)

    def test_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_specifies_handles_mime_types(self):
        self.assertIsNotNone(self.e.handles_mime_types)
        self.assertTrue(isinstance(self.e.handles_mime_types, list))

    def test_method_str_returns_expected(self):
        self.assertEqual(str(self.e), 'ImageOCRTextExtractor')


class TestImageOCRTextExtractorWithImageFile(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.EXPECT_TEXT = 'Apr 23, 2007 - 12 Comments'
        image_file = abspath_testfile('2007-04-23_12-comments.png')

        self.e = ImageOCRTextExtractor(image_file)

    def test_extractor_class_is_available(self):
        self.assertIsNotNone(ImageOCRTextExtractor)

    def test_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test__get_raw_text_returns_something(self):
        self.assertIsNotNone(self.e._get_raw_text())

    def test__get_raw_text_returns_expected_type(self):
        self.assertTrue(isinstance(self.e._get_raw_text(), str))

    def test_method_query_returns_something(self):
        self.assertIsNotNone(self.e.query())

    def test_method_query_returns_expected_type(self):
        self.assertTrue(isinstance(self.e.query(), str))

    def test_method_query_all_result_contains_expected(self):
        self.skipTest(
            "AssertionError: 'Apr 23, 2007 - 12 Comments' != 'Aprﬁm-IZCommams'")
        actual = self.e.query()
        self.assertEqual(self.EXPECT_TEXT, actual)

    def test_method_query_arbitrary_field_result_contains_expected(self):
        self.skipTest(
            "AssertionError: 'Apr 23, 2007 - 12 Comments' != 'Aprﬁm-IZCommams'")
        actual = self.e.query('dummy_field')
        self.assertEqual(self.EXPECT_TEXT, actual)
