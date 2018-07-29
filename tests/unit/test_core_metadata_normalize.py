# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from core.metadata.normalize import cleanup_full_title
from core.metadata.normalize import normalize_full_title


class TestNormalizeFullTitle(TestCase):
    def _assert_normalized_title(self, expected, given):
        actual = normalize_full_title(given)
        self.assertEqual(expected, actual)

    def test_none(self):
        self._assert_normalized_title('', None)

    def test_returns_trivial_input_as_is(self):
        self._assert_normalized_title('foo', 'foo')

    def test_removes_noisy_characters(self):
        TESTDATA_GIVEN_EXPECT = [
            ('foo:', 'foo'),
            ('^~foo', 'foo'),
            ('fo%"o', 'foo'),
            ('fo%"o 123', 'foo 123'),
            ('foo: bar', 'foo bar'),
        ]
        for given, expect in TESTDATA_GIVEN_EXPECT:
            self._assert_normalized_title(expect, given)

    def test_replaces_certain_characters(self):
        TESTDATA_GIVEN_EXPECT = [
            ('foo & bar', 'foo and bar'),
        ]
        for given, expect in TESTDATA_GIVEN_EXPECT:
            self._assert_normalized_title(expect, given)

    def test_returns_expected_string(self):
        TESTDATA_GIVEN_EXPECT = [
            ('foo:', 'foo'),
            ('foo: ', 'foo'),
            ('^~ foo', 'foo'),
            ('  fo%"o ', 'foo'),
            ('  fo%"o 123 ', 'foo 123'),
            ('  foo:  bar ', 'foo bar'),
        ]
        for given, expect in TESTDATA_GIVEN_EXPECT:
            self._assert_normalized_title(expect, given)

    def test_removes_trailing_file_extension(self):
        self._assert_normalized_title('probability theory', 'Probability Theory.djvu')
        self._assert_normalized_title('probability theory', 'Probability Theory.epub')

    def test_samples_from_actual_usage(self):
        self._assert_normalized_title('practical data analysis', 'Practical Data Analysis - ')


class TestCleanupFullTitle(TestCase):
    def _assert_cleaned_up_title(self, expected, given):
        actual = cleanup_full_title(given)
        self.assertEqual(expected, actual)

    def test_returns_empty_string_given_none(self):
        self._assert_cleaned_up_title('', None)

    def test_returns_trivial_input_as_is(self):
        self._assert_cleaned_up_title('foo', 'foo')

    def test_replaces_certain_characters(self):
        TESTDATA_GIVEN_EXPECT = [
            ('foo & bar', 'foo and bar'),
        ]
        for given, expect in TESTDATA_GIVEN_EXPECT:
            self._assert_cleaned_up_title(expect, given)

    def test_returns_expected_string(self):
        TESTDATA_GIVEN_EXPECT = [
            ('foo:', 'foo:'),
            ('foo: ', 'foo:'),
            ('^~ foo', '^~ foo'),
            ('  fo%"o ', 'fo%"o'),
            ('  fo%"o 123 ', 'fo%"o 123'),
            ('  foo:  bar ', 'foo: bar'),
        ]
        for given, expect in TESTDATA_GIVEN_EXPECT:
            self._assert_cleaned_up_title(expect, given)

    def test_replaces_non_breaking_spaces(self):
        self._assert_cleaned_up_title('foo', '\xa0foo')

    def test_removes_trailing_file_extension(self):
        self._assert_cleaned_up_title('Probability Theory', 'Probability Theory.djvu')
        self._assert_cleaned_up_title('Probability Theory', 'Probability Theory.epub')

    def test_samples_from_actual_usage(self):
        for given in [
            'Practical Data Analysis-',
            'Practical Data Analysis -',
            'Practical Data Analysis - ',
            'Practical Data Analysis--',
            'Practical Data Analysis --',
            'Practical Data Analysis -- ',
        ]:
            with self.subTest(given=given):
                self._assert_cleaned_up_title('Practical Data Analysis', given)
