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

from unit import constants as uuconst
from util.text.filter import RegexFilter
from util.text.filter import RegexLineFilter


def _get_regex_filter(*args, **kwargs):
    return RegexFilter(*args, **kwargs)


def _get_regex_line_filter(*args, **kwargs):
    return RegexLineFilter(*args, **kwargs)


class TestRegexFilter(TestCase):
    def test_returns_compiled_regexes_when_passing_valid_args_to_init(self):
        for given in [
            '',
            [''],
            ['', ''],
            ['a', 'b'],
            ['.*', 'b?'],
            [r'.*', r'b?'],
            ['[fF]oo', '.*a.*'],
            [r'[fF]oo', r'.*a.*'],
        ]:
            f = _get_regex_filter(given)
            for actual_regex in f.regexes:
                self.assertIsInstance(actual_regex, uuconst.BUILTIN_REGEX_TYPE)

    def test_raises_assertion_error_when_passing_bad_args_to_init(self):
        for given_expressions in [
            [None],
            [r'[fF]oo', None],
            [r'[fF]oo', 1],
            [r'[fF]oo', []],
        ]:
            with self.subTest(given=given_expressions):
                with self.assertRaises(AssertionError):
                    _ = _get_regex_filter(given_expressions)

    def test_raises_encoding_violation_when_bad_byte_strings_to_init(self):
        for given_expressions in [
            [rb'[fF]oo'],
            [rb'[fF]oo', 'bar'],
            [b'[fF]oo'],
            [b'[fF]oo', 'bar'],
        ]:
            with self.subTest(given=given_expressions):
                with self.assertRaises(AssertionError):
                    _ = _get_regex_filter(given_expressions)

    def test_len_is_zero_when_passing_empty_list_to_init(self):
        f = _get_regex_filter(list())
        self.assertEqual(0, len(f))

    def test_len_matches_number_of_compiled_regexes_passing_list_to_init(self):
        f = _get_regex_filter([r'[fF]oo', r'.*a.*'])
        self.assertEqual(2, len(f))

    def test_len_matches_number_of_compiled_regexes_passing_str_to_init(self):
        f = _get_regex_filter(r'[fF]oo')
        self.assertEqual(1, len(f))

    def test_len_matches_number_of_unique_compiled_regexes(self):
        f = _get_regex_filter([r'[fF]oo', r'.*', r'.*'])
        self.assertEqual(2, len(f))

    def test_call_returns_expected_when_called_with_unicode_strings(self):
        f = _get_regex_filter(r'X?fo.*')
        for given, expected in [
            ('bar',      'bar'),
            ('Foo',      'Foo'),
            ('Afo',      'Afo'),
            ('Xfo',      None),
            ('fo',       None),
            ('foo',      None),
            ('foo\nbar', None),
        ]:
            with self.subTest(given=given):
                actual = f(given)
                self.assertEqual(expected, actual)

    def test_call_returns_expected_when_called_with_list_of_strings(self):
        f = _get_regex_filter(r'X?fo.*')
        for given, expected in [
            (['bar'],      ['bar']),
            (['Foo'],      ['Foo']),
            (['Afo'],      ['Afo']),
            (['Xfo'],      []),
            (['fo'],       []),
            (['foo'],      []),
            (['foo\nbar'], []),

            (['foo', 'bar', 'Xfoo'],  ['bar']),
            (['bar', 'Foo'],          ['bar', 'Foo']),
            (['Afo', 'Xfoo'],         ['Afo']),
            (['fo', 'foooo'],         []),
        ]:
            with self.subTest(given=given):
                actual = f(given)
                self.assertEqual(expected, actual)

    def test_call_returns_expected_when_called_with_sets_of_strings(self):
        f = _get_regex_filter(r'X?fo.*')
        for given, expected in [
            ({'bar'},      {'bar'}),
            ({'Fo'},       {'Fo'}),
            ({'Foo'},      {'Foo'}),
            ({'fo'},       set([])),
            ({'foo'},      set([])),
            ({'foo\nbar'}, set([])),

            ({'foo', 'bar', 'Xfoo'}, {'bar'}),
            ({'bar', 'Foo'},         {'bar', 'Foo'}),
            ({'Afo', 'Xfoo'},        {'Afo'}),
            ({'fo', 'foooo'},        set([])),
        ]:
            with self.subTest(given=given):
                actual = f(given)
                self.assertEqual(expected, actual)


class TestRegexLineFilter(TestCase):
    def test_replaces_expected_with_ignore_case_true(self):
        regexes = [
            r'^[\.=-]+$',
            r'for your convenience .* has placed some of the front',
        ]
        f = _get_regex_line_filter(regexes, ignore_case=True)
        actual = f('For your convenience Foobar has placed some of the front')
        expected = None
        self.assertEqual(expected, actual)

    def test_replaces_expected_multiline_with_ignore_case_true(self):
        f = _get_regex_line_filter(r'[=A-]+', ignore_case=True)
        actual = f('''----------
MEOW MEOW
==========
aaa
----------
BBB
''')
        expected = '''MEOW MEOW
BBB
'''
        self.assertEqual(expected, actual)

    def test_replaces_expected_multiline_with_ignore_case_false(self):
        f = _get_regex_line_filter(r'[=A-]+', ignore_case=False)
        actual = f('''----------
MEOW MEOW
==========
aaa
----------
BBB
''')
        expected = '''MEOW MEOW
aaa
BBB
'''
        self.assertEqual(expected, actual)


class TestRegexLineFilterTestsStolenFromRemoveBlacklistedReLines(TestCase):
    def _assert_that_it_returns(self, expected, given_text, expressions):
        f = _get_regex_line_filter(expressions)
        actual = f(given_text)
        self.assertEqual(expected, actual)

    def test_returns_text_as_is_if_blacklist_is_empty_list(self):
        self._assert_that_it_returns(
            expected='foo\nbar',
            given_text='foo\nbar',
            expressions=[]
        )

    def test_removes_one_matching_blacklisted_line(self):
        self._assert_that_it_returns(
            expected='''
Foo Bar: A Modern Approach
Foo Bar
''',
            given_text='''
Foo Bar: A Modern Approach
This page intentionally left blank
Foo Bar
''',
            expressions=[r'.*intentionally.*']
        )

    def test_removes_single_matching_line_and_keeps_line_breaks(self):
        self._assert_that_it_returns(
            expected='''
Foo Bar: A Modern Approach


a

b
''',
            given_text='''
Foo Bar: A Modern Approach

This page intentionally left blank

a

b
''',
            expressions=['.*intentionally.*']
        )

    def test_removes_one_matching_line_with_one_blacklist_regex(self):
        self._assert_that_it_returns(
            expected='''
a
b

c
''',
            given_text='''
a
b
MEOW

c
''',
            expressions=['M..W']
        )

    def test_removes_multiple_matching_lines_with_one_blacklist_regex(self):
        self._assert_that_it_returns(
            expected='''
a
b

c
''',
            given_text='''
a
MEOW
MEOW
b
MEOW

c
MEOW
''',
            expressions=['M.*W']
        )

    def test_removes_matching_lines_with_two_blacklist_regexes(self):
        self._assert_that_it_returns(
            expected='''
a

c
''',
            given_text='''
a
MEOW

c
''',
            expressions=['M.*W', 'b']
        )

    def test_removes_matching_lines_with_multiple_blacklist_regexes(self):
        self._assert_that_it_returns(
            expected='''
a MEOW

''',
            given_text='''
a MEOW
MEOW
c
MEOW
b
MEOW

cat
MEOW
''',
            expressions=['M.*', 'b', 'c.*']
        )
