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

from core.analyze.analysis import (
    get_analyzer_mime_mappings,
    get_analyzer_classes,
    get_instantiated_analyzers,
    Results, ANALYSIS_RESULTS_FIELDS,
    get_analyzer_classes_basename
)

from core.analyze.analyze_pdf import PdfAnalyzer
from core.analyze.analyze_image import ImageAnalyzer
from core.analyze.analyze_text import TextAnalyzer
from core.analyze.analyze_video import VideoAnalyzer
from core.analyze.analyze_filename import FilenameAnalyzer
from core.analyze.analyze_filesystem import FilesystemAnalyzer


# NOTE: Hardcoded analyzer names!
EXPECT_ANALYZER_CLASSES = ['core.analyze.analyze_image.ImageAnalyzer',
                           'core.analyze.analyze_filesystem.FilesystemAnalyzer',
                           'core.analyze.analyze_filename.FilenameAnalyzer',
                           'core.analyze.analyze_video.VideoAnalyzer',
                           'core.analyze.analyze_pdf.PdfAnalyzer',
                           'core.analyze.analyze_text.TextAnalyzer']

EXPECT_ANALYZER_CLASSES_BASENAME = ['ImageAnalyzer',
                                    'FilesystemAnalyzer',
                                    'FilenameAnalyzer',
                                    'VideoAnalyzer',
                                    'PdfAnalyzer',
                                    'TextAnalyzer']


class TestTests(TestCase):
    def test_constant_expect_analyzer_classes(self):
        pass

    def test_constant_expect_analyzer_classes_basename(self):
        _expect_basenames = [c.split('.')[-1] for c in EXPECT_ANALYZER_CLASSES]
        self.assertEquals(_expect_basenames, EXPECT_ANALYZER_CLASSES_BASENAME)


class TestAnalysisUtilityFunctions(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_get_analyzer_classes_basename_returns_expected_count(self):
        _classes = get_analyzer_classes_basename()
        self.assertEqual(len(_classes), len(EXPECT_ANALYZER_CLASSES_BASENAME))

    def test_get_analyzer_classes_basename_returns_expected_contents(self):
        _classes = get_analyzer_classes_basename()
        self.assertEqual(sorted(_classes),
                         sorted(EXPECT_ANALYZER_CLASSES_BASENAME))

    def test_get_analysis_mime_mappings(self):
        ANALYZER_TYPE_LOOKUP = {ImageAnalyzer: ['jpg', 'png'],
                                PdfAnalyzer: 'pdf',
                                TextAnalyzer: ['txt', 'md'],
                                VideoAnalyzer: 'mp4',
                                FilesystemAnalyzer: None,
                                FilenameAnalyzer: None}
        self.assertEqual(ANALYZER_TYPE_LOOKUP, get_analyzer_mime_mappings())

    def test_get_analyzer_classes_returns_expected_count(self):
        _class_names = [c.__name__ for c in get_analyzer_classes()]
        self.assertCountEqual(EXPECT_ANALYZER_CLASSES_BASENAME, _class_names)

    def test_get_analyzer_classes_returns_expected_contents(self):
        self.skipTest('TODO: Implement ..')
        _classes = get_analyzer_classes()

    def test_get_instantiated_analyzers(self):
        self.skipTest('Fix/skip this test ..')
        # _analyzers = get_instantiated_analyzers()
        # INSTANTIATED_ANALYZERS = [ImageAnalyzer(None), PdfAnalyzer(None),
        #                           TextAnalyzer(None), VideoAnalyzer(None),
        #                           FilesystemAnalyzer(None),
        #                           FilenameAnalyzer(None)]
        # self.assertEqual(INSTANTIATED_ANALYZERS, _analyzers)


class TestAnalysis(TestCase):
    def setUp(self):
        pass


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
