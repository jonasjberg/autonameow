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

from core.namebuilder.builder import FilenamePostprocessor


class TestFilenamePostprocessor(TestCase):
    def test_lowercase_filename_true(self):
        p = FilenamePostprocessor(lowercase_filename=True)
        actual = p('Foo Bar')
        self.assertEqual(actual, 'foo bar')

    def test_lowercase_filename_false(self):
        p = FilenamePostprocessor(lowercase_filename=False)
        actual = p('Foo Bar')
        self.assertEqual(actual, 'Foo Bar')

    def test_uppercase_filename_true(self):
        p = FilenamePostprocessor(uppercase_filename=True)
        actual = p('Foo Bar')
        self.assertEqual(actual, 'FOO BAR')

    def test_uppercase_filename_false(self):
        p = FilenamePostprocessor(uppercase_filename=False)
        actual = p('Foo Bar')
        self.assertEqual(actual, 'Foo Bar')

    def test_lowercase_filename_true_and_uppercase_filename_true(self):
        p = FilenamePostprocessor(uppercase_filename=True,
                                  lowercase_filename=True)
        actual = p('Foo Bar')
        self.assertEqual(actual, 'foo bar')

    def test_no_replacements(self):
        for reps in [None, {}]:
            p = FilenamePostprocessor(regex_replacements=reps)
            actual = p('Foo Bar')
            self.assertEqual(actual, 'Foo Bar')


class TestFilenamePostprocessor2(TestCase):
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
            p = FilenamePostprocessor(regex_replacements=reps)
            actual = p('Foo Bar')
            self.assertEqual(actual, 'Foo Bar')

    def test_one_replacement(self):
        reps = [
            (re.compile(r'Foo'), 'Mjao')
        ]
        p = FilenamePostprocessor(regex_replacements=reps)
        actual = p('Foo Bar')
        self.assertEqual(actual, 'Mjao Bar')

    def test_two_replacements(self):
        reps = [
            (re.compile(r'Foo'), 'Mjao'),
            (re.compile(r' '), 'X'),
        ]
        p = FilenamePostprocessor(regex_replacements=reps)
        actual = p('Foo Bar')
        self.assertEqual(actual, 'MjaoXBar')
