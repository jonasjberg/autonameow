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

import re

from unittest import TestCase

from core.types import BUILTIN_REGEX_TYPE
from core.namebuilder.builder import (
    displayable_replacement,
    FilenamePostprocessor
)


class TestFilenamePostprocessor(TestCase):
    def __check_call(self, **kwargs):
        given = kwargs.pop('given')
        expect = kwargs.pop('expect')
        p = FilenamePostprocessor(**kwargs)
        actual = p(given)
        self.assertEqual(actual, expect)

    def test_lowercase_filename_true(self):
        self.__check_call(given='Foo Bar', expect='foo bar',
                          lowercase_filename=True)

    def test_lowercase_filename_false(self):
        self.__check_call(given='Foo Bar', expect='Foo Bar',
                          lowercase_filename=False)

    def test_uppercase_filename_true(self):
        self.__check_call(given='Foo Bar', expect='FOO BAR',
                          uppercase_filename=True)

    def test_uppercase_filename_false(self):
        self.__check_call(given='Foo Bar', expect='Foo Bar',
                          uppercase_filename=False)

    def test_lowercase_filename_true_and_uppercase_filename_true(self):
        self.__check_call(given='Foo Bar', expect='foo bar',
                          uppercase_filename=True,
                          lowercase_filename=True)

    def test_no_replacements(self):
        for reps in [None, {}]:
            with self.subTest(reps=reps):
                self.__check_call(given='Foo Bar', expect='Foo Bar',
                                  regex_replacements=reps)

    def test_one_replacement(self):
        reps = [
            (re.compile(r'Foo'), 'Mjao')
        ]
        self.__check_call(given='Foo Bar', expect='Mjao Bar',
                          regex_replacements=reps)

    def test_two_replacements(self):
        reps = [
            (re.compile(r'Foo'), 'Mjao'),
            (re.compile(r' '), 'X'),
        ]
        self.__check_call(given='Foo Bar', expect='MjaoXBar',
                          regex_replacements=reps)


class TestDisplayableReplacement(TestCase):
    def __check_replacement(self, original, regex, replacement,
                            expect_old, expect_new):
        assert regex and isinstance(regex, BUILTIN_REGEX_TYPE)
        for arg in (original, replacement, expect_old, expect_new):
            assert isinstance(arg, str)

        COLOR = 'RED'
        ANSI_COLOR = '\x1b[31m'
        ANSI_RESET = '\x1b[39m'

        _expected_old = expect_old.format(COL=ANSI_COLOR, RES=ANSI_RESET)
        _expected_new = expect_new.format(COL=ANSI_COLOR, RES=ANSI_RESET)
        actual_old, actual_new = displayable_replacement(
            original, replacement, regex, COLOR
        )

        def __unescape_ansi(s):
            return s.replace(ANSI_COLOR, '{COL}').replace(ANSI_RESET, '{RES}')

        self.assertEqual(
            actual_old, _expected_old,
            'OLD :: Actual: "{!s}"  Expected: "{!s}"'.format(
                __unescape_ansi(actual_old), __unescape_ansi(_expected_old)
            )
        )
        self.assertEqual(
            actual_new, _expected_new,
            'NEW :: Actual: "{!s}"  Expected: "{!s}"'.format(
                __unescape_ansi(actual_new), __unescape_ansi(_expected_new)
            )
        )

    def test_unchanged_when_regex_does_not_match(self):
        self.__check_replacement(
            original='Bar, x123',
            regex=re.compile(r'Foo'),
            replacement='Mjao',
            expect_old='Bar, x123',
            expect_new='Bar, x123'
        )

    def test_unchanged_when_regex_match_equals_replacement_string(self):
        self.__check_replacement(
            original='Bar, x123',
            regex=re.compile(r'Bar'),
            replacement='Bar',
            expect_old='Bar, x123',
            expect_new='Bar, x123'
        )

    def test_one_single_character_replacement(self):
        self.__check_replacement(
            original='Bar, x123',
            regex=re.compile(r'x'),
            replacement='Mjao',
            expect_old='Bar, {COL}x{RES}123',
            expect_new='Bar, {COL}Mjao{RES}123'
        )

    def test_two_single_character_replacements_one_leading(self):
        self.__check_replacement(
            original='xBar, x123',
            regex=re.compile(r'x'),
            replacement='mjao',
            expect_old='{COL}x{RES}Bar, {COL}x{RES}123',
            expect_new='{COL}mjao{RES}Bar, {COL}mjao{RES}123'
        )

    def test_three_single_character_replacements_one_leading_one_trailing(self):
        self.__check_replacement(
            original='xBar, x123x',
            regex=re.compile(r'x'),
            replacement='mjao',
            expect_old='{COL}x{RES}Bar, {COL}x{RES}123{COL}x{RES}',
            expect_new='{COL}mjao{RES}Bar, {COL}mjao{RES}123{COL}mjao{RES}'
        )

    def test_multiple_character_replacement_a(self):
        self.__check_replacement(
            original='Bar,, x123',
            regex=re.compile(r'[x,]+'),
            replacement='Z',
            expect_old='Bar{COL},,{RES} {COL}x{RES}123',
            expect_new='Bar{COL}Z{RES} {COL}Z{RES}123'
        )

    def test_multiple_character_replacement_b(self):
        self.skipTest('TODO: [TD0096] Fix invalid replacement colouring')
        self.__check_replacement(
            original='Bar,, x123',
            regex=re.compile(r'[x,]'),
            replacement='Z',
            expect_old='Bar{COL},,{RES} {COL}x{RES}123',
            expect_new='Bar{COL}Z{RES}{COL}Z{RES} {COL}Z{RES}123'
        )

    # TODO: [TD0096] Fix invalid colouring if the replacement is the last character.
    #
    # Applying custom replacement. Regex: "re.compile('\\.$')" Replacement: ""
    # Applying custom replacement: "2007-04-23_12-comments.png." -> "2007-04-23_12-comments.png"
    #                                                     ^   ^
    #                 Should not be colored red, but is --'   '-- Should be red, but isn't ..
    def test_bug_replacement_is_last_character(self):
        self.skipTest('TODO: [TD0096] Fix invalid replacement colouring')
        self.__check_replacement(
            original='2007-04-23_12-comments.png.',
            regex=re.compile(r'\.$'),
            replacement='',
            expect_old='2007-04-23_12-comments.png{COL}.{RES}',
            expect_new='2007-04-23_12-comments.png'
        )
