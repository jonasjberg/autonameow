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
from unittest.mock import (
    Mock,
    patch
)

from core import constants as C
from core.model.genericfields import (
    GenericAuthor,
    GenericCreator,
    GenericDateCreated,
    GenericDateModified,
    GenericField,
    GenericMimeType,
    GenericProducer,
    GenericSubject,
    GenericTags,
    get_all_generic_field_klasses,
    get_field_for_uri_leaf,
)
import unit.utils as uu
import unit.constants as uuconst


class TestGenericFieldBase(TestCase):
    def test_uri_returns_expected(self):
        actual = GenericField.uri()
        expected = '{}.{}.{}'.format(GenericField.meowuri_root.lower(),
                                     GenericField.meowuri_child.lower(),
                                     GenericField.meowuri_leaf.lower())
        self.assertEqual(actual, expected)

    def test_base_class_uri_root_is_defined(self):
        self.assertEqual(GenericField.meowuri_root,
                         C.MEOWURI_ROOT_GENERIC)

    def test_base_class_uri_child_is_undefined(self):
        self.assertEqual(GenericField.meowuri_child,
                         C.UNDEFINED_MEOWURI_PART)

    def test_base_class_uri_leaf_is_undefined(self):
        self.assertEqual(GenericField.meowuri_leaf,
                         C.UNDEFINED_MEOWURI_PART)


class TestGenericFieldStr(TestCase):
    def setUp(self):
        self.klass_expected = [
            (GenericAuthor, uuconst.MEOWURI_GEN_METADATA_AUTHOR),
            (GenericCreator, uuconst.MEOWURI_GEN_METADATA_CREATOR),
            (GenericDateCreated, uuconst.MEOWURI_GEN_METADATA_DATECREATED),
            (GenericDateModified, uuconst.MEOWURI_GEN_METADATA_DATEMODIFIED),
            (GenericMimeType, uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE),
            (GenericProducer, uuconst.MEOWURI_GEN_METADATA_PRODUCER),
            (GenericSubject, uuconst.MEOWURI_GEN_METADATA_SUBJECT),
            (GenericTags, uuconst.MEOWURI_GEN_METADATA_TAGS),
        ]

    def test_returns_expected_uri_string(self):
        for generic_field, expected_uri in self.klass_expected:
            actual = generic_field.uri()
            self.assertEqual(actual, expected_uri)


class TestGetAllGenericFieldKlasses(TestCase):
    def test_returns_sequence_type(self):
        actual = get_all_generic_field_klasses()
        list_actual = [x for x in actual]
        self.assertTrue(all(x in actual for x in list_actual))
        self.assertTrue(all(x in list_actual for x in actual))

    def test_returns_at_least_ten_generic_field_class(self):
        actual = get_all_generic_field_klasses()
        self.assertGreaterEqual(len(actual), 10)

    def test_returns_subclasses_of_generic_field(self):
        actual = get_all_generic_field_klasses()
        for a in actual:
            with self.subTest(actual_field_klass=a):
                self.assertTrue(uu.is_class(a))
                self.assertTrue(issubclass(a, GenericField))


class TestGetFieldForUriLeaf(TestCase):
    def test_returns_none_given_empty_or_none_argument(self):
        for given in [None, '', ' ']:
            with self.subTest(given=given):
                self.assertIsNone(get_field_for_uri_leaf(given))

    def test_returns_none_if_no_corresponding_field_class_is_found(self):
        for given in ['foo', 'foo bar', 'foo_bar']:
            with self.subTest(given=given):
                self.assertIsNone(get_field_for_uri_leaf(given))

    @patch('core.model.genericfields._get_field_uri_leaf_to_klass_mapping')
    def test_returns_expected_given_generic_field_class_leaf(
            self, mock__get_field_uri_leaf_to_klass_mapping
    ):
        DUMMY_MAPPING = {
            'author': 'GenericAuthor',
            'creator': 'GenericCreator',
            'date_created': 'GenericDateCreated',
            'date_modified': 'GenericDateModified',
            'description': 'GenericDescription',
            'edition': 'GenericEdition',
            'mime_type': 'GenericMimeType',
            'producer': 'GenericProducer',
            'publisher': 'GenericPublisher',
            'subject': 'GenericSubject',
            'tags': 'GenericTags',
            'text': 'GenericText',
            'title': 'GenericTitle',
        }
        mock__get_field_uri_leaf_to_klass_mapping.return_value = dict(DUMMY_MAPPING)
        for string in DUMMY_MAPPING.keys():
            actual = get_field_for_uri_leaf(string)
            self.assertEqual(DUMMY_MAPPING[string], actual)

    def test_returns_expected(self):
        # TODO: [hardcoded] Must be updated when modifying generic fields ..
        from core.model.genericfields import (
            GenericDescription,
            GenericEdition,
            GenericPublisher,
            GenericText,
            GenericTitle
        )
        EXPECTED_MAPPING = {
            'author': GenericAuthor,
            'creator': GenericCreator,
            'date_created': GenericDateCreated,
            'date_modified': GenericDateModified,
            'description': GenericDescription,
            'edition': GenericEdition,
            'mime_type': GenericMimeType,
            'producer': GenericProducer,
            'publisher': GenericPublisher,
            'subject': GenericSubject,
            'tags': GenericTags,
            'text': GenericText,
            'title': GenericTitle,
        }
        for string in EXPECTED_MAPPING.keys():
            actual = get_field_for_uri_leaf(string)
            self.assertEqual(EXPECTED_MAPPING[string], actual)
