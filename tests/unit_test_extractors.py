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

import os
from unittest import TestCase

import unit_utils as uu
import extractors
from extractors.metadata import AbstractMetadataExtractor
from extractors.textual import AbstractTextExtractor


class TestExtractorsConstants(TestCase):
    def test_autonameow_extractor_path_is_defined(self):
        self.assertIsNotNone(extractors.AUTONAMEOW_EXTRACTOR_PATH)

    def test_extractor_path_is_an_existing_directory(self):
        self.assertTrue(os.path.exists(extractors.AUTONAMEOW_EXTRACTOR_PATH))
        self.assertTrue(os.path.isdir(extractors.AUTONAMEOW_EXTRACTOR_PATH))

    def test_extractor_path_contains_expected_top_level_directory(self):
        _top = 'extractors'
        self.assertTrue(extractors.AUTONAMEOW_EXTRACTOR_PATH.endswith(_top))


class TestBaseExtractor(TestCase):
    def setUp(self):
        self.e = extractors.BaseExtractor(uu.make_temporary_file())

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
            self.e.query()
            self.e.query(field='some_field')

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
            self.assertIsNotNone(self.e.can_handle(self.fo))
            self.assertFalse(self.e.can_handle(self.fo))

    def test_abstract_class_does_not_specify_which_mime_types_are_handled(self):
        self.assertIsNone(self.e.handles_mime_types)

    def test_abstract_class_does_not_specify_data_query_string(self):
        self.assertIsNone(self.e.data_query_string)


class TestFindExtractorSourceFiles(TestCase):
    def test_find_extractor_files_is_defined(self):
        self.assertIsNotNone(extractors.find_extractor_files)

    def test_find_extractor_files_returns_expected_type(self):
        actual = extractors.find_extractor_files()
        self.assertTrue(isinstance(actual, list))

    def test_find_extractor_files_returns_expected_files(self):
        actual = extractors.find_extractor_files()

        # TODO: [hardcoded] Likely to break; requires manual updates.
        self.assertIn('textual.py', actual)
        self.assertIn('metadata.py', actual)


class TestGetAllExtractorClasses(TestCase):
    def setUp(self):
        self.sources = ['textual.py', 'metadata.py']

    def test_get_extractor_classes_returns_expected_type(self):
        actual = extractors._get_all_extractor_classes(self.sources)
        self.assertTrue(isinstance(actual, tuple))

    def test_get_extractor_classes_returns_subclasses_of_base_extractor(self):
        def __subclasses_base_extractor(klass):
            self.assertTrue(issubclass(klass, extractors.BaseExtractor))

        actual = extractors._get_all_extractor_classes(self.sources)

        actual_abstract, _ = actual
        for _abstract in actual_abstract:
            __subclasses_base_extractor(_abstract)

        _, actual_implemented = actual
        for _implemented in actual_implemented:
            __subclasses_base_extractor(_implemented)

    def test_get_extractor_classes_does_not_include_base_extractor(self):
        abstract, implemented = extractors._get_all_extractor_classes(self.sources)
        self.assertNotIn(extractors.BaseExtractor, abstract)
        self.assertNotIn(extractors.BaseExtractor, implemented)


class TestGetImplementedExtractorClasses(TestCase):
    def setUp(self):
        self.sources = ['textual.py', 'metadata.py']
        self.actual = extractors.get_extractor_classes(self.sources)

    def test_get_extractor_classes_returns_expected_type(self):
        self.assertTrue(isinstance(self.actual, list))

    def test_get_extractor_classes_returns_subclasses_of_base_extractor(self):
        for klass in self.actual:
            self.assertTrue(issubclass(klass, extractors.BaseExtractor))

    def test_get_extractor_classes_does_not_include_base_extractor(self):
        self.assertNotIn(extractors.BaseExtractor, self.actual)

    def test_get_extractor_classes_does_not_include_abstract_extractors(self):
        self.assertNotIn(AbstractMetadataExtractor, self.actual)
        self.assertNotIn(AbstractTextExtractor, self.actual)


class TestNumberOfAvailableExtractorClasses(TestCase):
    def setUp(self):
        self.sources = ['text_ocr.py', 'text_pdf.py', 'text_plain.py',
                        'metadata_exiftool.py', 'metadata_pypdf.py']
        self.actual = extractors.get_extractor_classes(self.sources)

    # TODO: [hardcoded] Testing number of extractor classes needs fixing.
    def test_get_extractor_classes_returns_at_least_one_extractor(self):
        self.assertGreaterEqual(len(self.actual), 1)

    def test_get_extractor_classes_returns_at_least_two_extractors(self):
        self.assertGreaterEqual(len(self.actual), 2)

    def test_get_extractor_classes_returns_at_least_three_extractors(self):
        self.assertGreaterEqual(len(self.actual), 3)

    def test_get_extractor_classes_returns_at_least_four_extractors(self):
        self.assertGreaterEqual(len(self.actual), 4)


class TestGetQueryStrings(TestCase):
    def setUp(self):
        self.actual = extractors.get_query_strings()

    def test_returns_expected_container_type(self):
        self.assertTrue(isinstance(self.actual, set))

    def test_returns_expected_contained_types(self):
        for q in self.actual:
            self.assertTrue(isinstance(q, str))

    def test_contains_expected_metadata_query_strings(self):
        self.assertIn('metadata.exiftool', self.actual)
        self.assertIn('metadata.pypdf', self.actual)

    def test_contains_expected_contents_query_strings(self):
        self.assertIn('contents.visual.ocr_text', self.actual)
        self.assertIn('contents.textual.raw_text', self.actual)

    def test_does_not_contain_unexpected_query_strings(self):
        self.assertNotIn('foo.bar', self.actual)
        self.assertNotIn('.', self.actual)
        self.assertNotIn('', self.actual)
        self.assertNotIn(None, self.actual)


class TestSuitableDataExtractorsForFile(TestCase):
    def test_returns_expected_extractors_for_mp4_video_file(self):
        self.fo = uu.get_mock_fileobject(mime_type='video/mp4')
        actual = [c.__name__ for c in
                  extractors.suitable_data_extractors_for(self.fo)]
        self.assertIn('ExiftoolMetadataExtractor', actual)

    def test_returns_expected_extractors_for_png_image_file(self):
        self.fo = uu.get_mock_fileobject(mime_type='image/png')
        actual = [c.__name__ for c in
                  extractors.suitable_data_extractors_for(self.fo)]
        self.assertIn('ExiftoolMetadataExtractor', actual)
        self.assertIn('ImageOCRTextExtractor', actual)

    def test_returns_expected_extractors_for_pdf_file(self):
        self.fo = uu.get_mock_fileobject(mime_type='application/pdf')
        actual = [c.__name__ for c in
                  extractors.suitable_data_extractors_for(self.fo)]
        self.assertIn('ExiftoolMetadataExtractor', actual)
        self.assertIn('PyPDFMetadataExtractor', actual)
        self.assertIn('PdfTextExtractor', actual)
