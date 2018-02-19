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
from unittest.mock import Mock

import analyzers
import unit.utils as uu
from core import analysis
from core.analysis import filter_able_to_handle


class TestAnalysis(TestCase):
    def setUp(self):
        self.fo = uu.get_mock_fileobject()

        mock_config = Mock()
        self.config = mock_config

    def test_analysis__start_requires_fileobject_argument(self):
        for _bad_arg in [None, 'foo', object()]:
            with self.assertRaises(AssertionError):
                analysis._start(_bad_arg, self.config)

    def test_analysis__start_requires_config_argument(self):
        for _bad_arg in [None, 'foo', object()]:
            with self.assertRaises(AssertionError):
                analysis._start(self.fo, _bad_arg)

    def test__instantiate_analyzers_returns_expected_type(self):
        analyzer_classes = analyzers.get_analyzer_classes()
        actual = analysis._instantiate_analyzers(
            self.fo, analyzer_classes, self.config
        )

        self.assertIsInstance(actual, list)
        for ac in actual:
            self.assertTrue(uu.is_class_instance(ac))
            self.assertTrue(issubclass(ac.__class__, analyzers.BaseAnalyzer))


class TestFilterAbleToHandle(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.ALL_AVAILABLE_ANALYZERS = analyzers.ProviderClasses

    def _assert_suitable(self, fileobject, expect_analyzers):
        actual = [
            c.__name__ for c in
            filter_able_to_handle(self.ALL_AVAILABLE_ANALYZERS, fileobject)
        ]
        for analyzer in expect_analyzers:
            self.assertIn(analyzer, actual)

    def test_returns_expected_analyzers_for_mp4_video_file(self):
        fo = uu.get_mock_fileobject(mime_type='video/mp4')
        self._assert_suitable(fo, expect_analyzers=['FilenameAnalyzer'])

    def test_returns_expected_analyzers_for_png_image_file(self):
        fo = uu.get_mock_fileobject(mime_type='image/png')
        self._assert_suitable(fo, expect_analyzers=['FilenameAnalyzer'])

    def test_returns_expected_analyzers_for_pdf_file(self):
        fo = uu.get_mock_fileobject(mime_type='application/pdf')
        self._assert_suitable(fo, expect_analyzers=['FilenameAnalyzer',
                                                    'DocumentAnalyzer'])
