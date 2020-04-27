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

import itertools
import re
from unittest import TestCase

from core.namebuilder.postprocess import FilenamePostprocessor


class TestFilenamePostprocessor(TestCase):
    def __check_call(self, **kwargs):
        given = kwargs.pop('given')
        expect = kwargs.pop('expect')
        p = FilenamePostprocessor(**kwargs)
        actual = p(given)
        self.assertEqual(expect, actual)

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

    def test_three_replacements(self):
        reps = [
            (re.compile(r'Foo'), 'Mjao'),
            (re.compile(r' '), 'X'),
            (re.compile(r'(bar){2,}'), 'bar'),
        ]
        self.__check_call(given='Foo barbar Bar', expect='MjaoXbarXBar',
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
                self.__check_call(given='The Cat In A Hat',
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
                self.__check_call(given='The Cat In A Hat InA The FlAt',
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
                self.__check_call(given='a cat And a Dog In A thing in The HAT',
                                  expect='a cat and a Dog in a thing in the HAT',
                                  regex_replacements=reps_order)

    def test_replaces_single_quote(self):
        self.__check_call(given='Foo\'s Bar', expect='Foos Bar',
                          regex_replacements=[(re.compile(r'[\']'), '')])
        self.__check_call(given='Foo\'s Bar', expect='Foos Bar',
                          regex_replacements=[(re.compile(r"'"), '')])
        self.__check_call(given='Foo\'s Bar', expect='Foos Bar',
                          regex_replacements=[(re.compile("'"), '')])

    def test_simplify_unicode(self):
        self.__check_call(given='foo', expect='foo',
                          simplify_unicode=False)
        self.__check_call(given='Fooçalbar', expect='Fooçalbar',
                          simplify_unicode=False)
        self.__check_call(given='Fooçalbar', expect='Foocalbar',
                          simplify_unicode=True)
