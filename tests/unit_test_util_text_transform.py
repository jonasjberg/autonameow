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

from util import encoding as enc
from util.text.transform import (
    collapse_whitespace,
    remove_nonbreaking_spaces,
    strip_ansiescape
)


class TestCollapseWhitespace(TestCase):
    def _check(self, given, expect):
        actual = collapse_whitespace(given)
        self.assertEqual(expect, actual)

    def test_returns_empty_as_is(self):
        self._check('', '')

        # Assumes that type-checks is handled elsewhere.
        self._check(None, None)
        self._check([], [])

    def test_raises_exception_given_non_string_types(self):
        with self.assertRaises(AssertionError):
            _ = collapse_whitespace(['foo'])

        with self.assertRaises(AssertionError):
            _ = collapse_whitespace(object())

    def test_returns_string_without_whitespace_as_is(self):
        self._check('foo', 'foo')

    def test_does_not_strip_trailing_leading_whitespace(self):
        self._check('foo ', 'foo ')
        self._check(' foo', ' foo')
        self._check(' foo ', ' foo ')
        self._check(' foo bar', ' foo bar')
        self._check(' foo bar ', ' foo bar ')

    def test_does_not_change_single_newline(self):
        self._check('foo\n', 'foo\n')
        self._check('\nfoo', '\nfoo')
        self._check('\nfoo\n', '\nfoo\n')
        self._check('\nfoo bar\n', '\nfoo bar\n')
        self._check('\nfoo\nbar\n', '\nfoo\nbar\n')

    def test_does_not_change_single_newline_and_space(self):
        self._check('foo\n ', 'foo\n ')
        self._check(' \nfoo', ' \nfoo')
        self._check(' \nfoo\n ', ' \nfoo\n ')
        self._check(' \nfoo bar\n', ' \nfoo bar\n')
        self._check(' \nfoo\nbar\n', ' \nfoo\nbar\n')

        self._check('\n foo', '\n foo')
        self._check('\n foo\n ', '\n foo\n ')
        self._check('\n foo bar\n', '\n foo bar\n')
        self._check('\n foo\nbar\n', '\n foo\nbar\n')

    def test_does_not_change_newlines_and_space(self):
        self._check('foo\n\n ', 'foo\n\n ')
        self._check(' \n\nfoo', ' \n\nfoo')
        self._check(' \n\nfoo\n ', ' \n\nfoo\n ')
        self._check(' \n\nfoo bar\n', ' \n\nfoo bar\n')
        self._check(' \n\nfoo\nbar\n', ' \n\nfoo\nbar\n')

        self._check('\n\n foo', '\n\n foo')
        self._check('\n\n foo\n ', '\n\n foo\n ')
        self._check('\n\n foo bar\n', '\n\n foo bar\n')
        self._check('\n\n foo\nbar\n', '\n\n foo\nbar\n')

    def test_collapses_multiple_spaces(self):
        self._check('foo  ', 'foo ')
        self._check('foo   ', 'foo ')
        self._check('foo    ', 'foo ')
        self._check('  foo', ' foo')
        self._check('   foo', ' foo')
        self._check('    foo', ' foo')
        self._check('foo  bar', 'foo bar')
        self._check('foo   bar', 'foo bar')
        self._check('foo    bar', 'foo bar')
        self._check('foo  bar  ', 'foo bar ')
        self._check('foo   bar   ', 'foo bar ')
        self._check('foo    bar    ', 'foo bar ')
        self._check('  foo  bar  ', ' foo bar ')
        self._check('   foo   bar   ', ' foo bar ')
        self._check('    foo    bar    ', ' foo bar ')

    def test_collapses_multiple_spaces_with_newline(self):
        self._check('foo  \n', 'foo \n')
        self._check('foo   \n', 'foo \n')
        self._check('foo    \n', 'foo \n')
        self._check('  foo\n', ' foo\n')
        self._check('   foo\n', ' foo\n')
        self._check('    foo\n', ' foo\n')
        self._check('foo  bar\n', 'foo bar\n')
        self._check('foo   bar\n', 'foo bar\n')
        self._check('foo    bar\n', 'foo bar\n')
        self._check('foo  bar  \n', 'foo bar \n')
        self._check('foo   bar   \n', 'foo bar \n')
        self._check('foo    bar    \n', 'foo bar \n')
        self._check('  foo  bar  \n', ' foo bar \n')
        self._check('   foo   bar   \n', ' foo bar \n')
        self._check('    foo    bar    \n', ' foo bar \n')

    def test_collapsees_multiple_spaces_with_newlines(self):
        self._check('foo   \n   bar\n   ', 'foo \n bar\n ')
        self._check('foo   \n   bar   \n', 'foo \n bar \n')

    def test_does_not_replace_single_tab_with_space(self):
        self._check('foo\t', 'foo\t')
        self._check('\tfoo', '\tfoo')
        self._check('\tfoo\t', '\tfoo\t')

    def test_replaces_single_tab_and_single_space_with_space(self):
        self._check('foo \t', 'foo ')
        self._check('\t foo', ' foo')
        self._check('\t foo \t', ' foo ')

    def test_replaces_tabs_and_spaces_with_single_space(self):
        self._check('foo  \t', 'foo ')
        self._check('\t  foo', ' foo')
        self._check('\t  foo  \t', ' foo ')
        self._check('foo \t\t', 'foo ')
        self._check('\t\t foo', ' foo')
        self._check('\t\t foo \t\t', ' foo ')

        self._check('foo  \t bar', 'foo bar')
        self._check('bar\t  foo', 'bar foo')
        self._check('bar\t  foo  \t', 'bar foo ')
        self._check('foo \t\tbar', 'foo bar')
        self._check('bar\t\t foo', 'bar foo')
        self._check('bar\t\t foo \t\t', 'bar foo ')

    def test_collapses_multiple_tabs(self):
        self._check('foo\t\t', 'foo ')
        self._check('foo\t\t\t', 'foo ')
        self._check('\t\tfoo', ' foo')
        self._check('\t\t\tfoo', ' foo')

        self._check('foo\t\tbar', 'foo bar')
        self._check('foo\t\t\tbar', 'foo bar')
        self._check('\t\tfoo bar', ' foo bar')
        self._check('\t\t\tfoo bar', ' foo bar')


class TestRemoveNonBreakingSpaces(TestCase):
    def test_remove_non_breaking_spaces_removes_expected(self):
        expected = 'foo bar'

        non_breaking_space = '\xa0'
        actual = remove_nonbreaking_spaces(
            'foo' + enc.decode_(non_breaking_space) + 'bar'
        )
        self.assertEqual(expected, actual)

    def test_remove_non_breaking_spaces_returns_expected(self):
        expected = 'foo bar'
        actual = remove_nonbreaking_spaces('foo bar')
        self.assertEqual(expected, actual)

    def test_remove_non_breaking_spaces_handles_empty_string(self):
        expected = ''
        actual = remove_nonbreaking_spaces('')
        self.assertEqual(expected, actual)


class TestStripAnsiEscape(TestCase):
    def _aE(self, test_input, expected):
        actual = strip_ansiescape(test_input)
        self.assertEqual(actual, expected)

    def test_strips_ansi_escape_codes(self):
        self._aE('', '')
        self._aE('a', 'a')
        self._aE('[30m[44mautonameow[49m[39m', 'autonameow')
