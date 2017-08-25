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

from core import (
    namebuilder,
    exceptions
)


class TestNameBuilder(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.populate = namebuilder.populate_name_template

    def test_populate_name_template_using_template_1_given_all_fields(self):
        template = '{title} - {author} {datetime}.{extension}'
        data = {'title': '11 years old and dying',
                'author': 'Gibson',
                'datetime': '2017-05-27',
                'extension': 'pdf'}
        expected = '11 years old and dying - Gibson 2017-05-27.pdf'

        self.assertEqual(self.populate(template, **data), expected)

    def test_populate_name_template_using_template_1_some_fields_missing(self):
        with self.assertRaises(exceptions.NameTemplateSyntaxError):
            template = '{title} - {author} {datetime}.{extension}'
            data = {'author': None,
                    'datetime': '2017-05-27',
                    'extension': None}
            expected = '11 years old and dying - Gibson 2017-05-27.pdf'
            self.assertEqual(self.populate(template, **data), expected)

    def test_populate_name_template_using_template_2_given_all_fields(self):
        template = '{publisher} {title} {edition} - {author} {date}.{extension}'
        data = {'title': '11 years old and dying',
                'publisher': 'CatPub',
                'edition': 'Final Edition',
                'author': 'Gibson',
                'date': '2017',
                'extension': 'pdf'}
        expected = 'CatPub 11 years old and dying Final Edition - Gibson 2017.pdf'

        self.assertEqual(self.populate(template, **data), expected)

    def test_populate_name_template_using_template_2_all_fields_missing(self):
        with self.assertRaises(exceptions.NameTemplateSyntaxError):
            template = '{publisher} {title} {edition} - {author} {date}.{extension}'
            data = {}
            expected = 'CatPub 11 years old and dying Final Edition - Gibson 2017.pdf'
            self.assertEqual(self.populate(template, **data), expected)


class TestFormatStringPlaceholders(TestCase):
    def setUp(self):
        self.formatsph = namebuilder.format_string_placeholders

    def test_format_string_placeholders_no_input(self):
        self.assertEqual(self.formatsph(None), [])

    def test_format_string_placeholders_no_placeholders(self):
        self.assertEqual(self.formatsph('abc'), [])

    def test_format_string_placeholders_one_placeholder(self):
        self.assertEqual(self.formatsph('abc {foo}'), ['foo'])

    def test_format_string_placeholders_two_unique_placeholders(self):
        self.assertEqual(self.formatsph('{abc} abc {foo}'),
                         ['abc', 'foo'])

    def test_format_string_placeholders_duplicate_placeholders(self):
        self.assertEqual(self.formatsph('{foo} abc {foo}'),
                         ['foo', 'foo'])


class TestAllTemplateFieldsDefined(TestCase):
    def setUp(self):
        self.all_defined = namebuilder.all_template_fields_defined
        self.template = '{datetime} {title} -- tag.{extension}'
        self.data_sources_ok = {'datetime': 'dummy',
                                'extension': 'dummy',
                                'title': 'dummy'}
        self.data_sources_missing = {'datetime': 'dummy',
                                     'extension': 'dummy'}

    def test_return_false_if_sources_does_not_include_all_template_fields(self):
        self.assertFalse(self.all_defined(self.template,
                                          self.data_sources_missing))

    def test_return_true_if_sources_contain_all_template_fields(self):
        self.assertTrue(self.all_defined(self.template, self.data_sources_ok))
