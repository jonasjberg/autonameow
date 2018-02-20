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
from extractors import (
    AUTONAMEOW_EXTRACTOR_PATH,
    BaseExtractor,
    EXTRACTOR_CLASS_PACKAGES,
    EXTRACTOR_CLASS_PACKAGES_METADATA,
    EXTRACTOR_CLASS_PACKAGES_TEXT,
    _find_extractor_classes_in_packages,
    get_extractor_classes,
    ProviderClasses
)


class TestExtractorsConstants(TestCase):
    def test_autonameow_extractor_path_is_defined(self):
        self.assertIsNotNone(AUTONAMEOW_EXTRACTOR_PATH)

    def test_extractor_path_is_an_existing_directory(self):
        self.assertTrue(
            uu.dir_exists(AUTONAMEOW_EXTRACTOR_PATH)
        )

    def test_extractor_path_contains_expected_top_level_directory(self):
        _top = 'extractors'
        self.assertTrue(AUTONAMEOW_EXTRACTOR_PATH.endswith(_top))

    def _assert_list_of_strings(self, given):
        self.assertIsInstance(given, list)
        for element in given:
            self.assertIsInstance(element, str)

    def test_extractor_class_packages(self):
        self._assert_list_of_strings(EXTRACTOR_CLASS_PACKAGES)

    def test_extractor_class_packages_text(self):
        self._assert_list_of_strings(EXTRACTOR_CLASS_PACKAGES_TEXT)

    def test_extractor_class_packages_metadata(self):
        self._assert_list_of_strings(EXTRACTOR_CLASS_PACKAGES_METADATA)


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

        self.e = BaseExtractor

    def test_unimplemented_check_dependencies(self):
        with self.assertRaises(NotImplementedError):
            _ = self.e.check_dependencies()

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


class TestFindExtractorClassesInPackages(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = _find_extractor_classes_in_packages(EXTRACTOR_CLASS_PACKAGES)

    def test_returns_expected_type(self):
        self.assertIsInstance(self.actual, list)

    def test_returns_subclasses_of_base_extractor(self):
        for klass in self.actual:
            with self.subTest(klass):
                self.assertTrue(uu.is_class(klass))
                self.assertTrue(issubclass(klass, BaseExtractor))

    def test_does_not_include_base_extractor(self):
        self.assertNotIn(BaseExtractor, self.actual)


class TestGetImplementedExtractorClasses(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = get_extractor_classes(
            packages=EXTRACTOR_CLASS_PACKAGES,
        )

    def test_get_extractor_classes_returns_expected_type(self):
        self.assertIsInstance(self.actual, list)

    def test_get_extractor_classes_returns_subclasses_of_base_extractor(self):
        for klass in self.actual:
            self.assertTrue(uu.is_class(klass))
            self.assertTrue(issubclass(klass, BaseExtractor))

    def test_get_extractor_classes_does_not_include_base_extractor(self):
        self.assertNotIn(BaseExtractor, self.actual)

    def test_get_extractor_classes_does_not_include_abstract_extractors(self):
        from extractors.text.common import AbstractTextExtractor
        self.assertNotIn(AbstractTextExtractor, self.actual)


class TestGetTextExtractorClasses(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = get_extractor_classes(
            packages=EXTRACTOR_CLASS_PACKAGES_TEXT,
        )

    def test_get_extractor_classes_returns_expected_type(self):
        self.assertIsInstance(self.actual, list)

    def test_get_extractor_classes_returns_subclasses_of_base_extractor(self):
        for klass in self.actual:
            self.assertTrue(uu.is_class(klass))
            self.assertTrue(issubclass(klass, BaseExtractor))

    def test_get_extractor_classes_does_not_include_base_extractor(self):
        self.assertNotIn(BaseExtractor, self.actual)

    def test_get_extractor_classes_does_not_include_abstract_extractors(self):
        from extractors.text.common import AbstractTextExtractor
        self.assertNotIn(AbstractTextExtractor, self.actual)

    def test_returns_text_extractors(self):
        from extractors.text.common import AbstractTextExtractor
        for klass in self.actual:
            self.assertTrue(issubclass(klass, AbstractTextExtractor))


class TestGetMetadataExtractorClasses(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = get_extractor_classes(
            packages=EXTRACTOR_CLASS_PACKAGES_METADATA,
        )

    def test_get_extractor_classes_returns_expected_type(self):
        self.assertIsInstance(self.actual, list)

    def test_get_extractor_classes_returns_subclasses_of_base_extractor(self):
        for klass in self.actual:
            self.assertTrue(uu.is_class(klass))
            self.assertTrue(issubclass(klass, BaseExtractor))

    def test_get_extractor_classes_does_not_include_base_extractor(self):
        self.assertNotIn(BaseExtractor, self.actual)

    def test_get_extractor_classes_does_not_include_abstract_extractors(self):
        from extractors.text.common import AbstractTextExtractor
        self.assertNotIn(AbstractTextExtractor, self.actual)

    def test_returns_metadata_extractors_verified_by_name(self):
        for klass in self.actual:
            _klass_name = klass.__name__
            self.assertIn('Metadata', _klass_name)

    def test_returns_metadata_extractors_verified_by_meowuri_prefix(self):
        for klass in self.actual:
            _meowuri_prefix = str(klass.meowuri_prefix())
            self.assertTrue(_meowuri_prefix.startswith('extractor.metadata'))


class TestNumberOfAvailableExtractorClasses(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = get_extractor_classes(
            packages=EXTRACTOR_CLASS_PACKAGES,
        )

    # This tests up to the current number of extractors without dependencies.
    # TODO: [hardcoded] Testing number of extractor classes needs fixing.
    def test_get_extractor_classes_returns_at_least_one_extractor(self):
        self.assertGreaterEqual(len(self.actual), 1)

    def test_get_extractor_classes_returns_at_least_two_extractors(self):
        self.assertGreaterEqual(len(self.actual), 2)

    def test_get_extractor_classes_returns_at_least_three_extractors(self):
        self.assertGreaterEqual(len(self.actual), 3)


class TestExtractorClassMeowURIs(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.extractor_class_names = [e.__name__ for e in ProviderClasses]
        cls.actual = [k.meowuri_prefix() for k in ProviderClasses]

    def test_returns_expected_type(self):
        from core.model import MeowURI
        for meowuri in self.actual:
            self.assertIsInstance(meowuri, MeowURI)
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
        _conditional_assert_in('PdfTextExtractor',
                               'extractor.text.pdf')
        _conditional_assert_in('TesseractOCRTextExtractor',
                               'extractor.text.tesseractocr')
        _conditional_assert_in('RichTextFormatTextExtractor',
                               'extractor.text.rtf')
        _conditional_assert_in('MarkdownTextExtractor',
                               'extractor.text.markdown')
