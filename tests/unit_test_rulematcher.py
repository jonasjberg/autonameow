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

from core import constants as C
from core.config.configuration import Configuration
from core.config import DEFAULT_CONFIG
from core.evaluate.rulematcher import (
    RuleMatcher,
    prioritize_rules,
)
import unit_utils as uu
import unit_utils_constants as uuconst


uu.init_session_repository()
uu.init_provider_registry()


def get_testrules():
    test_config = Configuration(DEFAULT_CONFIG)
    return test_config.rules


class TestRuleMatcher(TestCase):
    def test_can_be_instantiated_with_none_fileobject_and_mock_rules(self):
        rules = get_testrules()
        matcher = RuleMatcher(None, rules)
        self.assertIsNotNone(matcher)

    def test_can_be_instantiated_with_none_fileobject_and_no_rules(self):
        rules = []
        matcher = RuleMatcher(None, rules)
        self.assertIsNotNone(matcher)


class TestRuleMatcherDataQueryWithSomeDataUnavailable(TestCase):
    def setUp(self):
        fo = uu.get_mock_fileobject()
        rules = get_testrules()
        self.rm = RuleMatcher(fo, rules)

    def test_querying_unavailable_data_returns_false(self):
        self.assertFalse(
            self.rm.request_data(uuconst.MEOWURI_AZR_FILENAME_PUBLISHER)
        )


class TestRuleMatcherProducesExpectedMatches(TestCase):
    SHARED_FILEOBJECT = uu.get_mock_fileobject(mime_type='application/pdf')

    def test_returns_none_if_no_rules_are_available(self):
        rules = []
        matcher = RuleMatcher(self.SHARED_FILEOBJECT, rules)
        matcher.start()
        actual = matcher.best_match
        self.assertIsNone(actual)

    # def test_best_match(self):
    #     rules = get_testrules()
    #     matcher = RuleMatcher(self.SHARED_FILEOBJECT, rules)
    #     actual = matcher.best_match
    #     self.assertEqual(actual.description, 'Foo Rule Description')


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
