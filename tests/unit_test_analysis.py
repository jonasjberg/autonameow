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
    Analyzer
)
from core.analysis import (
    AnalysisResults,
    AnalysisRunQueue,
    Analysis
)
from core.constants import ANALYSIS_RESULTS_FIELDS
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
        self.assertIsNotNone(Analysis,
                             'The Analysis class should exist and be available')

    def test_analysis_requires_file_object_argument(self):
        with self.assertRaises(TypeError):
            a = Analysis(None)
            a = Analysis('  ')

    def test_analysis_start_method_exists(self):
        self.assertIsNotNone(self.a.start)

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


class TestGetInstantiatedAnalyzers(TestCase):
    def test_get_instantiated_analyzers_returns_something(self):
        self.assertIsNotNone(get_instantiated_analyzers())

    def test_get_instantiated_analyzers_returns_expected_type(self):
        actual = get_instantiated_analyzers()
        self.assertEqual(type(actual), list)

        for a in actual:
            self.assertTrue(issubclass(a.__class__, Analyzer))


