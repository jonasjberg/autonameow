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
    PropertyMock,
    patch
)

import unit.utils as uu
from core import constants as C
from extractors.common import (
    BaseExtractor,
    _fieldmeta_filepath_from_extractor_source_filepath,
)


class TestBaseExtractor(TestCase):
    def setUp(self):
        self.test_file = uu.make_temporary_file()
        self.e = BaseExtractor()

        self.fo = uu.fileobject_testfile('magic_jpg.jpg')

    def test_base_extractor_class_is_available(self):
        self.assertIsNotNone(BaseExtractor)

    def test_base_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_calling_extract_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e.extract(self.test_file)

    def test_metainfo_returns_expected_type(self):
        actual = self.e.metainfo()
        self.assertIsInstance(actual, dict)

    def test_abstract_class_does_not_specify_metainfo(self):
        actual = self.e.metainfo()
        self.assertEqual(len(actual), 0)

    def test_metainfo_is_not_mutable(self):
        first = self.e.metainfo()
        first['foo'] = 'bar'
        second = self.e.metainfo()
        self.assertNotEqual(first, second)
        self.assertNotIn('foo', second)

    def test_dependencies_satisfied_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            _ = self.e.dependencies_satisfied()

    def test_str_is_defined_and_reachable(self):
        self.assertIsNotNone(str(self.e))
        self.assertIsNotNone(self.e.__str__)

    def test_str_returns_type_string(self):
        self.assertTrue(uu.is_internalstring(str(self.e)))
        self.assertTrue(uu.is_internalstring(str(self.e.__str__)))

    def test_str_returns_expected(self):
        self.assertEqual(str(self.e), 'BaseExtractor')

    def test_abstract_class_does_not_specify_which_mime_types_are_handled(self):
        self.assertIsNone(self.e.HANDLES_MIME_TYPES)

    def test_abstract_class_does_not_specify_meowuri_node(self):
        self.assertEqual(self.e.MEOWURI_CHILD, C.MEOWURI_UNDEFINED_PART)

    def test_abstract_class_does_not_specify_meowuri_leaf(self):
        self.assertEqual(self.e.MEOWURI_LEAF, C.MEOWURI_UNDEFINED_PART)

    def test__meowuri_node_from_module_name(self):
        actual = self.e._meowuri_node_from_module_name()
        self.assertEqual(actual, C.MEOWURI_ROOT_SOURCE_EXTRACTORS)

    def test__meowuri_leaf_from_module_name(self):
        actual = self.e._meowuri_leaf_from_module_name()
        expect = 'common'
        self.assertEqual(actual, expect)


class TestBaseExtractorClassMethods(TestCase):
    def setUp(self):
        self.mock_fileobject = Mock()
        self.mock_fileobject.mime_type = 'image/jpeg'

        self.e = BaseExtractor

    def test_unimplemented_dependencies_satisfied(self):
        with self.assertRaises(NotImplementedError):
            _ = self.e.dependencies_satisfied()

    def test_can_handle_raises_exception_if_handles_mime_types_is_none(self):
        with self.assertRaises(NotImplementedError):
            _ = self.e.can_handle(self.mock_fileobject)

    @patch('extractors.BaseExtractor.HANDLES_MIME_TYPES',
           new_callable=PropertyMock, return_value=['text/plain'])
    def test_can_handle_returns_false(self, mock_attribute):
        e = BaseExtractor()
        actual = e.can_handle(self.mock_fileobject)
        self.assertFalse(actual)

    @patch('extractors.BaseExtractor.HANDLES_MIME_TYPES',
           new_callable=PropertyMock, return_value=['image/jpeg'])
    def test_can_handle_returns_true(self, mock_attribute):
        e = BaseExtractor()
        actual = e.can_handle(self.mock_fileobject)
        self.assertTrue(actual)


class TestFieldmetaFilepathFromExtractorSourceFilepath(TestCase):
    def test_returns_expected(self):
        actual = _fieldmeta_filepath_from_extractor_source_filepath(
            '/tmp/autonameow.git/autonameow/extractors/metadata/exiftool.py'
        )
        # Result may be '/private/tmp/autonameow...' on MacOS, instead of just '/tmp/autonameow...'
        self.assertTrue(actual.endswith('/tmp/autonameow.git/autonameow/extractors/metadata/exiftool_fieldmeta.yaml'))
