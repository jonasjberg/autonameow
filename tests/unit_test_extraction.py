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

from core import constants
from core.exceptions import InvalidDataSourceError
from core.extraction import (
    ExtractedData,
    suitable_data_extractors_for,
    get_extractor_classes,
    Extraction
)
from extractors.extractor import Extractor
from unit_utils import get_mock_fileobject


class TestExtractedData(TestCase):
    def setUp(self):
        self.d = ExtractedData()

    def test_extracted_data_can_be_instantiated(self):
        self.assertIsNotNone(self.d)

    def test_add_data_with_invalid_label_raises_error(self):
        self.skipTest('TODO: to be removed')
        with self.assertRaises(InvalidDataSourceError):
            self.d.add('not_a_label.surely', 'data')
        with self.assertRaises(InvalidDataSourceError):
            self.d.add('', 'data')
        with self.assertRaises(InvalidDataSourceError):
            self.d.add(None, 'data')

    def test_adds_data_with_valid_label(self):
        valid_labels = constants.VALID_DATA_SOURCES[:3]
        for valid_label in valid_labels:
            self.d.add(valid_label, 'data')

    def test_initial_len_returns_expected(self):
        self.assertEqual(len(self.d), 0)

    def test_adding_data_increments_len(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(valid_label, 'data')
        self.assertEqual(len(self.d), 1)

    def test_adding_data_with_different_labels_increments_len(self):
        first_valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(first_valid_label, 'data')
        self.assertEqual(len(self.d), 1)

        second_valid_label = constants.VALID_DATA_SOURCES[1]
        self.d.add(second_valid_label, 'data')
        self.assertEqual(len(self.d), 2)

    def test_adding_data_with_same_label_increments_len(self):
        first_valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(first_valid_label, 'data')
        self.assertEqual(len(self.d), 1)

        second_valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(second_valid_label, 'data')
        self.assertEqual(len(self.d), 2)

    def test_get_data_with_invalid_label_raises_error(self):
        self.skipTest('TODO: to be removed ..')
        with self.assertRaises(InvalidDataSourceError):
            self.d.get('not_a_label.surely')
        with self.assertRaises(InvalidDataSourceError):
            self.d.get('')
        with self.assertRaises(InvalidDataSourceError):
            self.d.get(None)

    def test_get_data_with_valid_label_returns_false_when_empty(self):
        valid_labels = constants.VALID_DATA_SOURCES[:3]
        for valid_label in valid_labels:
            actual = self.d.get(valid_label)
            self.assertFalse(actual)

    def test_valid_label_returns_expected_data(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(valid_label, 'expected_data')

        actual = self.d.get(valid_label)
        self.assertEqual(actual, 'expected_data')

    def test_valid_label_returns_expected_data_multiple_entries(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(valid_label, 'expected_data_a')
        self.d.add(valid_label, 'expected_data_b')

        actual = self.d.get(valid_label)
        self.assertIn('expected_data_a', actual)
        self.assertIn('expected_data_b', actual)


class TestExtraction(TestCase):
    def setUp(self):
        self.e = Extraction(get_mock_fileobject())

    def test_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_initial_results_data_len_is_zero(self):
        self.assertEqual(len(self.e.data), 0)

    def test_raises_exception_For_invalid_results(self):
        self.skipTest('TODO: to be removed ..')
        with self.assertRaises(InvalidDataSourceError):
            self.e.collect_results('not_a_valid_source_surely', 'image/jpeg')

    def test_collects_valid_results(self):
        self.e.collect_results('contents.mime_type', 'image/jpeg')

    def test_collecting_valid_results_increments_data_len(self):
        self.e.collect_results('contents.mime_type', 'image/jpeg')
        self.assertEqual(len(self.e.data), 1)
        self.e.collect_results('filesystem.basename.extension', 'jpg')
        self.assertEqual(len(self.e.data), 2)

    def test_collecting_results_with_empty_data_does_not_increment_len(self):
        self.e.collect_results('contents.mime_type', None)
        self.assertEqual(len(self.e.data), 0)
        self.e.collect_results('filesystem.basename.extension', None)
        self.assertEqual(len(self.e.data), 0)

    def test_has_method__instantiate_extractors(self):
        self.assertIsNotNone(self.e._instantiate_extractors)

    def test__instantiate_extractors_returns_expected_type(self):
        extractor_classes = get_extractor_classes()
        actual = self.e._instantiate_extractors(extractor_classes)

        self.assertTrue(isinstance(actual, list))
        for ec in actual:
            self.assertTrue(issubclass(ec.__class__, Extractor))

    def test_has_method__execute_run_queue(self):
        self.assertIsNotNone(self.e._execute_run_queue)


class TestSuitableDataExtractorsForFile(TestCase):
    def test_returns_expected_extractors_for_mp4_video_file(self):
        self.fo = get_mock_fileobject(mime_type='video/mp4')
        actual = [c.__name__ for c in suitable_data_extractors_for(self.fo)]
        self.assertIn('ExiftoolMetadataExtractor', actual)

    def test_returns_expected_extractors_for_png_image_file(self):
        self.fo = get_mock_fileobject(mime_type='image/png')
        actual = [c.__name__ for c in suitable_data_extractors_for(self.fo)]
        self.assertIn('ExiftoolMetadataExtractor', actual)
        self.assertIn('ImageOCRTextExtractor', actual)

    def test_returns_expected_extractors_for_pdf_file(self):
        self.fo = get_mock_fileobject(mime_type='application/pdf')
        actual = [c.__name__ for c in suitable_data_extractors_for(self.fo)]
        self.assertIn('ExiftoolMetadataExtractor', actual)
        self.assertIn('PyPDFMetadataExtractor', actual)
        self.assertIn('PdfTextExtractor', actual)


class TestGetExtractorClasses(TestCase):
    def test_get_extractor_classes_returns_expected_type(self):
        self.assertTrue(isinstance(get_extractor_classes(), list))
        for c in get_extractor_classes():
            self.assertTrue(issubclass(c, Extractor))

    # TODO: [hardcoded] Testing number of extractor classes needs fixing.
    def test_get_extractor_classes_returns_at_least_one_extractor(self):
        self.assertGreaterEqual(len(get_extractor_classes()), 1)

    def test_get_extractor_classes_returns_at_least_two_extractors(self):
        self.assertGreaterEqual(len(get_extractor_classes()), 2)

    def test_get_extractor_classes_returns_at_least_three_extractors(self):
        self.assertGreaterEqual(len(get_extractor_classes()), 3)

    def test_get_extractor_classes_returns_at_least_four_extractors(self):
        self.assertGreaterEqual(len(get_extractor_classes()), 4)
