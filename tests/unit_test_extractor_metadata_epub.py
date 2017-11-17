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

from extractors.metadata import EpubMetadataExtractor
import unit_utils as uu
from unit_utils_extractors import (
    TestCaseExtractorBasics,
    TestCaseExtractorOutput,
    TestCaseExtractorOutputTypes
)


unmet_dependencies = not EpubMetadataExtractor.check_dependencies()
dependency_error = 'Extractor dependencies not satisfied'


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestEpubMetadataExtractor(TestCaseExtractorBasics):
    EXTRACTOR_CLASS = EpubMetadataExtractor

    def test_method_str_returns_expected(self):
        actual = str(self.extractor)
        expect = 'EpubMetadataExtractor'
        self.assertEqual(actual, expect)


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestEpubMetadataExtractorOutputTypes(TestCaseExtractorOutputTypes):
    EXTRACTOR_CLASS = EpubMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('pg38145-images.epub')


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestEpubMetadataExtractorOutputTestFileA(TestCaseExtractorOutput):
    EXTRACTOR_CLASS = EpubMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('pg38145-images.epub')
    _dt = uu.str_to_datetime
    EXPECTED_FIELD_TYPE_VALUE = [
        ('title', str, 'Human, All Too Human: A Book for Free Spirits'),
    ]
