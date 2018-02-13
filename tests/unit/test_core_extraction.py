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

from unittest import TestCase

import extractors
from core.extraction import (
    filter_able_to_handle,
)
import unit.utils as uu


class TestFilterAbleToHandle(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.all_provider_classes = set(extractors.ProviderClasses)
        cls.extractor_class_names = [
            e.__name__ for e in cls.all_provider_classes
        ]

    def _assert_in_if_available(self, member, container):
        """
        Test with the currently available extractors.
        """
        if member in self.extractor_class_names:
            self.assertIn(member, container)
        else:
            self.assertNotIn(member, container)

    def _names_of_resulting_extractors(self, fileobject):
        klasses = filter_able_to_handle(self.all_provider_classes, fileobject)
        return [k.__name__ for k in klasses]

    def _check_returned_extractors_for(self, fileobject, expected, if_available):
        actual = self._names_of_resulting_extractors(fileobject)
        for x in expected:
            with self.subTest(expected=x):
                self.assertIn(x, actual)

        for cx in if_available:
            with self.subTest(expect_if_available=cx):
                self._assert_in_if_available(cx, actual)

        with self.subTest('Number of expected should >= number of actual'):
            _num_total = len(expected) + len(if_available)
            self.assertGreaterEqual(_num_total, len(actual))

    def test_returns_expected_extractors_for_mp4_video_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='video/mp4'),
            expected=['CrossPlatformFileSystemExtractor', 'FiletagsExtractor'],
            if_available=['ExiftoolMetadataExtractor']
        )

    def test_returns_expected_extractors_for_png_image_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='image/png'),
            expected=['CrossPlatformFileSystemExtractor', 'FiletagsExtractor'],
            if_available=['ExiftoolMetadataExtractor',
                          'TesseractOCRTextExtractor']
        )

    def test_returns_expected_extractors_for_pdf_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='application/pdf'),
            expected=['CrossPlatformFileSystemExtractor', 'FiletagsExtractor'],
            if_available=['ExiftoolMetadataExtractor',
                          'PdfTextExtractor']
        )

    def test_returns_expected_extractors_for_text_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='text/plain'),
            expected=['CrossPlatformFileSystemExtractor', 'FiletagsExtractor',
                      'PlainTextExtractor'],
            if_available=['ExiftoolMetadataExtractor']
        )

    def test_returns_expected_extractors_for_empty_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='inode/x-empty'),
            expected=['CrossPlatformFileSystemExtractor', 'FiletagsExtractor'],
            if_available=[]
        )

    def test_returns_expected_extractors_for_rtf_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='text/rtf'),
            expected=['CrossPlatformFileSystemExtractor', 'FiletagsExtractor'],
            if_available=['RichTextFormatTextExtractor',
                          'ExiftoolMetadataExtractor']
        )
