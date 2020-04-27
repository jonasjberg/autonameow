# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from unittest import TestCase

import extractors
import unit.utils as uu
from core.extraction import filter_able_to_handle


class TestFilterAbleToHandle(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ALL_AVAILABLE_EXTRACTORS = extractors.registry.all_providers
        cls.extractor_class_names = [
            # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
            e.name() for e in cls.ALL_AVAILABLE_EXTRACTORS
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
        klasses = filter_able_to_handle(self.ALL_AVAILABLE_EXTRACTORS, fileobject)
        # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
        return [k.name() for k in klasses]

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
            expected=['CrossPlatformFileSystemExtractor', 'FiletagsMetadataExtractor'],
            if_available=['ExiftoolMetadataExtractor', 'GuessitMetadataExtractor']
        )

    def test_returns_expected_extractors_for_png_image_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='image/png'),
            expected=['CrossPlatformFileSystemExtractor', 'FiletagsMetadataExtractor'],
            if_available=['ExiftoolMetadataExtractor']
        )

    def test_returns_expected_extractors_for_pdf_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='application/pdf'),
            expected=['CrossPlatformFileSystemExtractor', 'FiletagsMetadataExtractor'],
            if_available=['ExiftoolMetadataExtractor']
        )

    def test_returns_expected_extractors_for_text_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='text/plain'),
            expected=['CrossPlatformFileSystemExtractor', 'FiletagsMetadataExtractor'],
            if_available=['ExiftoolMetadataExtractor']
        )

    def test_returns_expected_extractors_for_empty_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='inode/x-empty'),
            expected=['CrossPlatformFileSystemExtractor', 'FiletagsMetadataExtractor'],
            if_available=[]
        )

    def test_returns_expected_extractors_for_rtf_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='text/rtf'),
            expected=['CrossPlatformFileSystemExtractor', 'FiletagsMetadataExtractor'],
            if_available=['ExiftoolMetadataExtractor']
        )

    def test_returns_expected_extractors_for_markdown_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.fileobject_from_samplefile('sample.md'),
            expected=['CrossPlatformFileSystemExtractor', 'FiletagsMetadataExtractor'],
            if_available=['ExiftoolMetadataExtractor', 'PandocMetadataExtractor']
        )
