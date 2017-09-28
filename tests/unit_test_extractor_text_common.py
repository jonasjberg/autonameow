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
from extractors import ExtractorError
from extractors.text.common import (
    AbstractTextExtractor,
    normalize_unicode
)
import unit_utils as uu


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

    def test_query_raises_exception_with__get_raw_text_unimplemented(self):
        with self.assertRaises(ExtractorError):
            self.e.execute(self.test_file)

    def test_method_str_is_defined_and_reachable(self):
        self.assertIsNotNone(str(self.e))
        self.assertIsNotNone(self.e.__str__)

    def test_method_str_returns_type_string(self):
        self.assertTrue(isinstance(str(self.e), str))
        self.assertTrue(isinstance(str(self.e.__str__), str))

    def test_method_str_returns_expected(self):
        self.assertEqual(str(self.e), 'AbstractTextExtractor')

    def test_class_method_can_handle_is_defined(self):
        self.assertIsNotNone(self.e.can_handle)

    def test_class_method_can_handle_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.assertIsNotNone(self.e.can_handle(self.fo))

        with self.assertRaises(NotImplementedError):
            self.assertFalse(self.e.can_handle(self.fo))

    def test_abstract_class_does_not_specify_which_mime_types_are_handled(self):
        self.assertIsNone(self.e.HANDLES_MIME_TYPES)

    def test_abstract_class_does_not_specify_meowuri_node(self):
        self.assertEqual(self.e.MEOWURI_NODE, C.UNDEFINED_MEOWURI_PART)

    def test_abstract_class_does_not_specify_meowuri_leaf(self):
        self.assertEqual(self.e.MEOWURI_LEAF, C.UNDEFINED_MEOWURI_PART)

    def test__get_raw_text_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e._get_text(self.test_file)

    def test_check_dependencies_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e.check_dependencies()


class TestNormalizeUnicode(TestCase):
    def test_returns_expected(self):
        actual = normalize_unicode('...')
        expected = '...'
        self.assertEqual(actual, expected)

    def test_simplifies_three_periods(self):
        actual = normalize_unicode('…')
        expected = '...'
        self.assertEqual(actual, expected)
