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

try:
    from ebooklib import epub
except ImportError:
    epub = None

import unit.utils as uu
from extractors import ExtractorError
from extractors.text.extractor_epub import EpubTextExtractor
from extractors.text.extractor_epub import _extract_text_with_ebooklib
from unit.case_extractors_text import CaseTextExtractorBasics
from unit.case_extractors_text import CaseTextExtractorOutput
from unit.case_extractors_text import CaseTextExtractorOutputTypes


UNMET_DEPENDENCIES = (
    not EpubTextExtractor.dependencies_satisfied(),
    'Extractor dependencies not satisfied'
)

SAMPLEFILE_A = uu.samplefile_abspath('pg38145-images.epub')
SAMPLEFILE_A_EXPECTED = uu.get_expected_text_for_samplefile('pg38145-images.epub')


class TestPrerequisites(TestCase):
    def test_samplefile_a_exists(self):
        self.assertTrue(uu.file_exists(SAMPLEFILE_A))

    def test_expected_text_is_loaded(self):
        self.assertIsNotNone(SAMPLEFILE_A_EXPECTED)


@skipIf(*UNMET_DEPENDENCIES)
class TestEpubTextExtractor(CaseTextExtractorBasics, TestCase):
    EXTRACTOR_CLASS = EpubTextExtractor
    EXTRACTOR_NAME = 'EpubTextExtractor'


@skipIf(*UNMET_DEPENDENCIES)
class TestEpubTextExtractorOutputTypes(CaseTextExtractorOutputTypes, TestCase):
    EXTRACTOR_CLASS = EpubTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_from_filepath(SAMPLEFILE_A)


@skipIf(*UNMET_DEPENDENCIES)
class TestEpubTextExtractorOutputSamplefileA(CaseTextExtractorOutput, TestCase):
    EXTRACTOR_CLASS = EpubTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_from_filepath(SAMPLEFILE_A)
    EXPECTED_TEXT = SAMPLEFILE_A_EXPECTED


# TODO:  Rework the tests or the extractors.. ?
# NOTE(jonas): Text extractors pass results to parent class that wraps the data
#              to the format returned directly by the metadata extractors ..
# @skipIf(*UNMET_DEPENDENCIES)
# class TestEpubTextExtractorOutputTypes(TestCaseExtractorOutputTypes):
#     EXTRACTOR_CLASS = EpubTextExtractor
#     SOURCE_FILEOBJECT = uu.fileobject_from_filepath('magic_jpg.jpg')


@skipIf(*UNMET_DEPENDENCIES)
class TestExtractTextWithEbooklib(TestCase):
    def setUp(self):
        self.sample_file = uu.samplefile_abspath('pg38145-images.epub')
        self.assertTrue(uu.file_exists(self.sample_file))

    def test_does_not_open_non_epub_files(self):
        not_epub_file = uu.samplefile_abspath('gmail.pdf')
        self.assertTrue(uu.file_exists(not_epub_file))

        with self.assertRaises(ExtractorError):
            _ = _extract_text_with_ebooklib(not_epub_file)

    def test_returns_expected_type(self):
        actual = _extract_text_with_ebooklib(self.sample_file)
        self.assertIsInstance(actual, str)
