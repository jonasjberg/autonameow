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

from unittest import skipIf, TestCase

import unit.utils as uu
from extractors.text import MarkdownTextExtractor
from unit.case_extractors import (
    CaseExtractorBasics,
    CaseExtractorOutput,
    CaseExtractorOutputTypes
)


UNMET_DEPENDENCIES = (
    MarkdownTextExtractor.dependencies_satisfied() is False,
    'Extractor dependencies not satisfied (!)'
)

TESTFILE_A = uu.abspath_testfile('sample.md')
TESTFILE_A_EXPECTED = uu.get_expected_text_for_testfile('sample.md')


class TestPrerequisites(TestCase):
    def test_test_file_exists_a(self):
        self.assertTrue(uu.file_exists(TESTFILE_A))

    def test_expected_test_is_loaded(self):
        self.assertIsNotNone(TESTFILE_A_EXPECTED)


@skipIf(*UNMET_DEPENDENCIES)
class TestMarkdownTextExtractor(CaseExtractorBasics, TestCase):
    EXTRACTOR_CLASS = MarkdownTextExtractor
    EXTRACTOR_NAME = 'MarkdownTextExtractor'


@skipIf(*UNMET_DEPENDENCIES)
class TestMarkdownTextExtractorOutputTypes(CaseExtractorOutputTypes,
                                           TestCase):
    EXTRACTOR_CLASS = MarkdownTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile(TESTFILE_A)


@skipIf(*UNMET_DEPENDENCIES)
class TestMarkdownTextExtractorOutputTestFileA(CaseExtractorOutput,
                                               TestCase):
    EXTRACTOR_CLASS = MarkdownTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile(TESTFILE_A)
    EXPECTED_FIELD_TYPE_VALUE = [
        ('full', str, TESTFILE_A_EXPECTED),
    ]


@skipIf(*UNMET_DEPENDENCIES)
class TestMarkdownTextExtractorInternals(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.test_fileobject = uu.fileobject_testfile('sample.md')
        self.e = MarkdownTextExtractor()

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


class TestMarkdownTextExtractorCanHandle(TestCase):
    def setUp(self):
        self.e = MarkdownTextExtractor()

        self.fo_image = uu.get_mock_fileobject(mime_type='image/jpeg')
        self.fo_pdf = uu.get_mock_fileobject(mime_type='application/pdf')
        self.fo_rtf = uu.get_mock_fileobject(mime_type='text/rtf')
        self.fo_txt = uu.get_mock_fileobject(mime_type='text/plain')
        self.fo_md = uu.fileobject_testfile('sample.md')

    def test_class_method_can_handle_returns_expected(self):
        self.assertFalse(self.e.can_handle(self.fo_image))
        self.assertFalse(self.e.can_handle(self.fo_pdf))
        self.assertFalse(self.e.can_handle(self.fo_rtf))
        self.assertFalse(self.e.can_handle(self.fo_txt))
        self.assertTrue(self.e.can_handle(self.fo_md))
