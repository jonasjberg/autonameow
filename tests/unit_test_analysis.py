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

from analyzers.analyzer import (
    Analyzer,
    get_analyzer_classes
)
from core.analysis import (
    AnalysisResults,
    AnalysisRunQueue,
    Analysis,
    suitable_analyzers_for
)
from core.constants import ANALYSIS_RESULTS_FIELDS
from core.extraction import get_extractor_classes
from unit_utils import (
    get_mock_analyzer,
    get_mock_fileobject,
    get_mock_extractor_data,
    get_instantiated_analyzers
)


class TestAnalysis(TestCase):
    def setUp(self):
        self.a = Analysis(get_mock_fileobject(),
                          get_mock_extractor_data())

    def test_analysis_is_defined(self):
        self.assertIsNotNone(Analysis)

    def test_analysis_requires_file_object_argument(self):
        with self.assertRaises(TypeError):
            a = Analysis(None)
            a = Analysis('  ')

    def test_analysis_start_method_exists(self):
        self.assertIsNotNone(self.a.start)

    def test_has_method__instantiate_analyzers(self):
        self.assertIsNotNone(self.a._instantiate_analyzers)

    def test__instantiate_analyzers_returns_expected_type(self):
        analyzer_classes = get_analyzer_classes()
        actual = self.a._instantiate_analyzers(analyzer_classes)

        self.assertTrue(isinstance(actual, list))
        for ac in actual:
            self.assertTrue(issubclass(ac.__class__, Analyzer))

    def test_initial_results_data_len_is_zero(self):
        self.skipTest('Requires Results to implement "__len__"')
        self.assertEqual(len(self.a.results), 0)

    def test_collects_valid_results(self):
        self.a.collect_results('contents.mime_type', 'image/jpeg')

    def test_collecting_valid_results_increments_results_len(self):
        self.skipTest('Requires Results to implement "__len__"')
        self.a.collect_results('contents.mime_type', 'image/jpeg')
        self.assertEqual(len(self.a.results), 1)
        self.a.collect_results('filesystem.basename.extension', 'jpg')
        self.assertEqual(len(self.a.results), 2)

    def test_collecting_results_with_empty_data_does_not_increment_len(self):
        self.skipTest('Requires Results to implement "__len__"')
        self.a.collect_results('contents.mime_type', None)
        self.assertEqual(len(self.a.results), 0)
        self.a.collect_results('filesystem.basename.extension', None)
        self.assertEqual(len(self.a.results), 0)

    def test_analysis__populate_run_queue_method_exists(self):
        self.assertIsNotNone(self.a._populate_run_queue)

    def test_analysis__populate_run_queue_populates_queue(self):
        self.assertEqual(len(self.a.analyzer_queue), 0)
        self.a._populate_run_queue()
        self.assertEqual(len(self.a.analyzer_queue), 2)

    def test_analysis__execute_run_queue_method_exists(self):
        self.assertIsNotNone(self.a._execute_run_queue)

    def test_analysis__execute_run_queue_increases_number_of_results(self):
        self.skipTest('Requires Results to implement "__len__"')
        _results_len = len(self.a.results)
        self.assertEqual(_results_len, 0)


class TestAnalysisResults(TestCase):
    def setUp(self):
        self.results = AnalysisResults()

    def test_results_init_contains_valid_results_fields(self):
        for field in ANALYSIS_RESULTS_FIELDS:
            self.assertTrue(field in self.results._data)

    def test_results_init_contains_all_valid_results_fields(self):
        self.assertEqual(len(ANALYSIS_RESULTS_FIELDS), len(self.results._data))

    def test_results_init_results_fields_are_type_list(self):
        for field in ANALYSIS_RESULTS_FIELDS:
            self.assertEqual(type(self.results._data[field]), list)

    def test_results_init_results_fields_are_empty(self):
        for field in ANALYSIS_RESULTS_FIELDS:
            self.assertEqual(len(self.results._data[field]), 0)

    def test_add_with_invalid_field_raises_exception(self):
        _field = 'invalid_field_surely'
        _results = []

        with self.assertRaises(KeyError):
            self.results.add(_field, _results)

    def test_add(self):
        _field = ANALYSIS_RESULTS_FIELDS[0]
        _results = []

        self.results.add(_field, _results)


class TestAnalysisRunQueue(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.q = AnalysisRunQueue()

    def test_init(self):
        self.assertIsNotNone(self.q)

    def test_len_initial(self):
        self.assertEqual(len(self.q), 0)

    def test_len_after_enqueueing_analyzer(self):
        self.q.enqueue(get_mock_analyzer())
        self.assertEqual(len(self.q), 1)
        self.q.enqueue(get_mock_analyzer())
        self.assertEqual(len(self.q), 2)

    def test_enqueue_single_analyzer(self):
        ma = next(get_mock_analyzer())
        self.q.enqueue(ma)

        for a in self.q:
            self.assertEqual(ma, a)

    def test_enqueue_multiple_analyzers(self):
        enqueued = []

        for ma in get_mock_analyzer():
            enqueued.append(ma)
            self.q.enqueue(ma)

        for dequeued in self.q:
            self.assertTrue(dequeued in enqueued)


class TestGetAnalyzerClasses(TestCase):
    def test_get_analyzer_classes_returns_expected_type(self):
        self.assertTrue(isinstance(get_analyzer_classes(), list))
        for a in get_analyzer_classes():
            self.assertTrue(issubclass(a, Analyzer))

    # TODO: [hardcoded] Testing number of extractor classes needs fixing.
    def test_get_analyzer_classes_returns_at_least_one_analyzer(self):
        self.assertGreaterEqual(len(get_analyzer_classes()), 1)

    def test_get_analyzer_classes_returns_at_least_two_analyzers(self):
        self.assertGreaterEqual(len(get_analyzer_classes()), 2)

    def test_get_analyzer_classes_returns_at_least_three_analyzers(self):
        self.assertGreaterEqual(len(get_analyzer_classes()), 3)

    def test_get_analyzer_classes_returns_at_least_four_analyzers(self):
        self.assertGreaterEqual(len(get_analyzer_classes()), 4)

    def test_get_analyzer_classes_returns_at_least_five_analyzers(self):
        self.assertGreaterEqual(len(get_analyzer_classes()), 5)

    def test_get_analyzer_classes_returns_at_least_six_analyzers(self):
        self.assertGreaterEqual(len(get_analyzer_classes()), 6)


class TestSuitableAnalyzersForFile(TestCase):
    def test_returns_expected_analyzers_for_mp4_video_file(self):
        self.fo = get_mock_fileobject(mime_type='video/mp4')
        actual = [c.__name__ for c in suitable_analyzers_for(self.fo)]
        self.assertIn('FilesystemAnalyzer', actual)
        self.assertIn('FilenameAnalyzer', actual)
        self.assertIn('VideoAnalyzer', actual)

    def test_returns_expected_analyzers_for_png_image_file(self):
        self.fo = get_mock_fileobject(mime_type='image/png')
        actual = [c.__name__ for c in suitable_analyzers_for(self.fo)]
        self.assertIn('FilenameAnalyzer', actual)
        self.assertIn('FilesystemAnalyzer', actual)
        self.assertIn('ImageAnalyzer', actual)

    def test_returns_expected_analyzers_for_pdf_file(self):
        self.fo = get_mock_fileobject(mime_type='application/pdf')
        actual = [c.__name__ for c in suitable_analyzers_for(self.fo)]
        self.assertIn('FilenameAnalyzer', actual)
        self.assertIn('FilesystemAnalyzer', actual)
        self.assertIn('PdfAnalyzer', actual)
