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

import time
from unittest import (
    skipIf,
    TestCase,
)

import unit.utils as uu
from extractors.text import PdftotextTextExtractor
from extractors.text.pdftotext import extract_pdf_content_with_pdftotext
from unit.case_extractors import (
    CaseExtractorBasics,
    CaseExtractorOutput,
    CaseExtractorOutputTypes
)


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


class TestPrerequisites(TestCase):
    def test_test_file_exists_a(self):
        self.assertTrue(uu.file_exists(TESTFILE_A))

    def test_test_file_exists_b(self):
        self.assertTrue(uu.file_exists(TESTFILE_B))


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdftotextTextExtractor(CaseExtractorBasics):
    __test__ = True
    EXTRACTOR_CLASS = PdftotextTextExtractor

    def test_method_str_returns_expected(self):
        actual = str(self.extractor)
        expect = 'PdftotextTextExtractor'
        self.assertEqual(actual, expect)


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdftotextTextExtractorOutputTypes(CaseExtractorOutputTypes):
    __test__ = True
    EXTRACTOR_CLASS = PdftotextTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile(TESTFILE_A)


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdftotextTextExtractorOutputTestFileA(CaseExtractorOutput):
    __test__ = True
    EXTRACTOR_CLASS = PdftotextTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile(TESTFILE_A)
    _dt = uu.str_to_datetime
    EXPECTED_FIELD_TYPE_VALUE = [
        ('full', str, TESTFILE_A_EXPECTED),
    ]


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdftotextTextExtractorOutputTestFileB(CaseExtractorOutput):
    __test__ = True
    EXTRACTOR_CLASS = PdftotextTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile(TESTFILE_B)
    _dt = uu.str_to_datetime
    EXPECTED_FIELD_TYPE_VALUE = [
        ('full', str, TESTFILE_B_EXPECTED),
    ]


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestCachingRuntime(TestCase):
    """
    These will likely fail on some systems. The idea is to make sure that
    the caching system works as intended for an actual use-case. The timing
    thresholds are arbitrarily chosen and should be tweaked if these tests
    fail on other systems.

    Just make sure that the caching does not make the extraction SLOWER!
    """
    @classmethod
    def setUpClass(cls):
        source_a = uu.fileobject_testfile(TESTFILE_A)
        source_b = uu.fileobject_testfile(TESTFILE_B)

        # Patch to disable caching.
        # "Should" be equivalent to not calling 'init_cache()' in '__init__()'.
        e_no_cache = PdftotextTextExtractor()
        e_no_cache.cache = None

        start_time = time.time()
        _ = e_no_cache.extract(source_a)
        _ = e_no_cache.extract(source_b)
        runtime_cache_disabled = time.time() - start_time

        # Enable caching.
        e_cached = PdftotextTextExtractor()
        e_cached.init_cache()

        start_time = time.time()
        _ = e_cached.extract(source_a)
        _ = e_cached.extract(source_b)
        runtime_cache_enabled = time.time() - start_time

    def test_sanity_check_runtime_cache_disabled(self):
        self.assertGreater(self.runtime_cache_disabled, 0.0)

    def test_sanity_check_runtime_cache_enabled(self):
        self.assertGreater(self.runtime_cache_enabled, 0.0)

    def test_caching_decreases_total_runtime(self):
        self.assertLess(self.runtime_cache_enabled, self.runtime_cache_disabled)

    def __assert_runtime_improvement(self, seconds):
        delta = self.runtime_cache_disabled - self.runtime_cache_enabled
        self.assertGreaterEqual(delta, seconds)

    def test_caching_improves_runtime_by_at_least_one_nanosecond(self):
        self.__assert_runtime_improvement(0.001 * 0.001 * 0.001)

    def test_caching_improves_runtime_by_at_least_one_microsecond(self):
        self.__assert_runtime_improvement(0.001 * 0.001)

    def test_caching_improves_runtime_by_at_least_one_millisecond(self):
        self.__assert_runtime_improvement(0.001)

    def test_caching_improves_runtime_by_at_least_ten_milliseconds(self):
        self.__assert_runtime_improvement(0.010)


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestExtractPdfContentWithPdftotext(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.actual = extract_pdf_content_with_pdftotext(TESTFILE_A)

    def test_returns_expected_type(self):
        self.assertTrue(uu.is_internalstring(self.actual))

    def test_returns_expected_text(self):
        self.assertEqual(self.actual, TESTFILE_A_EXPECTED)


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdftotextTextExtractorInternals(TestCase):
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
        self.assertIsInstance(actual, dict)


class TestPdftotextTextExtractorCanHandle(TestCase):
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
