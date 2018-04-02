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

import unit.utils as uu
from core.exceptions import EncodingBoundaryViolation
from util.textutils import (
    extract_digits,
    extract_lines,
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
            with self.assertRaises(EncodingBoundaryViolation):
                extract_digits(test_data)

        _assert_raises(None)
        _assert_raises([])
        _assert_raises(1)
        _assert_raises(b'foo')
        _assert_raises(b'1')


class TestExtractLines(TestCase):
    SAMPLE_TEXT = '''A
B
C
D
E
'''
    SAMPLE_TEXT_NUMLINES = len(SAMPLE_TEXT.split())

    def test_returns_none_for_none_input(self):
        self.assertIsNone(extract_lines(None, 1, 1))
        self.assertIsNone(extract_lines(None, 1, 0))

    def test_extracts_lines_from_first_to_any_last(self):
        def _assert_extracts(first_line, last_line, expected):
            self.assertEqual(
                extract_lines(self.SAMPLE_TEXT, first_line, last_line),
                expected
            )

        first = 1
        _assert_extracts(first, 1, 'A\n')
        _assert_extracts(first, 2, 'A\nB\n')
        _assert_extracts(first, 3, 'A\nB\nC\n')
        _assert_extracts(first, 4, 'A\nB\nC\nD\n')
        _assert_extracts(first, 5, 'A\nB\nC\nD\nE\n')
        _assert_extracts(first, 6, 'A\nB\nC\nD\nE\n')
        _assert_extracts(first, 7, 'A\nB\nC\nD\nE\n')

    def test_extracts_lines_from_any_first_to_last(self):
        def _assert_extracts(first_line, last_line, expected):
            actual = extract_lines(self.SAMPLE_TEXT, first_line, last_line)
            self.assertEqual(expected, actual)

        last = 6
        _assert_extracts(1, last, 'A\nB\nC\nD\nE\n')
        _assert_extracts(2, last, 'B\nC\nD\nE\n')
        _assert_extracts(3, last, 'C\nD\nE\n')
        _assert_extracts(4, last, 'D\nE\n')
        _assert_extracts(5, last, 'E\n')
        _assert_extracts(6, last, '')
        _assert_extracts(7, last, '')
        _assert_extracts(8, last, '')

    def test_extracts_lines_from_any_first_to_any_last(self):
        def _assert_extracts(first_line, last_line, expected):
            self.assertEqual(
                extract_lines(self.SAMPLE_TEXT, first_line, last_line),
                expected
            )

        # _assert_extracts(1, 0, '')
        _assert_extracts(1, 1, 'A\n')
        _assert_extracts(1, 2, 'A\nB\n')
        _assert_extracts(1, 3, 'A\nB\nC\n')
        _assert_extracts(1, 4, 'A\nB\nC\nD\n')
        _assert_extracts(1, 5, 'A\nB\nC\nD\nE\n')
        _assert_extracts(2, 1, '')
        _assert_extracts(2, 2, 'B\n')
        _assert_extracts(2, 3, 'B\nC\n')
        _assert_extracts(2, 4, 'B\nC\nD\n')
        _assert_extracts(2, 5, 'B\nC\nD\nE\n')
        _assert_extracts(3, 1, '')
        _assert_extracts(3, 2, '')
        _assert_extracts(3, 3, 'C\n')
        _assert_extracts(3, 4, 'C\nD\n')
        _assert_extracts(3, 5, 'C\nD\nE\n')
        _assert_extracts(4, 1, '')
        _assert_extracts(4, 2, '')
        _assert_extracts(4, 3, '')
        _assert_extracts(4, 4, 'D\n')
        _assert_extracts(4, 5, 'D\nE\n')
        _assert_extracts(5, 1, '')
        _assert_extracts(5, 2, '')
        _assert_extracts(5, 3, '')
        _assert_extracts(5, 4, '')
        _assert_extracts(5, 5, 'E\n')
        _assert_extracts(6, 1, '')
        _assert_extracts(6, 2, '')
        _assert_extracts(6, 3, '')
        _assert_extracts(6, 4, '')
        _assert_extracts(6, 5, '')

    def test_edge_cases(self):
        self.assertEqual(extract_lines('', 1, 1), '')
        self.assertEqual(extract_lines(' ', 1, 1), ' ')

    def test_raises_exceptions_given_bad_argument(self):
        with self.assertRaises(EncodingBoundaryViolation):
            extract_lines(b'foo', 0, 0)

        with self.assertRaises(EncodingBoundaryViolation):
            extract_lines(1, 0, 0)

        with self.assertRaises(AssertionError):
            extract_lines('foo', -1, 0)

        with self.assertRaises(AssertionError):
            extract_lines('foo', 0, -1)

    def test_number_of_extracted_lines(self):
        sample_text = '''first
second
third

fifth
'''

        def _check_number_of_lines(first, last, expect):
            actual = extract_lines(sample_text, first, last)
            actual_numlines = len(actual.splitlines())
            self.assertEqual(expect, actual_numlines)

        sample_lines = len(sample_text.splitlines())
        _check_number_of_lines(first=1, last=sample_lines, expect=sample_lines)
        _check_number_of_lines(first=2, last=sample_lines, expect=sample_lines-1)
        _check_number_of_lines(first=3, last=sample_lines, expect=sample_lines-2)

        _check_number_of_lines(first=1, last=1, expect=1)
        _check_number_of_lines(first=1, last=2, expect=2)
        _check_number_of_lines(first=1, last=3, expect=3)
        _check_number_of_lines(first=1, last=4, expect=4)
        _check_number_of_lines(first=1, last=5, expect=5)

        _check_number_of_lines(first=5, last=5, expect=1)
        _check_number_of_lines(first=4, last=5, expect=2)
        _check_number_of_lines(first=3, last=5, expect=3)
        _check_number_of_lines(first=2, last=5, expect=4)
