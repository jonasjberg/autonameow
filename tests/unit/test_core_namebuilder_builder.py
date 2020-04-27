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

from unittest import TestCase

from core import exceptions
from core.namebuilder import populate_name_template


class TestPopulateNameTemplate(TestCase):
    def test_strips_single_quotes_from_format_string(self):
        actual = populate_name_template("'foo' bar'")
        self.assertEqual('foo bar', actual)

    def test_strips_double_quotes_from_format_string(self):
        actual = populate_name_template('"foo" bar"')
        self.assertEqual('foo bar', actual)

    def test_strips_single_and_double_quotes_from_format_string(self):
        actual = populate_name_template('"foo" \'"baz"\' bar"')
        self.assertEqual('foo baz bar', actual)

    def test_name_template_using_template_1_given_all_fields(self):
        template = '{title} - {author} {datetime}.{extension}'
        data = {'title': '11 years old and dying',
                'author': 'Gibson',
                'datetime': '2017-05-27',
                'extension': 'pdf'}
        expect = '11 years old and dying - Gibson 2017-05-27.pdf'

        self.assertEqual(populate_name_template(template, **data), expect)

    def test_name_template_using_template_1_some_fields_missing(self):
        with self.assertRaises(exceptions.NameTemplateSyntaxError):
            template = '{title} - {author} {datetime}.{extension}'
            data = {'author': None,
                    'datetime': '2017-05-27',
                    'extension': None}
            expect = '11 years old and dying - Gibson 2017-05-27.pdf'
            self.assertEqual(populate_name_template(template, **data), expect)

    def test_name_template_using_template_2_given_all_fields(self):
        template = '{publisher} {title} {edition} - {author} {date}.{extension}'
        data = {'title': '11 years old and dying',
                'publisher': 'CatPub',
                'edition': 'Final Edition',
                'author': 'Gibson',
                'date': '2017',
                'extension': 'pdf'}
        expect = 'CatPub 11 years old and dying Final Edition - Gibson 2017.pdf'

        self.assertEqual(populate_name_template(template, **data), expect)

    def test_name_template_using_template_2_all_fields_missing(self):
        template = '{publisher} {title} {edition} - {author} {date}.{extension}'
        data = dict()
        expect = 'CatPub 11 years old and dying Final Edition - Gibson 2017.pdf'

        with self.assertRaises(exceptions.NameTemplateSyntaxError):
            self.assertEqual(populate_name_template(template, **data), expect)
