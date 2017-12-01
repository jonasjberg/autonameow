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
from unittest.mock import Mock, patch

from core import constants as C
from core.config.configuration import Configuration
from core.config import DEFAULT_CONFIG
from core.config.rules import Rule
from core.evaluate.rulematcher import (
    RuleMatcher,
    prioritize_rules,
)
import unit.unit_utils as uu
import unit.unit_utils_constants as uuconst


uu.init_session_repository()
uu.init_provider_registry()


def get_testrules():
    test_config = Configuration(DEFAULT_CONFIG)
    return test_config.rules


class TestRuleMatcher(TestCase):
    def test_can_be_instantiated_with_mock_rules(self):
        matcher = RuleMatcher(rules=get_testrules())
        self.assertIsNotNone(matcher)

    def test_can_be_instantiated_with_no_rules(self):
        matcher = RuleMatcher(rules=[])
        self.assertIsNotNone(matcher)


class TestRuleMatcherMatching(TestCase):
    SHARED_FILEOBJECT = uu.get_mock_fileobject(mime_type='application/pdf')

    def test_returns_empty_list_if_no_rules_are_available(self):
        matcher = RuleMatcher(rules=[])
        actual = matcher.match(self.SHARED_FILEOBJECT)
        expect = []
        self.assertEqual(actual, expect)

    def test_expected_return_values_given_rules_and_valid_fileobject(self):
        matcher = RuleMatcher(rules=get_testrules())
        actual = matcher.match(self.SHARED_FILEOBJECT)
        self.assertTrue(isinstance(actual, list))

        for triple in actual:
            self.assertTrue(isinstance(triple, tuple))

            self.assertTrue(isinstance(triple[0], Rule))

            _assumed_score = triple[1]
            _assumed_weight = triple[2]
            self.assertTrue(isinstance(_assumed_score, float))
            self.assertTrue(isinstance(_assumed_weight, float))
            self.assertTrue(0 <= _assumed_score <= 1)
            self.assertTrue(0 <= _assumed_weight <= 1)

    @staticmethod
    def _get_mock_rule(exact_match, evaluates_exact, num_conditions,
                       num_conditions_met, bias):
        rule = Mock()
        rule.description = 'Mock Rule'
        rule.exact_match = bool(exact_match)
        rule.evaluate_exact.return_value = bool(evaluates_exact)
        rule.number_conditions = int(num_conditions)
        rule.number_conditions_met.return_value = int(num_conditions_met)
        rule.ranking_bias = float(bias)

        _conditions = []
        for _ in range(num_conditions):
            rule_condition = Mock()
            _conditions.append(rule_condition)
        rule.conditions = _conditions

        return rule

    def _check_matcher_result(self, given, expect):
        matcher = RuleMatcher(rules=given)
        actual = matcher.match(self.SHARED_FILEOBJECT)
        self.assertEqual(actual, expect)

    def test_non_exact_matched_rule_has_zero_score_one_weight(self):
        rule = self._get_mock_rule(
            exact_match=False, evaluates_exact=True, num_conditions=3,
            num_conditions_met=0, bias=0.5
        )
        matcher = RuleMatcher(rules=[rule])
        actual = matcher.match(self.SHARED_FILEOBJECT)
        expect = [(rule, 0.0, 1.0)]
        self.assertEqual(actual, expect)

        self._check_matcher_result(
            given=[rule],
            expect=[(rule, 0.0, 1.0)]
        )

    def test_exact_matched_rule_has_one_score_one_weight(self):
        rule = self._get_mock_rule(
            exact_match=True, evaluates_exact=True, num_conditions=3,
            num_conditions_met=3, bias=0.5
        )
        matcher = RuleMatcher(rules=[rule])
        actual = matcher.match(self.SHARED_FILEOBJECT)
        expect = [(rule, 1.0, 1.0)]
        self.assertEqual(actual, expect)

    def test_one_exact_rule_one_not_exact_rule_same_score_and_weight(self):
        rule1 = self._get_mock_rule(
            exact_match=True, evaluates_exact=True, num_conditions=3,
            num_conditions_met=3, bias=0.5
        )
        rule2 = self._get_mock_rule(
            exact_match=False, evaluates_exact=True, num_conditions=3,
            num_conditions_met=3, bias=0.5
        )
        matcher = RuleMatcher(rules=[rule1, rule2])
        actual = matcher.match(self.SHARED_FILEOBJECT)
        expect = [(rule1, 1.0, 1.0), (rule2, 1.0, 1.0)]
        self.assertEqual(actual, expect)

    def test_one_exact_rule_one_not_exact_rule_different_score(self):
        rule1 = self._get_mock_rule(
            exact_match=True, evaluates_exact=True, num_conditions=3,
            num_conditions_met=3, bias=0.5
        )
        rule2 = self._get_mock_rule(
            exact_match=False, evaluates_exact=True, num_conditions=3,
            num_conditions_met=2, bias=0.5
        )
        matcher = RuleMatcher(rules=[rule1, rule2])
        actual = matcher.match(self.SHARED_FILEOBJECT)
        expect = [(rule1, 1.0, 1.0), (rule2, 0.6666666666666666, 1.0)]
        self.assertEqual(actual, expect)

    def test_one_exact_rule_one_not_exact_rule_different_weight(self):
        rule1 = self._get_mock_rule(
            exact_match=True, evaluates_exact=True, num_conditions=2,
            num_conditions_met=2, bias=0.5
        )
        rule2 = self._get_mock_rule(
            exact_match=False, evaluates_exact=True, num_conditions=5,
            num_conditions_met=5, bias=0.5
        )
        matcher = RuleMatcher(rules=[rule1, rule2])
        actual = matcher.match(self.SHARED_FILEOBJECT)
        expect = [(rule2, 1.0, 1.0), (rule1, 1.0, 0.4)]
        self.assertEqual(actual, expect)



class DummyRule(object):
    def __init__(self, exact_match):
        self.exact_match = exact_match
        self.ranking_bias = C.DEFAULT_RULE_RANKING_BIAS


class TestPrioritizeRules(TestCase):
    def test_prioritize_rules_raises_attribute_error_given_invalid_input(self):
        with self.assertRaises(AttributeError):
            prioritize_rules([None, None])
            prioritize_rules([None])

    def test_prioritize_rules_returns_expected_based_on_score_same_weight(self):
        r_a = DummyRule(exact_match=False)
        s_a = {'score': 3, 'weight': 0.5}
        r_b = DummyRule(exact_match=False)
        s_b = {'score': 0, 'weight': 0.5}
        expected = [r_a, r_b]
        actual = prioritize_rules({r_a: s_a, r_b: s_b})
        self.assertListEqual(actual, expected)

        r_a = DummyRule(exact_match=False)
        s_a = {'score': 0, 'weight': 0.5}

        r_b = DummyRule(exact_match=False)
        s_b = {'score': 3, 'weight': 0.5}
        expected = [r_b, r_a]
        actual = prioritize_rules({r_a: s_a, r_b: s_b})
        self.assertListEqual(actual, expected)

    def test_prioritize_rules_returns_expected_based_on_score_diff_weight(self):
        r_a = DummyRule(exact_match=False)
        s_a = {'score': 3, 'weight': 1}
        r_b = DummyRule(exact_match=False)
        s_b = {'score': 2, 'weight': 0}
        expected = [r_a, r_b]
        actual = prioritize_rules({r_a: s_a, r_b: s_b})
        self.assertListEqual(actual, expected)

        r_a = DummyRule(exact_match=False)
        s_a = {'score': 1, 'weight': 0.1}
        r_b = DummyRule(exact_match=False)
        s_b = {'score': 3, 'weight': 0.0}
        expected = [r_a, r_b]
        actual = prioritize_rules({r_a: s_a, r_b: s_b})
        self.assertListEqual(actual, expected)

    def test_prioritize_rules_returns_expected_based_on_weight_same_score(self):
        r_a = DummyRule(exact_match=False)
        s_a = {'score': 3, 'weight': 0.0}
        r_b = DummyRule(exact_match=False)
        s_b = {'score': 3, 'weight': 1.0}
        expected = [r_b, r_a]
        actual = prioritize_rules({r_a: s_a, r_b: s_b})
        self.assertListEqual(actual, expected)

    def test_prioritize_rules_returns_expected_based_on_weight_zero_score(self):
        r_a = DummyRule(exact_match=False)
        s_a = {'score': 0, 'weight': 0.1}
        r_b = DummyRule(exact_match=False)
        s_b = {'score': 0, 'weight': 0.5}
        expected = [r_b, r_a]
        actual = prioritize_rules({r_a: s_a, r_b: s_b})
        self.assertListEqual(actual, expected)
