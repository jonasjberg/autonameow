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
    ExtractorRunner,
    keep_slow_extractors_if_required,
    suitable_extractors_for
)
import unit.utils as uu


class TestExtractorRunnerWithNoAvailableExtractors(TestCase):
    def setUp(self):
        self.er = ExtractorRunner()

    # def test_available_extractors_returns_empty_list(self):
    #     actual = self.er.available_extractors
    #     self.assertEqual(actual, [])


class MockExtractor(object):
    is_slow = False

    def __init__(self):
        pass

    @classmethod
    def can_handle(cls, fileobject):
        return True

    def __eq__(self, other):
        if isinstance(other, self.__class__):
            return True
        return False


class MockSlowExtractor(MockExtractor):
    is_slow = True


class TestExtractorRunnerWithOneAvailableExtractor(TestCase):
    def setUp(self):
        self.er = ExtractorRunner(available_extractors=[MockExtractor])

    # def test_available_extractors_returns_one_extractor(self):
    #     actual = self.er.available_extractors
    #     self.assertEqual(actual, [MockExtractor])

    # def test_suitable_extractors_for_returns_mock_extractor(self):
    #     fo = uu.get_mock_fileobject(mime_type='text/plain')
    #     actual = self.er.suitable_extractors_for(fo)
    #     self.assertEqual(actual, [MockExtractor])


class TestExtractorRunnerUsageA(TestCase):
    def setUp(self):
        self.er = ExtractorRunner(available_extractors=[MockExtractor])

    # def test_foo(self):
    #     er = ExtractorRunner(available_extractors=[MockExtractor])
    #     er.skip_slow = False
    #     er.filter = None
    #     er.extractfrom(fo)


class TestKeepSlowExtractorsIfRequiredWithSlowExtractor(TestCase):
    def setUp(self):
        self.fast = MockExtractor
        self.slow = MockSlowExtractor

        self.input = [self.fast, self.fast, self.slow]

    def test_slow_extractors_are_excluded_if_not_required(self):
        actual = keep_slow_extractors_if_required(self.input, [])
        self.assertNotIn(self.slow, actual,
                         'Slow extractor class should be excluded')
        self.assertNotEqual(len(actual), len(self.input),
                            'Expect one less extractor class in the output')

    def test_slow_extractors_are_included_if_required(self):
        required = [self.slow]
        actual = keep_slow_extractors_if_required(self.input, required)
        self.assertIn(self.slow, actual,
                      'Slow extractor class is kept when required')
        self.assertEqual(len(self.input), len(actual),
                         'Expect the same number of extractor classes')


class TestKeepSlowExtractorsIfRequired(TestCase):
    def setUp(self):
        self.fast = MockExtractor
        self.slow = MockSlowExtractor
        self.input = [self.fast, self.fast, self.fast]

    def test_slow_extractor_are_excluded_if_not_required(self):
        actual = keep_slow_extractors_if_required(self.input, [])
        self.assertNotIn(self.slow, actual,
                         'Slow extractor class should be excluded')
        self.assertEqual(len(self.input), len(actual),
                         'Expect the same number of extractor classes')

    def test_slow_extractor_are_included_if_required(self):
        required = [self.slow]
        actual = keep_slow_extractors_if_required(self.input, required)
        self.assertNotIn(self.slow, actual,
                         'There was no slow extractor class to start with')
        self.assertEqual(len(self.input), len(actual),
                         'Expect the same number of extractor classes')


class TestSuitableExtractorsForFile(TestCase):
    extractor_class_names = [e.__name__ for e in extractors.ProviderClasses]

    def _assert_in_if_available(self, member, container):
        """
        Test with the currently available extractors.
        """
        if member in self.extractor_class_names:
            self.assertIn(member, container)
        else:
            self.assertNotIn(member, container)

    @staticmethod
    def _get_suitable_extractors_for(fileobject):
        return [c.__name__ for c in suitable_extractors_for(fileobject)]

    def _check_returned_extractors_for(self, fileobject, expected, if_available):
        actual = self._get_suitable_extractors_for(fileobject)
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
            expected=['CrossPlatformFileSystemExtractor'],
            if_available=['ExiftoolMetadataExtractor']
        )

    def test_returns_expected_extractors_for_png_image_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='image/png'),
            expected=['CrossPlatformFileSystemExtractor'],
            if_available=['ExiftoolMetadataExtractor',
                          'TesseractOCRTextExtractor']
        )

    def test_returns_expected_extractors_for_pdf_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='application/pdf'),
            expected=['CrossPlatformFileSystemExtractor'],
            if_available=['ExiftoolMetadataExtractor',
                          'PdftotextTextExtractor']
        )

    def test_returns_expected_extractors_for_text_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='text/plain'),
            expected=['CrossPlatformFileSystemExtractor',
                      'PlainTextExtractor'],
            if_available=['ExiftoolMetadataExtractor']
        )

    def test_returns_expected_extractors_for_empty_file(self):
        self._check_returned_extractors_for(
            fileobject=uu.get_mock_fileobject(mime_type='inode/x-empty'),
            expected=['CrossPlatformFileSystemExtractor'],
            if_available=[]
        )
