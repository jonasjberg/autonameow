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

from devscripts.todo_id import find_todo_ids_in_line


class TestFindTodoIdsInLine(TestCase):
    def __assert_matches(self, given, expect):
        actual = find_todo_ids_in_line(given)
        self.assertEqual(len(expect), len(actual))
        for element in expect:
            self.assertIn(element, actual)

    def test_finds_single_id(self):
        self.__assert_matches(
            given='# TODO: [TD0666]',
            expect=[{'id': '0666', 'text': ''}]
        )

    def test_finds_single_id_with_text(self):
        self.__assert_matches(
            given='# TODO: [TD0666] Foo bar.',
            expect=[{'id': '0666', 'text': 'Foo bar.'}]
        )

    def test_finds_single_id_on_indented_line(self):
        self.__assert_matches(
            given='    # TODO: [TD0666]',
            expect=[{'id': '0666', 'text': ''}]
        )

    def test_finds_single_id_with_text_on_indented_line(self):
        self.__assert_matches(
            given='    # TODO: [TD0666] Foo bar.',
            expect=[{'id': '0666', 'text': 'Foo bar.'}]
        )

    def test_finds_two_ids_in_single_todo(self):
        self.__assert_matches(
            given='# TODO: [TD1337][TD1338]',
            expect=[{'id': '1337', 'text': ''},
                    {'id': '1338', 'text': ''}]
        )

    def test_finds_two_ids_with_text_in_single_todo(self):
        self.__assert_matches(
            given='# TODO: [TD1337][TD1338] Implement baz.',
            expect=[{'id': '1337', 'text': 'Implement baz.'},
                    {'id': '1338', 'text': 'Implement baz.'}]
        )

    def test_finds_two_ids_with_text_in_single_todo_on_indented_line(self):
        self.__assert_matches(
            given='    # TODO: [TD1337][TD1338] Implement baz.',
            expect=[{'id': '1337', 'text': 'Implement baz.'},
                    {'id': '1338', 'text': 'Implement baz.'}]
        )

    def test_finds_three_ids_with_text_in_single_todo(self):
        self.__assert_matches(
            given='# TODO: [TD1337][TD1338][TD1339] Implement baz.',
            expect=[{'id': '1337', 'text': 'Implement baz.'},
                    {'id': '1338', 'text': 'Implement baz.'},
                    {'id': '1339', 'text': 'Implement baz.'}]
        )

    def test_finds_three_ids_with_text_in_single_todo_on_indented_line(self):
        self.__assert_matches(
            given='    # TODO: [TD1337][TD1338][TD1339] Implement baz.',
            expect=[{'id': '1337', 'text': 'Implement baz.'},
                    {'id': '1338', 'text': 'Implement baz.'},
                    {'id': '1339', 'text': 'Implement baz.'}]
        )

    def test_ignores_related_ids(self):
        self.__assert_matches(
            given='>       continue to go unused.  See also, related entry: `[TD0060]`',
            expect=[]
        )

    def test_ignores_multiple_related_ids(self):
        self.__assert_matches(
            given='>   __Related:__ `[TD0015][TD0017][TD0049]`',
            expect=[]
        )
