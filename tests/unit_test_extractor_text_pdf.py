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
from extractors.text import PdfTextExtractor
from extractors.text.pdf import (
    extract_pdf_content_with_pdftotext,
    extract_pdf_content_with_pypdf
)
import unit_utils as uu


unmet_dependencies = PdfTextExtractor.check_dependencies() is False
dependency_error = 'Extractor dependencies not satisfied'


class TestExtractPdfContentWithPdfTotext(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_extract_pdf_content_with_pdftotext_returns_expected_type(self):
        self.assertEqual(type(extract_pdf_content_with_pdftotext(pdf_file)),
                         str)

    def test_extract_pdf_content_with_pdftotext_returns_expected_text(self):
        self.assertEqual(extract_pdf_content_with_pdftotext(pdf_file),
                         expected_text)


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


class TestSetup(unittest.TestCase):
    def test_sample_pdf_file_exists(self):
        self.assertTrue(uu.file_exists(pdf_file))


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestExtractPdfContentWithPyPdf(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_extract_pdf_content_with_pypdf_returns_expected_type(self):
        self.assertEqual(type(extract_pdf_content_with_pypdf(pdf_file)), str)

    def test_extract_pdf_content_with_pypdf_returns_expected_text(self):
        self.skipTest('PyPDF strips all whitespace for some reason. '
                      'Will use pdftotext instead.')
        self.assertEqual(extract_pdf_content_with_pypdf(pdf_file),
                         expected_text)


class TestPdfTextExtractor(unittest.TestCase):
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

    def test_pdf_text_extractor_class_is_available(self):
        self.assertIsNotNone(PdfTextExtractor)

    def test_pdf_text_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test__get_raw_text_returns_something(self):
        self.assertIsNotNone(self.e._get_text())

    def test__get_raw_text_returns_expected_type(self):
        self.assertEqual(type(self.e._get_text()), str)

    def test_method_execute_returns_something(self):
        self.assertIsNotNone(self.e.execute())

    def test_method_execute_returns_expected_type(self):
        actual = self.e.execute()
        self.assertTrue(isinstance(actual.value, str))

    def test_method_execute_all_result_contains_expected(self):
        self.skipTest('Fix expected text encoding issue')
        actual = self.e.execute()
        self.assertEqual(actual.value, self.EXPECT_TEXT)

    def test_method_execute_arbitrary_field_result_contains_expected(self):
        self.skipTest('Fix expected text encoding issue')
        actual = self.e.execute(field='dummy_field')
        self.assertEqual(actual.value, self.EXPECT_TEXT)

    def test_class_method_can_handle_is_defined(self):
        self.assertIsNotNone(self.e.can_handle)

    def test_class_method_can_handle_returns_expected(self):
        self.assertFalse(self.e.can_handle(self.fo_image))
        self.assertTrue(self.e.can_handle(self.fo_pdf))
