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

import itertools
from unittest import TestCase

from util.text.substring import _get_top_tied_counts
from util.text.substring import find_separators
from util.text.substring import main_separator
from util.text.substring import separator_counts
from util.text.substring import smart_split


class TestFindSeparators(TestCase):
    def _assert_separators(self, given_string, *expect_separators):
        assert all(isinstance(x, str) for x in expect_separators)
        actual = find_separators(given_string)
        self.assertEqual(sorted(expect_separators), sorted(actual))

    def test_finds_separator_semicolon(self):
        self._assert_separators('foo;bar', ';')
        self._assert_separators('foo;bar;baz', ';', ';')

    def test_finds_separator_semicolon_with_spaces(self):
        self._assert_separators('foo; bar', '; ')
        self._assert_separators('foo; bar; baz', '; ', '; ')
        self._assert_separators('foo; bar;baz', '; ', ';')

    def test_finds_separator_period(self):
        self._assert_separators('foo.bar', '.')
        self._assert_separators('foo.bar.baz', '.', '.')

    def test_finds_separator_period_with_spaces(self):
        self._assert_separators('foo. bar', '. ')
        self._assert_separators('foo. bar. baz', '. ', '. ')
        self._assert_separators('foo. bar.baz', '. ', '.')
        self._assert_separators('foo .bar', ' .')
        self._assert_separators('foo .bar. baz', ' .', '. ')
        self._assert_separators('foo .bar.baz', ' .', '.')

    def test_finds_separator_dash(self):
        self._assert_separators('foo-bar', '-')
        self._assert_separators('foo-bar-baz', '-', '-')

    def test_finds_separator_dash_with_spaces(self):
        self._assert_separators('foo- bar', '- ')
        self._assert_separators('foo- bar- baz', '- ', '- ')
        self._assert_separators('foo-bar- baz', '-', '- ')
        self._assert_separators('foo -bar', ' -')
        self._assert_separators('foo -bar -baz', ' -', ' -')
        self._assert_separators('foo-bar -baz', '-', ' -')

    def test_finds_separator_underline(self):
        self._assert_separators('foo_bar', '_')
        self._assert_separators('foo_bar_baz', '_', '_')

    def test_finds_separator_underline_with_spaces(self):
        self._assert_separators('foo_ bar', '_ ')
        self._assert_separators('foo_ bar_ baz', '_ ', '_ ')
        self._assert_separators('foo_bar_ baz', '_', '_ ')
        self._assert_separators('foo _bar', ' _')
        self._assert_separators('foo _bar _baz', ' _', ' _')
        self._assert_separators('foo_bar _baz', '_', ' _')

    def test_finds_periods_and_dashes(self):
        self._assert_separators('foo.bar-baz', '.', '-')

    def test_finds_periods_and_semicolons(self):
        self._assert_separators('foo.bar;baz', '.', ';')

    def test_finds_periods_and_underlines(self):
        self._assert_separators('foo.bar_baz', '.', '_')

    def test_finds_dashes_and_underlines(self):
        self._assert_separators('foo-bar_baz', '-', '_')

    def test_finds_dashes_and_semicolons(self):
        self._assert_separators('foo-bar;baz', '-', ';')

    def test_finds_underlines_and_semicolons(self):
        self._assert_separators('foo_bar;baz', '_', ';')

    def test_finds_all_separators_in_string(self):
        self._assert_separators('foo-bar_baz.meow', '-', '_', '.')
        self._assert_separators('foo-bar_baz;meow', '-', '_', ';')
        self._assert_separators('foo-bar_baz;meow.com', '-', '_', ';', '.')
        self._assert_separators('foo bar_baz;meow.com', ' ', '_', ';', '.')
        self._assert_separators('foo bar_baz;meow com', ' ', '_', ';', ' ')


class TestSeparatorCounts(TestCase):
    def _assert_counts(self, given_string, *expect_separators):
        actual = separator_counts(given_string, max_count=5)
        self.assertEqual(sorted(expect_separators), sorted(actual))

    def test_find_separators_all_periods(self):
        self._assert_counts('foo.bar.1234.baz', ('.', 3))

    def test_find_separators_periods_and_brackets(self):
        self._assert_counts('foo.bar.[1234].baz', ('.', 3), ('[', 1), (']', 1))

    def test_find_separators_underlines(self):
        self._assert_counts('foo_bar_1234_baz', ('_', 3))

    def test_find_separators_dashes(self):
        self._assert_counts('foo-bar-1234-baz', ('-', 3))

    def test_find_separators_spaces(self):
        self._assert_counts('foo bar 1234 baz', (' ', 3))

    def test_find_separators_underlines_and_dashes(self):
        self._assert_counts('foo-bar_1234_baz', ('_', 2), ('-', 1))

    def test_find_separators_underlines_dashes(self):
        self._assert_counts('a-b c_d', (' ', 1), ('-', 1), ('_', 1))


class TestMainSeparator(TestCase):
    def _assert_main_separator(self, given_string, expect_main_separator):
        actual = main_separator(given_string)
        self.assertEqual(expect_main_separator, actual)

    def test_find_separators_all_periods(self):
        self._assert_main_separator('foo.bar.1234.baz', '.')

    def test_find_separators_periods_and_brackets(self):
        self._assert_main_separator('foo.bar.[1234].baz', '.')

    def test_find_separators_underlines(self):
        self._assert_main_separator('foo_bar_1234_baz', '_')

    def test_find_separators_dashes(self):
        self._assert_main_separator('foo-bar-1234-baz', '-')

    def test_find_separators_spaces(self):
        self._assert_main_separator('foo bar 1234 baz', ' ')

    def test_uses_only_available_separator(self):
        self._assert_main_separator('a b', ' ')
        self._assert_main_separator('a-b', '-')
        self._assert_main_separator('a_b', '_')

        self._assert_main_separator('a  b', ' ')
        self._assert_main_separator('a--b', '-')
        self._assert_main_separator('a__b', '_')

    def test_uses_separator_with_highest_number_of_occurences(self):
        self._assert_main_separator('foo-bar_1234_baz', '_')
        self._assert_main_separator('a_b_c_d_c', '_')
        self._assert_main_separator('a-b_c_d_c', '_')
        self._assert_main_separator('a_b-c_d_c', '_')
        self._assert_main_separator('a-b-c-d_c', '-')
        self._assert_main_separator('a-b-c-d-c', '-')
        self._assert_main_separator('a_b-c-d-c', '-')

        self._assert_main_separator('a_b c_d', '_')
        self._assert_main_separator('a_b c_d', '_')
        self._assert_main_separator('a-b c-d', '-')
        self._assert_main_separator('a_b-c-d', '-')
        self._assert_main_separator('a b-c-d', '-')
        self._assert_main_separator('a-b-c d', '-')

    def test_uses_hardcoded_preferred_separator_when_tied(self):
        self._assert_main_separator('a-b c_d', ' ')
        self._assert_main_separator('a_b c-d', ' ')
        self._assert_main_separator('a b_c-d', ' ')
        self._assert_main_separator('a b-c_d', ' ')

        self._assert_main_separator('a_bb-cc-dd_c', '_')
        self._assert_main_separator('a bb-cc-dd c', ' ')
        self._assert_main_separator('a bb_cc_dd c', ' ')

    def test_finds_main_separator(self):
        self._assert_main_separator('shell-scripts.github', '-')
        self._assert_main_separator('Unison-OS-X-2.48.15.zip', '-')

        # TODO: Are we looking for field- or word-separator_counts..? (!?)
        self._assert_main_separator('2012-02-18-14-18_Untitled-meeting.log', '-')


class TestGotTopTiedCounts(TestCase):
    def _assert_top_tied(self, given_counted_seps, expected):
        actual = _get_top_tied_counts(given_counted_seps)
        self.assertEqual(sorted(expected), sorted(actual))

        for counted_seps_perm in itertools.permutations(given_counted_seps):
            actual = _get_top_tied_counts(counted_seps_perm)
            self.assertEqual(sorted(expected), sorted(actual))

    def test_returns_single_separator_with_highest_count(self):
        counted_seps = [
            (' ', 3),
            ('-', 2),
            ('_', 1),
        ]
        self._assert_top_tied(counted_seps, [' '])

    def test_returns_values_of_two_tied_separators(self):
        counted_seps = [
            (' ', 2),
            ('-', 2),
            ('_', 1),
        ]
        self._assert_top_tied(counted_seps, [' ', '-'])

        for counted_seps_perm in itertools.permutations(counted_seps):
            self._assert_top_tied(counted_seps_perm, [' ', '-'])

    def test_returns_values_of_three_tied_separators(self):
        counted_seps = [
            (' ', 2),
            ('-', 2),
            ('_', 2),
            ('x', 1),
        ]
        self._assert_top_tied(counted_seps, [' ', '-', '_'])

        for counted_seps_perm in itertools.permutations(counted_seps):
            self._assert_top_tied(counted_seps_perm, [' ', '-', '_'])


class TestSmartSplit(TestCase):
    def _assert_splits(self, given, expect):
        assert isinstance(given, str)
        actual = smart_split(given)
        self.assertEqual(expect, actual)

    def test_splits_string_by_whitespace(self):
        self._assert_splits('a',     ['a'])
        self._assert_splits('a b',   ['a', 'b'])
        self._assert_splits('a b c', ['a', 'b', 'c'])
