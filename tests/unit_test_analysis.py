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

from core import constants
from core.analysis import (
    AnalysisResults,
    AnalysisRunQueue,
    Analysis
)
from extractors.extractor import ExtractedData
from core.constants import ANALYSIS_RESULTS_FIELDS
from core.exceptions import InvalidDataSourceError
from unit_utils import (
    get_mock_analyzer,
    get_mock_fileobject
)


class TestAnalysis(TestCase):
    def setUp(self):
        self.a = Analysis(get_mock_fileobject())

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
        self.assertEqual(len(self.a.analysis_run_queue), 0)
        self.a._populate_run_queue()
        self.assertEqual(len(self.a.analysis_run_queue), 2)

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


class TestExtractedData(TestCase):
    def setUp(self):
        self.d = ExtractedData()

    def test_extracted_data_can_be_instantiated(self):
        self.assertIsNotNone(self.d)

    def test_add_data_with_invalid_label_raises_error(self):
        with self.assertRaises(InvalidDataSourceError):
            self.d.add('not_a_label.surely', 'data')
        with self.assertRaises(InvalidDataSourceError):
            self.d.add('', 'data')
        with self.assertRaises(InvalidDataSourceError):
            self.d.add(None, 'data')

    def test_adds_data_with_valid_label(self):
        valid_labels = constants.VALID_DATA_SOURCES[:3]
        for valid_label in valid_labels:
            self.d.add(valid_label, 'data')

    def test_initial_len_returns_expected(self):
        self.assertEqual(len(self.d), 0)

    def test_adding_data_increments_len(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(valid_label, 'data')
        self.assertEqual(len(self.d), 1)

    def test_adding_data_with_different_labels_increments_len(self):
        first_valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(first_valid_label, 'data')
        self.assertEqual(len(self.d), 1)

        second_valid_label = constants.VALID_DATA_SOURCES[1]
        self.d.add(second_valid_label, 'data')
        self.assertEqual(len(self.d), 2)

    def test_adding_data_with_same_label_increments_len(self):
        first_valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(first_valid_label, 'data')
        self.assertEqual(len(self.d), 1)

        second_valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(second_valid_label, 'data')
        self.assertEqual(len(self.d), 2)

    def test_get_data_with_invalid_label_raises_error(self):
        with self.assertRaises(InvalidDataSourceError):
            self.d.get('not_a_label.surely')
        with self.assertRaises(InvalidDataSourceError):
            self.d.get('')
        with self.assertRaises(InvalidDataSourceError):
            self.d.get(None)

    def test_get_data_with_valid_label_returns_false_when_empty(self):
        valid_labels = constants.VALID_DATA_SOURCES[:3]
        for valid_label in valid_labels:
            actual = self.d.get(valid_label)
            self.assertFalse(actual)

    def test_valid_label_returns_expected_data(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(valid_label, 'expected_data')

        actual = self.d.get(valid_label)
        self.assertEqual(actual, 'expected_data')

    def test_valid_label_returns_expected_data_multiple_entries(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(valid_label, 'expected_data_a')
        self.d.add(valid_label, 'expected_data_b')

        actual = self.d.get(valid_label)
        self.assertIn('expected_data_a', actual)
        self.assertIn('expected_data_b', actual)
