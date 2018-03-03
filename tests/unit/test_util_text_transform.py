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
import re
from unittest import TestCase, skipIf

try:
    import unidecode
except ImportError:
    UNIDECODE_IS_NOT_AVAILABLE = True, 'Missing required module "unidecode"'
else:
    UNIDECODE_IS_NOT_AVAILABLE = False, ''

import unit.utils as uu
from core.exceptions import EncodingBoundaryViolation
from util.text.transform import (
    collapse_whitespace,
    html_unescape,
    indent,
    batch_regex_replace,
    normalize_unicode,
    remove_blacklisted_lines,
    remove_nonbreaking_spaces,
    remove_zerowidth_spaces,
    simplify_unicode,
    _strip_accents_homerolled,
    _strip_accents_unidecode,
    strip_ansiescape,
    urldecode,
)


class TestCollapseWhitespace(TestCase):
    def _check(self, given, expect):
        actual = collapse_whitespace(given)
        self.assertEqual(actual, expect)

    def test_returns_empty_as_is(self):
        self._check('', '')

        # Assumes that type-checks is handled elsewhere.
        self._check(None, None)
        self._check([], [])

    def test_raises_exception_given_non_string_types(self):
        with self.assertRaises(TypeError):
            _ = collapse_whitespace(['foo'])

        with self.assertRaises(TypeError):
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

    def test_collapses_multiple_spaces_with_newlines(self):
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


class TestIndent(TestCase):
    def test_invalid_arguments_raises_exception(self):
        def _assert_raises(exception_type, *args, **kwargs):
            with self.assertRaises(exception_type):
                indent(*args, **kwargs)

        _assert_raises(ValueError, None)
        _assert_raises(EncodingBoundaryViolation, b'')
        _assert_raises(ValueError, 'foo', amount=0)
        _assert_raises(TypeError, 'foo', amount=object())

        # TODO: Should raise 'TypeError' when given 'ch=1' (expects str)
        _assert_raises(EncodingBoundaryViolation, 'foo', amount=2, ch=1)
        _assert_raises(EncodingBoundaryViolation, 'foo', amount=2, ch=b'')
        _assert_raises(EncodingBoundaryViolation, 'foo', ch=b'')

    def test_indents_single_line(self):
        self.assertEqual(indent('foo'), '    foo')
        self.assertEqual(indent('foo bar'), '    foo bar')

    def test_indents_two_lines(self):
        self.assertEqual(indent('foo\nbar'), '    foo\n    bar')

    def test_indents_three_lines(self):
        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('    foo\n'
                  '      bar\n'
                  '    baz\n')
        self.assertEqual(indent(input_), expect)

    def test_indents_single_line_specified_amount(self):
        self.assertEqual(indent('foo', amount=1), ' foo')
        self.assertEqual(indent('foo', amount=2), '  foo')
        self.assertEqual(indent('foo', amount=3), '   foo')
        self.assertEqual(indent('foo', amount=4), '    foo')
        self.assertEqual(indent('foo bar', amount=2), '  foo bar')

    def test_indents_two_lines_specified_amount(self):
        self.assertEqual(indent('foo\nbar', amount=2), '  foo\n  bar')

    def test_indents_three_lines_specified_amount(self):
        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('  foo\n'
                  '    bar\n'
                  '  baz\n')
        self.assertEqual(indent(input_, amount=2), expect)

        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('   foo\n'
                  '     bar\n'
                  '   baz\n')
        self.assertEqual(indent(input_, amount=3), expect)

    def test_indents_single_line_specified_padding(self):
        self.assertEqual(indent('foo', ch='X'), 'XXXXfoo')
        self.assertEqual(indent('foo bar', ch='X'), 'XXXXfoo bar')

    def test_indents_two_lines_specified_padding(self):
        self.assertEqual(indent('foo\nbar', ch='X'),
                         'XXXXfoo\nXXXXbar')
        self.assertEqual(indent('foo\nbar', ch='Xj'),
                         'XjXjXjXjfoo\nXjXjXjXjbar')

    def test_indents_three_lines_specified_padding(self):
        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('XXXXfoo\n'
                  'XXXX  bar\n'
                  'XXXXbaz\n')
        self.assertEqual(indent(input_, ch='X'), expect)

        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('XjXjXjXjfoo\n'
                  'XjXjXjXj  bar\n'
                  'XjXjXjXjbaz\n')
        self.assertEqual(indent(input_, ch='Xj'), expect)

    def test_indents_text_single_line_specified_padding_and_amount(self):
        self.assertEqual(indent('foo', amount=1, ch='  '), '  foo')
        self.assertEqual(indent('foo', amount=2, ch='  '), '    foo')
        self.assertEqual(indent('foo', amount=1, ch=''), 'foo')
        self.assertEqual(indent('foo', amount=2, ch=''), 'foo')
        self.assertEqual(indent('foo', amount=3, ch=''), 'foo')
        self.assertEqual(indent('foo', amount=4, ch=''), 'foo')
        self.assertEqual(indent('foo', ch='X', amount=2), 'XXfoo')
        self.assertEqual(indent('foo bar', ch='X', amount=2),
                         'XXfoo bar')

    def test_indents_two_lines_specified_padding_and_amount(self):
        self.assertEqual(indent('foo\nbar', ch='X', amount=2),
                         'XXfoo\nXXbar')
        self.assertEqual(indent('foo\nbar', ch='X', amount=4),
                         'XXXXfoo\nXXXXbar')

    def test_indents_three_lines_specified_padding_and_amount(self):
        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('XXfoo\n'
                  'XX  bar\n'
                  'XXbaz\n')
        self.assertEqual(indent(input_, ch='X', amount=2), expect)

        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('XXXfoo\n'
                  'XXX  bar\n'
                  'XXXbaz\n')
        self.assertEqual(indent(input_, ch='X', amount=3), expect)


class TestNormalizeUnicode(TestCase):
    def _aE(self, test_input, expected):
        actual = normalize_unicode(test_input)
        self.assertEqual(actual, expected)

    def test_raises_exception_given_bad_input(self):
        def _aR(test_input):
            with self.assertRaises(TypeError):
                normalize_unicode(test_input)

        _aR(None)
        _aR([])
        _aR(['foo'])
        _aR({})
        _aR({'foo': 'bar'})
        _aR(object())
        _aR(1)
        _aR(1.0)
        _aR(b'')
        _aR(b'foo')

    def test_returns_expected(self):
        self._aE('', '')
        self._aE(' ', ' ')
        self._aE('foo', 'foo')
        self._aE('...', '...')

    def test_simplifies_three_periods(self):
        self._aE('…', '...')
        self._aE(' …', ' ...')
        self._aE(' … ', ' ... ')

    def test_replaces_dashes(self):
        self._aE('\u2212', '-')
        self._aE('\u2013', '-')
        self._aE('\u2014', '-')
        self._aE('\u05be', '-')
        self._aE('\u2010', '-')
        self._aE('\u2015', '-')
        self._aE('\u30fb', '-')

    def test_replaces_overlines(self):
        self._aE('\u0305', '-')
        self._aE('\u203e', '-')


class TestRemoveNonBreakingSpaces(TestCase):
    def test_remove_non_breaking_spaces_removes_expected(self):
        non_breaking_space = '\xa0'
        actual = remove_nonbreaking_spaces(
            'foo' + uu.decode(non_breaking_space) + 'bar'
        )
        expected = 'foo bar'
        self.assertEqual(expected, actual)

    def test_remove_non_breaking_spaces_removes_expected_2(self):
        actual = remove_nonbreaking_spaces('foo\u00A0bar')
        self.assertEqual('foo bar', actual)

    def test_remove_non_breaking_spaces_returns_expected(self):
        expected = 'foo bar'
        actual = remove_nonbreaking_spaces('foo bar')
        self.assertEqual(actual, expected)

    def test_remove_non_breaking_spaces_handles_empty_string(self):
        expected = ''
        actual = remove_nonbreaking_spaces('')
        self.assertEqual(actual, expected)


class TestZeroWidthSpaces(TestCase):
    def test_removes_expected(self):
        actual = remove_zerowidth_spaces('foo\u200Bbar')
        self.assertEqual('foobar', actual)

    def test_passthrough(self):
        expected = 'foo bar'
        actual = remove_zerowidth_spaces('foo bar')
        self.assertEqual(expected, actual)

    def test_handles_empty_string(self):
        actual = remove_zerowidth_spaces('')
        self.assertEqual('', actual)


class TestStripAnsiEscape(TestCase):
    def _aE(self, test_input, expected):
        actual = strip_ansiescape(test_input)
        self.assertEqual(actual, expected)

    def test_strips_ansi_escape_codes(self):
        self._aE('', '')
        self._aE('a', 'a')
        self._aE('[30m[44mautonameow[49m[39m', 'autonameow')


class TestUrlDecode(TestCase):
    def test_returns_expected_given_valid_arguments(self):
        def _aE(test_input, expected):
            actual = urldecode(test_input)
            self.assertEqual(expected, actual)

        _aE('%2C', ',')
        _aE('%20', ' ')
        _aE('f.bar?t=%D0%B7%D0%B0%D1%89%D0%B8%D1%82%D0%B0', 'f.bar?t=защита')


class TestHtmlUnescape(TestCase):
    def test_pass_through(self):
        actual = html_unescape('foo')
        self.assertEqual('foo', actual)

    def test_returns_expected_given_valid_arguments(self):
        def _aE(test_input, expected):
            actual = html_unescape(test_input)
            self.assertEqual(expected, actual)

        _aE('&amp;', '&')
        _aE('Gibson &amp; Associates', 'Gibson & Associates')


class TestSimplifyUnicode(TestCase):
    def _assert_strips(self, given, expect):
        actual = simplify_unicode(given)
        self.assertEqual(expect, actual)

    def test_returns_none_as_is(self):
        self._assert_strips(None, None)

    def test_pass_through(self):
        self._assert_strips(given='', expect='')
        self._assert_strips(given=' ', expect=' ')
        self._assert_strips(given='foo', expect='foo')

    def test_strips_accent(self):
        self._assert_strips(given='ç', expect='c')
        self._assert_strips(given='Fooçalbar', expect='Foocalbar')
        self._assert_strips(given='Montréal', expect='Montreal')
        self._assert_strips(given=' über, 12.89', expect=' uber, 12.89')

        # TODO: Handle "strokes" like 'ø'.
        # self._assert_strips(given='ø', expect='o')

    def test_strips_accents(self):
        self._assert_strips(given='Mère, Françoise, noël, 889',
                            expect='Mere, Francoise, noel, 889')


class TestStripAccentsHomeRolled(TestCase):
    def _assert_strips(self, given, expect):
        actual = _strip_accents_homerolled(given)
        self.assertEqual(expect, actual)

    def test_pass_through(self):
        self._assert_strips(given='', expect='')
        self._assert_strips(given=' ', expect=' ')
        self._assert_strips(given='foo', expect='foo')

    def test_strips_accent(self):
        self._assert_strips(given='ç', expect='c')
        self._assert_strips(given='Fooçalbar', expect='Foocalbar')
        self._assert_strips(given='Montréal', expect='Montreal')
        self._assert_strips(given=' über, 12.89', expect=' uber, 12.89')

        # TODO: Handle "strokes" like 'ø'.
        # self._assert_strips(given='ø', expect='o')

    def test_strips_accents(self):
        self._assert_strips(given='Mère, Françoise, noël, 889',
                            expect='Mere, Francoise, noel, 889')


@skipIf(*UNIDECODE_IS_NOT_AVAILABLE)
class TestStripAccentsUnidecode(TestCase):
    def _assert_strips(self, given, expect):
        actual = _strip_accents_unidecode(given)
        self.assertEqual(expect, actual)

    def test_pass_through(self):
        self._assert_strips(given='', expect='')
        self._assert_strips(given=' ', expect=' ')
        self._assert_strips(given='foo', expect='foo')

    def test_strips_accent(self):
        self._assert_strips(given='ç', expect='c')
        self._assert_strips(given='Fooçalbar', expect='Foocalbar')
        self._assert_strips(given='Montréal', expect='Montreal')
        self._assert_strips(given=' über, 12.89', expect=' uber, 12.89')

        # TODO: Handle "strokes" like 'ø'.
        # self._assert_strips(given='ø', expect='o')

    def test_strips_accents(self):
        self._assert_strips(given='Mère, Françoise, noël, 889',
                            expect='Mere, Francoise, noel, 889')


class TestBatchRegexReplace(TestCase):
    def _check_call(self, given, expect, regex_replacements):
        actual = batch_regex_replace(regex_replacements, given)
        self.assertEqual(expect, actual)

    def test_one_replacement(self):
        reps = [
            (re.compile(r'Foo'), 'Mjao')
        ]
        self._check_call(given='Foo Bar', expect='Mjao Bar',
                          regex_replacements=reps)

    def test_two_replacements(self):
        reps = [
            (re.compile(r'Foo'), 'Mjao'),
            (re.compile(r' '), 'X'),
        ]
        self._check_call(given='Foo Bar', expect='MjaoXBar',
                          regex_replacements=reps)

    def test_three_replacements(self):
        reps = [
            (re.compile(r'Foo'), 'Mjao'),
            (re.compile(r' '), 'X'),
            (re.compile(r'(bar){2,}'), 'bar'),
        ]
        self._check_call(given='Foo barbar Bar', expect='MjaoXbarXBar',
                          regex_replacements=reps)

    def test_perform_longer_replacements_first(self):
        reps = [
            (re.compile(r'In A'), 'in a'),
            (re.compile(r'In'), 'in'),
            (re.compile(r'A'), 'a'),
            (re.compile(r'The'), 'the'),
        ]
        for reps_order in itertools.permutations(reps):
            with self.subTest(replacements=reps_order):
                self._check_call(given='The Cat In A Hat',
                                  expect='the Cat in a Hat',
                                  regex_replacements=reps_order)

    def test_perform_longer_replacements_first_with_word_boundaries(self):
        reps = [
            (re.compile(r'\bIn A\b'), 'in a'),
            (re.compile(r'\bIn\b'), 'in'),
            (re.compile(r'\bA\b'), 'a'),
            (re.compile(r'\bThe\b'), 'the'),
        ]
        for reps_order in itertools.permutations(reps):
            with self.subTest(replacements=reps_order):
                self._check_call(given='The Cat In A Hat InA The FlAt',
                                  expect='the Cat in a Hat InA the FlAt',
                                  regex_replacements=reps_order)

    def test_does_not_exhibit_inconsistent_behaviour(self):
        reps = [
            (re.compile(r'\bThe\b'), 'the'),
            (re.compile(r'\bAnd\b'), 'and'),
            (re.compile(r'\bIn\b'), 'in'),
            (re.compile(r'\bOf\b'), 'of'),
            (re.compile(r'\bIn A\b'), 'in a'),
        ]
        for reps_order in itertools.permutations(reps):
            with self.subTest(replacements=reps_order):
                self._check_call(given='a cat And a Dog In A thing in The HAT',
                                  expect='a cat and a Dog in a thing in the HAT',
                                  regex_replacements=reps_order)

    def test_replaces_single_quote(self):
        self._check_call(given='Foo\'s Bar', expect='Foos Bar',
                          regex_replacements=[(re.compile(r'[\']'), '')])
        self._check_call(given='Foo\'s Bar', expect='Foos Bar',
                          regex_replacements=[(re.compile(r"'"), '')])
        self._check_call(given='Foo\'s Bar', expect='Foos Bar',
                          regex_replacements=[(re.compile("'"), '')])


class TestRemoveBlacklistedLines(TestCase):
    def _assert_that_it_returns(self, expected, given_text, given_blacklist):
        actual = remove_blacklisted_lines(given_text, given_blacklist)
        self.assertEqual(expected, actual)

    def test_removes_single_blacklisted_line(self):
        self._assert_that_it_returns(
            expected='''Foo Bar: A Modern Approach
Foo Bar''',
            given_text='''Foo Bar: A Modern Approach
This page intentionally left blank
Foo Bar''',
            given_blacklist=frozenset(['This page intentionally left blank'])
        )
