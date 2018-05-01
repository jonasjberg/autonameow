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

try:
    from ebooklib import epub
except ImportError:
    epub = None

import unit.utils as uu
from extractors import ExtractorError
from extractors.text import EpubTextExtractor
from extractors.text.epub import extract_text_with_ebooklib
from unit.case_extractors import CaseExtractorBasics
from unit.case_extractors import CaseExtractorOutput
from unit.case_extractors import CaseExtractorOutputTypes


UNMET_DEPENDENCIES = (
    not EpubTextExtractor.dependencies_satisfied(),
    'Extractor dependencies not satisfied'
)

TESTFILE_A = uu.fileobject_testfile('pg38145-images.epub')
TESTFILE_A_EXPECTED = uu.get_expected_text_for_testfile('pg38145-images.epub')


@skipIf(*UNMET_DEPENDENCIES)
class TestEpubTextExtractor(CaseExtractorBasics, TestCase):
    EXTRACTOR_CLASS = EpubTextExtractor
    EXTRACTOR_NAME = 'EpubTextExtractor'


@skipIf(*UNMET_DEPENDENCIES)
class TestEpubTextExtractorOutputTypes(CaseExtractorOutputTypes, TestCase):
    EXTRACTOR_CLASS = EpubTextExtractor
    SOURCE_FILEOBJECT = TESTFILE_A


@skipIf(*UNMET_DEPENDENCIES)
class TestEpubTextExtractorOutputTestFileA(CaseExtractorOutput, TestCase):
    EXTRACTOR_CLASS = EpubTextExtractor
    SOURCE_FILEOBJECT = TESTFILE_A
    EXPECTED_FIELD_TYPE_VALUE = [
        ('full', str, TESTFILE_A_EXPECTED),
    ]


# TODO:  Rework the tests or the extractors.. ?
# NOTE(jonas): Text extractors pass results to parent class that wraps the data
#              to the format returned directly by the metadata extractors ..
# @skipIf(*UNMET_DEPENDENCIES)
# class TestEpubTextExtractorOutputTypes(TestCaseExtractorOutputTypes):
#     EXTRACTOR_CLASS = EpubTextExtractor
#     SOURCE_FILEOBJECT = uu.fileobject_testfile('magic_jpg.jpg')


@skipIf(*UNMET_DEPENDENCIES)
class TestExtractTextWithEbooklib(TestCase):
    def setUp(self):
        self.sample_file = uu.abspath_testfile('pg38145-images.epub')
        self.assertTrue(uu.file_exists(self.sample_file))

    def test_does_not_open_non_epub_files(self):
        not_epub_file = uu.abspath_testfile('gmail.pdf')
        self.assertTrue(uu.file_exists(not_epub_file))

        with self.assertRaises(ExtractorError):
            _ = extract_text_with_ebooklib(not_epub_file)

    def test_returns_expected_type(self):
        actual = extract_text_with_ebooklib(self.sample_file)
        self.assertIsInstance(actual, str)
