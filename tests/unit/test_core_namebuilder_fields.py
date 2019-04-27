# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from core.namebuilder import fields
from util import coercers


FIELDS_AUTHOR = fields.Author
FIELDS_CREATOR = fields.Creator
FIELDS_DATE = fields.Date
FIELDS_DATETIME = fields.DateTime
FIELDS_DESCRIPTION = fields.Description
FIELDS_EDITION = fields.Edition
FIELDS_EXTENSION = fields.Extension
FIELDS_PUBLISHER = fields.Publisher
FIELDS_TAGS = fields.Tags
FIELDS_TIME = fields.Time
FIELDS_TITLE = fields.Title


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

        _aIn(FIELDS_AUTHOR)
        _aIn(FIELDS_CREATOR)
        _aIn(FIELDS_DATE)
        _aIn(FIELDS_DATETIME)
        _aIn(FIELDS_DESCRIPTION)
        _aIn(FIELDS_EDITION)
        _aIn(FIELDS_EXTENSION)
        _aIn(FIELDS_PUBLISHER)
        _aIn(FIELDS_TAGS)
        _aIn(FIELDS_TITLE)


class TestNameTemplateField(TestCase):
    def test_comparison(self):
        self.assertEqual(FIELDS_AUTHOR, FIELDS_AUTHOR)

        a1 = FIELDS_AUTHOR
        a2 = FIELDS_AUTHOR
        self.assertEqual(a1, a2)

        self.assertNotEqual(FIELDS_AUTHOR, FIELDS_TITLE)

    def test_membership(self):
        s = set()
        self.assertNotIn(FIELDS_AUTHOR, s)
        self.assertNotIn(FIELDS_TITLE, s)
        self.assertNotIn(FIELDS_PUBLISHER, s)

        s.add(FIELDS_AUTHOR)
        self.assertEqual(len(s), 1)

        s.add(FIELDS_AUTHOR)
        self.assertEqual(len(s), 1)

        s.add(FIELDS_TITLE)
        self.assertEqual(len(s), 2)

        self.assertIn(FIELDS_AUTHOR, s)
        self.assertIn(FIELDS_TITLE, s)
        self.assertNotIn(FIELDS_PUBLISHER, s)


class TestNameTemplateFieldSubclasses(TestCase):
    def test_as_placeholder_returns_expected(self):
        for field, expected in [
            (FIELDS_AUTHOR, 'author'),
            (FIELDS_CREATOR, 'creator'),
            (FIELDS_DATE, 'date'),
            (FIELDS_DATETIME, 'datetime'),
            (FIELDS_DESCRIPTION, 'description'),
            (FIELDS_EDITION, 'edition'),
            (FIELDS_EXTENSION, 'extension'),
            (FIELDS_PUBLISHER, 'publisher'),
            (FIELDS_TAGS, 'tags'),
            (FIELDS_TIME, 'time'),
            (FIELDS_TITLE, 'title'),
        ]:
            actual = field.as_placeholder()
            self.assertEqual(expected, actual)

    def test___str___returns_expected(self):
        for field, expected in [
            (FIELDS_AUTHOR, '{author}'),
            (FIELDS_CREATOR, '{creator}'),
            (FIELDS_DATE, '{date}'),
            (FIELDS_DATETIME, '{datetime}'),
            (FIELDS_DESCRIPTION, '{description}'),
            (FIELDS_EDITION, '{edition}'),
            (FIELDS_EXTENSION, '{extension}'),
            (FIELDS_PUBLISHER, '{publisher}'),
            (FIELDS_TAGS, '{tags}'),
            (FIELDS_TIME, '{time}'),
            (FIELDS_TITLE, '{title}'),
        ]:
            actual = str(field)
            self.assertEqual(expected, actual)

    def test___repr__returns_expected(self):
        for field, expected in [
            (FIELDS_AUTHOR, 'NameTemplateField<Author>'),
            (FIELDS_CREATOR, 'NameTemplateField<Creator>'),
            (FIELDS_DATE, 'NameTemplateField<Date>'),
            (FIELDS_DATETIME, 'NameTemplateField<DateTime>'),
            (FIELDS_DESCRIPTION, 'NameTemplateField<Description>'),
            (FIELDS_EDITION, 'NameTemplateField<Edition>'),
            (FIELDS_EXTENSION, 'NameTemplateField<Extension>'),
            (FIELDS_PUBLISHER, 'NameTemplateField<Publisher>'),
            (FIELDS_TAGS, 'NameTemplateField<Tags>'),
            (FIELDS_TIME, 'NameTemplateField<Time>'),
            (FIELDS_TITLE, 'NameTemplateField<Title>'),
        ]:
            actual = repr(field)
            self.assertEqual(expected, actual)


class TestIsValidTemplateField(TestCase):
    def test_invalid_fields_returns_false(self):
        def _aF(test_input):
            self.assertFalse(fields.is_valid_template_field(test_input))

        _aF(None)
        _aF(False)
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
        _aE('author', FIELDS_AUTHOR)
        _aE('title', FIELDS_TITLE)


class NameTemplateFieldCompatible(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.coercers_AW_INTEGER = coercers.AW_INTEGER
        cls.coercers_AW_STRING = coercers.AW_STRING
        cls.coercers_AW_TIMEDATE = coercers.AW_TIMEDATE

    def _compatible(self, nametemplate_field, coercer_class, multivalued):
        actual = nametemplate_field.type_compatible(coercer_class, multivalued)
        self.assertTrue(actual)

    def _incompatible(self, nametemplate_field, coercer_class, multivalued):
        actual = nametemplate_field.type_compatible(coercer_class, multivalued)
        self.assertFalse(actual)

    def test_compatible_with_name_template_field_description(self):
        self._compatible(FIELDS_DESCRIPTION, self.coercers_AW_STRING, multivalued=False)

        self._compatible(FIELDS_DESCRIPTION, self.coercers_AW_INTEGER, multivalued=False)

    def test_not_compatible_with_name_template_field_description(self):
        self._incompatible(FIELDS_DESCRIPTION, self.coercers_AW_STRING, multivalued=True)
        self._incompatible(FIELDS_DESCRIPTION, self.coercers_AW_INTEGER, multivalued=True)

        self._incompatible(FIELDS_DESCRIPTION, self.coercers_AW_TIMEDATE, multivalued=True)
        self._incompatible(FIELDS_DESCRIPTION, self.coercers_AW_TIMEDATE, multivalued=False)

    def test_compatible_with_name_template_field_tags(self):
        self._compatible(FIELDS_TAGS, self.coercers_AW_STRING, multivalued=True)

    def test_not_compatible_with_name_template_field_tags(self):
        self._incompatible(FIELDS_TAGS, self.coercers_AW_STRING, multivalued=False)

        self._incompatible(FIELDS_TAGS, self.coercers_AW_TIMEDATE, multivalued=False)
        self._incompatible(FIELDS_TAGS, self.coercers_AW_TIMEDATE, multivalued=True)

    def test_compatible_with_name_template_field_title(self):
        self._compatible(FIELDS_TITLE, self.coercers_AW_STRING, multivalued=False)

        self._compatible(FIELDS_TITLE, self.coercers_AW_INTEGER, multivalued=False)

    def test_not_compatible_with_name_template_field_title(self):
        self._incompatible(FIELDS_TITLE, self.coercers_AW_STRING, multivalued=True)

        self._incompatible(FIELDS_TITLE, self.coercers_AW_INTEGER, multivalued=True)

