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
    remove_nonbreaking_spaces,
    strip_ansiescape
)


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
