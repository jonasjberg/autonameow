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

from unittest import TestCase

from devscripts.todo_id import find_todo_ids_in_line
from devscripts.todo_id import find_todo_ids_in_lines
from devscripts.todo_id import TodoPriority


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


class TestFindTodoIdsInLines(TestCase):
    def __assert_matches(self, given, expect):
        for todo_id_dict in expect:
            if 'priority' not in todo_id_dict:
                todo_id_dict.update({'priority': None})

        actual = find_todo_ids_in_lines(given)
        # self.assertEqual(len(expect), len(actual))
        for element in expect:
            self.assertIn(element, actual)

    def test_finds_single_id_and_ignores_lines_with_only_whitespace(self):
        self.__assert_matches(
            given=[' \n', '\n', '# TODO: [TD0666]\n', 'foo bar\n'],
            expect=[{'id': '0666', 'text': ''}]
        )

    def test_finds_single_id_with_text(self):
        self.__assert_matches(
            given=['# TODO: [TD0666] Foo bar.\n'],
            expect=[{'id': '0666', 'text': 'Foo bar.'}]
        )

    def test_finds_two_ids_in_single_todo(self):
        self.__assert_matches(
            given=['# TODO: [TD1337][TD1348]\n'],
            expect=[{'id': '1337', 'text': ''},
                    {'id': '1348', 'text': ''}]
        )

    def test_finds_two_ids_with_text_in_single_todo(self):
        self.__assert_matches(
            given=['# TODO: [TD1337][TD1348] Implement baz.\n'],
            expect=[{'id': '1337', 'text': 'Implement baz.'},
                    {'id': '1348', 'text': 'Implement baz.'}]
        )

    def test_returns_todo_priority_high(self):
        self.__assert_matches(
            given=['\n',
                   '\n',
                   'High Priority\n',
                   '-------------\n',
                   '\n',
                   '* `[TD1348]` What have I done?\n',
                   ''],
            expect=[{
                'id': '1348',
                'text': 'What have I done?',
                'priority': TodoPriority.HIGH,
            }]
        )

    def test_returns_todo_priority_medium(self):
        self.__assert_matches(
            given=['\n',
                   '\n',
                   'Medium Priority\n',
                   '---------------\n',
                   '\n',
                   '* `[TD1348]` What have I done?\n',
                   '\n',
                   '* `[TD1349]` 2 + 2 = 5\n',
                   ''],
            expect=[
                {
                    'id': '1348',
                    'text': 'What have I done?',
                    'priority': TodoPriority.MEDIUM,
                }, {
                    'id': '1349',
                    'text': '2 + 2 = 5',
                    'priority': TodoPriority.MEDIUM,
                },
            ]
        )

    def test_returns_todo_priority_low(self):
        self.__assert_matches(
            given=['\n',
                   '\n',
                   'Low Priority\n',
                   '------------\n',
                   '\n',
                   '* `[TD2000]` foo\n',
                   '\n',
                   '* `[TD2001]` bar\n',
                   ''],
            expect=[
                {
                    'id': '2000',
                    'text': 'foo',
                    'priority': TodoPriority.LOW,
                }, {
                    'id': '2001',
                    'text': 'bar',
                    'priority': TodoPriority.LOW,
                },
            ]
        )

    def test_returns_todo_priorities_high_and_medium(self):
        self.__assert_matches(
            given=['\n',
                   '\n',
                   'Medium Priority\n',
                   '---------------\n',
                   '\n',
                   '* `[TD1348]` What have I done?\n',
                   '\n',
                   '* `[TD1349]` 2 + 2 = 5\n',
                   ''],
            expect=[
                {
                    'id': '1348',
                    'text': 'What have I done?',
                    'priority': TodoPriority.MEDIUM,
                }, {
                    'id': '1349',
                    'text': '2 + 2 = 5',
                    'priority': TodoPriority.MEDIUM,
                },
            ]
        )
