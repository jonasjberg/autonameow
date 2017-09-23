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
    GenericAuthor,
    GenericCreator,
    GenericDateCreated,
    GenericDateModified,
    GenericField,
    GenericMimeType,
    GenericProducer,
    GenericSubject,
    GenericTags
)
import unit_utils as uu


class TestGenericFieldBase(TestCase):
    def test_uri_returns_expected(self):
        actual = GenericField.uri()
        expected = '{}.{}.{}'.format(GenericField.meowuri_root.lower(),
                                     GenericField.meowuri_node_generic,
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

