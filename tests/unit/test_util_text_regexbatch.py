# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from util.text.regexbatch import replace
from util.text.regexbatch import find_longest_match


class TestBatchRegexReplace(TestCase):
    def _check_call(self, given, expect, regex_replacements):
        actual = replace(regex_replacements, given)
        self.assertEqual(expect, actual)

    def _check_call_ignorecase(self, given, expect, regex_replacements):
        actual = replace(regex_replacements, given, ignore_case=True)
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

    def test_longer_replacements_first_with_word_boundaries_string_patterns(self):
        reps = [
            (r'\bIn A\b', 'in a'),
            (r'\bIn\b', 'in'),
            (r'\bA\b', 'a'),
            (r'\bThe\b', 'the'),
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

    def test_does_not_exhibit_inconsistent_behaviour_given_string_patterns(self):
        reps = [
            (r'\bThe\b', 'the'),
            (r'\bAnd\b', 'and'),
            (r'\bIn\b', 'in'),
            (r'\bOf\b', 'of'),
            (r'\bIn A\b', 'in a'),
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

    def test_replaces_publisher_substring(self):
        self._check_call_ignorecase(
            given='Foo publications',
            expect='Foo PUBLISHING',
            regex_replacements=[
                (r'Publ?(\.|i(cations|sh(ers|ing)))?$', 'PUBLISHING'),
            ]
        )


class TestFindLongestMatch(TestCase):
    def _t(self, given, expect, regexes):
        actual = find_longest_match(regexes, given, ignore_case=False)
        self.assertEqual(expect, actual)

    def test_one_regex_when_string_does_not_match(self):
        regexes = [
            re.compile(r'Fo+'),
        ]
        self._t(given='Bar Baz', expect=None, regexes=regexes)

    def test_one_regex_when_string_matches(self):
        regexes = [
            re.compile(r'Fo+'),
        ]
        self._t(given='Foo Bar', expect='Foo', regexes=regexes)
        self._t(given='Foo Fooo Bar', expect='Fooo', regexes=regexes)

    def test_two_regexes_when_string_does_not_match(self):
        regexes = [
            re.compile(r'Fo+'),
            re.compile(r'Ba+'),
        ]
        self._t(given='meow meow', expect=None, regexes=regexes)

    def test_two_regexes_when_string_matches(self):
        regexes = [
            re.compile(r'Fo+'),
            re.compile(r'Bar+'),
        ]
        self._t(given='Foo Bar', expect='Foo', regexes=regexes)
        self._t(given='Foo Fooo Barrrrr', expect='Barrrrr', regexes=regexes)
        self._t(given='Foo Fooo Barrrrr', expect='Barrrrr', regexes=reversed(regexes))
