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

import extractors
from extractors.text.common import AbstractTextExtractor
from core import constants as C
import unit_utils as uu
import unit_utils_constants as uuconst


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

        class DummyFileObject(object):
            def __init__(self):
                self.mime_type = 'image/jpeg'
        self.fo = DummyFileObject()

    def test_base_extractor_class_is_available(self):
        self.assertIsNotNone(extractors.BaseExtractor)

    def test_base_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_method_query_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e.execute(self.test_file)

    def test_method_str_is_defined_and_reachable(self):
        self.assertIsNotNone(str(self.e))
        self.assertIsNotNone(self.e.__str__)

    def test_method_str_returns_type_string(self):
        self.assertTrue(isinstance(str(self.e), str))
        self.assertTrue(isinstance(str(self.e.__str__), str))

    def test_method_str_returns_expected(self):
        self.assertEqual(str(self.e), 'BaseExtractor')

    def test_class_method_can_handle_is_defined(self):
        self.assertIsNotNone(self.e.can_handle)

    def test_class_method_can_handle_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e.can_handle(self.fo)

    def test_abstract_class_does_not_specify_which_mime_types_are_handled(self):
        self.assertIsNone(self.e.HANDLES_MIME_TYPES)

    def test_abstract_class_does_not_specify_meowuri_node(self):
        self.assertEqual(self.e.MEOWURI_NODE, C.UNDEFINED_MEOWURI_PART)

    def test_abstract_class_does_not_specify_meowuri_leaf(self):
        self.assertEqual(self.e.MEOWURI_LEAF, C.UNDEFINED_MEOWURI_PART)


class TestFindExtractorModuleSourceFiles(TestCase):
    def test_find_extractor_module_files_is_defined(self):
        self.assertIsNotNone(extractors.find_extractor_module_files)

    def test_returns_expected_type(self):
        actual = extractors.find_extractor_module_files()
        self.assertTrue(isinstance(actual, list))

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

    def test_get_extractor_classes_returns_expected_type(self):
        actual = extractors._get_package_classes(self.sources)
        self.assertTrue(isinstance(actual, tuple))

    def test_get_extractor_classes_returns_subclasses_of_base_extractor(self):
        actual = extractors._get_package_classes(self.sources)

        actual_abstract, _ = actual
        for _abstract in actual_abstract:
            self.assertTrue(subclasses_base_extractor(_abstract))

        _, actual_implemented = actual
        for _implemented in actual_implemented:
            self.assertTrue(subclasses_base_extractor(_implemented))

    def test_get_extractor_classes_does_not_include_base_extractor(self):
        abstract, implemented = extractors._get_package_classes(self.sources)
        self.assertNotIn(extractors.BaseExtractor, abstract)
        self.assertNotIn(extractors.BaseExtractor, implemented)


class TestGetImplementedExtractorClasses(TestCase):
    def setUp(self):
        self.actual = extractors.get_extractor_classes(
            packages=uuconst.EXTRACTOR_CLASS_PACKAGES,
            modules=uuconst.EXTRACTOR_CLASS_MODULES
        )

    def test_get_extractor_classes_returns_expected_type(self):
        self.assertTrue(isinstance(self.actual, list))

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


class TestSuitableExtractorsForFile(TestCase):
    extractor_class_names = [e.__name__ for e in extractors.ExtractorClasses]

    def assert_in_if_available(self, member, container):
        """
        Test with the currently available extractors.
        """
        if member in self.extractor_class_names:
            self.assertIn(member, container)

    def test_returns_expected_extractors_for_mp4_video_file(self):
        self.fo = uu.get_mock_fileobject(mime_type='video/mp4')
        actual = [c.__name__ for c in
                  extractors.suitable_extractors_for(self.fo)]
        self.assertIn('CrossPlatformFileSystemExtractor', actual)
        self.assert_in_if_available('ExiftoolMetadataExtractor', actual)

    def test_returns_expected_extractors_for_png_image_file(self):
        self.fo = uu.get_mock_fileobject(mime_type='image/png')
        actual = [c.__name__ for c in
                  extractors.suitable_extractors_for(self.fo)]
        self.assertIn('CrossPlatformFileSystemExtractor', actual)
        self.assert_in_if_available('ExiftoolMetadataExtractor', actual)
        self.assert_in_if_available('ImageOCRTextExtractor', actual)

    def test_returns_expected_extractors_for_pdf_file(self):
        self.fo = uu.get_mock_fileobject(mime_type='application/pdf')
        actual = [c.__name__ for c in
                  extractors.suitable_extractors_for(self.fo)]
        self.assertIn('CrossPlatformFileSystemExtractor', actual)
        self.assert_in_if_available('ExiftoolMetadataExtractor', actual)
        self.assert_in_if_available('PyPDFMetadataExtractor', actual)
        self.assert_in_if_available('PdfTextExtractor', actual)


class TestMapMeowURIToExtractors(TestCase):
    def setUp(self):
        self.actual = extractors.map_meowuri_to_extractors()

    def test_returns_expected_type(self):
        self.assertIsNotNone(self.actual)
        self.assertTrue(isinstance(self.actual, dict))

        for meowuri, klass_list in self.actual.items():
            self.assertTrue(isinstance(meowuri, str))
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
        self.actual = [k.meowuri() for k in extractors.ExtractorClasses]

    def test_returns_expected_type(self):
        for meowuri in self.actual:
            self.assertTrue(isinstance(meowuri, str))
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
        _conditional_assert_in('PyPDFMetadataExtractor',
                               'extractor.metadata.pypdf')
        _conditional_assert_in('PdfTextExtractor',
                               'extractor.text.pdf')
        _conditional_assert_in('ImageOCRTextExtractor',
                               'extractor.text.ocr')
