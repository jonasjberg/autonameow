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

from devscripts.find_todo_comments import find_todo_comments_in_text


class TestFindTodoCommentsInText(TestCase):
    def test_returns_empty_list_given_empty_text(self):
        actual = find_todo_comments_in_text('')
        self.assertFalse(actual)

    def _assert_finds(self, expected, given_text):
        actual = find_todo_comments_in_text(given_text)
        self.assertEqual(expected, actual)

    def test_single_line_without_todo(self):
        actual = find_todo_comments_in_text('foo')
        self.assertEqual(list(), actual)

    def test_single_line_with_single_todo(self):
        actual = find_todo_comments_in_text('# TODO: foo\n')
        self.assertEqual(['# TODO: foo'], actual)

    def test_multiple_lines_with_single_todo(self):
        actual = find_todo_comments_in_text('\nfoobar\n\n# TODO: foo\n')
        self.assertEqual(['# TODO: foo'], actual)

    def test_hack_todo_single_line(self):
        self.skipTest('TODO')
        self._assert_finds(
            expected=[
                '# TODO: [hack] Fix failing regression test 9017 properly!',
            ],
            given_text='''
    # TODO: [hack] Fix failing regression test 9017 properly!
''')

    def test_hack_todo_multiple_lines(self):
        self._assert_finds(
            expected=[
                '# TODO: [hack] Sorting is reversed so that,\n'
                '#       ..lower values in the "year" field.\n'
                '#       This applies only when foo are bar.'
            ],
            given_text='''
# TODO: [hack] Sorting is reversed so that,
#       ..lower values in the "year" field.
#       This applies only when foo are bar.
''')

    def test_hack_todo_multiple_lines_and_other_todo(self):
        self._assert_finds(
            expected=[
                '# TODO: [hack] Sorting is reversed so that,\n'
                '#       ..lower values in the "year" field.\n'
                '#       This applies only when whatever ..',

                '# TODO: foo bar',
            ],
            given_text='''
# TODO: [hack] Sorting is reversed so that,
#       ..lower values in the "year" field.
#       This applies only when whatever ..

# TODO: foo bar
''')
