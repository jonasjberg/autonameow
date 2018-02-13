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
from extractors.text import PdfTextExtractor
from extractors.text.pdf import extract_pdf_content_with_pdftotext
from unit.case_extractors import (
    CaseExtractorBasics,
    CaseExtractorOutput,
    CaseExtractorOutputTypes
)


UNMET_DEPENDENCIES = PdfTextExtractor.check_dependencies() is False
DEPENDENCY_ERROR = 'Extractor dependencies not satisfied'

# NOTE: It seems that pdftotext strips trailing whitespace on MacOS (v0.57.0)
#       but not on Linux (v0.41.0) --- gives inconsistent test results (?)

TESTFILE_A = uu.abspath_testfile('simplest_pdf.md.pdf')
TESTFILE_A_EXPECTED = uu.get_expected_text_for_testfile('simplest_pdf.md.pdf')

TESTFILE_B = uu.abspath_testfile('magic_pdf.pdf')
TESTFILE_B_EXPECTED = uu.get_expected_text_for_testfile('magic_pdf.pdf')


class TestPrerequisites(TestCase):
    def test_test_file_exists_a(self):
        self.assertTrue(uu.file_exists(TESTFILE_A))

    def test_test_file_exists_b(self):
        self.assertTrue(uu.file_exists(TESTFILE_B))


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdfTextExtractor(CaseExtractorBasics):
    __test__ = True
    EXTRACTOR_CLASS = PdfTextExtractor

    def test_method_str_returns_expected(self):
        actual = str(self.extractor)
        expect = 'PdfTextExtractor'
        self.assertEqual(expect, actual)


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdfTextExtractorOutputTypes(CaseExtractorOutputTypes):
    __test__ = True
    EXTRACTOR_CLASS = PdfTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile(TESTFILE_A)


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdfTextExtractorOutputTestFileA(CaseExtractorOutput):
    __test__ = True
    EXTRACTOR_CLASS = PdfTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile(TESTFILE_A)
    EXPECTED_FIELD_TYPE_VALUE = [
        ('full', str, TESTFILE_A_EXPECTED),
    ]


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdfTextExtractorOutputTestFileB(CaseExtractorOutput):
    __test__ = True
    EXTRACTOR_CLASS = PdfTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile(TESTFILE_B)
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
        e_no_cache = PdfTextExtractor()
        e_no_cache.cache = None

        start_time = time.time()
        _ = e_no_cache.extract(source_a)
        _ = e_no_cache.extract(source_b)
        cls.runtime_cache_disabled = time.time() - start_time

        # Enable caching.
        e_cached = PdfTextExtractor()
        e_cached.init_cache()

        start_time = time.time()
        _ = e_cached.extract(source_a)
        _ = e_cached.extract(source_b)
        cls.runtime_cache_enabled = time.time() - start_time

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
        self.assertEqual(TESTFILE_A_EXPECTED, self.actual)


@skipIf(UNMET_DEPENDENCIES, DEPENDENCY_ERROR)
class TestPdfTextExtractorInternals(TestCase):
    def setUp(self):
        self.test_fileobject = uu.fileobject_testfile('gmail.pdf')
        self.e = PdfTextExtractor()

    def test__get_text_returns_something(self):
        actual = self.e.extract_text(self.test_fileobject)
        self.assertIsNotNone(actual)

    def test__get_text_returns_expected_type(self):
        actual = self.e.extract_text(self.test_fileobject)
        self.assertIsInstance(actual, str)

    def test_method_extract_returns_something(self):
        self.assertIsNotNone(self.e.extract(self.test_fileobject))

    def test_method_extract_returns_expected_type(self):
        actual = self.e.extract(self.test_fileobject)
        self.assertIsInstance(actual, dict)


class TestPdfTextExtractorCanHandle(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.e = PdfTextExtractor()

        class DummyFileObject(object):
            def __init__(self, mime):
                self.mime_type = mime
        self.fo_image = DummyFileObject(mime='image/jpeg')
        self.fo_pdf = DummyFileObject(mime='application/pdf')

    def test_class_method_can_handle_returns_expected(self):
        self.assertFalse(self.e.can_handle(self.fo_image))
        self.assertTrue(self.e.can_handle(self.fo_pdf))
