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

from core import constants as C
from core import fields
from core.fields import (
    available_nametemplatefield_classes,
    format_string_placeholders,
    GenericAuthor,
    GenericCreator,
    GenericDateCreated,
    GenericDateModified,
    GenericField,
    GenericMimeType,
    GenericProducer,
    GenericSubject,
    GenericTags,
    nametemplatefield_class_from_string
)
import unit_utils as uu


class TestGenericFieldBase(TestCase):
    def test_uri_returns_expected(self):
        actual = GenericField.uri()
        expected = '{}.{}.{}'.format(GenericField.meowuri_root.lower(),
                                     GenericField.meowuri_node.lower(),
                                     GenericField.meowuri_leaf.lower())
        self.assertEqual(actual, expected)

    def test_base_class_uri_root_is_undefined(self):
        self.assertEqual(GenericField.meowuri_root,
                         C.UNDEFINED_MEOWURI_PART)

    def test_base_class_uri_leaf_is_undefined(self):
        self.assertEqual(GenericField.meowuri_leaf,
                         C.UNDEFINED_MEOWURI_PART)


class TestGenericFieldStr(TestCase):
    def setUp(self):
        self.test_data = [
            (GenericAuthor, 'metadata.generic.author'),
            (GenericCreator, 'metadata.generic.creator'),
            (GenericDateCreated, 'metadata.generic.date_created'),
            (GenericDateModified, 'metadata.generic.date_modified'),
            (GenericMimeType, 'contents.generic.mime_type'),
            (GenericProducer, 'metadata.generic.producer'),
            (GenericSubject, 'metadata.generic.subject'),
            (GenericTags, 'metadata.generic.tags'),
        ]

    def test_returns_expected_uri_string(self):
        for generic_field, expected_uri in self.test_data:
            actual = generic_field.uri()
            self.assertEqual(actual, expected_uri)


class TestGenericMeowURIs(TestCase):
    def test_returns_expected_type(self):
        actual = fields.meowuri_genericfield_map()
        self.assertTrue(isinstance(actual, dict))

        for meowuri, field_klass in actual.items():
            self.assertTrue(isinstance(meowuri, str))

            self.assertTrue(uu.is_class(field_klass))
            self.assertTrue(issubclass(field_klass, GenericField))


class TestFormatStringPlaceholders(TestCase):
    def _assert_contains(self, template, expected):
        self.assertEqual(format_string_placeholders(template), expected)

    def test_empty_or_whitespace(self):
        self._assert_contains('', [])
        self._assert_contains(' ', [])

    def test_unexpected_input_raises_valueerror(self):
        def _assert_raises(template):
            with self.assertRaises(TypeError):
                format_string_placeholders(template)

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
        actual = available_nametemplatefield_classes()
        self.assertGreater(len(actual), 0)

    def test_does_not_return_base_class(self):
        actual = available_nametemplatefield_classes()
        self.assertNotIn(fields.NameTemplateField, actual)

    def test_returns_subset_of_expected(self):
        actual = available_nametemplatefield_classes()
        self.assertIn(fields.Author, actual)
        self.assertIn(fields.Creator, actual)
        self.assertIn(fields.Date, actual)
        self.assertIn(fields.DateTime, actual)
        self.assertIn(fields.Description, actual)
        self.assertIn(fields.Edition, actual)
        self.assertIn(fields.Extension, actual)
        self.assertIn(fields.Publisher, actual)
        self.assertIn(fields.Tags, actual)
        self.assertIn(fields.Title, actual)


class TestNametemplatefieldClassFromString(TestCase):
    def _aE(self, string, expected):
        actual = nametemplatefield_class_from_string(string)
        self.assertEqual(actual, expected)

    def test_returns_expected_classes(self):
        self._aE('author', fields.Author)
        self._aE('title', fields.Title)
