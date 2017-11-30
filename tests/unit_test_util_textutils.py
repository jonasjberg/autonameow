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

from unittest import (
    skipIf,
    TestCase
)

try:
    import chardet
except ImportError:
    chardet = None

from core import types
from core.exceptions import EncodingBoundaryViolation
from util import encoding as enc
from util.textutils import (
    autodetect_decode,
    compiled_ordinal_regexes,
    extract_digits,
    extract_lines,
    extractlines_do,
    indent,
    normalize_unicode,
    remove_nonbreaking_spaces,
    strip_ansiescape,
    urldecode
)
import unit_utils as uu


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
            with self.assertRaises(EncodingBoundaryViolation):
                extract_digits(test_data)

        _assert_raises(None)
        _assert_raises([])
        _assert_raises(1)
        _assert_raises(b'foo')
        _assert_raises(b'1')


@unittest.skipIf(chardet is None, 'Unable to import required module "chardet"')
class TestAutodetectDecode(TestCase):
    def _assert_encodes(self, encoding, string):
        _encoded_text = string.encode(encoding)
        self.assertTrue(uu.is_internalbytestring(_encoded_text))

        actual = autodetect_decode(_encoded_text)
        self.assertEqual(string, actual)
        self.assertEqual(type(string), type(actual))

    def test_raises_exception_for_non_strings(self):
        with self.assertRaises(TypeError):
            autodetect_decode(object())

        with self.assertRaises(TypeError):
            autodetect_decode(None)

    def test_returns_expected_given_unicode(self):
        actual = autodetect_decode('foo bar')
        self.assertEqual('foo bar', actual)

    def test_returns_expected_given_ascii(self):
        self._assert_encodes('ascii', '')
        self._assert_encodes('ascii', ' ')
        self._assert_encodes('ascii', '\n')
        self._assert_encodes('ascii', '\n ')
        self._assert_encodes('ascii', ' \n ')
        self._assert_encodes('ascii', 'foo bar')
        self._assert_encodes('ascii', 'foo \n ')

    def test_returns_expected_given_ISO8859(self):
        self._assert_encodes('iso-8859-1', '')
        self._assert_encodes('iso-8859-1', ' ')
        self._assert_encodes('iso-8859-1', '\n')
        self._assert_encodes('iso-8859-1', '\n ')
        self._assert_encodes('iso-8859-1', ' \n ')
        self._assert_encodes('iso-8859-1', 'foo bar')
        self._assert_encodes('iso-8859-1', 'foo \n ')

    def test_returns_expected_given_cp1252(self):
        self._assert_encodes('cp1252', '')
        self._assert_encodes('cp1252', ' ')
        self._assert_encodes('cp1252', '\n')
        self._assert_encodes('cp1252', '\n ')
        self._assert_encodes('cp1252', ' \n ')
        self._assert_encodes('cp1252', 'foo bar')
        self._assert_encodes('cp1252', 'foo \n ')

    def test_returns_expected_given_utf8(self):
        self._assert_encodes('utf-8', '')
        self._assert_encodes('utf-8', ' ')
        self._assert_encodes('utf-8', '\n')
        self._assert_encodes('utf-8', '\n ')
        self._assert_encodes('utf-8', ' \n ')
        self._assert_encodes('utf-8', 'foo bar')
        self._assert_encodes('utf-8', 'foo \n ')


class TestExtractLines(TestCase):
    def test_returns_none_for_none_input(self):
        self.assertIsNone(extract_lines(None, 0, 0))
        self.assertIsNone(extract_lines(None, 0, 1))
        self.assertIsNone(extract_lines(None, 1, 1))
        self.assertIsNone(extract_lines(None, 1, 0))

    def test_extracts_lines_from_zero_to_any_last(self):
        sample_text = 'A\nB\nC\nD\nE\n'

        def _assert_extracts(first_line, last_line, expected):
            self.assertEqual(
                extract_lines(sample_text, first_line, last_line),
                expected
            )

        _assert_extracts(0, 1, 'A\n')
        _assert_extracts(0, 2, 'A\nB\n')
        _assert_extracts(0, 3, 'A\nB\nC\n')
        _assert_extracts(0, 4, 'A\nB\nC\nD\n')
        _assert_extracts(0, 5, 'A\nB\nC\nD\nE\n')
        _assert_extracts(0, 6, 'A\nB\nC\nD\nE\n')
        _assert_extracts(0, 7, 'A\nB\nC\nD\nE\n')

    def test_extracts_lines_from_any_first_to_last(self):
        sample_text = 'A\nB\nC\nD\nE\n'

        def _assert_extracts(first_line, last_line, expected):
            self.assertEqual(
                extract_lines(sample_text, first_line, last_line),
                expected
            )

        last = 6
        _assert_extracts(0, last, 'A\nB\nC\nD\nE\n')
        _assert_extracts(1, last, 'B\nC\nD\nE\n')
        _assert_extracts(2, last, 'C\nD\nE\n')
        _assert_extracts(3, last, 'D\nE\n')
        _assert_extracts(4, last, 'E\n')
        _assert_extracts(5, last, '')
        _assert_extracts(6, last, '')
        _assert_extracts(7, last, '')

    def test_extracts_lines_from_any_first_to_any_last(self):
        sample_text = 'A\nB\nC\nD\nE\n'

        def _assert_extracts(first_line, last_line, expected):
            self.assertEqual(
                extract_lines(sample_text, first_line, last_line),
                expected
            )

        _assert_extracts(0, 0, '')
        _assert_extracts(0, 1, 'A\n')
        _assert_extracts(0, 2, 'A\nB\n')
        _assert_extracts(0, 3, 'A\nB\nC\n')
        _assert_extracts(0, 4, 'A\nB\nC\nD\n')
        _assert_extracts(0, 5, 'A\nB\nC\nD\nE\n')
        _assert_extracts(1, 0, '')
        _assert_extracts(1, 1, '')
        _assert_extracts(1, 2, 'B\n')
        _assert_extracts(1, 3, 'B\nC\n')
        _assert_extracts(1, 4, 'B\nC\nD\n')
        _assert_extracts(1, 5, 'B\nC\nD\nE\n')
        _assert_extracts(2, 0, '')
        _assert_extracts(2, 1, '')
        _assert_extracts(2, 2, '')
        _assert_extracts(2, 3, 'C\n')
        _assert_extracts(2, 4, 'C\nD\n')
        _assert_extracts(2, 5, 'C\nD\nE\n')
        _assert_extracts(3, 0, '')
        _assert_extracts(3, 1, '')
        _assert_extracts(3, 2, '')
        _assert_extracts(3, 3, '')
        _assert_extracts(3, 4, 'D\n')
        _assert_extracts(3, 5, 'D\nE\n')
        _assert_extracts(4, 0, '')
        _assert_extracts(4, 1, '')
        _assert_extracts(4, 2, '')
        _assert_extracts(4, 3, '')
        _assert_extracts(4, 4, '')
        _assert_extracts(4, 5, 'E\n')
        _assert_extracts(5, 0, '')
        _assert_extracts(5, 1, '')
        _assert_extracts(5, 2, '')
        _assert_extracts(5, 3, '')
        _assert_extracts(5, 4, '')
        _assert_extracts(5, 5, '')

    def test_edge_cases(self):
        self.assertEqual(extract_lines('', 0, 0), '')
        self.assertEqual(extract_lines(' ', 0, 0), '')

    def test_raises_exceptions_given_bad_argument(self):
        with self.assertRaises(EncodingBoundaryViolation):
            extract_lines(b'foo', 0, 0)

        with self.assertRaises(EncodingBoundaryViolation):
            extract_lines(1, 0, 0)

        with self.assertRaises(AssertionError):
            extract_lines('foo', -1, 0)

        with self.assertRaises(AssertionError):
            extract_lines('foo', 0, -1)


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


class TestStripAnsiEscape(TestCase):
    def _aE(self, test_input, expected):
        actual = strip_ansiescape(test_input)
        self.assertEqual(actual, expected)

    def test_strips_ansi_escape_codes(self):
        self._aE('', '')
        self._aE('a', 'a')
        self._aE('[30m[44mautonameow[49m[39m', 'autonameow')


class TestExtractlinesDo(TestCase):
    def setUp(self):
        self.text = '''foo
2. bar
3. baz
4. foo
'''

    def test_transforms_all_lines(self):
        actual = extractlines_do(
            lambda t: t.upper(),
            self.text, fromline=0, toline=4
        )
        expect = '''FOO
2. BAR
3. BAZ
4. FOO
'''
        self.assertEqual(actual, expect)

    def test_transforms_subset_of_lines(self):
        actual = extractlines_do(
            lambda t: t.upper(),
            self.text, fromline=1, toline=3
        )
        expect = '''2. BAR
3. BAZ
'''
        self.assertEqual(actual, expect)


class TestCompiledOrdinalRegexes(TestCase):
    def setUp(self):
        self.actual = compiled_ordinal_regexes()

    def test_returns_expected_type(self):
        self.assertIsNotNone(self.actual)
        self.assertTrue(isinstance(self.actual, dict))

    def test_returns_compiled_regular_expressions(self):
        re_one = self.actual.get(1)
        self.assertTrue(isinstance(re_one, types.BUILTIN_REGEX_TYPE))

        for _pattern in self.actual.values():
            self.assertTrue(isinstance(_pattern, types.BUILTIN_REGEX_TYPE))

    def test_returned_regexes_matches_strings(self):
        def _aM(test_input):
            match = self.actual.get(2).search(test_input)
            actual = match.group(0)
            expected = 2
            self.assertTrue(actual, expected)

        _aM('2nd')
        _aM('second')
        _aM('SECOND')
        _aM('foo 2nd bar')
        _aM('foo 2ND bar')


class TestUrlDecode(TestCase):
    def test_returns_expected_given_valid_arguments(self):
        def _aE(test_input, expected):
            actual = urldecode(test_input)
            self.assertEqual(actual, expected)

        _aE('%2C', ',')
        _aE('%20', ' ')
        _aE('f.bar?t=%D0%B7%D0%B0%D1%89%D0%B8%D1%82%D0%B0', 'f.bar?t=защита')
