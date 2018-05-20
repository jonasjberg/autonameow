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

from util.text.substring import main_separator
from util.text.substring import separator_counts


class TestSeparatorCounts(TestCase):
    def _assert_separator_counts(self, given_string, expect_separators):
        actual = separator_counts(given_string, max_count=5)
        self.assertEqual(sorted(expect_separators), sorted(actual))

    def test_find_separators_all_periods(self):
        self._assert_separator_counts('foo.bar.1234.baz',
                                      [('.', 3)])

    def test_find_separators_periods_and_brackets(self):
        self._assert_separator_counts('foo.bar.[1234].baz',
                                      [('.', 3), ('[', 1), (']', 1)])

    def test_find_separators_underlines(self):
        self._assert_separator_counts('foo_bar_1234_baz',
                                      [('_', 3)])

    def test_find_separators_dashes(self):
        self._assert_separator_counts('foo-bar-1234-baz',
                                      [('-', 3)])

    def test_find_separators_spaces(self):
        self._assert_separator_counts('foo bar 1234 baz',
                                      [(' ', 3)])

    def test_find_separators_underlines_and_dashes(self):
        self._assert_separator_counts('foo-bar_1234_baz',
                                      [('_', 2), ('-', 1)])

    def test_find_separators_underlines_dashes(self):
        self._assert_separator_counts('a-b c_d',
                                      [(' ', 1), ('-', 1), ('_', 1)])


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

    def test_find_separators_underlines_and_dashes(self):
        self._assert_main_separator('foo-bar_1234_baz', '_')

    def test_find_separators_underlines_dashes(self):
        self._assert_main_separator('a-b c_d', ' ')

    def test_find_main_separator(self):
        self._assert_main_separator('a b', ' ')
        self._assert_main_separator('a-b-c_d', '-')
        self._assert_main_separator('a-b', '-')
        self._assert_main_separator('a_b', '_')
        self._assert_main_separator('a--b', '-')
        self._assert_main_separator('a__b', '_')

        self._assert_main_separator('a b', ' ')
        self._assert_main_separator('shell-scripts.github', '-')
        self._assert_main_separator('Unison-OS-X-2.48.15.zip', '-')

        # TODO: Are we looking for field- or word-separator_counts..? (!?)
        self._assert_main_separator('2012-02-18-14-18_Untitled-meeting.log', '-')

    def test_resolve_tied_counts(self):
        assume_preferred_separator = '_'

        self._assert_main_separator('a-b c', ' ')
        self._assert_main_separator('a_b c', ' ')
        self._assert_main_separator('-a b', ' ')
        self._assert_main_separator('_a b', ' ')
        self._assert_main_separator('a-b c_d', ' ')
        self._assert_main_separator('a_b c-d', ' ')
        self._assert_main_separator('-a b_d', ' ')
        self._assert_main_separator('_a b-d', ' ')

        for given_string in [
            'a-b_c',
            'a_b-c',
            'a_-b',
            'a-_b',
            'a-b_c-d_e',
            'a_b-c_d-e',
            'a_-b-_c',
            'a-_b_-c',
            'a-_b',
            'a_-b',
        ]:
            self._assert_main_separator(given_string, assume_preferred_separator)

    # def test_get_seps_with_tied_counts(self):
    #     def _assert_separator_counts(test_input, expect):
    #         actual = FilenameTokenizer.get_seps_with_tied_counts(test_input)
    #         self.assertEqual(expect, actual)
    #
    #     _assert_separator_counts([('a', 2), ('b', 1)], expect=[])
    #     _assert_separator_counts([('a', 2), ('b', 2)], expect=['a', 'b'])
    #     _assert_separator_counts([('a', 2), ('b', 1), ('c', 1)], expect=['b', 'c'])
    #     _assert_separator_counts([('a', 2), ('b', 1), ('c', 1), ('d', 2)], expect=['a', 'b', 'c', 'd'])
    #     _assert_separator_counts([('a', 2), ('b', 1), ('c', 1), ('d', 1)], expect=['b', 'c', 'd'])
