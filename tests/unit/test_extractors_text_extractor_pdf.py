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

import time
from unittest import skipIf, TestCase

import unit.utils as uu
from extractors.text.extractor_pdf import extract_pdf_content_with_pdftotext
from extractors.text.extractor_pdf import PdfTextExtractor
from extractors.text.extractor_pdf import remove_intercharacter_spaces
from unit.case_extractors_text import CaseTextExtractorBasics
from unit.case_extractors_text import CaseTextExtractorOutput
from unit.case_extractors_text import CaseTextExtractorOutputTypes


UNMET_DEPENDENCIES = (
    PdfTextExtractor.dependencies_satisfied() is False,
    'Extractor dependencies not satisfied'
)

# NOTE: It seems that pdftotext strips trailing whitespace on MacOS (v0.57.0)
#       but not on Linux (v0.41.0) --- gives inconsistent test results (?)

TESTFILE_A = uu.samplefile_abspath('simplest_pdf.md.pdf')
TESTFILE_A_EXPECTED = uu.get_expected_text_for_testfile('simplest_pdf.md.pdf')

TESTFILE_B = uu.samplefile_abspath('magic_pdf.pdf')
TESTFILE_B_EXPECTED = uu.get_expected_text_for_testfile('magic_pdf.pdf')


class TestPrerequisites(TestCase):
    def test_test_file_exists_a(self):
        self.assertTrue(uu.file_exists(TESTFILE_A))

    def test_test_file_exists_b(self):
        self.assertTrue(uu.file_exists(TESTFILE_B))

    def test_expected_text_is_type_str_a(self):
        self.assertIsInstance(TESTFILE_A_EXPECTED, str)

    def test_expected_text_is_type_str_b(self):
        self.assertIsInstance(TESTFILE_B_EXPECTED, str)


@skipIf(*UNMET_DEPENDENCIES)
class TestPdfTextExtractor(CaseTextExtractorBasics, TestCase):
    EXTRACTOR_CLASS = PdfTextExtractor
    EXTRACTOR_NAME = 'PdfTextExtractor'


@skipIf(*UNMET_DEPENDENCIES)
class TestPdfTextExtractorOutputTypes(CaseTextExtractorOutputTypes, TestCase):
    EXTRACTOR_CLASS = PdfTextExtractor
    SOURCE_FILEOBJECT = uu.as_fileobject(TESTFILE_A)


@skipIf(*UNMET_DEPENDENCIES)
class TestPdfTextExtractorOutputTestFileA(CaseTextExtractorOutput, TestCase):
    EXTRACTOR_CLASS = PdfTextExtractor
    SOURCE_FILEOBJECT = uu.as_fileobject(TESTFILE_A)
    EXPECTED_TEXT = TESTFILE_A_EXPECTED


@skipIf(*UNMET_DEPENDENCIES)
class TestPdfTextExtractorOutputTestFileB(CaseTextExtractorOutput, TestCase):
    EXTRACTOR_CLASS = PdfTextExtractor
    SOURCE_FILEOBJECT = uu.as_fileobject(TESTFILE_B)
    EXPECTED_TEXT = TESTFILE_B_EXPECTED


def _get_current_time():
    return time.time()


@skipIf(*UNMET_DEPENDENCIES)
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
        source_a = uu.as_fileobject(TESTFILE_A)
        source_b = uu.as_fileobject(TESTFILE_B)

        # Patch to disable caching.
        # "Should" be equivalent to not calling 'init_cache()' in '__init__()'.
        e_no_cache = PdfTextExtractor()
        e_no_cache.cache = None

        # Measure runtime with caching disabled.
        start_time = _get_current_time()
        _ = e_no_cache.extract_text(source_a)
        _ = e_no_cache.extract_text(source_b)
        cls.runtime_cache_disabled = _get_current_time() - start_time

        # Enable caching.
        e_cached = PdfTextExtractor()
        e_cached.init_cache()
        # Run once to make sure the cache contains these files during the timed run.
        _ = e_cached.extract_text(source_a)
        _ = e_cached.extract_text(source_b)

        # Measure runtime with caching enabled.
        start_time = _get_current_time()
        _ = e_cached.extract_text(source_a)
        _ = e_cached.extract_text(source_b)
        cls.runtime_cache_enabled = _get_current_time() - start_time

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


@skipIf(*UNMET_DEPENDENCIES)
class TestExtractPdfContentWithPdftotext(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.actual = extract_pdf_content_with_pdftotext(TESTFILE_A)

    def test_returns_expected_type(self):
        self.assertTrue(uu.is_internalstring(self.actual))

    def test_returns_expected_text(self):
        self.assertEqual(TESTFILE_A_EXPECTED, self.actual)


@skipIf(*UNMET_DEPENDENCIES)
class TestPdfTextExtractorInternals(TestCase):
    def setUp(self):
        self.test_fileobject = uu.fileobject_testfile('gmail.pdf')

        self.e = PdfTextExtractor()
        # Disable the cache
        self.e.cache = None

    def test__get_text_returns_something(self):
        actual = self.e._extract_text(self.test_fileobject)
        self.assertIsNotNone(actual)

    def test__get_text_returns_expected_type(self):
        actual = self.e._extract_text(self.test_fileobject)
        self.assertIsInstance(actual, str)

    def test_method_extract_returns_something(self):
        self.assertIsNotNone(self.e.extract_text(self.test_fileobject))


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


class TestRemoveIntercharacterSpaces(TestCase):
    def _assert_equals(self, given, expect):
        with self.subTest(given=given, expect=expect):
            actual = remove_intercharacter_spaces(given)
            self.assertEqual(expect, actual)

    def test_returns_text_without_intercharacter_spaces_as_is(self):
        for given_and_expected in [
            '',
            ' ',
            'foo',
            'foo bar',
        ]:
            self._assert_equals(given_and_expected, given_and_expected)

    # def test_removes_spaces_from_single_word(self):
    #     self._assert_equals(
    #         given='L i n e a r',
    #         expect='Linear'
    #     )
    #     self._assert_equals(
    #         given='l i n e a r',
    #         expect='linear'
    #     )

    # def test_removes_extra_spaces_from_one_of_two_words(self):
    #     self._assert_equals(
    #         given='T h i r d Pass',
    #         expect='Third Pass'
    #     )

    # def test_removes_spaces_from_single_word(self):
    #     self._assert_equals(
    #         given='A L i n e a r O b s e r v e d T i m e S t a t i s t i c a l P a r s e r',
    #         expect='ALinearObservedTimeStatisticalParser'
    #     )
