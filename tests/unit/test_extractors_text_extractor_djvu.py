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
from extractors.text.extractor_djvu import DjvuTextExtractor
from unit.case_extractors_text import CaseTextExtractorBasics
from unit.case_extractors_text import CaseTextExtractorOutput
from unit.case_extractors_text import CaseTextExtractorOutputTypes


UNMET_DEPENDENCIES = (
    DjvuTextExtractor.dependencies_satisfied() is False,
    'Extractor dependencies not satisfied'
)

TESTFILE_A = uu.samplefile_abspath('Critique_of_Pure_Reason.djvu')
TESTFILE_A_EXPECTED = uu.get_expected_text_for_testfile('Critique_of_Pure_Reason.djvu')


class TestPrerequisites(TestCase):
    def test_test_file_exists_a(self):
        self.assertTrue(uu.file_exists(TESTFILE_A))

    def test_expected_text_is_type_str_a(self):
        self.assertIsInstance(TESTFILE_A_EXPECTED, str)


@skipIf(*UNMET_DEPENDENCIES)
class TestDjvuTextExtractor(CaseTextExtractorBasics, TestCase):
    EXTRACTOR_CLASS = DjvuTextExtractor
    EXTRACTOR_NAME = 'DjvuTextExtractor'


@skipIf(*UNMET_DEPENDENCIES)
class TestDjvuTextExtractorOutputTypes(CaseTextExtractorOutputTypes, TestCase):
    EXTRACTOR_CLASS = DjvuTextExtractor
    SOURCE_FILEOBJECT = uu.as_fileobject(TESTFILE_A)


@skipIf(*UNMET_DEPENDENCIES)
class TestDjvuTextExtractorOutputTestFileA(CaseTextExtractorOutput, TestCase):
    EXTRACTOR_CLASS = DjvuTextExtractor
    SOURCE_FILEOBJECT = uu.as_fileobject(TESTFILE_A)
    EXPECTED_TEXT = TESTFILE_A_EXPECTED


class TestDjvuTextExtractorCanHandle(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.e = DjvuTextExtractor()

        class DummyFileObject(object):
            def __init__(self, mime):
                self.mime_type = mime

        cls.fo_image = DummyFileObject(mime='image/jpeg')
        cls.fo_pdf = DummyFileObject(mime='application/pdf')
        cls.fo_djvu = DummyFileObject(mime='image/vnd.djvu')

    def test_class_method_can_handle_returns_false_as_expected(self):
        self.assertFalse(self.e.can_handle(self.fo_image))
        self.assertFalse(self.e.can_handle(self.fo_pdf))

    def test_class_method_can_handle_returns_true_as_expected(self):
        self.assertTrue(self.e.can_handle(self.fo_djvu))
