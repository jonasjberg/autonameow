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

from unittest import skipIf, TestCase

import unit.utils as uu
from extractors.text.extractor_markdown import MarkdownTextExtractor
from unit.case_extractors_text import CaseTextExtractorBasics
from unit.case_extractors_text import CaseTextExtractorOutput
from unit.case_extractors_text import CaseTextExtractorOutputTypes


UNMET_DEPENDENCIES = (
    MarkdownTextExtractor.dependencies_satisfied() is False,
    'Extractor dependencies not satisfied (!)'
)

TESTFILE_A = uu.samplefile_abspath('sample.md')
TESTFILE_A_EXPECTED = uu.get_expected_text_for_testfile('sample.md')


class TestPrerequisites(TestCase):
    def test_test_file_exists_a(self):
        self.assertTrue(uu.file_exists(TESTFILE_A))

    def test_expected_text_is_loaded(self):
        self.assertIsNotNone(TESTFILE_A_EXPECTED)


@skipIf(*UNMET_DEPENDENCIES)
class TestMarkdownTextExtractor(CaseTextExtractorBasics, TestCase):
    EXTRACTOR_CLASS = MarkdownTextExtractor
    EXTRACTOR_NAME = 'MarkdownTextExtractor'


@skipIf(*UNMET_DEPENDENCIES)
class TestMarkdownTextExtractorOutputTypes(CaseTextExtractorOutputTypes,
                                           TestCase):
    EXTRACTOR_CLASS = MarkdownTextExtractor
    SOURCE_FILEOBJECT = uu.as_fileobject(TESTFILE_A)


@skipIf(*UNMET_DEPENDENCIES)
class TestMarkdownTextExtractorOutputTestFileA(CaseTextExtractorOutput,
                                               TestCase):
    EXTRACTOR_CLASS = MarkdownTextExtractor
    SOURCE_FILEOBJECT = uu.as_fileobject(TESTFILE_A)
    EXPECTED_TEXT = TESTFILE_A_EXPECTED


@skipIf(*UNMET_DEPENDENCIES)
class TestMarkdownTextExtractorInternals(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.test_fileobject = uu.as_fileobject(TESTFILE_A)

        self.e = MarkdownTextExtractor()
        # Disable the cache
        self.e.cache = None

    def test__get_text_returns_something(self):
        actual = self.e._extract_text(self.test_fileobject)
        self.assertIsNotNone(actual)

    def test__get_text_returns_expected_type(self):
        actual = self.e._extract_text(self.test_fileobject)
        self.assertIsInstance(actual, str)


class TestMarkdownTextExtractorCanHandle(TestCase):
    def setUp(self):
        self.e = MarkdownTextExtractor()

        self.fo_image = uu.get_mock_fileobject(mime_type='image/jpeg')
        self.fo_pdf = uu.get_mock_fileobject(mime_type='application/pdf')
        self.fo_rtf = uu.get_mock_fileobject(mime_type='text/rtf')
        self.fo_txt = uu.get_mock_fileobject(mime_type='text/plain')
        self.fo_md = uu.as_fileobject(TESTFILE_A)

    def test_class_method_can_handle_returns_expected(self):
        self.assertFalse(self.e.can_handle(self.fo_image))
        self.assertFalse(self.e.can_handle(self.fo_pdf))
        self.assertFalse(self.e.can_handle(self.fo_rtf))
        self.assertFalse(self.e.can_handle(self.fo_txt))
        self.assertTrue(self.e.can_handle(self.fo_md))
