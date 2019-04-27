# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from analyzers.analyze_document import find_titles_in_text


class TestFindTitlesInText(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.EXAMPLE_TEXT = '''
Foo

bar

baz Foo

meow
'''

    def _assert_that_it_returns(self, expected, given_num_lines_to_search):
        actual = find_titles_in_text(self.EXAMPLE_TEXT, given_num_lines_to_search)
        for actual, expect in zip(actual, expected):
            actual_text, actual_score = actual
            expect_text, expect_score = expect
            self.assertEqual(expect_text, actual_text)
            self.assertAlmostEqual(expect_score, actual_score)

    def test_returns_expected_when_searching_one_line(self):
        self._assert_that_it_returns(
            expected=[
                ('Foo', 1.0),
            ],
            given_num_lines_to_search=1
        )

    def test_returns_expected_when_searching_two_lines(self):
        self._assert_that_it_returns(
            expected=[
                ('Foo', 1.0),
                ('bar', 0.5),
            ],
            given_num_lines_to_search=2
        )

    def test_returns_expected_when_searching_three_lines(self):
        self._assert_that_it_returns(
            expected=[
                ('Foo', 1.0),
                ('bar', 0.66666666),
                ('baz Foo', 0.3333333),
            ],
            given_num_lines_to_search=3
        )

    def test_returns_expected_when_searching_four_lines(self):
        self._assert_that_it_returns(
            expected=[
                ('Foo', 1.0),
                ('bar', 0.75),
                ('baz Foo', 0.5),
                ('meow', 0.25),
            ],
            given_num_lines_to_search=4
        )
