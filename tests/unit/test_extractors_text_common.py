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
from core import constants as C
from extractors.text.common import AbstractTextExtractor


ALL_EXTRACTOR_FIELDS_TYPES = [
    ('full', str),
]


class TestAbstractTextExtractor(TestCase):
    def setUp(self):
        self.test_file = uu.make_temporary_file()
        self.e = AbstractTextExtractor()

        class DummyFileObject(object):
            def __init__(self):
                self.mime_type = 'image/jpeg'
        self.fo = DummyFileObject()

    def test_abstract_text_extractor_class_is_available(self):
        self.assertIsNotNone(AbstractTextExtractor)

    def test_abstract_text_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_method_str_does_not_return_none(self):
        self.assertIsNotNone(str(self.e))
        self.assertIsNotNone(self.e.__str__)

    def test_method_str_returns_type_string(self):
        self.assertTrue(uu.is_internalstring(str(self.e)))
        self.assertTrue(uu.is_internalstring(str(self.e.__str__)))

    def test_method_str_returns_expected(self):
        self.assertEqual(str(self.e), 'AbstractTextExtractor')

    def test_class_method_can_handle_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            _ = self.e.can_handle(self.fo)

    def test_extract_text_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e.extract_text(self.test_file)

    def test_extract_raises_exception_with_extract_text_unimplemented(self):
        with self.assertRaises(NotImplementedError):
            _ = self.e.extract(self.test_file)

    def test_abstract_class_does_not_specify_which_mime_types_are_handled(self):
        self.assertIsNone(self.e.HANDLES_MIME_TYPES)

    def test_abstract_class_does_not_specify_meowuri_node(self):
        self.assertEqual(self.e.MEOWURI_CHILD, C.MEOWURI_UNDEFINED_PART)

    def test_abstract_class_does_not_specify_meowuri_leaf(self):
        self.assertEqual(self.e.MEOWURI_LEAF, C.MEOWURI_UNDEFINED_PART)

    def test__get_raw_text_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e.extract_text(self.test_file)

    def test_check_dependencies_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e.check_dependencies()


class TestAbstractTextExtractorMetainfo(TestCase):
    def setUp(self):
        _extractor_instance = AbstractTextExtractor()
        self.actual = _extractor_instance.metainfo()

    def test_metainfo_returns_expected_type(self):
        self.assertIsInstance(self.actual, dict)

    def test_metainfo_returns_expected_fields(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn(_field, self.actual)

    def test_metainfo_specifies_types_for_all_fields(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            self.assertIn('coercer', self.actual.get(_field, {}))

    def test_metainfo_multivalued_is_none_or_boolean(self):
        for _field, _ in ALL_EXTRACTOR_FIELDS_TYPES:
            _field_lookup_entry = self.actual.get(_field, {})
            self.assertIn('multivalued', _field_lookup_entry)

            actual = _field_lookup_entry.get('multivalued')
            self.assertIsInstance(actual, (bool, type(None)))
