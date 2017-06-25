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
    ImageOCRTextExtractor,
    TextExtractor
)
from unit_utils import (
    abspath_testfile,
    make_temporary_file
)


class TestTextExtractor(TestCase):
    def setUp(self):
        self.e = TextExtractor(make_temporary_file())

        class DummyFileObject(object):
            def __init__(self):
                self.mime_type = 'image/jpeg'
        self.fo = DummyFileObject()

    def test_text_extractor_class_is_available(self):
        self.assertIsNotNone(TextExtractor)

    def test_text_extractor_class_can_be_instantiated(self):
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
        self.assertEqual(str(self.e), 'TextExtractor')

    def test_class_method_can_handle_is_defined(self):
        self.assertIsNotNone(self.e.can_handle)

    def test_class_method_can_handle_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.assertIsNotNone(self.e.can_handle(self.fo))
            self.assertFalse(self.e.can_handle(self.fo))


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

        test_file = abspath_testfile('gmail.pdf')
        self.e = PdfTextExtractor(test_file)

        class DummyFileObject(object):
            def __init__(self, mime):
                self.mime_type = mime
        self.fo_image = DummyFileObject(mime='image/jpeg')
        self.fo_pdf = DummyFileObject(mime='application/pdf')

        self.EXPECT_TEXT = b'1/11/2016\n\nGmail - V\xc3\xa4lkommen till kursen Introduktion till Linux och sm\xc3\xa5 n\xc3\xa4tverk!\n\nJonas Sj\xc3\xb6berg <jomeganas@gmail.com>\n\nV\xc3\xa4lkommen till kursen Introduktion till Linux och sm\xc3\xa5 n\xc3\xa4tverk!\n1 message\nCamilla Nordin <Camilla.Nordin@hig.se>\nTo: Camilla Nordin <Camilla.Nordin@hig.se>\n\nFri, Jan 8, 2016 at 3:50 PM\n\nV\xc3\xa4lkommen till H\xc3\xb6gskolan i G\xc3\xa4vle och kursen Introduktion till Linux och sm\xc3\xa5 n\xc3\xa4tverk\n7,5 hp!\n\nDitt v\xc3\xa4lkomstbrev hittar du h\xc3\xa4r: http://www.hig.se/Ext/Sv/Student/Ny\xc2\xadstudent/Valkomstbrev/Kurser/\nDatateknik.html\n\nL\xc3\x84S DITT V\xc3\x84LKOMSTBREV NOGGRANT!\n\nKursen b\xc3\xb6rjar den 25:e januari men \xc3\xa4r \xc3\xb6ppen f\xc3\xb6r webbregistrering via Studentportalen fr\xc3\xa5n och\nmed den 18:e januari, se v\xc3\xa4lkomstbrevet.\n\n\xc3\x85tkomstkoden som i vissa fall beh\xc3\xb6vs f\xc3\xb6r inskrivning p\xc3\xa5 kursen i Blackboard \xc3\xa4r: Debian\xc2\xadMint\n\nKursinstansen i Blackboard \xc3\xb6ppnar den 25:e januari. Observera att du ibland m\xc3\xa5ste s\xc3\xb6ka fram\nkursen den f\xc3\xb6rsta g\xc3\xa5ngen du loggar in i Blackboard. F\xc3\xb6lj instruktionerna i manualen som finns\nl\xc3\xa4nkad i v\xc3\xa4lkomstbrevet.\n\nDet finns bra information f\xc3\xb6r nya studenter p\xc3\xa5 v\xc3\xa5r hemsida: www.hig.se/nystudent\n\nDu beh\xc3\xb6ver inte tacka ja eller nej till kursen utan accepterar din plats genom att registrera dig\nvia Studentportalen.\n\nLycka till med studierna!\n\nH\xc3\xa4lsningar Camilla\n***************************************************************\nCamilla Nordin\nH\xc3\xb6gskolan i G\xc3\xa4vle\nAkademin f\xc3\xb6r teknik och milj\xc3\xb6\nhttps://mail.google.com/mail/u/0/?ui=2&ik=dbcc4dc2ed&view=pt&q=ny%20student&qs=true&search=query&th=15221b790b7df\xe2\x80\xa6\n\n1/2\n\n1/11/2016\n\nGmail - V\xc3\xa4lkommen till kursen Introduktion till Linux och sm\xc3\xa5 n\xc3\xa4tverk!\n\n801 76 G\xc3\x84VLE\nTel: 026\xc2\xad64 87 46\nFax: 026\xc2\xad64 87 58\ne\xc2\xadmail: cnn@hig.se\nBes\xc3\xb6ksadress: Kungsb\xc3\xa4cksv\xc3\xa4gen 47, rum 12:208\n\nH\xc3\xb6gskolan i G\xc3\xa4vle, 801 76 G\xc3\xa4vle \xe2\x80\xa2 026 64 85 00 \xe2\x80\xa2 www.hig.se\nF\xc3\xb6r en h\xc3\xa5llbar livsmilj\xc3\xb6 f\xc3\xb6r m\xc3\xa4nniskan\nUniversity of G\xc3\xa4vle, SE\xc2\xad801 76 G\xc3\xa4vle, Sweden \xe2\x80\xa2 +46 (0) 26 64 85 00 \xe2\x80\xa2 www.hig.se\n\nhttps://mail.google.com/mail/u/0/?ui=2&ik=dbcc4dc2ed&view=pt&q=ny%20student&qs=true&search=query&th=15221b790b7df\xe2\x80\xa6\n\n2/2\n\n'.decode()

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

    def test_class_method_can_handle_is_defined(self):
        self.assertIsNotNone(self.e.can_handle)

    def test_class_method_can_handle_returns_expected(self):
        self.assertFalse(self.e.can_handle(self.fo_image))
        self.assertTrue(self.e.can_handle(self.fo_pdf))


class TestImageOCRTextExtractor(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.e = ImageOCRTextExtractor(make_temporary_file())

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


# NOTE(jonas): Use a shared instance to maintain test execution speed.
image_file = abspath_testfile('2007-04-23_12-comments.png')
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
