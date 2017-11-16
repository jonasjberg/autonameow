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
from unittest import TestCase

from extractors.metadata import EpubMetadataExtractor
import unit_utils as uu
from unit_utils_extractors import TestCaseExtractorOutputTypes


unmet_dependencies = not EpubMetadataExtractor.check_dependencies()
dependency_error = 'Extractor dependencies not satisfied'


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestEpubMetadataExtractorOutputTypes(TestCaseExtractorOutputTypes):
    EXTRACTOR_CLASS = EpubMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('pg38145-images.epub')


class TestEpubMetadataExtractor(TestCase):
    def setUp(self):
        self.e = EpubMetadataExtractor()

    def test_extractor_class_is_available(self):
        self.assertIsNotNone(EpubMetadataExtractor)

    def test_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_specifies_handles_mime_types(self):
        self.assertIsNotNone(self.e.HANDLES_MIME_TYPES)
        self.assertTrue(isinstance(self.e.HANDLES_MIME_TYPES, list))

    def test_method_str_returns_expected(self):
        self.assertEqual(str(self.e), 'EpubMetadataExtractor')


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestEpubMetadataExtractorWithTestFile(unittest.TestCase):
    def setUp(self):
        self.e = EpubMetadataExtractor()
        self.test_fileobject = uu.fileobject_testfile('pg38145-images.epub')

        self.actual = self.e.extract(self.test_fileobject)

    def test_method_extract_returns_expected_title(self):
        actual = self.actual['title']['value']
        expect = 'Human, All Too Human: A Book for Free Spirits'
        self.assertEqual(actual, expect)
