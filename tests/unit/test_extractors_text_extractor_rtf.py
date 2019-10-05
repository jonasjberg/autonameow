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

from unittest import skip, skipIf, TestCase

import unit.utils as uu
from extractors.text.extractor_rtf import RichTextFormatTextExtractor
from unit.case_extractors_text import CaseTextExtractorBasics
from unit.case_extractors_text import CaseTextExtractorOutput
from unit.case_extractors_text import CaseTextExtractorOutputTypes


UNMET_DEPENDENCIES = (
    not RichTextFormatTextExtractor.dependencies_satisfied(),
    'Extractor dependencies not satisfied'
)

# TODO: This will fail. Either normalize text before returning or skip this!
SAMPLEFILE_A = uu.samplefile_abspath('ObjectCalisthenics.rtf')
SAMPLEFILE_A_EXPECTED = uu.get_expected_text_for_samplefile('ObjectCalisthenics.rtf')

SAMPLEFILE_B = uu.samplefile_abspath('sample.rtf')
SAMPLEFILE_B_EXPECTED = uu.get_expected_text_for_samplefile('sample.rtf')


class TestPrerequisites(TestCase):
    def test_samplefile_a_exists(self):
        self.assertTrue(uu.file_exists(SAMPLEFILE_A))

    def test_samplefile_b_exists(self):
        self.assertTrue(uu.file_exists(SAMPLEFILE_B))

    def test_expected_text_is_type_str_a(self):
        self.assertIsInstance(SAMPLEFILE_A_EXPECTED, str)

    def test_expected_text_is_type_str_b(self):
        self.assertIsInstance(SAMPLEFILE_B_EXPECTED, str)


@skipIf(*UNMET_DEPENDENCIES)
class TestRichTextFormatTextExtractor(CaseTextExtractorBasics, TestCase):
    EXTRACTOR_CLASS = RichTextFormatTextExtractor
    EXTRACTOR_NAME = 'RichTextFormatTextExtractor'


@skipIf(*UNMET_DEPENDENCIES)
class TestRichTextFormatTextExtractorOutputTypes(CaseTextExtractorOutputTypes,
                                                 TestCase):
    EXTRACTOR_CLASS = RichTextFormatTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_from_filepath(SAMPLEFILE_A)


@skip('TODO: Messy whitespace and unquoted control characters ..')
@skipIf(*UNMET_DEPENDENCIES)
class TestRichTextFormatTextExtractorOutputSamplefileA(CaseTextExtractorOutput,
                                                     TestCase):
    EXTRACTOR_CLASS = RichTextFormatTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_from_filepath(SAMPLEFILE_A)
    EXPECTED_TEXT = SAMPLEFILE_A_EXPECTED


@skipIf(*UNMET_DEPENDENCIES)
class TestRichTextFormatTextExtractorOutputSamplefileB(CaseTextExtractorOutput,
                                                     TestCase):
    EXTRACTOR_CLASS = RichTextFormatTextExtractor
    SOURCE_FILEOBJECT = uu.fileobject_from_filepath(SAMPLEFILE_B)
    EXPECTED_TEXT = SAMPLEFILE_B_EXPECTED


@skipIf(*UNMET_DEPENDENCIES)
class TestRichTextFormatTextExtractorInternals(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.sample_fileobject = uu.fileobject_from_filepath(SAMPLEFILE_A)

        self.e = RichTextFormatTextExtractor()
        # Disable the cache
        self.e.cache = None

    def test__get_text_returns_something(self):
        actual = self.e._extract_text(self.sample_fileobject)
        self.assertIsNotNone(actual)

    def test__get_text_returns_expected_type(self):
        actual = self.e._extract_text(self.sample_fileobject)
        self.assertIsInstance(actual, str)

    def test_method_extract_returns_something(self):
        self.assertIsNotNone(self.e.extract_text(self.sample_fileobject))


class TestRichTextFormatTextExtractorCanHandle(TestCase):
    def setUp(self):
        self.e = RichTextFormatTextExtractor()

        class DummyFileObject(object):
            def __init__(self, mime):
                self.mime_type = mime

        self.fo_image = DummyFileObject(mime='image/jpeg')
        self.fo_pdf = DummyFileObject(mime='application/pdf')
        self.fo_rtf = DummyFileObject(mime='text/rtf')

    def test_class_method_can_handle_returns_expected(self):
        self.assertFalse(self.e.can_handle(self.fo_image))
        self.assertFalse(self.e.can_handle(self.fo_pdf))
        self.assertTrue(self.e.can_handle(self.fo_rtf))
