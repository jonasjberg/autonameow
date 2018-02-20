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

import unit.utils as uu
from core import types
from core.namebuilder import fields


class TestFormatStringPlaceholders(TestCase):
    def _assert_contains(self, template, expected):
        self.assertEqual(fields.format_string_placeholders(template), expected)

    def test_empty_or_whitespace(self):
        self._assert_contains('', [])
        self._assert_contains(' ', [])

    def test_unexpected_input_raises_valueerror(self):
        def _assert_raises(template):
            with self.assertRaises(TypeError):
                fields.format_string_placeholders(template)

        _assert_raises(None)
        _assert_raises(1)
        _assert_raises(uu.str_to_datetime('2016-01-11 124132'))
        _assert_raises(b'')
        _assert_raises(b' ')
        _assert_raises(b'foo')
        _assert_raises(b'{foo}')

    def test_no_placeholders(self):
        self._assert_contains('abc', [])
        self._assert_contains('abc}', [])
        self._assert_contains('{abc', [])
        self._assert_contains('{abc {foo', [])
        self._assert_contains('{abc foo}', [])

    def test_one_placeholder(self):
        self._assert_contains('abc {foo}', ['foo'])
        self._assert_contains('abc {foo}', ['foo'])
        self._assert_contains('{abc {foo}', ['foo'])
        self._assert_contains('abc} {foo}', ['foo'])
        self._assert_contains('{abc def} {foo}', ['foo'])
        self._assert_contains('abc{ def} {foo}', ['foo'])

    def test_two_unique_placeholders(self):
        self._assert_contains('{abc} {foo}', ['abc', 'foo'])
        self._assert_contains('{abc} abc {foo}', ['abc', 'foo'])
        self._assert_contains('{abc} {{foo}', ['abc', 'foo'])
        self._assert_contains('{abc} {abc {foo}', ['abc', 'foo'])
        self._assert_contains('{abc} {abc }{foo}', ['abc', 'foo'])

    def test_duplicate_placeholders(self):
        self._assert_contains('{foo} {foo}', ['foo', 'foo'])
        self._assert_contains('{foo} abc {foo}', ['foo', 'foo'])
        self._assert_contains('{foo} {foo}', ['foo', 'foo'])
        self._assert_contains('{foo} {abc {foo}', ['foo', 'foo'])
        self._assert_contains('{foo} abc} {foo}', ['foo', 'foo'])
        self._assert_contains('{foo} {abc } {foo}', ['foo', 'foo'])
        self._assert_contains('{foo} {abc} {foo}', ['foo', 'abc', 'foo'])
        self._assert_contains('{abc} {abc} {foo}', ['abc', 'abc', 'foo'])


class TestAvailableNametemplatefieldClasses(TestCase):
    def test_returns_something(self):
        actual = fields.available_nametemplatefield_classes()
        self.assertGreater(len(actual), 0)

    def test_does_not_return_base_class(self):
        actual = fields.available_nametemplatefield_classes()
        self.assertNotIn(fields.NameTemplateField, actual)

    def test_returns_subset_of_expected(self):
        actual = fields.available_nametemplatefield_classes()

        def _aIn(member):
            self.assertIn(member, actual)

        _aIn(fields.Author)
        _aIn(fields.Creator)
        _aIn(fields.Date)
        _aIn(fields.DateTime)
        _aIn(fields.Description)
        _aIn(fields.Edition)
        _aIn(fields.Extension)
        _aIn(fields.Publisher)
        _aIn(fields.Tags)
        _aIn(fields.Title)


class TestNameTemplateField(TestCase):
    def test_comparison(self):
        self.assertEqual(fields.Author, fields.Author)

        a1 = fields.Author
        a2 = fields.Author
        self.assertEqual(a1, a2)

        self.assertNotEqual(fields.Author, fields.Title)

    def test_membership(self):
        s = set()
        self.assertNotIn(fields.Author, s)
        self.assertNotIn(fields.Title, s)
        self.assertNotIn(fields.Publisher, s)

        s.add(fields.Author)
        self.assertEqual(len(s), 1)

        s.add(fields.Author)
        self.assertEqual(len(s), 1)

        s.add(fields.Title)
        self.assertEqual(len(s), 2)

        self.assertIn(fields.Author, s)
        self.assertIn(fields.Title, s)
        self.assertNotIn(fields.Publisher, s)


class TestIsValidTemplateField(TestCase):
    def test_invalid_fields_returns_false(self):
        def _aF(test_input):
            self.assertFalse(fields.is_valid_template_field(test_input))

        _aF(None)
        _aF('')
        _aF('foo')

    def test_valid_fields_return_true(self):
        def _aT(test_input):
            self.assertTrue(fields.is_valid_template_field(test_input))

        _aT('author')
        _aT('date')
        _aT('datetime')
        _aT('description')
        _aT('edition')
        _aT('extension')
        _aT('publisher')
        _aT('tags')
        _aT('title')


class TestNametemplatefieldClassFromString(TestCase):
    def test_returns_expected_classes(self):
        def _aE(string, expected):
            actual = fields.nametemplatefield_class_from_string(string)
            self.assertEqual(actual, expected)

        _aE('', None)
        _aE('auuuthoorrr', None)
        _aE('author', fields.Author)
        _aE('title', fields.Title)


class TestNametemplatefieldClassesInFormatstring(TestCase):
    def _aC(self, string, klass_list):
        actual = fields.nametemplatefield_classes_in_formatstring(string)
        for klass in klass_list:
            self.assertIn(klass, actual)

    def test_contains_none(self):
        self._aC('', [])
        self._aC('foo', [])

    def test_contains_expected_1(self):
        self._aC('{title}', [fields.Title])
        self._aC('{title} foo', [fields.Title])
        self._aC('{title} title', [fields.Title])

    def test_contains_expected_2(self):
        self._aC('{title} {author}',
                 [fields.Title, fields.Author])
        self._aC('{title} foo {author}',
                 [fields.Title, fields.Author])
        self._aC('{title} title {author} author',
                 [fields.Title, fields.Author])

    def test_contains_expected_3(self):
        self._aC('{title} {author} {description}',
                 [fields.Title, fields.Author, fields.Description])
        self._aC('foo {title} {author} - {description}.foo',
                 [fields.Title, fields.Author, fields.Description])


class NameTemplateFieldCompatible(TestCase):
    def _compatible(self, nametemplate_field, coercer_class):
        tf = nametemplate_field()
        actual = tf.type_compatible(coercer_class)
        self.assertTrue(actual)

    def _incompatible(self, nametemplate_field, coercer_class):
        tf = nametemplate_field()
        actual = tf.type_compatible(coercer_class)
        self.assertFalse(actual)

    def test_compatible_with_name_template_field_description(self):
        self._compatible(fields.Description, types.AW_STRING)
        self._compatible(fields.Description, types.AW_INTEGER)

    def test_not_compatible_with_name_template_field_description(self):
        self._incompatible(fields.Description, types.AW_TIMEDATE)
        self._incompatible(fields.Description, types.listof(types.AW_STRING))

    def test_compatible_with_name_template_field_tags(self):
        self._compatible(fields.Tags, types.AW_STRING)
        self._compatible(fields.Tags, types.listof(types.AW_STRING))

    def test_not_compatible_with_name_template_field_tags(self):
        self._incompatible(fields.Description, types.AW_TIMEDATE)
        self._incompatible(fields.Description, types.listof(types.AW_TIMEDATE))


class TestTitle(TestCase):
    def test___str__(self):
        self.skipTest('TODO: [TD0140] Fix Template field classes __str__')
        actual = str(fields.Title)
        expect = 'Title'
        self.assertEqual(expect, actual)
