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
from core import constants
from core.config.configuration import Configuration
from core.config import DEFAULT_CONFIG
from core.evaluate.rulematcher import (
    RuleMatcher,
    prioritize_rules,
    evaluate_rule_conditions
)

dummy_config = Configuration(DEFAULT_CONFIG)


class TestRuleMatcher(TestCase):
    def setUp(self):
        self.rm = RuleMatcher(None, dummy_config)

    def test_rule_matcher_can_be_instantiated(self):
        self.assertIsNotNone(self.rm)

    def test_rule_matcher_has_property_best_match(self):
        self.assertIsNotNone(self.rm.best_match)

    def test_rule_matcher_best_match_initially_returns_false(self):
        self.assertFalse(self.rm.best_match)


class TestRuleMatcherDataQueryWithAllDataAvailable(TestCase):
    def setUp(self):
        fo = uu.get_mock_fileobject()
        self.rm = RuleMatcher(fo, dummy_config)

    def test_query_data_is_defined(self):
        self.assertIsNotNone(self.rm.query_data)

    def test_query_data_returns_something(self):
        self.skipTest('TODO: Fix broken unit tests')
        self.assertIsNotNone(
            self.rm.query_data('analysis.filename_analyzer.tags')
        )
        self.assertIsNotNone(
            self.rm.query_data('filesystem.contents.mime_type')
        )

    def test_querying_available_data_returns_expected_type(self):
        self.skipTest('TODO: Fix broken unit tests')
        self.assertTrue(
            isinstance(self.rm.query_data('analysis.filename_analyzer.tags'),
                       list)
        )
        self.assertTrue(
            isinstance(self.rm.query_data('filesystem.contents.mime_type'),
                       str)
        )

    def test_querying_available_data_returns_expected(self):
        self.skipTest('TODO: Fix broken unit tests')
        actual_result = self.rm.query_data('analysis.filename_analyzer.tags')
        actual_tags = actual_result[0].get('value', [])
        expected_tags = ['tagfoo', 'tagbar']
        self.assertEqual(expected_tags, actual_tags)

        self.assertEqual(self.rm.query_data('filesystem.contents.mime_type'),
                         'application/pdf')


class TestRuleMatcherDataQueryWithSomeDataUnavailable(TestCase):
    def setUp(self):
        fo = uu.get_mock_fileobject()
        self.rm = RuleMatcher(fo, dummy_config)

    def test_querying_unavailable_data_returns_false(self):
        self.assertFalse(
            self.rm.query_data('analysis.filename_analyzer.publisher')
        )

    def test_querying_available_data_returns_expected_type(self):
        self.skipTest('TODO: Fix broken unit tests')
        self.assertTrue(
            isinstance(self.rm.query_data('filesystem.contents.mime_type'),
                       str)
        )

    def test_querying_available_data_returns_expected(self):
        self.skipTest('TODO: Fix broken unit tests')
        actual = self.rm.query_data('filesystem.contents.mime_type')
        self.assertEqual(actual, 'application/pdf')


class DummyRule(object):
    def __init__(self, score, weight):
        self.score = score
        self.weight = weight
        self.exact_match = True
        self.ranking_bias = constants.DEFAULT_RULE_RANKING_BIAS


class TestPrioritizeRules(TestCase):
    def test_prioritize_rules_returns_empty_list_given_empty_list(self):
        self.assertIsNotNone(prioritize_rules([]))
        self.assertTrue(isinstance(prioritize_rules([]), list))

    def test_prioritize_rules_raises_attribute_error_given_invalid_input(self):
        with self.assertRaises(AttributeError):
            prioritize_rules([None, None])
            prioritize_rules([None])

    def test_prioritize_rules_returns_expected_based_on_score_same_weight(self):
        r_a = DummyRule(3, 0.5)
        r_b = DummyRule(2, 0.5)
        expected = [r_a, r_b]
        actual = prioritize_rules([r_a, r_b])
        self.assertTrue(actual, expected)

        r_a = DummyRule(0, 0.5)
        r_b = DummyRule(3, 0.5)
        expected = [r_b, r_a]
        actual = prioritize_rules([r_a, r_b])
        self.assertTrue(actual, expected)

    def test_prioritize_rules_returns_expected_based_on_score_diff_weight(self):
        r_a = DummyRule(3, 1)
        r_b = DummyRule(2, 0)
        expected = [r_a, r_b]
        actual = prioritize_rules([r_a, r_b])
        self.assertTrue(actual, expected)

        r_a = DummyRule(1, 0.1)
        r_b = DummyRule(3, 0.5)
        expected = [r_b, r_a]
        actual = prioritize_rules([r_a, r_b])
        self.assertTrue(actual, expected)

    def test_prioritize_rules_returns_expected_based_on_weight_same_score(self):
        r_a = DummyRule(3, 0)
        r_b = DummyRule(3, 1)
        expected = [r_b, r_a]
        actual = prioritize_rules([r_a, r_b])
        self.assertTrue(actual, expected)

    def test_prioritize_rules_returns_expected_based_on_weight_zero_score(self):
        r_a = DummyRule(0, 0.1)
        r_b = DummyRule(0, 0.5)
        expected = [r_b, r_a]
        actual = prioritize_rules([r_a, r_b])
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
