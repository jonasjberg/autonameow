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

from extractors import ExtractorError
from extractors.metadata import JpeginfoMetadataExtractor
from unit_utils_extractors import (
    CaseExtractorBasics,
    CaseExtractorOutput,
    CaseExtractorOutputTypes
)
import unit_utils as uu


ALL_EXTRACTOR_FIELDS_TYPES = [
    ('health', float),
    ('is_jpeg', bool),
]

unmet_dependencies = not JpeginfoMetadataExtractor.check_dependencies()
dependency_error = 'Extractor dependencies not satisfied'


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestJpeginfoMetadataExtractorOutputTypes(CaseExtractorOutputTypes):
    __test__ = True
    EXTRACTOR_CLASS = JpeginfoMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('magic_jpg.jpg')


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestJpeginfoMetadataExtractor(CaseExtractorBasics):
    __test__ = True
    EXTRACTOR_CLASS = JpeginfoMetadataExtractor

    def test_method_str_returns_expected_value(self):
        actual = str(self.extractor)
        expect = 'JpeginfoMetadataExtractor'
        self.assertEqual(actual, expect)


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestJpeginfoMetadataExtractorOutputTestFileA(CaseExtractorOutput):
    __test__ = True
    EXTRACTOR_CLASS = JpeginfoMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('magic_jpg.jpg')
    EXPECTED_FIELD_TYPE_VALUE = [
        ('health', float, 1.0),
        ('is_jpeg', bool, True),
    ]


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestJpeginfoMetadataExtractorOutputTestFileB(CaseExtractorOutput):
    __test__ = True
    EXTRACTOR_CLASS = JpeginfoMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('magic_png.png')
    EXPECTED_FIELD_TYPE_VALUE = [
        ('health', float, 0.66),
        ('is_jpeg', bool, False),
    ]


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestJpeginfoMetadataExtractorOutputTestFileC(CaseExtractorOutput):
    __test__ = True
    EXTRACTOR_CLASS = JpeginfoMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('magic_txt.txt')
    EXPECTED_FIELD_TYPE_VALUE = [
        ('health', float, 0.66),
        ('is_jpeg', bool, False),
    ]


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestJpeginfoMetadataExtractorMetainfo(unittest.TestCase):
    def setUp(self):
        _extractor_instance = JpeginfoMetadataExtractor()
        self.actual = _extractor_instance.metainfo()

    def test_metainfo_returns_expected_fields(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn(_field, self.actual)

    def test_metainfo_specifies_types_for_all_fields(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn('coercer', self.actual.get(_field, {}))

    def test_metainfo_multiple_is_bool_or_none(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            _field_lookup_entry = self.actual.get(_field, {})
            self.assertIn('multivalued', _field_lookup_entry)

            actual = _field_lookup_entry.get('multivalued')
            self.assertTrue(isinstance(actual, (bool, type(None))))
