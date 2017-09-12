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

import unittest

from core import util
from core.util import textutils

try:
    import chardet
except (ModuleNotFoundError, ImportError):
    chardet = None


class TestRemoveNonBreakingSpaces(unittest.TestCase):
    def test_remove_non_breaking_spaces_removes_expected(self):
        expected = 'foo bar'

        non_breaking_space = '\xa0'
        actual = textutils.remove_nonbreaking_spaces(
            'foo' + util.decode_(non_breaking_space) + 'bar'
        )
        self.assertEqual(expected, actual)

    def test_remove_non_breaking_spaces_returns_expected(self):
        expected = 'foo bar'
        actual = textutils.remove_nonbreaking_spaces('foo bar')
        self.assertEqual(expected, actual)

    def test_remove_non_breaking_spaces_handles_empty_string(self):
        expected = ''
        actual = textutils.remove_nonbreaking_spaces('')
        self.assertEqual(expected, actual)


class TestIndent(unittest.TestCase):
    def test_invalid_arguments_raises_exception(self):
        def _assert_raises(*args, **kwargs):
            with self.assertRaises(AssertionError):
                textutils.indent(*args, **kwargs)

        _assert_raises(None)
        _assert_raises(b'')
        _assert_raises('foo', amount=0)
        _assert_raises('foo', amount=2, ch=None)
        _assert_raises('foo', amount=2, ch=b'')
        _assert_raises('foo', ch=None)
        _assert_raises('foo', ch=b'')

    def test_indents_single_line(self):
        self.assertEqual(textutils.indent('foo'), '    foo')
        self.assertEqual(textutils.indent('foo bar'), '    foo bar')

    def test_indents_two_lines(self):
        self.assertEqual(textutils.indent('foo\nbar'), '    foo\n    bar')

    def test_indents_three_lines(self):
        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('    foo\n'
                  '      bar\n'
                  '    baz\n')
        self.assertEqual(textutils.indent(input_), expect)

    def test_indents_single_line_specified_amount(self):
        self.assertEqual(textutils.indent('foo', amount=1), ' foo')
        self.assertEqual(textutils.indent('foo', amount=2), '  foo')
        self.assertEqual(textutils.indent('foo', amount=3), '   foo')
        self.assertEqual(textutils.indent('foo', amount=4), '    foo')
        self.assertEqual(textutils.indent('foo bar', amount=2), '  foo bar')

    def test_indents_two_lines_specified_amount(self):
        self.assertEqual(textutils.indent('foo\nbar', amount=2), '  foo\n  bar')

    def test_indents_three_lines_specified_amount(self):
        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('  foo\n'
                  '    bar\n'
                  '  baz\n')
        self.assertEqual(textutils.indent(input_, amount=2), expect)

        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('   foo\n'
                  '     bar\n'
                  '   baz\n')
        self.assertEqual(textutils.indent(input_, amount=3), expect)

    def test_indents_single_line_specified_padding(self):
        self.assertEqual(textutils.indent('foo', ch='X'), 'XXXXfoo')
        self.assertEqual(textutils.indent('foo bar', ch='X'), 'XXXXfoo bar')

    def test_indents_two_lines_specified_padding(self):
        self.assertEqual(textutils.indent('foo\nbar', ch='X'),
                         'XXXXfoo\nXXXXbar')
        self.assertEqual(textutils.indent('foo\nbar', ch='Xj'),
                         'XjXjXjXjfoo\nXjXjXjXjbar')

    def test_indents_three_lines_specified_padding(self):
        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('XXXXfoo\n'
                  'XXXX  bar\n'
                  'XXXXbaz\n')
        self.assertEqual(textutils.indent(input_, ch='X'), expect)

        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('XjXjXjXjfoo\n'
                  'XjXjXjXj  bar\n'
                  'XjXjXjXjbaz\n')
        self.assertEqual(textutils.indent(input_, ch='Xj'), expect)

    def test_indents_text_single_line_specified_padding_and_amount(self):
        self.assertEqual(textutils.indent('foo', amount=1, ch='  '), '  foo')
        self.assertEqual(textutils.indent('foo', amount=2, ch='  '), '    foo')
        self.assertEqual(textutils.indent('foo', amount=1, ch=''), 'foo')
        self.assertEqual(textutils.indent('foo', amount=2, ch=''), 'foo')
        self.assertEqual(textutils.indent('foo', amount=3, ch=''), 'foo')
        self.assertEqual(textutils.indent('foo', amount=4, ch=''), 'foo')
        self.assertEqual(textutils.indent('foo', ch='X', amount=2), 'XXfoo')
        self.assertEqual(textutils.indent('foo bar', ch='X', amount=2),
                         'XXfoo bar')

    def test_indents_two_lines_specified_padding_and_amount(self):
        self.assertEqual(textutils.indent('foo\nbar', ch='X', amount=2),
                         'XXfoo\nXXbar')
        self.assertEqual(textutils.indent('foo\nbar', ch='X', amount=4),
                         'XXXXfoo\nXXXXbar')

    def test_indents_three_lines_specified_padding_and_amount(self):
        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('XXfoo\n'
                  'XX  bar\n'
                  'XXbaz\n')
        self.assertEqual(textutils.indent(input_, ch='X', amount=2), expect)

        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('XXXfoo\n'
                  'XXX  bar\n'
                  'XXXbaz\n')
        self.assertEqual(textutils.indent(input_, ch='X', amount=3), expect)


class TestExtractDigits(unittest.TestCase):
    def test_extract_digits_is_defined(self):
        self.assertIsNotNone(textutils.extract_digits)

    def test_extract_digits_returns_none_if_input_has_no_digits(self):
        def _assert_is_none(test_data):
            self.assertIsNone(textutils.extract_digits(test_data))

        _assert_is_none('')
        _assert_is_none(' ')
        _assert_is_none('_')
        _assert_is_none('ö')
        _assert_is_none('foo')

    def test_extract_digits_returns_only_digits_of_input_string(self):
        def _assert_equal(test_data, expect):
            actual = textutils.extract_digits(test_data)
            self.assertTrue(isinstance(actual, str))
            self.assertEqual(actual, expect)

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


@unittest.skipIf(chardet is None, 'Unable to import required module "chardet"')
class TestAutodetectDecode(unittest.TestCase):
    def _assert_encodes(self, encoding, unicode_text):
        input = unicode_text.encode(encoding)
        actual = textutils.autodetect_decode(input)
        self.assertEqual(unicode_text, actual)

    def test_returns_expected_given_unicode(self):
        actual = textutils.autodetect_decode('foo bar')
        self.assertEqual('foo bar', actual)

    def test_returns_expected_given_ascii(self):
        self._assert_encodes('ascii', 'foo bar')

    def test_returns_expected_given_ISO8859(self):
        self._assert_encodes('iso-8859-1', 'foo bar')

    def test_returns_expected_given_cp1252(self):
        self._assert_encodes('cp1252', 'foo bar')


class TestExtractLines(unittest.TestCase):
    def test_extracts_lines_from_zero_to_any_last(self):
        sample_text = 'A\nB\nC\nD\nE\n'

        def _assert_extracts(first_line, last_line, expected):
            self.assertEqual(
                textutils.extract_lines(sample_text, first_line, last_line),
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
                textutils.extract_lines(sample_text, first_line, last_line),
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
                textutils.extract_lines(sample_text, first_line, last_line),
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
        self.assertEqual(textutils.extract_lines('', 0, 0), '')
        self.assertEqual(textutils.extract_lines(' ', 0, 0), '')

    def test_raises_exceptions_given_bad_argument(self):
        with self.assertRaises(ValueError):
            textutils.extract_lines(None, 0, 0)

        with self.assertRaises(TypeError):
            textutils.extract_lines(b'foo', 0, 0)

        with self.assertRaises(TypeError):
            textutils.extract_lines(1, 0, 0)
