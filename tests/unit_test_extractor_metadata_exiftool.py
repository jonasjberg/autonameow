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
from datetime import datetime

from extractors import ExtractorError
from extractors.metadata import ExiftoolMetadataExtractor
from extractors.metadata.exiftool import (
    _get_exiftool_data,
    is_bad_metadata
)

import unit_utils as uu
import unit_utils_constants as uuconst
from unit_utils_extractors import (
    CaseExtractorBasics,
    CaseExtractorOutput,
    CaseExtractorOutputTypes
)


unmet_dependencies = not ExiftoolMetadataExtractor.check_dependencies()
dependency_error = 'Extractor dependencies not satisfied'


temp_fileobject = uu.get_mock_fileobject()
temp_file = uu.make_temporary_file()


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestExiftoolMetadataExtractorOutputTypes(CaseExtractorOutputTypes):
    __test__ = True
    EXTRACTOR_CLASS = ExiftoolMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('magic_jpg.jpg')


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestExiftoolMetadataExtractor(CaseExtractorBasics):
    __test__ = True
    EXTRACTOR_CLASS = ExiftoolMetadataExtractor

    def test_method_str_returns_expected(self):
        actual = str(self.extractor)
        expect = 'ExiftoolMetadataExtractor'
        self.assertEqual(actual, expect)


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestExiftoolMetadataExtractorOutputTestFileA(CaseExtractorOutput):
    __test__ = True
    EXTRACTOR_CLASS = ExiftoolMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('smulan.jpg')
    _dt = uu.str_to_datetime
    EXPECTED_FIELD_TYPE_VALUE = [
        ('EXIF:CreateDate', datetime, _dt('2010-01-31 161251')),
        ('EXIF:DateTimeOriginal', datetime, _dt('2010-01-31 161251')),
        ('EXIF:ExifImageHeight', int, 1944),
        ('EXIF:ExifImageWidth', int, 2592)
    ]


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestExiftoolMetadataExtractorOutputTestFileB(CaseExtractorOutput):
    __test__ = True
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


@unittest.skipIf(unmet_dependencies, dependency_error)
class TestExiftoolMetadataExtractorInternals(unittest.TestCase):
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


class TestIsBadMetadata(unittest.TestCase):
    def test_good_tags_values_return_true(self):
        def _aT(tag, value):
            actual = is_bad_metadata(tag, value)
            self.assertFalse(actual)
            self.assertTrue(isinstance(actual, bool))

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
            self.assertTrue(isinstance(actual, bool))

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
