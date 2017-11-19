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

from unittest import TestCase

import analyzers
from core import analysis, types
from core.analysis import suitable_analyzers_for
import unit_utils as uu
import unit_utils_constants as uuconst


class TestAnalysis(TestCase):
    def setUp(self):
        uu.init_provider_registry()
        uu.init_session_repository()
        self.fo = uu.get_mock_fileobject()
        self.config = uu.get_default_config()

    def test_analysis_start_requires_fileobject_argument(self):
        for _bad_arg in [None, 'foo', object()]:
            with self.assertRaises(AssertionError):
                analysis.start(_bad_arg, self.config)

    def test_analysis_start_requires_config_argument(self):
        for _bad_arg in [None, 'foo', object()]:
            with self.assertRaises(AssertionError):
                analysis.start(self.fo, _bad_arg)

    def test__instantiate_analyzers_returns_expected_type(self):
        analyzer_classes = analyzers.get_analyzer_classes()
        actual = analysis._instantiate_analyzers(
            self.fo, analyzer_classes, self.config
        )

        self.assertTrue(isinstance(actual, list))
        for ac in actual:
            self.assertTrue(uu.is_class_instance(ac))
            self.assertTrue(issubclass(ac.__class__, analyzers.BaseAnalyzer))

    # def test_collects_valid_results(self):
    #     _dummy_results = {
    #         'title': {
    #             'value': 'foo',
    #             'coercer': types.AW_STRING,
    #             'mapped_fields': None,
    #             'generic_field': None,
    #             'multivalued': False,
    #             'source': object
    #         }
    #     }
    #     analysis.collect_results(
    #         self.fo,
    #         'analyzer.filename',
    #         _dummy_results
    #     )


class TestSuitableAnalyzersFor(TestCase):
    def test_returns_expected_analyzers_for_mp4_video_file(self):
        self.fo = uu.get_mock_fileobject(mime_type='video/mp4')
        actual = [c.__name__ for c in suitable_analyzers_for(self.fo)]
        self.assertIn('FilesystemAnalyzer', actual)
        self.assertIn('FilenameAnalyzer', actual)
        self.assertIn('VideoAnalyzer', actual)

    def test_returns_expected_analyzers_for_png_image_file(self):
        self.fo = uu.get_mock_fileobject(mime_type='image/png')
        actual = [c.__name__ for c in suitable_analyzers_for(self.fo)]
        self.assertIn('FilenameAnalyzer', actual)
        self.assertIn('FilesystemAnalyzer', actual)
        self.assertIn('ImageAnalyzer', actual)

    def test_returns_expected_analyzers_for_pdf_file(self):
        self.fo = uu.get_mock_fileobject(mime_type='application/pdf')
        actual = [c.__name__ for c in suitable_analyzers_for(self.fo)]
        self.assertIn('FilenameAnalyzer', actual)
        self.assertIn('FilesystemAnalyzer', actual)
        self.assertIn('DocumentAnalyzer', actual)
