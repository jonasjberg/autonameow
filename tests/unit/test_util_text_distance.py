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

from util.text.distance import levenshtein
from util.text.distance import longest_common_substring_length
from util.text.distance import normalized_levenshtein
from util.text.distance import string_difference
from util.text.distance import string_similarity
from util.text.distance import total_common_substring_length


class TestLevenshtein(TestCase):
    def _assert_levenshtein_distance(self, expected, *given_strings):
        actual = levenshtein(*given_strings)
        self.assertEqual(expected, actual)

    def test_returns_zero_given_identical_strings(self):
        self._assert_levenshtein_distance(0, 'foo', 'foo')

    def test_returns_expected_number_of_edit_differences(self):
        self._assert_levenshtein_distance(1, 'foo', 'foZ')
        self._assert_levenshtein_distance(2, 'foo', 'fZZ')
        self._assert_levenshtein_distance(3, 'foo', 'ZZZ')


class TestNormalizedLevenshtein(TestCase):
    def _assert_normalized_levenshtein(self, expected, *given_strings):
        actual = normalized_levenshtein(*given_strings)
        self.assertAlmostEqual(expected, actual)

    def test_returns_zero_given_identical_strings(self):
        self._assert_normalized_levenshtein(0.0, 'foo', 'foo')

    def test_returns_expected_number_of_edit_differences(self):
        self._assert_normalized_levenshtein(0.3333333,  'foo', 'foZ')
        self._assert_normalized_levenshtein(0.66666666, 'foo', 'fZZ')
        self._assert_normalized_levenshtein(1.0,        'foo', 'ZZZ')
        self._assert_normalized_levenshtein(0.77777777, 'foo', 'meow meow')


class TestLongestCommonSubstringLength(TestCase):
    def _assert_lcs(self, expected, *given_strings):
        actual = longest_common_substring_length(*given_strings)
        self.assertEqual(expected, actual)

    def test_completely_different_strings(self):
        self._assert_lcs(0, 'foo', 'Z')
        self._assert_lcs(0, 'foo', 'ZZ')
        self._assert_lcs(0, 'foo', 'ZZZ')

    def test_single_word_strings_continuous_match(self):
        self._assert_lcs(1, 'foo', 'f')
        self._assert_lcs(2, 'foo', 'fo')
        self._assert_lcs(3, 'foo', 'foo')

    def test_single_word_strings_multiple_possible_matches(self):
        self._assert_lcs(4, 'fofoofooofoooo', 'fooo')

    def test_multi_word_strings_continuous_match(self):
        self._assert_lcs(1, 'foo meow baz', 'm')
        self._assert_lcs(2, 'foo meow baz', 'me')
        self._assert_lcs(3, 'foo meow baz', 'meo')
        self._assert_lcs(4, 'foo meow baz', 'meow')
        self._assert_lcs(5, 'foo meow baz', 'o meo')
        self._assert_lcs(6, 'foo meow baz', 'oo meo')
        self._assert_lcs(8, 'foo meow baz', 'foo meow')


class TestTotalCommonSubstringLength(TestCase):
    def _assert_lcs(self, expected, *given_strings):
        actual = total_common_substring_length(*given_strings)
        self.assertEqual(expected, actual)

    def test_completely_different_strings(self):
        self._assert_lcs(0, 'foo', 'Z')
        self._assert_lcs(0, 'foo', 'ZZ')
        self._assert_lcs(0, 'foo', 'ZZZ')

    def test_single_word_strings_two_matching_blocks(self):
        self._assert_lcs(2, 'foox', 'fx')
        self._assert_lcs(3, 'bfooxaz', 'fox')
        self._assert_lcs(3, 'bfooxaz', 'baz')
        self._assert_lcs(4, 'bfooxaz', 'boxz')

    def test_multi_word_strings_two_matching_blocks(self):
        self._assert_lcs(2, 'foo meow baz', 'mw')
        self._assert_lcs(4, 'foo meow baz', 'foaz')


class TestStringDifference(TestCase):
    def _assert_string_difference(self, expected, *given_strings):
        actual = string_difference(*given_strings)
        self.assertAlmostEqual(expected, actual)

    def test_returns_zero_given_identical_strings(self):
        self._assert_string_difference(0.0, 'foo', 'foo')

    def test_returns_one_given_completely_different_equal_length_strings(self):
        self._assert_string_difference(1.0, 'foo', 'ZZZ')


class TestStringSimilarity(TestCase):
    def _assert_string_similarity(self, expected, *given_strings):
        actual = string_similarity(*given_strings)
        self.assertAlmostEqual(expected, actual)

    def test_returns_one_given_identical_strings(self):
        self._assert_string_similarity(1.0, 'foo', 'foo')

    def test_returns_zero_given_completely_different_equal_length_strings(self):
        self._assert_string_similarity(0.0, 'foo', 'ZZZ')
