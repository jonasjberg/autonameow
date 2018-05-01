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

from core.metadata.normalize import cleanup_full_title
from core.metadata.normalize import normalize_full_title


class TestNormalizeFullTitle(TestCase):
    def test_none(self):
        actual = normalize_full_title(None)
        self.assertEqual('', actual)

    def test_returns_trivial_input_as_is(self):
        actual = normalize_full_title('foo')
        self.assertEqual('foo', actual)

    def test_removes_noisy_characters(self):
        TESTDATA_GIVEN_EXPECT = [
            ('foo:', 'foo'),
            ('^~foo', 'foo'),
            ('fo%"o', 'foo'),
            ('fo%"o 123', 'foo 123'),
            ('foo: bar', 'foo bar'),
        ]
        for given, expect in TESTDATA_GIVEN_EXPECT:
            actual = normalize_full_title(given)
            self.assertEqual(expect, actual)

    def test_replaces_certain_characters(self):
        TESTDATA_GIVEN_EXPECT = [
            ('foo & bar', 'foo and bar'),
        ]
        for given, expect in TESTDATA_GIVEN_EXPECT:
            actual = normalize_full_title(given)
            self.assertEqual(expect, actual)

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
            actual = normalize_full_title(given)
            self.assertEqual(expect, actual)


class TestCleanupFullTitle(TestCase):
    def _assert_cleaned_up_title_is(self, expected, given):
        actual = cleanup_full_title(given)
        self.assertEqual(expected, actual)

    def test_returns_empty_string_given_none(self):
        self._assert_cleaned_up_title_is('', None)

    def test_returns_trivial_input_as_is(self):
        self._assert_cleaned_up_title_is('foo', 'foo')

    def test_replaces_certain_characters(self):
        TESTDATA_GIVEN_EXPECT = [
            ('foo & bar', 'foo and bar'),
        ]
        for given, expect in TESTDATA_GIVEN_EXPECT:
            self._assert_cleaned_up_title_is(expect, given)

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
            self._assert_cleaned_up_title_is(expect, given)

    def test_replaces_non_breaking_spaces(self):
        self._assert_cleaned_up_title_is('foo', '\xa0foo')
