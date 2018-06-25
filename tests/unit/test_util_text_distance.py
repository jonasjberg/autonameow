# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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

from util.text.distance import levenshtein
from util.text.distance import normalized_levenshtein
from util.text.distance import string_difference
from util.text.distance import string_similarity


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
