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

from core.analyze.analyze_pdf import (
    extract_pdf_content_with_pypdf,
    extract_pdf_content_with_pdftotext
)

from unit_utils import abspath_testfile

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
