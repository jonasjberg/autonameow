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
from core.model import MeowURI
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
    meowuri_genericfield_map
)
import unit.utils as uu
import unit.constants as uuconst


class TestGenericFieldBase(TestCase):
    def test_uri_returns_expected(self):
        actual = GenericField.uri()
        expected = '{}.{}.{}'.format(GenericField.meowuri_root.lower(),
                                     GenericField.meowuri_node.lower(),
                                     GenericField.meowuri_leaf.lower())
        self.assertEqual(actual, expected)

    def test_base_class_uri_root_is_defined(self):
        self.assertEqual(GenericField.meowuri_root,
                         C.MEOWURI_ROOT_GENERIC)

    def test_base_class_uri_node_is_undefined(self):
        self.assertEqual(GenericField.meowuri_node,
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


class TestGenericMeowURIs(TestCase):
    def test_returns_expected_type(self):
        actual = meowuri_genericfield_map()
        self.assertTrue(isinstance(actual, dict))

        for meowuri, field_klass in actual.items():
            self.assertTrue(uu.is_class_instance(meowuri))
            self.assertTrue(isinstance(meowuri, MeowURI))

            self.assertTrue(uu.is_class(field_klass))
            self.assertTrue(issubclass(field_klass, GenericField))
