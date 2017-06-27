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

from analyzers.analyzer import Analyzer
from core.analysis import (
    AnalysisResults,
    AnalysisRunQueue,
    Analysis,
    suitable_analyzers_for,
    get_analyzer_classes,
    get_analyzer_classes_basename
)
from core.constants import ANALYSIS_RESULTS_FIELDS
from unit_utils import (
    get_mock_analyzer,
    get_mock_fileobject,
    get_mock_extractor_data,
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
        self.assertEqual(len(self.a.results), 0)

    def test_collects_valid_results(self):
        self.a.collect_results('contents.mime_type', 'image/jpeg')

    def test_collecting_valid_results_increments_results_len(self):
        self.a.collect_results('contents.mime_type', 'image/jpeg')
        self.assertEqual(len(self.a.results), 1)
        self.a.collect_results('filesystem.basename.extension', 'jpg')
        self.assertEqual(len(self.a.results), 2)

    def test_collecting_results_with_empty_data_does_not_increment_len(self):
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
        _results_len = len(self.a.results)
        self.assertEqual(_results_len, 0)


class TestAnalysisResults(TestCase):
    def setUp(self):
        self.results = AnalysisResults()

    def test_results_init_in_expected_state(self):
        self.assertTrue(isinstance(self.results._data, dict))
        self.assertEqual(len(self.results._data), 0)

    def test_results_len_initially_zero(self):
        self.assertEqual(len(self.results), 0)

    def test_add(self):
        _field = ANALYSIS_RESULTS_FIELDS[0]
        _results = []
        self.results.add(_field, _results)

    def test_add_increments_len(self):
        _field = ANALYSIS_RESULTS_FIELDS[0]
        _results = ['foo']
        self.results.add(_field, _results)

        self.assertEqual(len(self.results), 1)

    def test_add_empty_does_not_increment_len(self):
        _field = ANALYSIS_RESULTS_FIELDS[0]
        _results = []
        self.results.add(_field, _results)

        self.assertEqual(len(self.results), 0)


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


# TODO: [hardcoded] Likely to break; fixed analyzer names!
EXPECT_ANALYZER_CLASSES = ['analyzers.analyze_image.ImageAnalyzer',
                           'analyzers.analyze_filesystem.FilesystemAnalyzer',
                           'analyzers.analyze_filename.FilenameAnalyzer',
                           'analyzers.analyze_video.VideoAnalyzer',
                           'analyzers.analyze_pdf.PdfAnalyzer',
                           'analyzers.analyze_text.TextAnalyzer']
EXPECT_ANALYZER_CLASSES_BASENAME = [c.split('.')[-1]
                                    for c in EXPECT_ANALYZER_CLASSES]


class TestGetAnalyzerClasses(TestCase):
    def setUp(self):
        self.maxDiff = None

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

    # TODO: [hardcoded] Likely to break; fixed analyzer names!
    def test_get_analyzer_classes_returns_expected_count(self):
        _classes = get_analyzer_classes()
        self.assertEqual(len(_classes), len(EXPECT_ANALYZER_CLASSES))

    def test_get_analyzer_classes_returns_class_objects(self):
        analyzers = get_analyzer_classes()
        for a in analyzers:
            self.assertTrue(hasattr(a, '__class__'))


class TestGetAnalyzerClassesBasename(TestCase):
    def test_get_analyzer_classes_basename_returns_expected_count(self):
        _classes = get_analyzer_classes_basename()
        self.assertEqual(len(_classes), len(EXPECT_ANALYZER_CLASSES_BASENAME))

    def test_get_analyzer_classes_basename_returns_expected_contents(self):
        _classes = get_analyzer_classes_basename()
        self.assertEqual(sorted(_classes),
                         sorted(EXPECT_ANALYZER_CLASSES_BASENAME))

    def test_get_analyzer_classes_basename_returns_list_of_strings(self):
        self.assertTrue(isinstance(get_analyzer_classes_basename(), list))

        for a in get_analyzer_classes_basename():
            self.assertTrue(isinstance(a, str))


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
