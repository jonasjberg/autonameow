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

from core import util
from core.util import textutils


class TestRemoveNonBreakingSpaces(TestCase):
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


class TestIndent(TestCase):
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
        self.assertEqual(textutils.indent('foo', amount=2), '  foo')
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

    def test_indents_single_line_specified_padding(self):
        self.assertEqual(textutils.indent('foo', ch='X'), 'XXXXfoo')
        self.assertEqual(textutils.indent('foo bar', ch='X'), 'XXXXfoo bar')

    def test_indents_two_lines_specified_padding(self):
        self.assertEqual(textutils.indent('foo\nbar', ch='X'),
                         'XXXXfoo\nXXXXbar')

    def test_indents_three_lines_specified_padding(self):
        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('XXXXfoo\n'
                  'XXXX  bar\n'
                  'XXXXbaz\n')
        self.assertEqual(textutils.indent(input_, ch='X'), expect)

    def test_indents_text_single_line_specified_padding_and_amount(self):
        self.assertEqual(textutils.indent('foo', ch='X', amount=2), 'XXfoo')
        self.assertEqual(textutils.indent('foo bar', ch='X', amount=2),
                         'XXfoo bar')

    def test_indents_two_lines_specified_padding_and_amount(self):
        self.assertEqual(textutils.indent('foo\nbar', ch='X', amount=2),
                         'XXfoo\nXXbar')

    def test_indents_three_lines_specified_padding_and_amount(self):
        input_ = ('foo\n'
                  '  bar\n'
                  'baz\n')
        expect = ('XXfoo\n'
                  'XX  bar\n'
                  'XXbaz\n')
        self.assertEqual(textutils.indent(input_, ch='X', amount=2), expect)
