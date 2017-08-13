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
import unit_utils as uu

import analyzers
from core import (
    analysis,
    constants
)


class TestAnalysis(TestCase):
    def setUp(self):
        # TODO: [TD0074] Provide means of accessing the shared session data.
        # TODO: Pass dummy "data pool".
        self.a = analysis.Analysis(uu.get_mock_fileobject(), None)

    def test_analysis_is_defined(self):
        self.assertIsNotNone(analysis.Analysis)

    def test_analysis_requires_file_object_argument(self):
        with self.assertRaises(TypeError):
            a = analysis.Analysis(None)
            a = analysis.Analysis('  ')

    def test_analysis_start_method_exists(self):
        self.assertIsNotNone(self.a.start)

    def test_has_method__instantiate_analyzers(self):
        self.assertIsNotNone(self.a._instantiate_analyzers)

    def test__instantiate_analyzers_returns_expected_type(self):
        analyzer_classes = analyzers.get_analyzer_classes()
        actual = self.a._instantiate_analyzers(analyzer_classes)

        self.assertTrue(isinstance(actual, list))
        for ac in actual:
            self.assertTrue(uu.is_class_instance(ac))
            self.assertTrue(issubclass(ac.__class__, analyzers.BaseAnalyzer))

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
        self.a.collect_results('contents.mime_type', '')
        self.assertEqual(len(self.a.results), 0)
        self.a.collect_results('filesystem.basename.extension', '')
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


class TestAnalysisRunQueue(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.q = analysis.AnalysisRunQueue()

    def test_init(self):
        self.assertIsNotNone(self.q)

    def test_len_initial(self):
        self.assertEqual(len(self.q), 0)

    def test_len_after_enqueueing_analyzer(self):
        self.q.enqueue(uu.get_mock_analyzer())
        self.assertEqual(len(self.q), 1)
        self.q.enqueue(uu.get_mock_analyzer())
        self.assertEqual(len(self.q), 2)

    def test_enqueue_single_analyzer(self):
        ma = next(uu.get_mock_analyzer())
        self.q.enqueue(ma)

        for a in self.q:
            self.assertEqual(ma, a)

    def test_enqueue_multiple_analyzers(self):
        enqueued = []

        for ma in uu.get_mock_analyzer():
            enqueued.append(ma)
            self.q.enqueue(ma)

        for dequeued in self.q:
            self.assertTrue(dequeued in enqueued)
