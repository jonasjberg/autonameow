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
from unittest import skipIf, TestCase

import unit.utils as uu
from extractors.metadata import ExiftoolMetadataExtractor
from extractors.metadata.exiftool import is_bad_metadata
from extractors.metadata.exiftool import _filter_coerced_value
from unit.case_extractors import CaseExtractorBasics
from unit.case_extractors import CaseExtractorOutput
from unit.case_extractors import CaseExtractorOutputTypes


UNMET_DEPENDENCIES = (
    not ExiftoolMetadataExtractor.dependencies_satisfied(),
    'Extractor dependencies not satisfied'
)


@skipIf(*UNMET_DEPENDENCIES)
class TestExiftoolMetadataExtractor(CaseExtractorBasics, TestCase):
    EXTRACTOR_CLASS = ExiftoolMetadataExtractor
    EXTRACTOR_NAME = 'ExiftoolMetadataExtractor'


@skipIf(*UNMET_DEPENDENCIES)
class TestExiftoolMetadataExtractorOutputTypes(CaseExtractorOutputTypes,
                                               TestCase):
    EXTRACTOR_CLASS = ExiftoolMetadataExtractor
    SOURCE_FILEOBJECT = uu.fileobject_testfile('magic_jpg.jpg')


@skipIf(*UNMET_DEPENDENCIES)
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


@skipIf(*UNMET_DEPENDENCIES)
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


class TestIsBadMetadata(TestCase):
    def _assert_bad(self, tag, value):
        actual = is_bad_metadata(tag, value)
        self.assertTrue(actual)
        self.assertIsInstance(actual, bool)

    def _assert_bad_any_tag(self, value):
        for arbitrary_tag in [
            'File:FileModifyDate',
            'File:FileName',
            'File:FileSize',
            'File:FileType',
            'PDF:Author',
            'PDF:Subject',
            'PDF:Title',
            'XMP:Author',
            'XMP:Creator',
            'XMP:Creator',
            'XMP:Description',
            'XMP:Description',
            'XMP:Subject',
            'XMP:Subject',
            'XMP:Subject',
            'XMP:Subject',
            'XMP:Title',
        ]:
            actual = is_bad_metadata(arbitrary_tag, value)
            self.assertTrue(actual)
            self.assertIsInstance(actual, bool)

    def test_good_tags_values_return_false(self):
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

    def test_bad_tags_values_return_true(self):
        self._assert_bad('PDF:Author', 'Author')
        self._assert_bad('PDF:Author', 'First Edition')
        self._assert_bad('PDF:Author', 'Second Edition')
        self._assert_bad('PDF:Author', 'Third Edition')
        self._assert_bad('PDF:Subject', 'Subject')
        self._assert_bad('PDF:Title', 'Title')
        self._assert_bad('XMP:Author', 'Author')
        self._assert_bad('XMP:Creator', 'Author')
        self._assert_bad('XMP:Creator', 'Creator')
        self._assert_bad('XMP:Creator', 'First Edition')
        self._assert_bad('XMP:Creator', 'Second Edition')
        self._assert_bad('XMP:Creator', 'Third Edition')
        self._assert_bad('XMP:Description', 'Description')
        self._assert_bad('XMP:Description', 'Subject')
        self._assert_bad('XMP:Subject', 'Subject')
        self._assert_bad('XMP:Subject', ['Science', 'Subject'])
        self._assert_bad('XMP:Subject', ['Subject'])
        self._assert_bad('XMP:Subject', ['Title', 'Subject'])
        self._assert_bad('XMP:Title', 'Title')

        self._assert_bad('PDF:Author', 'Unknown')
        self._assert_bad('PDF:Subject', 'Unknown')
        self._assert_bad('PDF:Title', 'DjVu Document')
        self._assert_bad('PDF:Title', 'Unknown')
        self._assert_bad('XMP:Author', 'Unknown')
        self._assert_bad('XMP:Creator', 'Unknown')
        self._assert_bad('XMP:Description', 'Unknown')
        self._assert_bad('XMP:Subject', 'Unknown')
        self._assert_bad('XMP:Subject', ['Unknown'])
        self._assert_bad('XMP:Title', 'DjVu Document')
        self._assert_bad('XMP:Title', 'Unknown')

    def test_certain_bad_values_return_true_for_any_tag(self):
        self._assert_bad('PDF:Creator',  'www.allitebooks.com')
        self._assert_bad('PDF:Producer', 'www.allitebooks.com')
        self._assert_bad('PDF:Subject',  'www.allitebooks.com')
        self._assert_bad_any_tag('-|-  this layout: dynstab  -|-')
        self._assert_bad_any_tag('0101:01:01 00:00:00+00:00')
        self._assert_bad_any_tag('Advanced PDF Repair at http://www.datanumen.com/apdfr/')
        self._assert_bad_any_tag('http://cncmanual.com/')
        self._assert_bad_any_tag('http://freepdf-books.com')
        self._assert_bad_any_tag('Toolkit http://www.activepdf.com')
        self._assert_bad_any_tag('Toolkit http://www.activepdf.com(Infix)')
        self._assert_bad_any_tag('www.allitebooks.com')
        self._assert_bad_any_tag('www.allitebooks.com')
        self._assert_bad_any_tag('www.ebook777.com')
        self._assert_bad_any_tag('www.it-ebooks.info')
        self._assert_bad_any_tag('www.itbookshub.com')


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
