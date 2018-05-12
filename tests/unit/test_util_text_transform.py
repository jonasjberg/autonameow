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
from unittest import skipIf, TestCase

try:
    import unidecode
except ImportError:
    UNIDECODE_IS_NOT_AVAILABLE = True, 'Missing required module "unidecode"'
else:
    UNIDECODE_IS_NOT_AVAILABLE = False, ''

import unit.utils as uu
from util.text.transform import batch_regex_replace
from util.text.transform import collapse_whitespace
from util.text.transform import extract_digits
from util.text.transform import html_unescape
from util.text.transform import indent
from util.text.transform import normalize_unicode
from util.text.transform import normalize_whitespace
from util.text.transform import remove_blacklisted_lines
from util.text.transform import remove_nonbreaking_spaces
from util.text.transform import remove_zerowidth_spaces
from util.text.transform import simplify_unicode
from util.text.transform import strip_single_space_lines
from util.text.transform import truncate_text
from util.text.transform import urldecode
from util.text.transform import _strip_accents_homerolled
from util.text.transform import _strip_accents_unidecode


class TestCollapseWhitespace(TestCase):
    def _check(self, given, expect):
        actual = collapse_whitespace(given)
        self.assertEqual(actual, expect)

    def test_returns_empty_values_as_is(self):
        self._check('', '')
        self._check(None, None)
        self._check([], [])

    def test_raises_exception_given_non_string_types(self):
        for bad_input in [
            object(),
            b'foo',
            ['foo'],
        ]:
            with self.assertRaises(AssertionError):
                _ = collapse_whitespace(bad_input)

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


class TestStripSingleSpaceLines(TestCase):
    def _assert_returns(self, expect, given):
        actual = strip_single_space_lines(given)
        self.assertEqual(expect, actual)

    def test_returns_line_with_single_character_as_is(self):
        self._assert_returns('A', given='A')

    def test_returns_lines_with_one_character_per_line_as_is(self):
        self._assert_returns('A\nB', given='A\nB')
        self._assert_returns('A\nB\n', given='A\nB\n')

    def test_removes_line_containing_single_space_only(self):
        self._assert_returns('', given=' ')
        self._assert_returns('\n', given=' \n')

    def test_removes_lines_containing_single_space_only(self):
        self._assert_returns('\n', given=' \n')

    def test_removes_single_space_lines_and_returns_others_as_is(self):
        self._assert_returns('\nA', given=' \nA')
        self._assert_returns('\nA\n', given=' \nA\n')
        self._assert_returns('A\n\nB\n', given='A\n \nB\n')
        self._assert_returns('\nX\n', given=' \nX\n')


class TestNormalizeWhitespace(TestCase):
    def _assert_returns(self, expect, given):
        actual = normalize_whitespace(given)
        self.assertEqual(expect, actual)

    def test_returns_empty_values_as_is(self):
        for expect, given in [
            ('', ''),

            # Pass through empty/None/False values.
            (None, None),
            ([], []),
        ]:
            self._assert_returns(expect, given)

    def test_raises_exception_given_non_string_types(self):
        for bad_input in [
            object(),
            b'foo',
            ['foo'],
        ]:
            with self.assertRaises(AssertionError):
                _ = normalize_whitespace(bad_input)

    def test_returns_string_without_whitespace_as_is(self):
        self._assert_returns('foo', 'foo')

    def test_does_not_strip_trailing_leading_whitespace(self):
        for expected, given in [
            ('foo ', 'foo '),
            (' foo', ' foo'),
            (' foo ', ' foo '),
            (' foo bar', ' foo bar'),
            (' foo bar ', ' foo bar ')
        ]:
            self._assert_returns(expected, given)

    def test_does_not_change_single_newline(self):
        for expected, given in [
            ('foo\n', 'foo\n'),
            ('\nfoo', '\nfoo'),
            ('\nfoo\n', '\nfoo\n'),
            ('\nfoo bar\n', '\nfoo bar\n'),
            ('\nfoo\nbar\n', '\nfoo\nbar\n')
        ]:
            self._assert_returns(expected, given)

    def test_does_not_change_single_newline_and_space(self):
        for expected, given in [
            ('foo\n ', 'foo\n '),
            (' \nfoo', ' \nfoo'),
            (' \nfoo\n ', ' \nfoo\n '),
            (' \nfoo bar\n', ' \nfoo bar\n'),
            (' \nfoo\nbar\n', ' \nfoo\nbar\n'),

            ('\n foo', '\n foo'),
            ('\n foo\n ', '\n foo\n '),
            ('\n foo bar\n', '\n foo bar\n'),
            ('\n foo\nbar\n', '\n foo\nbar\n'),
        ]:
            self._assert_returns(expected, given)

    def test_does_not_change_newlines_and_space(self):
        for expected, given in [
            ('foo\n\n ', 'foo\n\n '),
            (' \n\nfoo', ' \n\nfoo'),
            (' \n\nfoo\n ', ' \n\nfoo\n '),
            (' \n\nfoo bar\n', ' \n\nfoo bar\n'),
            (' \n\nfoo\nbar\n', ' \n\nfoo\nbar\n'),

            ('\n\n foo', '\n\n foo'),
            ('\n\n foo\n ', '\n\n foo\n '),
            ('\n\n foo bar\n', '\n\n foo bar\n'),
            ('\n\n foo\nbar\n', '\n\n foo\nbar\n'),
        ]:
            self._assert_returns(expected, given)

    def test_collapses_multiple_spaces(self):
        self._assert_returns('foo ', given='foo  ')
        self._assert_returns('foo ', given='foo   ')
        self._assert_returns('foo ', given='foo    ')
        self._assert_returns(' foo', given='  foo')
        self._assert_returns(' foo', given='   foo')
        self._assert_returns(' foo', given='    foo')
        self._assert_returns('foo bar', given='foo  bar')
        self._assert_returns('foo bar', given='foo   bar')
        self._assert_returns('foo bar', given='foo    bar')
        self._assert_returns('foo bar ', given='foo  bar  ')
        self._assert_returns('foo bar ', given='foo   bar   ')
        self._assert_returns('foo bar ', given='foo    bar    ')
        self._assert_returns(' foo bar ', given='  foo  bar  ')
        self._assert_returns(' foo bar ', given='   foo   bar   ')
        self._assert_returns(' foo bar ', given='    foo    bar    ')

    def test_collapses_multiple_spaces_with_newline(self):
        self._assert_returns('foo \n', given='foo  \n')
        self._assert_returns('foo \n', given='foo   \n')
        self._assert_returns('foo \n', given='foo    \n')
        self._assert_returns(' foo\n', given='  foo\n')
        self._assert_returns(' foo\n', given='   foo\n')
        self._assert_returns(' foo\n', given='    foo\n')
        self._assert_returns('foo bar\n', given='foo  bar\n')
        self._assert_returns('foo bar\n', given='foo   bar\n')
        self._assert_returns('foo bar\n', given='foo    bar\n')
        self._assert_returns('foo bar \n', given='foo  bar  \n')
        self._assert_returns('foo bar \n', given='foo   bar   \n')
        self._assert_returns('foo bar \n', given='foo    bar    \n')
        self._assert_returns(' foo bar \n', given='  foo  bar  \n')
        self._assert_returns(' foo bar \n', given='   foo   bar   \n')
        self._assert_returns(' foo bar \n', given='    foo    bar    \n')

    def test_collapses_multiple_spaces_with_newlines(self):
        self._assert_returns('foo \n bar\n ', given='foo   \n   bar\n   ')
        self._assert_returns('foo \n bar \n', given='foo   \n   bar   \n')

    def test_replaces_single_tab_with_space(self):
        self._assert_returns('foo ', given='foo\t')
        self._assert_returns(' foo', given='\tfoo')
        self._assert_returns(' foo ', given='\tfoo\t')

    def test_replaces_single_tab_and_single_space_with_space(self):
        self._assert_returns('foo ', given='foo \t')
        self._assert_returns(' foo', given='\t foo')
        self._assert_returns(' foo ', given='\t foo \t')

    def test_replaces_tabs_and_spaces_with_single_space(self):
        self._assert_returns('foo ', given='foo  \t')
        self._assert_returns(' foo', given='\t  foo')
        self._assert_returns(' foo ', given='\t  foo  \t')
        self._assert_returns('foo ', given='foo \t\t')
        self._assert_returns(' foo', given='\t\t foo')
        self._assert_returns(' foo ', given='\t\t foo \t\t')

        self._assert_returns('foo bar', given='foo  \t bar')
        self._assert_returns('bar foo', given='bar\t  foo')
        self._assert_returns('bar foo ', given='bar\t  foo  \t')
        self._assert_returns('foo bar', given='foo \t\tbar')
        self._assert_returns('bar foo', given='bar\t\t foo')
        self._assert_returns('bar foo ', given='bar\t\t foo \t\t')

    def test_collapses_multiple_tabs(self):
        self._assert_returns('foo ', given='foo\t\t')
        self._assert_returns('foo ', given='foo\t\t\t')
        self._assert_returns(' foo', given='\t\tfoo')
        self._assert_returns(' foo', given='\t\t\tfoo')

        self._assert_returns('foo bar', given='foo\t\tbar')
        self._assert_returns('foo bar', given='foo\t\t\tbar')
        self._assert_returns(' foo bar', given='\t\tfoo bar')
        self._assert_returns(' foo bar', given='\t\t\tfoo bar')

    def test_replaces_tabs_and_spaces_with_single_space_keeps_newlines(self):
        self._assert_returns('foo \n', given='foo  \t\n')
        self._assert_returns(' foo\n', given='\t  foo\n')
        self._assert_returns(' foo \n', given='\t  foo  \t\n')
        self._assert_returns('foo \n', given='foo \t\t\n')
        self._assert_returns(' foo\n', given='\t\t foo\n')
        self._assert_returns(' foo \n', given='\t\t foo \t\t\n')

        self._assert_returns('foo bar\n', given='foo  \t bar\n')
        self._assert_returns('bar foo\n', given='bar\t  foo\n')
        self._assert_returns('bar foo \n', given='bar\t  foo  \t\n')
        self._assert_returns('foo bar\n', given='foo \t\tbar\n')
        self._assert_returns('bar foo\n', given='bar\t\t foo\n')
        self._assert_returns('bar foo \n', given='bar\t\t foo \t\t\n')

    def test_collapses_multiple_tabs_keeps_newlines(self):
        self._assert_returns('foo \n', given='foo\t\t\n')
        self._assert_returns('foo \n', given='foo\t\t\t\n')
        self._assert_returns(' foo\n', given='\t\tfoo\n')
        self._assert_returns(' foo\n', given='\t\t\tfoo\n')

        self._assert_returns('foo bar\n', given='foo\t\tbar\n')
        self._assert_returns('foo bar\n', given='foo\t\t\tbar\n')
        self._assert_returns(' foo bar\n', given='\t\tfoo bar\n')
        self._assert_returns(' foo bar\n', given='\t\t\tfoo bar\n')


class TestIndent(TestCase):
    def test_invalid_arguments_raises_exception(self):
        def _assert_raises(*args, **kwargs):
            with self.assertRaises(AssertionError):
                _ = indent(*args, **kwargs)

        _assert_raises(None)
        _assert_raises(b'')
        _assert_raises('foo', columns=0)
        _assert_raises('foo', columns=object())
        _assert_raises('foo', columns=2, padchar=1)
        _assert_raises('foo', columns=2, padchar=b'')
        _assert_raises('foo', padchar=b'')

    def test_indents_single_line(self):
        self.assertEqual('    foo', indent('foo'))
        self.assertEqual('    foo bar', indent('foo bar'))

    def test_indents_two_lines(self):
        self.assertEqual('    foo\n    bar', indent('foo\nbar'))

    def test_indents_three_lines(self):
        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('    foo\n'
                  '      bar\n'
                  '    baz\n')
        self.assertEqual(indent(input_), expect)

    def test_indents_single_line_specified_amount(self):
        self.assertEqual(' foo', indent('foo', columns=1))
        self.assertEqual('  foo', indent('foo', columns=2))
        self.assertEqual('   foo', indent('foo', columns=3))
        self.assertEqual('    foo', indent('foo', columns=4))
        self.assertEqual('  foo bar', indent('foo bar', columns=2))

    def test_indents_two_lines_specified_amount(self):
        self.assertEqual('  foo\n  bar', indent('foo\nbar', columns=2))

    def test_indents_three_lines_specified_amount(self):
        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('  foo\n'
                  '    bar\n'
                  '  baz\n')
        self.assertEqual(expect, indent(input_, columns=2))

        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('   foo\n'
                  '     bar\n'
                  '   baz\n')
        self.assertEqual(expect, indent(input_, columns=3))

    def test_indents_single_line_specified_padding(self):
        self.assertEqual('XXXXfoo', indent('foo', padchar='X'))
        self.assertEqual('XXXXfoo bar', indent('foo bar', padchar='X'))

    def test_indents_two_lines_specified_padding(self):
        self.assertEqual('XXXXfoo\nXXXXbar', indent('foo\nbar', padchar='X'))
        self.assertEqual('XjXjXjXjfoo\nXjXjXjXjbar', indent('foo\nbar', padchar='Xj'))

    def test_indents_three_lines_specified_padding(self):
        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('XXXXfoo\n'
                  'XXXX  bar\n'
                  'XXXXbaz\n')
        self.assertEqual(expect, indent(input_, padchar='X'))

        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('XjXjXjXjfoo\n'
                  'XjXjXjXj  bar\n'
                  'XjXjXjXjbaz\n')
        self.assertEqual(expect, indent(input_, padchar='Xj'))

    def test_indents_text_single_line_specified_padding_and_amount(self):
        self.assertEqual('  foo', indent('foo', columns=1, padchar='  '))
        self.assertEqual('    foo', indent('foo', columns=2, padchar='  '))
        self.assertEqual('foo', indent('foo', columns=1, padchar=''))
        self.assertEqual('foo', indent('foo', columns=2, padchar=''))
        self.assertEqual('foo', indent('foo', columns=3, padchar=''))
        self.assertEqual('foo', indent('foo', columns=4, padchar=''))
        self.assertEqual('XXfoo', indent('foo', padchar='X', columns=2))
        self.assertEqual('XXfoo bar', indent('foo bar', padchar='X', columns=2))

    def test_indents_two_lines_specified_padding_and_amount(self):
        self.assertEqual('XXfoo\nXXbar', indent('foo\nbar', padchar='X', columns=2))
        self.assertEqual('XXXXfoo\nXXXXbar', indent('foo\nbar', padchar='X', columns=4))

    def test_indents_three_lines_specified_padding_and_amount(self):
        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('XXfoo\n'
                  'XX  bar\n'
                  'XXbaz\n')
        self.assertEqual(expect, indent(input_, padchar='X', columns=2))

        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('XXXfoo\n'
                  'XXX  bar\n'
                  'XXXbaz\n')
        self.assertEqual(expect, indent(input_, padchar='X', columns=3))


class TestNormalizeUnicode(TestCase):
    def _aE(self, test_input, expected):
        actual = normalize_unicode(test_input)
        self.assertEqual(actual, expected)

    def _assert_unchanged(self, given_unicode):
        self._aE(given_unicode, given_unicode)

    def _assert_replaces_variations(self, given_unicode, replacement):
        def _format(template):
            return template.format(g=given_unicode, r=replacement)

        self._aE(given_unicode, replacement)
        self._aE(_format('{g}'),      _format('{r}'))
        self._aE(_format('{g} '),     _format('{r} '))
        self._aE(_format(' {g}'),     _format(' {r}'))
        self._aE(_format(' {g} '),    _format(' {r} '))

        self._aE(_format('{g}{g}'),   _format('{r}{r}'))
        self._aE(_format('{g}{g} '),  _format('{r}{r} '))
        self._aE(_format(' {g}{g}'),  _format(' {r}{r}'))
        self._aE(_format(' {g}{g} '), _format(' {r}{r} '))

        self._aE(_format('{g} {g}'),   _format('{r} {r}'))
        self._aE(_format('{g} {g} '),  _format('{r} {r} '))
        self._aE(_format(' {g} {g}'),  _format(' {r} {r}'))
        self._aE(_format(' {g} {g} '), _format(' {r} {r} '))

        self._aE(_format('ö{g}'),      _format('ö{r}'))
        self._aE(_format('{g}ö'),      _format('{r}ö'))
        self._aE(_format('å{g}'),      _format('å{r}'))
        self._aE(_format('{g}å'),      _format('{r}å'))
        self._aE(_format('ä{g}'),      _format('ä{r}'))
        self._aE(_format('{g}ä'),      _format('{r}ä'))
        self._aE(_format('Ö{g}'),      _format('Ö{r}'))
        self._aE(_format('{g}Ö'),      _format('{r}Ö'))
        self._aE(_format('Å{g}'),      _format('Å{r}'))
        self._aE(_format('{g}Å'),      _format('{r}Å'))
        self._aE(_format('Ä{g}'),      _format('Ä{r}'))
        self._aE(_format('{g}Ä'),      _format('{r}Ä'))

    def test_returns_empty_values_as_is(self):
        self._assert_unchanged('')
        self._assert_unchanged(b'')
        self._assert_unchanged(None)
        self._assert_unchanged([])
        self._assert_unchanged({})

    def test_raises_exception_given_bad_input(self):
        for bad_value in [
            ['foo'],
            {'foo': 'bar'},
            object(),
            1,
            1.0,
            b'foo',
        ]:
            with self.assertRaises(AssertionError):
                _ = normalize_unicode(bad_value)

    def test_returns_values_as_is(self):
        for given_and_expected in [
            '',
            ' ',
            'foo',
            '...',
            'båt',
            'sär',
            'hög',
            'söt',
            'åäö',
        ]:
            with self.subTest(given_and_expected=given_and_expected):
                self._assert_unchanged(given_and_expected)

    def test_replaces_ellipsis_with_three_periods(self):
        self._assert_replaces_variations('…', '...')
        self.assertEqual('…', '\u2026')
        self._assert_replaces_variations('\u2026', '...')

    def test_replaces_dashes_with_dash(self):
        REPLACEMENT = '-'
        for given_unicode_char in [
            '\u2212',
            '\u2013',
            '\u2014',
        ]:
            with self.subTest(given=given_unicode_char, expected=REPLACEMENT):
                self._assert_replaces_variations(given_unicode_char, REPLACEMENT)

    def test_replaces_dots_and_overlines_and_bars_and_punctuation_with_dash(self):
        REPLACEMENT = '-'
        for given_unicode_char in [
            '\u30fb',
            '\u2015',
            '\u0305',
            '\u203e',
            '\u05be',
        ]:
            with self.subTest(given=given_unicode_char, expected=REPLACEMENT):
                self._assert_replaces_variations(given_unicode_char, REPLACEMENT)

    def test_replaces_hyphens_with_dash(self):
        REPLACEMENT = '-'
        for given_unicode_char in [
            '\u002D',
            '\u00AD',
            '\u2010',
            '\u2011',
            '\u2012',
            '\u2043',
        ]:
            with self.subTest(given=given_unicode_char, expected=REPLACEMENT):
                self._assert_replaces_variations(given_unicode_char, REPLACEMENT)

        self._assert_replaces_variations('\xad', REPLACEMENT)


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


class TestTruncateText(TestCase):
    def _assert_that_it_returns(self, expected, given_text, **kwargs):
        actual = truncate_text(given_text, **kwargs)
        self.assertEqual(expected, actual)

    def test_returns_empty_string_as_is(self):
        self._assert_that_it_returns(expected='', given_text='')

    def test_returns_text_shorter_than_max_as_is(self):
        self._assert_that_it_returns(expected='abc',
                                     given_text='abc',
                                     maxlen=3)
        self._assert_that_it_returns(expected='abc',
                                     given_text='abc',
                                     maxlen=5)

    def test_truncates_text_if_given_text_is_longer_than_maxlen(self):
        self._assert_that_it_returns(expected='abc',
                                     given_text='abc def',
                                     maxlen=3)
        self._assert_that_it_returns(expected='abc d',
                                     given_text='abc def',
                                     maxlen=5)

    def test_truncates_text_if_given_text_is_longer_than_maxlen_append_info(self):
        self._assert_that_it_returns(expected='abc  (3/7 characters)',
                                     given_text='abc def',
                                     maxlen=3, append_info=True)
        self._assert_that_it_returns(expected='abc d  (5/7 characters)',
                                     given_text='abc def',
                                     maxlen=5, append_info=True)


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

    def test_returns_empty_values_or_whitespace_text_as_is(self):
        for text in ['', ' ', '\n', ' \n', ' \n ']:
            for blacklist in [[], ['a'], frozenset([]), frozenset(['a'])]:
                with self.subTest(given=text, blacklist=blacklist):
                    self._assert_that_it_returns(
                        expected=text,
                        given_text=text,
                        given_blacklist=blacklist
                    )

    def test_returns_text_as_is_if_blacklist_is_empty_list(self):
        self._assert_that_it_returns(
            expected='foo\nbar',
            given_text='foo\nbar',
            given_blacklist=[]
        )

    def test_returns_text_as_is_if_blacklist_is_empty_frozenset(self):
        self._assert_that_it_returns(
            expected='foo\nbar',
            given_text='foo\nbar',
            given_blacklist=frozenset([])
        )

    def test_removes_one_blacklisted_line(self):
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
            given_blacklist=frozenset(['This page intentionally left blank'])
        )

    def test_removes_single_blacklisted_line_and_keeps_line_breaks(self):
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
            given_blacklist=frozenset(['This page intentionally left blank'])
        )

    def test_removes_one_matching_line_with_one_blacklisted_word(self):
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
            given_blacklist=frozenset(['MEOW'])
        )

    def test_removes_multiple_matching_lines_with_one_blacklisted_word(self):
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
            given_blacklist=frozenset(['MEOW'])
        )

    def test_removes_matching_lines_with_two_blacklisted_words(self):
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
            given_blacklist=frozenset(['MEOW', 'b'])
        )

    def test_removes_matching_lines_with_multiple_blacklisted_words(self):
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

c
MEOW
''',
            given_blacklist=frozenset(['MEOW', 'b', 'c'])
        )


class TestExtractDigits(TestCase):
    def test_extract_digits_returns_empty_string_given_no_digits(self):
        def _assert_empty(test_data):
            actual = extract_digits(test_data)
            self.assertEqual(actual, '')

        _assert_empty('')
        _assert_empty(' ')
        _assert_empty('_')
        _assert_empty('ö')
        _assert_empty('foo')

    def test_extract_digits_returns_digits(self):
        def _assert_equal(test_data, expected):
            actual = extract_digits(test_data)
            self.assertTrue(uu.is_internalstring(actual))
            self.assertEqual(actual, expected)

        _assert_equal('0', '0')
        _assert_equal('1', '1')
        _assert_equal('1', '1')
        _assert_equal('_1', '1')
        _assert_equal('foo1', '1')
        _assert_equal('foo1bar', '1')
        _assert_equal('foo1bar2', '12')
        _assert_equal('1a2b3c4d', '1234')
        _assert_equal('  1a2b3c4d', '1234')
        _assert_equal('  1a2b3c4d  _', '1234')
        _assert_equal('1.0', '10')
        _assert_equal('2.3', '23')

    def test_raises_exception_given_bad_arguments(self):
        def _assert_raises(test_data):
            with self.assertRaises(AssertionError):
                extract_digits(test_data)

        _assert_raises(None)
        _assert_raises([])
        _assert_raises(1)
        _assert_raises(b'foo')
        _assert_raises(b'1')
