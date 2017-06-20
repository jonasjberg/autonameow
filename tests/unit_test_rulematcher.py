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
from core.evaluate.rulematcher import (
    RuleMatcher,
    prioritize_rules
)


class TestRuleMatcher(TestCase):
    def setUp(self):
        self.rm = RuleMatcher(None, None, None)

    def test_rule_matcher_can_be_instantiated(self):
        self.assertIsNotNone(self.rm)

    def test_rule_matcher_has_property_best_match(self):
        self.assertIsNotNone(self.rm.best_match)

    def test_rule_matcher_best_match_initially_returns_false(self):
        self.assertFalse(self.rm.best_match)


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

