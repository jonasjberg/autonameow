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

import extractors
import unit_utils as uu


class TestExtractorsConstants(TestCase):
    def test_autonameow_extractor_path_is_defined(self):
        self.assertIsNotNone(extractors.AUTONAMEOW_EXTRACTOR_PATH)

    def test_extractor_path_is_an_existing_directory(self):
        self.assertTrue(os.path.exists(extractors.AUTONAMEOW_EXTRACTOR_PATH))
        self.assertTrue(os.path.isdir(extractors.AUTONAMEOW_EXTRACTOR_PATH))

    def test_extractor_path_contains_expected_top_level_directory(self):
        _top = 'extractors'
        self.assertTrue(extractors.AUTONAMEOW_EXTRACTOR_PATH.endswith(_top))


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


class TestGetExtractorClasses(TestCase):
    def setUp(self):
        self.sources = ['textual.py', 'metadata.py']

    def test_get_extractor_classes_returns_expected_type(self):
        actual = extractors.get_extractor_classes(self.sources)

        self.assertTrue(isinstance(actual, list))
        for c in actual:
            self.assertTrue(issubclass(c, extractors.Extractor))

    # TODO: [hardcoded] Testing number of extractor classes needs fixing.
    def test_get_extractor_classes_returns_at_least_one_extractor(self):
        actual = extractors.get_extractor_classes(self.sources)
        self.assertGreaterEqual(len(actual), 1)

    def test_get_extractor_classes_returns_at_least_two_extractors(self):
        actual = extractors.get_extractor_classes(self.sources)
        self.assertGreaterEqual(len(actual), 2)

    def test_get_extractor_classes_returns_at_least_three_extractors(self):
        actual = extractors.get_extractor_classes(self.sources)
        self.assertGreaterEqual(len(actual), 3)

    def test_get_extractor_classes_returns_at_least_four_extractors(self):
        actual = extractors.get_extractor_classes(self.sources)
        self.assertGreaterEqual(len(actual), 4)


class TestNumberOfAvailableExtractorClasses(TestCase):
    def setUp(self):
        self.sources = ['textual.py', 'metadata.py']
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
