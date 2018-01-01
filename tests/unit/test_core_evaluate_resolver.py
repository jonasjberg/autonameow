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

from core.evaluate.resolver import dedupe_list_of_datadicts


class TestDedupeListOfDatadicts(TestCase):
    def _t(self, given, expect):
        actual = dedupe_list_of_datadicts(given)
        self.assertEqual(actual, expect)

    def test_returns_list_with_one_element_as_is(self):
        self._t(
            given=[{'value': 'A'}],
            expect=[{'value': 'A'}]
        )

    def test_returns_list_of_only_unique_values_as_is(self):
        self._t(
            given=[{'value': 'A'}, {'value': 'B'}],
            expect=[{'value': 'A'}, {'value': 'B'}]
        )

    def test_dedupes_two_equivalent_values(self):
        self._t(
            given=[{'value': 'A'}, {'value': 'A'}],
            expect=[{'value': 'A'}]
        )

    def test_dedupes_three_equivalent_values(self):
        self._t(
            given=[{'value': 'A'}, {'value': 'A'}, {'value': 'A'}],
            expect=[{'value': 'A'}]
        )

    def test_dedupes_two_duplicate_values_and_returns_one_as_is(self):
        self._t(
            given=[{'value': 'A'}, {'value': 'B'}, {'value': 'A'}],
            expect=[{'value': 'A'}, {'value': 'B'}]
        )


class TestDedupeListOfDatadictsContainingMultipleValues(TestCase):
    def _t(self, given, expect):
        actual = dedupe_list_of_datadicts(given)
        self.assertEqual(actual, expect)

    def test_returns_one_dict_with_one_list_element_as_is(self):
        self._t(
            given=[{'value': ['A']}],
            expect=[{'value': ['A']}]
        )

    def test_returns_two_dicts_with_one_unique_list_element_each_as_is(self):
        self._t(
            given=[{'value': ['A']}, {'value': ['B']}],
            expect=[{'value': ['A']}, {'value': ['B']}]
        )

    def test_dedupes_two_dicts_with_one_list_element_equivalent_values(self):
        self._t(
            given=[{'value': ['A']}, {'value': ['A']}],
            expect=[{'value': ['A']}]
        )

    def test_dedupes_three_dicts_one_list_element_equivalent_values(self):
        self._t(
            given=[{'value': ['A']}, {'value': ['A']}, {'value': ['A']}],
            expect=[{'value': ['A']}]
        )

    def test_dedupes_three_dicts_two_duplicate_values_one_unique(self):
        self._t(
            given=[{'value': ['A']}, {'value': ['B']}, {'value': ['A']}],
            expect=[{'value': ['A']}, {'value': ['B']}]
        )

    def test_dedupes_three_dicts_two_duplicate_values_one_unique_A(self):
        self._t(
            given=[{'value': ['A', 'B']}, {'value': ['C']},
                   {'value': ['B', 'A']}],
            expect=[{'value': ['A', 'B']}, {'value': ['C']}]
        )

    def test_dedupes_three_dicts_two_duplicate_values_one_unique_B(self):
        self._t(
            given=[{'value': ['A', 'B']}, {'value': ['C']},
                   {'value': ['A', 'B']}],
            expect=[{'value': ['A', 'B']}, {'value': ['C']}]
        )

    def test_returns_list_with_two_elements_as_is(self):
        self._t(
            given=[{'value': ['A', 'B']}],
            expect=[{'value': ['A', 'B']}]
        )

    def test_returns_two_dicts_two_elements_in_different_order_as_is(self):
        self._t(
            given=[{'value': ['A', 'B']}, {'value': ['B', 'A']}],
            expect=[{'value': ['A', 'B']}]
        )

    def test_returns_two_dicts_diff_number_of_unique_list_elements_as_is(self):
        self._t(
            given=[{'value': ['A', 'B']}, {'value': ['C']}],
            expect=[{'value': ['A', 'B']}, {'value': ['C']}]
        )

    def test_returns_two_dicts_with_diff_number_of_list_elements_as_is(self):
        self._t(
            given=[{'value': ['A', 'B']}, {'value': ['A']}],
            expect=[{'value': ['A', 'B']}, {'value': ['A']}]
        )
