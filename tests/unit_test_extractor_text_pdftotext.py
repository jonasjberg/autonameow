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

from extractors.text import PdftotextTextExtractor
from extractors.text.pdftotext import extract_pdf_content_with_pdftotext
from unit_utils_extractors import (
    CaseExtractorBasics,
    CaseExtractorOutput,
    CaseExtractorOutputTypes
)
import unit_utils as uu


UNMET_DEPENDENCIES = PdftotextTextExtractor.check_dependencies() is False
DEPENDENCY_ERROR = 'Extractor dependencies not satisfied'

# NOTE: It seems that pdftotext strips trailing whitespace on MacOS (v0.57.0)
#       but not on Linux (v0.41.0) --- gives inconsistent test results (?)

TESTFILE_A = uu.abspath_testfile('simplest_pdf.md.pdf')
TESTFILE_A_EXPECTED = '''Probably a title
Text following the title, probably.

Chapter One
First chapter text is missing!

Chapter Two
Second chapter depends on Chapter one ..
Test test. This file contains no digits whatsoever.

1'''

TESTFILE_B = uu.abspath_testfile('magic_pdf.pdf')
TESTFILE_B_EXPECTED = '''KURSPLAN

Akademin för teknik och miljö
Faculty of Engineering and Sustainable Development

Styrteknik med digitalteknik A 7,5 hp
Digital Control Theory 7,5 credits

Fastställd av Akademin för teknik och miljö
Version

Beslutad den
2010-03-15
2012-09-12

Fördjupning

G1N

Utbildningsnivå

Grundnivå

Kurskod

EE467A

Högskolepoäng

7,5 hp

Huvudområde

Elektronik

Ämnesgrupp

Elektronik

Utbildningsområde

Tekniska området 100%

Mål

Gäller fr.o.m.
2010-03-15
2012-11-05

Kursens mål är ett ge grundläggande kunskaper om komponenter utrustningar och metoder
som används inom digitaltekniken och vid styrning av industriella processer samt att ge
laborativa färdigheter och tillräckliga kunskaper för att utföra ett projektarbete med
logikstyrning.
Efter avslutad kurs skall studenten:
1. förstå och kunna analysera och dokumentera fundamentala logiska och enkla
reglertekniska konstruktioner
2. beskriva och använda de teorier och metoder som kursen omfattas av på ett korrekt sätt
3. visa på förståelse för och kunna uttrycka vanligt förekommande typer av beskrivningar av
logiska funktioner och sekvenser.
4. visa förmåga att med hjälp av adekvat metodik lösa uppgifter inom konstruktion och
programmering av logiska system.
5. tillgodogöra sig standardlitteratur inom området (inkl. datablad och liknande information)
6. använda laboratorieutrustning och programmerbara system i tillämplig mån

Kursens innehåll

Kobinatorik och sekvensstyrning
Översikt, grundläggande begrepp och komponenter inom styrning och reglering
Funktionsbeskrivningar
Programmerbara logikenheter
Praktisk reglerteknik
Funktionsbeskrivningar
Praktisk reglerteknik

Sida 1 av 2
Högskolan i Gävle accepterar inte fusk i någon form. Plagiat är en form av fusk, som innebär att du imiterar eller kopierar någon annans arbete, till exempel en text,
en bild eller en tabell, och framställer materialet som ditt eget. Högskolan använder antiplagiatsystem för att förebygga och upptäcka fusk i samband med skriftliga
inlämningsuppgifter.

Sortering och behandling av elektronik för återvinning
Beaktande av miljö- och energiaspekter vid dimensionering av styrsystem
Undervisning

Undervisningen ges i form av föreläsningar/övningar, laborationer samt ett projektarbete.
Laborationerna utförs normalt i grupper om två studenter. Stor vikt läggs vid förberedelser,
genomförandet och redovisningen av laborationerna och projektet. Undervisningen är ej
obligatorisk, med undantag för laborationerna och eventuella obligatoriska uppgifter.

Förkunskaper

Matematik D, Fysik B eller Matematik 3c, Fysik 2, (Områdesbehörighet 8/A8). Undantag
ges för Kemi A eller Kemi 1.

Examinationsform

0030 Tentamen 4,5 hp
0040 Laborationer 1,5 hp
0050 Projekt 1,5 hp

Moment

Saknas

Betyg

A, B, C, D, E, Fx, F

Begränsningar

Skriftlig tentamen ges vid kursens slut. Vid varje kursomgång ges ett ordinarie samt ett
omtentamenstillfälle.
Dessutom erfordras fullgjord laborationskurs och redovisat projektarbete.
Laborationsredovisningarna lämnas in senast en vecka efter ordinarie laborationstillfälle om
annan tid ej meddelats. Den som lämnar in redovisningen senare får vänta på rättning till
nästa kurstillfälle. Icke godkänd redovisning måste omarbetas enligt givna kommentarer.

Hållbar utveckling

Kursen har inslag av hållbar utveckling.

Kurslitteratur

Haag, Bengt (senaste upplagan). Industriell systemteknik. Lund: Studentlitteratur.
Kompendier och utdelat material

Sida 2 av 2
Högskolan i Gävle accepterar inte fusk i någon form. Plagiat är en form av fusk, som innebär att du imiterar eller kopierar någon annans arbete, till exempel en text,
en bild eller en tabell, och framställer materialet som ditt eget. Högskolan använder antiplagiatsystem för att förebygga och upptäcka fusk i samband med skriftliga
inlämningsuppgifter.'''


class TestPrerequisites(unittest.TestCase):
    def test_test_file_exists_a(self):
        self.assertTrue(uu.file_exists(TESTFILE_A))

    def test_test_file_exists_b(self):
        self.assertTrue(uu.file_exists(TESTFILE_B))


@unittest.skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdftotextTextExtractor(CaseExtractorBasics):
    EXTRACTOR_CLASS = PdftotextTextExtractor

    def test_method_str_returns_expected(self):
        actual = str(self.extractor)
        expect = 'PdftotextTextExtractor'
        self.assertEqual(actual, expect)


@unittest.skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdftotextTextExtractorOutputTypes(CaseExtractorOutputTypes):
    EXTRACTOR_CLASS = PdftotextTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile(TESTFILE_A)


@unittest.skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdftotextTextExtractorOutputTestFileA(CaseExtractorOutput):
    EXTRACTOR_CLASS = PdftotextTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile(TESTFILE_A)
    _dt = uu.str_to_datetime
    EXPECTED_FIELD_TYPE_VALUE = [
        ('full', str, TESTFILE_A_EXPECTED),
    ]


@unittest.skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdftotextTextExtractorOutputTestFileB(CaseExtractorOutput):
    EXTRACTOR_CLASS = PdftotextTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile(TESTFILE_B)
    _dt = uu.str_to_datetime
    EXPECTED_FIELD_TYPE_VALUE = [
        ('full', str, TESTFILE_B_EXPECTED),
    ]


@unittest.skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestExtractPdfContentWithPdftotext(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None
        self.actual = extract_pdf_content_with_pdftotext(TESTFILE_A)

    def test_returns_expected_type(self):
        self.assertTrue(uu.is_internalstring(self.actual))

    def test_returns_expected_text(self):
        self.assertEqual(self.actual, TESTFILE_A_EXPECTED)


@unittest.skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdftotextTextExtractorInternals(unittest.TestCase):
    def setUp(self):
        self.test_fileobject = uu.fileobject_testfile('gmail.pdf')
        self.e = PdftotextTextExtractor()

    def test__get_text_returns_something(self):
        actual = self.e.extract_text(self.test_fileobject)
        self.assertIsNotNone(actual)

    def test__get_text_returns_expected_type(self):
        actual = self.e.extract_text(self.test_fileobject)
        self.assertEqual(type(actual), str)

    def test_method_extract_returns_something(self):
        self.assertIsNotNone(self.e.extract(self.test_fileobject))

    def test_method_extract_returns_expected_type(self):
        actual = self.e.extract(self.test_fileobject)
        self.assertTrue(isinstance(actual, dict))


class TestPdftotextTextExtractorCanHandle(unittest.TestCase):
    def setUp(self):
        self.maxDiff = None

        self.e = PdftotextTextExtractor()

        class DummyFileObject(object):
            def __init__(self, mime):
                self.mime_type = mime
        self.fo_image = DummyFileObject(mime='image/jpeg')
        self.fo_pdf = DummyFileObject(mime='application/pdf')

    def test_class_method_can_handle_returns_expected(self):
        self.assertFalse(self.e.can_handle(self.fo_image))
        self.assertTrue(self.e.can_handle(self.fo_pdf))
