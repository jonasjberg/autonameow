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

import datetime
from unittest import TestCase

import unit_utils as uu
from core.analysis import AnalysisResults
from core.config.configuration import Configuration
from core.config import DEFAULT_CONFIG
from core.evaluate.rulematcher import (
    RuleMatcher,
    prioritize_rules,
    evaluate_rule_conditions
)
from core.extraction import ExtractedData

dummy_config = Configuration(DEFAULT_CONFIG)


class TestRuleMatcher(TestCase):
    def setUp(self):
        self.rm = RuleMatcher(None, None, dummy_config)

    def test_rule_matcher_can_be_instantiated(self):
        self.assertIsNotNone(self.rm)

    def test_rule_matcher_has_property_best_match(self):
        self.assertIsNotNone(self.rm.best_match)

    def test_rule_matcher_best_match_initially_returns_false(self):
        self.assertFalse(self.rm.best_match)


def get_dummy_analysis_results_empty():
    results = AnalysisResults()
    results.add('analysis.filename_analyzer.datetime', [])
    results.add('analysis.filename_analyzer.tags', [])
    results.add('analysis.filename_analyzer.title', [])
    results.add('analysis.filesystem_analyzer.datetime', [])
    results.add('analysis.filesystem_analyzer.tags', [])
    results.add('analysis.filesystem_analyzer.title', [])
    return results


def get_dummy_analysis_results():
    # TODO: [TD0075] Consolidate/remove data container classes.
    results = AnalysisResults()
    results.add('analysis.filename_analyzer.tags',
                [{'source': 'filenamepart_tags',
                  'value': ['tagfoo', 'tagbar'],
                  'weight': 1}])
    results.add('analysis.filename_analyzer.title',
                [{'source': 'filenamepart_base',
                  'value': 'gmail',
                  'weight': 0.25}])
    results.add('analysis.filesystem_analyzer.datetime',
                [{'source': 'modified',
                  'value': datetime.datetime(2017, 6, 12, 22, 38, 34),
                  'weight': 1},
                 {'source': 'created',
                  'value': datetime.datetime(2017, 6, 12, 22, 38, 34),
                  'weight': 1},
                 {'source': 'accessed',
                  'value': datetime.datetime(2017, 6, 12, 22, 38, 34),
                  'weight': 0.25}])
    return results


def get_dummy_extraction_results():
    # TODO: [TD0075] Consolidate/remove data container classes.
    results = ExtractedData()
    results.add('filesystem.basename.full', b'gmail.pdf')
    results.add('filesystem.basename.extension', b'pdf.pdf')
    results.add('filesystem.basename.suffix', b'pdf.pdf')
    results.add('filesystem.pathname.parent', b'test_files')
    results.add('contents.mime_type', 'application/pdf')
    results.add('metadata.exiftool.PDF:Creator', 'Chromium')
    return results


class TestRuleMatcherDataQueryWithAllDataAvailable(TestCase):
    def setUp(self):
        # TODO: [TD0075] Consolidate/remove data container classes.
        analysis_data = get_dummy_analysis_results()
        extraction_data = get_dummy_extraction_results()
        self.rm = RuleMatcher(analysis_data, extraction_data, dummy_config)

    def test_query_data_is_defined(self):
        self.assertIsNotNone(self.rm.query_data)

    def test_query_data_returns_something(self):
        self.assertIsNotNone(
            self.rm.query_data('analysis.filename_analyzer.tags')
        )
        self.assertIsNotNone(
            self.rm.query_data('contents.mime_type')
        )

    def test_querying_available_data_returns_expected_type(self):
        self.assertTrue(
            isinstance(self.rm.query_data('analysis.filename_analyzer.tags'),
                       list)
        )
        self.assertTrue(
            isinstance(self.rm.query_data('contents.mime_type'),
                       str)
        )

    def test_querying_available_data_returns_expected(self):
        actual_result = self.rm.query_data('analysis.filename_analyzer.tags')
        actual_tags = actual_result[0].get('value', [])
        expected_tags = ['tagfoo', 'tagbar']
        self.assertEqual(expected_tags, actual_tags)

        self.assertEqual(self.rm.query_data('contents.mime_type'),
                         'application/pdf')


class TestRuleMatcherDataQueryWithSomeDataUnavailable(TestCase):
    def setUp(self):
        # TODO: [TD0075] Consolidate/remove data container classes.
        analysis_data = get_dummy_analysis_results_empty()
        extraction_data = get_dummy_extraction_results()
        self.rm = RuleMatcher(analysis_data, extraction_data, dummy_config)

    def test_querying_unavailable_data_returns_false(self):
        self.assertFalse(
            self.rm.query_data('analysis.filename_analyzer.tags')
        )

    def test_querying_available_data_returns_expected_type(self):
        self.assertTrue(
            isinstance(self.rm.query_data('contents.mime_type'),
                       str)
        )

    def test_querying_available_data_returns_expected(self):
        actual = self.rm.query_data('contents.mime_type')
        self.assertEqual(actual, 'application/pdf')


class DummyFileRule(object):
    def __init__(self, score, weight):
        self.score = score
        self.weight = weight


class TestPrioritizeRules(TestCase):
    def test_prioritize_rules_returns_empty_list_given_empty_list(self):
        self.assertIsNotNone(prioritize_rules([]))
        self.assertTrue(isinstance(prioritize_rules([]), list))

    def test_prioritize_rules_raises_attribute_error_given_invalid_input(self):
        with self.assertRaises(AttributeError):
            prioritize_rules([None, None])
            prioritize_rules([None])

    def test_prioritize_rules_returns_expected_based_on_score_same_weight(self):
        fr_a = DummyFileRule(3, 0.5)
        fr_b = DummyFileRule(2, 0.5)
        expected = [fr_a, fr_b]
        actual = prioritize_rules([fr_a, fr_b])
        self.assertTrue(actual, expected)

        fr_a = DummyFileRule(0, 0.5)
        fr_b = DummyFileRule(3, 0.5)
        expected = [fr_b, fr_a]
        actual = prioritize_rules([fr_a, fr_b])
        self.assertTrue(actual, expected)

    def test_prioritize_rules_returns_expected_based_on_score_diff_weight(self):
        fr_a = DummyFileRule(3, 1)
        fr_b = DummyFileRule(2, 0)
        expected = [fr_a, fr_b]
        actual = prioritize_rules([fr_a, fr_b])
        self.assertTrue(actual, expected)

        fr_a = DummyFileRule(1, 0.1)
        fr_b = DummyFileRule(3, 0.5)
        expected = [fr_b, fr_a]
        actual = prioritize_rules([fr_a, fr_b])
        self.assertTrue(actual, expected)

    def test_prioritize_rules_returns_expected_based_on_weight_same_score(self):
        fr_a = DummyFileRule(3, 0)
        fr_b = DummyFileRule(3, 1)
        expected = [fr_b, fr_a]
        actual = prioritize_rules([fr_a, fr_b])
        self.assertTrue(actual, expected)

    def test_prioritize_rules_returns_expected_based_on_weight_zero_score(self):
        fr_a = DummyFileRule(0, 0.1)
        fr_b = DummyFileRule(0, 0.5)
        expected = [fr_b, fr_a]
        actual = prioritize_rules([fr_a, fr_b])
        self.assertTrue(actual, expected)


class TestEvaluateRuleConditions(TestCase):
    def setUp(self):
        self.rules_to_examine = uu.get_dummy_rules_to_examine()

        # NOTE: Simulates no data available, no rules should pass evaluation.
        self.dummy_query_function = lambda *_: False

    def test_evaluate_rule_conditions_is_defined(self):
        self.assertIsNotNone(evaluate_rule_conditions)

    def test_returns_expected_type(self):
        actual = evaluate_rule_conditions(self.rules_to_examine,
                                          self.dummy_query_function)
        self.assertTrue(isinstance(actual, list))

    def test_no_valid_rules_pass_with_dummy_query_function(self):
        actual = evaluate_rule_conditions(self.rules_to_examine,
                                          self.dummy_query_function)
        self.assertEqual(len(actual), 0)
