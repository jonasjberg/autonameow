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

from core import util
from extractors.textual import (
    extract_pdf_content_with_pdftotext,
    extract_pdf_content_with_pypdf,
    PdfTextExtractor,
    ImageOCRTextExtractor,
    AbstractTextExtractor
)
import unit_utils as uu


class TestAbstractTextExtractor(TestCase):
    def setUp(self):
        self.e = AbstractTextExtractor(uu.make_temporary_file())

        class DummyFileObject(object):
            def __init__(self):
                self.mime_type = 'image/jpeg'
        self.fo = DummyFileObject()

    def test_abstract_text_extractor_class_is_available(self):
        self.assertIsNotNone(AbstractTextExtractor)

    def test_abstract_text_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_method_query_returns_something(self):
        self.assertIsNotNone(self.e.query())
        self.assertIsNotNone(self.e.query(field='some_field'))

    def test_method_str_is_defined_and_reachable(self):
        self.assertIsNotNone(str(self.e))
        self.assertIsNotNone(self.e.__str__)

    def test_method_str_returns_type_string(self):
        self.assertTrue(isinstance(str(self.e), str))
        self.assertTrue(isinstance(str(self.e.__str__), str))

    def test_method_str_returns_expected(self):
        self.assertEqual(str(self.e), 'AbstractTextExtractor')

    def test_class_method_can_handle_is_defined(self):
        self.assertIsNotNone(self.e.can_handle)

    def test_class_method_can_handle_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.assertIsNotNone(self.e.can_handle(self.fo))
            self.assertFalse(self.e.can_handle(self.fo))


pdf_file = uu.abspath_testfile('simplest_pdf.md.pdf')
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

        test_file = util.normpath(uu.abspath_testfile('gmail.pdf'))
        self.e = PdfTextExtractor(test_file)

        class DummyFileObject(object):
            def __init__(self, mime):
                self.mime_type = mime
        self.fo_image = DummyFileObject(mime='image/jpeg')
        self.fo_pdf = DummyFileObject(mime='application/pdf')

        self.EXPECT_TEXT = '''1/11/2016

Gmail - Välkommen till kursen Introduktion till Linux och små nätverk!

Jonas Sjöberg <jomeganas@gmail.com>

Välkommen till kursen Introduktion till Linux och små nätverk! 
1 message
Camilla Nordin <Camilla.Nordin@hig.se>
To: Camilla Nordin <Camilla.Nordin@hig.se>

Fri, Jan 8, 2016 at 3:50 PM

Välkommen till Högskolan i Gävle och kursen Introduktion till Linux och små nätverk
7,5 hp!
 
Ditt välkomstbrev hittar du här: http://www.hig.se/Ext/Sv/Student/Ny­student/Valkomstbrev/Kurser/
Datateknik.html
 
LÄS DITT VÄLKOMSTBREV NOGGRANT!
 
Kursen börjar den 25:e januari men är öppen för webbregistrering via Studentportalen från och
med den 18:e januari, se välkomstbrevet.
 
Åtkomstkoden som i vissa fall behövs för inskrivning på kursen i Blackboard är: Debian­Mint
 
Kursinstansen i Blackboard öppnar den 25:e januari. Observera att du ibland måste söka fram
kursen  den första gången du loggar in i Blackboard. Följ instruktionerna i manualen som finns
länkad i välkomstbrevet.
 
Det finns bra information för nya studenter på vår hemsida: www.hig.se/nystudent
 
Du behöver inte tacka ja eller nej till kursen utan accepterar din plats genom att registrera dig
via Studentportalen.
 
Lycka till med studierna!
 

Hälsningar Camilla 
*************************************************************** 
Camilla Nordin 
Högskolan i Gävle 
Akademin för teknik och miljö 
https://mail.google.com/mail/u/0/?ui=2&ik=dbcc4dc2ed&view=pt&q=ny%20student&qs=true&search=query&th=15221b790b7df…

1/2

1/11/2016

Gmail - Välkommen till kursen Introduktion till Linux och små nätverk!

801 76 GÄVLE 
Tel: 026­64 87 46 
Fax: 026­64 87 58 
e­mail: cnn@hig.se 
Besöksadress: Kungsbäcksvägen 47, rum 12:208
 

Högskolan i Gävle, 801 76 Gävle • 026 64 85 00 • www.hig.se
För en hållbar livsmiljö för människan
University of Gävle, SE­801 76 Gävle, Sweden • +46 (0) 26 64 85 00 • www.hig.se

https://mail.google.com/mail/u/0/?ui=2&ik=dbcc4dc2ed&view=pt&q=ny%20student&qs=true&search=query&th=15221b790b7df…

2/2

'''

    def test_method_query_returns_something(self):
        self.assertIsNotNone(self.e.query())

    def test_method_query_returns_expected_type(self):
        self.assertTrue(isinstance(self.e.query(), str))

    def test_method_query_all_result_contains_expected(self):
        self.skipTest('Fix expected text encoding issue')
        actual = self.e.query()
        self.assertEqual(self.EXPECT_TEXT, actual)

    def test_method_query_arbitrary_field_result_contains_expected(self):
        self.skipTest('Fix expected text encoding issue')
        actual = self.e.query('dummy_field')
        self.assertEqual(self.EXPECT_TEXT, actual)

    def test_class_method_can_handle_is_defined(self):
        self.assertIsNotNone(self.e.can_handle)

    def test_class_method_can_handle_returns_expected(self):
        self.assertFalse(self.e.can_handle(self.fo_image))
        self.assertTrue(self.e.can_handle(self.fo_pdf))


class TestImageOCRTextExtractor(TestCase):
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


class TestImageOCRTextExtractorWithEmptyFile(TestCase):
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


class TestImageOCRTextExtractorWithImageFile(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.EXPECT_TEXT = 'Apr 23, 2007 - 12 Comments'

        self.e = image_ocr_extractor

    def test_extractor_class_is_available(self):
        self.assertIsNotNone(ImageOCRTextExtractor)

    def test_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test__get_raw_text_returns_expected_type(self):
        self.assertTrue(isinstance(self.e._get_raw_text(), str))

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
