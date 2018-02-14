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

import re
from unittest import TestCase
from unittest.mock import (
    MagicMock,
    patch
)

from core.namebuilder.builder import (
    FilenamePostprocessor
)


class TestFilenamePostprocessor(TestCase):
    @patch('core.namebuilder.builder.view', MagicMock())
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

    def test_simplify_unicode(self):
        self.__check_call(given='foo', expect='foo',
                          simplify_unicode=False)
        self.__check_call(given='Fooçalbar', expect='Fooçalbar',
                          simplify_unicode=False)
        self.__check_call(given='Fooçalbar', expect='Foocalbar',
                          simplify_unicode=True)
