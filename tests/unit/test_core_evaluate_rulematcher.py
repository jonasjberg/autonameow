# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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
from unittest.mock import MagicMock, Mock, patch

import unit.utils as uu
from core import constants as C
from core.evaluate.rulematcher import prioritize_rules
from core.evaluate.rulematcher import RuleConditionEvaluator
from core.evaluate.rulematcher import RuleMatcher


uu.init_session_repository()
uu.init_provider_registry()


SHARED_FILEOBJECT = uu.get_mock_fileobject(mime_type='application/pdf')


def _get_rulematcher(**kwargs):
    rules = kwargs.get('rules', None)
    provider = kwargs.get('provider', None)
    list_rulematch = kwargs.get('list_rulematch', None)
    mock_view = Mock()
    return RuleMatcher(
        rules, provider, SHARED_FILEOBJECT, mock_view, list_rulematch
    )


def _init_master_data_provider(active_config):
    uu.init_master_data_provider(active_config)


def _get_testrules(active_config):
    return active_config.rules


class TestRuleMatcher(TestCase):
    def test_can_be_instantiated_with_mock_rules(self):
        # TODO: [hack][cleanup] Mock properly! Remove?
        active_config = uu.get_default_config()
        matcher = _get_rulematcher(rules=_get_testrules(active_config), provider=None)
        self.assertIsNotNone(matcher)

    def test_can_be_instantiated_with_no_rules(self):
        matcher = _get_rulematcher(rules=[], provider=None)
        self.assertIsNotNone(matcher)


class TestRuleMatcherMatching(TestCase):
    def test_returns_empty_list_if_no_rules_are_available(self):
        matcher = _get_rulematcher(rules=[])
        actual = matcher.get_matched_rules()
        expect = list()
        self.assertEqual(expect, actual)

    @staticmethod
    def _get_mock_rule(exact_match, num_conditions, bias):
        rule = Mock()
        rule.description = 'Mock Rule'
        rule.exact_match = bool(exact_match)
        rule.ranking_bias = float(bias)
        rule.data_sources = list()

        name_template = Mock()
        name_template.placeholders = list()
        rule.name_template = name_template

        # NOTE(jonas): Prevent 'TypeError: unorderable types: Mock() < Mock()'
        #              when sorting rules in 'get_matched_rules()'.
        rule.__gt__ = lambda _, other: 0

        _conditions = list()
        for _ in range(num_conditions):
            rule_condition = Mock()
            _conditions.append(rule_condition)
        rule.conditions = _conditions

        return rule

    def _check_matcher_result(self, given, expect):
        matcher = _get_rulematcher(rules=given, provider=None)
        actual = matcher.get_matched_rules()
        self.assertEqual(expect, actual)

    @patch('core.evaluate.rulematcher.RuleConditionEvaluator.passed')
    def test_non_exact_matched_rule_has_zero_score_one_relscore(self, mock_passed):
        self.skipTest('TODO: Fix bad mocking ..')
        rule = self._get_mock_rule(
            exact_match=False, num_conditions=3, bias=0.5
        )
        # 0 conditions met
        mock_passed.return_value = list()
        matcher = _get_rulematcher(rules=[rule], provider=None)
        actual = matcher.get_matched_rules()
        expect = [(rule, 0.0, 1.0)]
        self.assertEqual(actual, expect)

        self._check_matcher_result(
            given=[rule],
            expect=[(rule, 0.0, 1.0)]
        )

    @patch('core.evaluate.rulematcher.RuleConditionEvaluator.evaluate', MagicMock())
    @patch('core.evaluate.rulematcher.RuleConditionEvaluator.passed')
    def test_exact_matched_rule_has_one_score_one_relscore(self, mock_passed):
        rule = self._get_mock_rule(
            exact_match=True, num_conditions=3, bias=0.5
        )
        # 3 conditions met
        mock_passed.return_value = ['a', 'b', 'c']

        matcher = _get_rulematcher(rules=[rule], provider=None)
        actual = matcher.get_matched_rules()
        expect = [(rule, 1.0, 1.0)]
        self.assertEqual(expect, actual)

    @patch('core.evaluate.rulematcher.RuleConditionEvaluator.evaluate', MagicMock())
    @patch('core.evaluate.rulematcher.RuleConditionEvaluator.passed')
    def test_one_exact_rule_one_not_exact_rule_same_score_and_relscore(self, mock_passed):
        rule1 = self._get_mock_rule(
            exact_match=True, num_conditions=3, bias=0.5
        )
        rule2 = self._get_mock_rule(
            exact_match=False, num_conditions=3, bias=0.5
        )
        # 3 conditions met for both rules
        mock_passed.return_value = ['a', 'b', 'c']

        matcher = _get_rulematcher(rules=[rule1, rule2], provider=None)
        actual = matcher.get_matched_rules()
        expect = [(rule1, 1.0, 1.0), (rule2, 1.0, 1.0)]
        self.assertEqual(expect, actual)

    @patch('core.evaluate.rulematcher.RuleConditionEvaluator.evaluate', MagicMock())
    @patch('core.evaluate.rulematcher.RuleConditionEvaluator.passed')
    def test_both_exact_different_relscore(self, mock_passed):
        # 2/2 conditions met
        rule1 = self._get_mock_rule(
            exact_match=False, num_conditions=2, bias=0.5
        )
        # 5/5 conditions met
        rule2 = self._get_mock_rule(
            exact_match=False, num_conditions=5, bias=0.5
        )
        mock_passed.side_effect = [['a', 'b'], ['a', 'b', 'c', 'd', 'e']]

        matcher = _get_rulematcher(rules=[rule1, rule2], provider=None)
        actual = matcher.get_matched_rules()
        expect = [(rule2, 1.0, 1.0), (rule1, 1.0, 0.4)]
        self.assertEqual(expect, actual)


class DummyRule(object):
    def __init__(self, exact_match):
        self.exact_match = exact_match
        self.ranking_bias = C.DEFAULT_RULE_RANKING_BIAS
        self.data_sources = list()

        # self.name_template = Mock()
        from core.namebuilder.template import NameTemplate
        self.name_template = NameTemplate('foo {datetime} {title} bar.txt')


class TestPrioritizeRules(TestCase):
    def test_prioritize_rules_raises_attribute_error_given_invalid_input(self):
        with self.assertRaises(AttributeError):
            prioritize_rules([None, None])
            prioritize_rules([None])

    def test_prioritize_rules_returns_expected_based_on_score_same_relscore(self):
        r_a = DummyRule(exact_match=False)
        s_a = {'score': 3, 'relative_score': 0.5}
        r_b = DummyRule(exact_match=False)
        s_b = {'score': 0, 'relative_score': 0.5}
        expected = [r_a, r_b]
        actual = prioritize_rules({r_a: s_a, r_b: s_b})
        self.assertListEqual(actual, expected)

        r_a = DummyRule(exact_match=False)
        s_a = {'score': 0, 'relative_score': 0.5}

        r_b = DummyRule(exact_match=False)
        s_b = {'score': 3, 'relative_score': 0.5}
        expected = [r_b, r_a]
        actual = prioritize_rules({r_a: s_a, r_b: s_b})
        self.assertListEqual(actual, expected)

    def test_prioritize_rules_returns_expected_based_on_score_diff_relscore(self):
        r_a = DummyRule(exact_match=False)
        s_a = {'score': 3, 'relative_score': 1}
        r_b = DummyRule(exact_match=False)
        s_b = {'score': 2, 'relative_score': 0}
        expected = [r_a, r_b]
        actual = prioritize_rules({r_a: s_a, r_b: s_b})
        self.assertListEqual(actual, expected)

        r_a = DummyRule(exact_match=False)
        s_a = {'score': 1, 'relative_score': 0.1}
        r_b = DummyRule(exact_match=False)
        s_b = {'score': 3, 'relative_score': 0.0}
        expected = [r_a, r_b]
        actual = prioritize_rules({r_a: s_a, r_b: s_b})
        self.assertListEqual(actual, expected)

    def test_prioritize_rules_returns_expected_based_on_relscore_same_score(self):
        r_a = DummyRule(exact_match=False)
        s_a = {'score': 3, 'relative_score': 0.0}
        r_b = DummyRule(exact_match=False)
        s_b = {'score': 3, 'relative_score': 1.0}
        expected = [r_b, r_a]
        actual = prioritize_rules({r_a: s_a, r_b: s_b})
        self.assertListEqual(actual, expected)

    def test_prioritize_rules_returns_expected_based_on_relscore_zero_score(self):
        r_a = DummyRule(exact_match=False)
        s_a = {'score': 0, 'relative_score': 0.1}
        r_b = DummyRule(exact_match=False)
        s_b = {'score': 0, 'relative_score': 0.5}
        expected = [r_b, r_a]
        actual = prioritize_rules({r_a: s_a, r_b: s_b})
        self.assertListEqual(actual, expected)

    def test_prioritization_based_solely_on_number_of_data_sources(self):
        r_a = DummyRule(exact_match=False)
        r_a.data_sources = ['a']
        s_a = {'score': 0, 'relative_score': 0.0}
        r_b = DummyRule(exact_match=False)
        r_b.data_sources = ['a', 'b']
        s_b = {'score': 0, 'relative_score': 0.0}
        expected = [r_b, r_a]
        actual = prioritize_rules({r_a: s_a, r_b: s_b})
        self.assertListEqual(actual, expected)

    def test_rules_without_data_sources_are_deprioritized_when_otherwise_tied(self):
        r_a = DummyRule(exact_match=False)
        r_a.data_sources = ['a']
        s_a = {'score': 2, 'relative_score': 0.5}
        r_b = DummyRule(exact_match=False)
        r_b.data_sources = []
        s_b = {'score': 2, 'relative_score': 0.5}
        expected = [r_a, r_b]
        actual = prioritize_rules({r_a: s_a, r_b: s_b})
        self.assertListEqual(actual, expected)


class TestRuleConditionEvaluator(TestCase):
    @classmethod
    def setUpClass(cls):
        # TODO: [hack][cleanup] Does this behave as the "mocked" systems? (!)
        cls._mock_request_data_function = lambda _, __: None

    def test_init(self):
        _ = RuleConditionEvaluator(self._mock_request_data_function)

    def test_evaluate_rule(self):
        evaluator = RuleConditionEvaluator(self._mock_request_data_function)
        _rule = uu.get_dummy_rule()
        evaluator.evaluate(_rule)

    def test_all_conditions_fails_if_requested_data_is_unavailable(self):
        mock_request_data_function = Mock()
        evaluator = RuleConditionEvaluator(mock_request_data_function)
        rule = uu.get_dummy_rule()

        self.assertEqual([], evaluator.failed(rule),
                         'Initially no rule conditions failed')
        self.assertEqual([], evaluator.passed(rule),
                         'Initially no rule conditions passed')
        evaluator.evaluate(rule)

        rule_conditions = rule.conditions
        for condition in rule_conditions:
            self.assertIn(condition, evaluator.failed(rule))
            self.assertNotIn(condition, evaluator.passed(rule))
