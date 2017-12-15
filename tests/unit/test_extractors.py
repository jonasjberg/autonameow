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
from unittest.mock import (
    Mock,
    PropertyMock,
    patch
)

from core import constants as C
import extractors
from extractors.text.common import AbstractTextExtractor
import unit.utils as uu
import unit.constants as uuconst


class TestExtractorsConstants(TestCase):
    def test_autonameow_extractor_path_is_defined(self):
        self.assertIsNotNone(extractors.AUTONAMEOW_EXTRACTOR_PATH)

    def test_extractor_path_is_an_existing_directory(self):
        self.assertTrue(
            uu.dir_exists(extractors.AUTONAMEOW_EXTRACTOR_PATH)
        )

    def test_extractor_path_contains_expected_top_level_directory(self):
        _top = 'extractors'
        self.assertTrue(extractors.AUTONAMEOW_EXTRACTOR_PATH.endswith(_top))


class TestBaseExtractor(TestCase):
    def setUp(self):
        self.test_file = uu.make_temporary_file()
        self.e = extractors.BaseExtractor()

        self.fo = uu.fileobject_testfile('magic_jpg.jpg')

    def test_base_extractor_class_is_available(self):
        self.assertIsNotNone(extractors.BaseExtractor)

    def test_base_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_calling_extract_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e.extract(self.test_file)

    def test_metainfo_returns_expected_type(self):
        actual = self.e.metainfo(self.test_file)
        self.assertIsInstance(actual, dict)

    def test_abstract_class_does_not_specify_metainfo(self):
        actual = self.e.metainfo(self.test_file)
        self.assertEqual(len(actual), 0)

    def test_metainfo_is_not_mutable(self):
        first = self.e.metainfo(self.test_file)
        first['foo'] = 'bar'
        second = self.e.metainfo(self.test_file)
        self.assertNotEqual(first, second)
        self.assertNotIn('foo', second)

    def test_check_dependencies_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            _ = self.e.check_dependencies()

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
        self.assertEqual(self.e.MEOWURI_CHILD, C.UNDEFINED_MEOWURI_PART)

    def test_abstract_class_does_not_specify_meowuri_leaf(self):
        self.assertEqual(self.e.MEOWURI_LEAF, C.UNDEFINED_MEOWURI_PART)

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

        self.e = extractors.BaseExtractor

    def test_unimplemented_check_dependencies(self):
        with self.assertRaises(NotImplementedError):
            _ = self.e.check_dependencies()

    def test_can_handle_raises_exception_if_handles_mime_types_is_none(self):
        with self.assertRaises(NotImplementedError):
            _ = self.e.can_handle(self.mock_fileobject)

    @patch('extractors.BaseExtractor.HANDLES_MIME_TYPES',
           new_callable=PropertyMock, return_value=['text/plain'])
    def test_can_handle_returns_false(self, mock_attribute):
        e = extractors.BaseExtractor()
        actual = e.can_handle(self.mock_fileobject)
        self.assertFalse(actual)

    @patch('extractors.BaseExtractor.HANDLES_MIME_TYPES',
           new_callable=PropertyMock, return_value=['image/jpeg'])
    def test_can_handle_returns_true(self, mock_attribute):
        e = extractors.BaseExtractor()
        actual = e.can_handle(self.mock_fileobject)
        self.assertTrue(actual)


class TestFindExtractorModuleSourceFiles(TestCase):
    def test_returns_expected_type(self):
        actual = extractors.find_extractor_module_files()
        self.assertIsInstance(actual, list)

    def test_returns_expected_files(self):
        actual = extractors.find_extractor_module_files()

        self.assertNotIn('__init__.py', actual)
        self.assertNotIn('__pycache__', actual)
        self.assertNotIn('common.py', actual)


def subclasses_base_extractor(klass):
    return uu.is_class(klass) and issubclass(klass, extractors.BaseExtractor)


class TestGetAllExtractorClasses(TestCase):
    def setUp(self):
        self.sources = ['text', 'metadata']
        self.actual = extractors._get_package_classes(self.sources)

    def test_returns_expected_type(self):
        self.assertIsInstance(self.actual, tuple)

    def test_returns_abstract_subclasses_of_base_extractor(self):
        actual_abstract, _ = self.actual
        for _abstract in actual_abstract:
            with self.subTest(klass=_abstract):
                self.assertTrue(subclasses_base_extractor(_abstract))

    def test_returns_implemented_subclasses_of_base_extractor(self):
        _, actual_implemented = self.actual
        for _implemented in actual_implemented:
            with self.subTest(_implemented):
                self.assertTrue(subclasses_base_extractor(_implemented))

    def test_does_not_include_base_extractor(self):
        abstract, implemented = self.actual
        self.assertNotIn(extractors.BaseExtractor, abstract)
        self.assertNotIn(extractors.BaseExtractor, implemented)


class TestGetImplementedExtractorClasses(TestCase):
    def setUp(self):
        self.actual = extractors.get_extractor_classes(
            packages=uuconst.EXTRACTOR_CLASS_PACKAGES,
            modules=uuconst.EXTRACTOR_CLASS_MODULES
        )

    def test_get_extractor_classes_returns_expected_type(self):
        self.assertIsInstance(self.actual, list)

    def test_get_extractor_classes_returns_subclasses_of_base_extractor(self):
        for klass in self.actual:
            self.assertTrue(uu.is_class(klass))
            self.assertTrue(issubclass(klass, extractors.BaseExtractor))

    def test_get_extractor_classes_does_not_include_base_extractor(self):
        self.assertNotIn(extractors.BaseExtractor, self.actual)

    def test_get_extractor_classes_does_not_include_abstract_extractors(self):
        self.assertNotIn(AbstractTextExtractor, self.actual)


class TestNumberOfAvailableExtractorClasses(TestCase):
    def setUp(self):
        self.actual = extractors.get_extractor_classes(
            packages=uuconst.EXTRACTOR_CLASS_PACKAGES,
            modules=uuconst.EXTRACTOR_CLASS_MODULES
        )

    # This tests up to the current number of extractors without dependencies.
    # TODO: [hardcoded] Testing number of extractor classes needs fixing.
    def test_get_extractor_classes_returns_at_least_one_extractor(self):
        self.assertGreaterEqual(len(self.actual), 1)

    def test_get_extractor_classes_returns_at_least_two_extractors(self):
        self.assertGreaterEqual(len(self.actual), 2)

    def test_get_extractor_classes_returns_at_least_three_extractors(self):
        self.assertGreaterEqual(len(self.actual), 3)


class TestMapMeowURIToExtractors(TestCase):
    def setUp(self):
        self.actual = extractors.map_meowuri_to_extractors()

    def test_returns_expected_type(self):
        self.assertIsNotNone(self.actual)
        self.assertIsInstance(self.actual, dict)

        for meowuri, klass_list in self.actual.items():
            self.assertTrue(uu.is_internalstring(meowuri))
            self.assertTrue(C.UNDEFINED_MEOWURI_PART not in meowuri)

            for klass in klass_list:
                self.assertTrue(subclasses_base_extractor(klass))
                self.assertTrue(uu.is_class(klass))

    def test_returns_one_extractor_per_meowuri(self):
        # This assumption is likely bound to change some time soon.
        for meowuri, klass_list in self.actual.items():
            self.assertEqual(len(klass_list), 1)


class TestExtractorClassMeowURIs(TestCase):
    extractor_class_names = [e.__name__ for e in extractors.ExtractorClasses]

    def setUp(self):
        self.actual = [k.meowuri_prefix() for k in extractors.ExtractorClasses]

    def test_returns_expected_type(self):
        for meowuri in self.actual:
            self.assertTrue(uu.is_internalstring(meowuri))
            self.assertTrue(C.UNDEFINED_MEOWURI_PART not in meowuri)

    def test_returns_meowuris_for_extractors_assumed_always_available(self):
        def _assert_in(member):
            self.assertIn(member, self.actual)

        _assert_in('extractor.filesystem.xplat')
        _assert_in('extractor.text.plain')

    def test_returns_meowuris_for_available_extractors(self):
        def _conditional_assert_in(klass, member):
            if klass in self.extractor_class_names:
                self.assertIn(member, self.actual)

        _conditional_assert_in('CrossPlatformFileSystemExtractor',
                               'extractor.filesystem.xplat')
        _conditional_assert_in('ExiftoolMetadataExtractor',
                               'extractor.metadata.exiftool')
        _conditional_assert_in('PdftotextTextExtractor',
                               'extractor.text.pdftotext')
        _conditional_assert_in('TesseractOCRTextExtractor',
                               'extractor.text.tesseractocr')
