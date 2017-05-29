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

from core.analyze.analysis import Results
from core.analyze.analyze_image import ImageAnalyzer
from core.config.constants import ANALYSIS_RESULTS_FIELDS

# TODO: [hardcoded] Likely to break; fixed analyzer names!
EXPECT_ANALYZER_CLASSES = ['core.analyze.analyze_image.ImageAnalyzer',
                           'core.analyze.analyze_filesystem.FilesystemAnalyzer',
                           'core.analyze.analyze_filename.FilenameAnalyzer',
                           'core.analyze.analyze_video.VideoAnalyzer',
                           'core.analyze.analyze_pdf.PdfAnalyzer',
                           'core.analyze.analyze_text.TextAnalyzer']

EXPECT_ANALYZER_CLASSES_BASENAME = [c.split('.')[-1]
                                    for c in EXPECT_ANALYZER_CLASSES]


class TestAnalysis(TestCase):
    def setUp(self):
        # TODO: Add tests ..
        self.skipTest('TODO: Add tests ..')

    def test_analysis(self):
        # TODO: Add tests ..
        self.skipTest('TODO: Add tests ..')


class TestResults(TestCase):
    def setUp(self):
        self.results = Results()

    def test_results_init_contains_valid_results_fields(self):
        for field in ANALYSIS_RESULTS_FIELDS:
            self.assertTrue(field in self.results._data)

    def test_results_init_contains_all_valid_results_fields(self):
        self.assertEqual(len(ANALYSIS_RESULTS_FIELDS), len(self.results._data))

    def test_results_init_results_fields_are_type_dict(self):
        for field in ANALYSIS_RESULTS_FIELDS:
            self.assertEqual(type(self.results._data[field]), dict)

    def test_results_init_results_fields_are_empty(self):
        for field in ANALYSIS_RESULTS_FIELDS:
            self.assertEqual(len(self.results._data[field]), 0)

    def test_add_with_invalid_field_raises_exception(self):
        _field = 'invalid_field_surely'
        _results = []

        with self.assertRaises(KeyError):
            self.results.add(_field, _results, ImageAnalyzer)

    def test_add_with_invalid_analyzer_raises_exception(self):
        _field = ANALYSIS_RESULTS_FIELDS[0]
        _results = []

        with self.assertRaises(TypeError):
            self.results.add(_field, _results, 'InvalidAnalyzerSurely')

    def test_add(self):
        _field = ANALYSIS_RESULTS_FIELDS[0]
        _results = []

        self.results.add(_field, _results, 'ImageAnalyzer')
