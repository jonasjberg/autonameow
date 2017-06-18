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
    PdfTextExtractor,
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


class TestPdfTextExtractor(TestCase):
    def setUp(self):
        self.maxDiff = None

        image = abspath_testfile('gmail.pdf')
        self.e = PdfTextExtractor(image)

        self.EXPECT_TEXT = '''1/11/2016

Gmail - Valkommen till kursen Introduktion till Linux och sma natverk!

Jonas Sjoberg <jomeganas@gmail.com>

Valkommen till kursen Introduktion till Linux och sma natverk!
1 message
Camilla Nordin <Camilla.Nordin@hig.se>
To: Camilla Nordin <Camilla.Nordin@hig.se>

Fri, Jan 8, 2016 at 3:50 PM

Valkommen till Hogskolan i Gavle och kursen Introduktion till Linux och sma natverk
7,5 hp!

Ditt valkomstbrev hittar du har: http://www.hig.se/Ext/Sv/Student/Nystudent/Valkomstbrev/Kurser/
Datateknik.html

LAS DITT VALKOMSTBREV NOGGRANT!

Kursen borjar den 25:e januari men ar oppen for webbregistrering via Studentportalen fran och
med den 18:e januari, se valkomstbrevet.

Atkomstkoden som i vissa fall behovs for inskrivning pa kursen i Blackboard ar: DebianMint

Kursinstansen i Blackboard oppnar den 25:e januari. Observera att du ibland maste soka fram
kursen den forsta gangen du loggar in i Blackboard. Folj instruktionerna i manualen som finns
lankad i valkomstbrevet.

Det finns bra information for nya studenter pa var hemsida: www.hig.se/nystudent

Du behover inte tacka ja eller nej till kursen utan accepterar din plats genom att registrera dig
via Studentportalen.

Lycka till med studierna!

Halsningar Camilla
***************************************************************
Camilla Nordin
Hogskolan i Gavle
Akademin for teknik och miljo
https://mail.google.com/mail/u/0/?ui=2&ik=dbcc4dc2ed&view=pt&q=ny%20student&qs=true&search=query&th=15221b790b7df...

1/2

1/11/2016

Gmail - Valkommen till kursen Introduktion till Linux och sma natverk!

801 76 GAVLE
Tel: 02664 87 46
Fax: 02664 87 58
email: cnn@hig.se
Besoksadress: Kungsbacksvagen 47, rum 12:208

Hogskolan i Gavle, 801 76 Gavle * 026 64 85 00 * www.hig.se
For en hallbar livsmiljo for manniskan
University of Gavle, SE801 76 Gavle, Sweden * +46 (0) 26 64 85 00 * www.hig.se

https://mail.google.com/mail/u/0/?ui=2&ik=dbcc4dc2ed&view=pt&q=ny%20student&qs=true&search=query&th=15221b790b7df...

2/2

'''

    def test_method_query_returns_something(self):
        self.assertIsNotNone(self.e.query())

    def test_method_query_returns_expected_type(self):
        self.assertTrue(isinstance(self.e.query(), str))

    def test_method_query_all_result_contains_expected(self):
        actual = self.e.query()
        self.assertEqual(self.EXPECT_TEXT, actual)

    def test_method_query_arbitrary_field_result_contains_expected(self):
        actual = self.e.query('dummy_field')
        self.assertEqual(self.EXPECT_TEXT, actual)


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
