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

from datetime import datetime
from unittest import (
    skipIf,
    TestCase,
)

import unit.utils as uu
import unit.constants as uuconst
from extractors import ExtractorError
from extractors.metadata import ExiftoolMetadataExtractor
from extractors.metadata.exiftool import (
    _filter_coerced_value,
    _get_exiftool_data,
    is_bad_metadata
)

from unit.case_extractors import (
    CaseExtractorBasics,
    CaseExtractorOutput,
    CaseExtractorOutputTypes
)


unmet_dependencies = not ExiftoolMetadataExtractor.check_dependencies()
dependency_error = 'Extractor dependencies not satisfied'


temp_fileobject = uu.get_mock_fileobject()
temp_file = uu.make_temporary_file()


@skipIf(unmet_dependencies, dependency_error)
class TestExiftoolMetadataExtractor(CaseExtractorBasics, TestCase):
    EXTRACTOR_CLASS = ExiftoolMetadataExtractor
    EXTRACTOR_NAME = 'ExiftoolMetadataExtractor'


@skipIf(unmet_dependencies, dependency_error)
class TestExiftoolMetadataExtractorOutputTypes(CaseExtractorOutputTypes,
                                               TestCase):
    EXTRACTOR_CLASS = ExiftoolMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('magic_jpg.jpg')


@skipIf(unmet_dependencies, dependency_error)
class TestExiftoolMetadataExtractorOutputTestFileA(CaseExtractorOutput,
                                                   TestCase):
    EXTRACTOR_CLASS = ExiftoolMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('smulan.jpg')
    _dt = uu.str_to_datetime
    EXPECTED_FIELD_TYPE_VALUE = [
        ('EXIF:CreateDate', datetime, _dt('2010-01-31 161251')),
        ('EXIF:DateTimeOriginal', datetime, _dt('2010-01-31 161251')),
        ('EXIF:ExifImageHeight', int, 1944),
        ('EXIF:ExifImageWidth', int, 2592)
    ]
    EXPECTED_NOT_PRESENT_FIELDS = [
        'EXIF:UserComment'  # Empty string, should be filtered out
    ]


@skipIf(unmet_dependencies, dependency_error)
class TestExiftoolMetadataExtractorOutputTestFileB(CaseExtractorOutput,
                                                   TestCase):
    EXTRACTOR_CLASS = ExiftoolMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('simplest_pdf.md.pdf')
    _dt = uu.str_to_datetime
    EXPECTED_FIELD_TYPE_VALUE = [
        ('File:FileSize', int, 51678),
        ('File:FileType', str, 'PDF'),
        ('File:FileTypeExtension', bytes, b'PDF'),
        ('File:MIMEType', str, 'application/pdf'),
        ('PDF:CreateDate', datetime, _dt('2016-05-24 144711', tz='+0200')),
        ('PDF:ModifyDate', datetime, _dt('2016-05-24 144711', tz='+0200')),
        ('PDF:Creator', str, 'LaTeX with hyperref package'),
        ('PDF:PageCount', int, 1),
        ('PDF:Producer', str, 'pdfTeX-1.40.16')
    ]


@skipIf(unmet_dependencies, dependency_error)
class TestExiftoolMetadataExtractorInternals(TestCase):
    def setUp(self):
        self.e = ExiftoolMetadataExtractor()

    def test__get_metadata_raises_expected_exceptions(self):
        with self.assertRaises(ExtractorError):
            e = ExiftoolMetadataExtractor()
            e._get_metadata(None)

        with self.assertRaises(ExtractorError):
            f = ExiftoolMetadataExtractor()
            f._get_metadata(uuconst.ASSUMED_NONEXISTENT_BASENAME)

    def test_get_exiftool_data_raises_expected_exception(self):
        with self.assertRaises(ExtractorError):
            _ = ExiftoolMetadataExtractor()
            _get_exiftool_data(None)

        with self.assertRaises(ExtractorError):
            _ = ExiftoolMetadataExtractor()
            _get_exiftool_data(uuconst.ASSUMED_NONEXISTENT_BASENAME)


class TestIsBadMetadata(TestCase):
    def test_good_tags_values_return_true(self):
        def _aT(tag, value):
            actual = is_bad_metadata(tag, value)
            self.assertFalse(actual)
            self.assertIsInstance(actual, bool)

        _aT('File:FileName', 'gmail.pdf')
        _aT('File:FileSize', 2702410)
        _aT('File:FileModifyDate', '2016:08:28 10:36:30+02:00')
        _aT('File:FileType', 'PDF')
        _aT('XMP:Date', [1918, '2009:08:20'])
        _aT('XMP:Subject', ['Non-Fiction', 'Human Science', 'Philosophy',
                            'Religion', 'Science and Technics', 'Science'])

    def test_bad_tags_values_return_false(self):
        def _aF(tag, value):
            actual = is_bad_metadata(tag, value)
            self.assertTrue(actual)
            self.assertIsInstance(actual, bool)

        _aF('PDF:Subject', 'Subject')
        _aF('PDF:Author', 'Author')
        _aF('PDF:Title', 'Title')
        _aF('XMP:Author', 'Author')
        _aF('XMP:Creator', 'Author')
        _aF('XMP:Creator', 'Creator')
        _aF('XMP:Description', 'Subject')
        _aF('XMP:Description', 'Description')
        _aF('XMP:Subject', 'Subject')
        _aF('XMP:Title', 'Title')
        _aF('XMP:Subject', ['Subject'])
        _aF('XMP:Subject', ['Science', 'Subject'])
        _aF('XMP:Subject', ['Title', 'Subject'])

        _aF('PDF:Author', 'Unknown')
        _aF('PDF:Subject', 'Unknown')
        _aF('PDF:Title', 'Unknown')
        _aF('XMP:Author', 'Unknown')
        _aF('XMP:Creator', 'Unknown')
        _aF('XMP:Description', 'Unknown')
        _aF('XMP:Subject', 'Unknown')
        _aF('XMP:Subject', ['Unknown'])
        _aF('XMP:Title', 'Unknown')


class TestFilterCoercedValue(TestCase):
    def _assert_filter_returns(self, expect, given):
        actual = _filter_coerced_value(given)
        self.assertEqual(expect, actual)

    def test_removes_none_values(self):
        self._assert_filter_returns(None, given=None)
        self._assert_filter_returns(None, given=[])
        self._assert_filter_returns(None, given=[None])
        self._assert_filter_returns(None, given=[None, None])

    def test_removes_empty_strings(self):
        self._assert_filter_returns(None, given='')
        self._assert_filter_returns(None, given=[''])
        self._assert_filter_returns(None, given=['', ''])

    def test_removes_strings_with_only_whitespace(self):
        self._assert_filter_returns(None, given=' ')
        self._assert_filter_returns(None, given=['  '])
        self._assert_filter_returns(None, given=[' ', ' '])

    def test_passes_strings(self):
        self._assert_filter_returns('a', given='a')
        self._assert_filter_returns(['a', 'b'], given=['a', 'b'])

    def test_passes_strings_but_removes_none(self):
        self._assert_filter_returns(['a'], given=['a', None])
        self._assert_filter_returns(['a', 'b'], given=['a', None, 'b'])

    def test_passes_strings_but_removes_empty_strings(self):
        self._assert_filter_returns(['a'], given=['a', ''])
        self._assert_filter_returns(['a'], given=['', 'a'])
        self._assert_filter_returns(['a', 'b'], given=['a', '', 'b'])

    def test_passes_strings_but_removes_whitespace_only_strings(self):
        self._assert_filter_returns(['a'], given=['a', ' '])
        self._assert_filter_returns(['a'], given=[' ', 'a'])
        self._assert_filter_returns(['a', 'b'], given=['a', ' ', 'b'])

    def test_passes_integers_and_floats(self):
        self._assert_filter_returns(1, given=1)
        self._assert_filter_returns([1], given=[1])
        self._assert_filter_returns(1.0, given=1.0)
        self._assert_filter_returns([1.0], given=[1.0])
