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
from core import (
    constants,
    extraction,
    exceptions
)
from core.extraction import (
    ExtractedData,
    Extraction,
)
import unit_utils as uu


class TestExtractedData(TestCase):
    def setUp(self):
        self.d = ExtractedData()

    def test_extracted_data_can_be_instantiated(self):
        self.assertIsNotNone(self.d)

    def test_add_data_with_invalid_label_raises_error(self):
        with self.assertRaises(exceptions.InvalidDataSourceError):
            self.d.add(None, 'data')
        with self.assertRaises(exceptions.InvalidDataSourceError):
            self.d.add('', 'data')

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

    def test_get_data_with_invalid_label_returns_false(self):
        self.assertFalse(self.d.get('not_a_label.surely'))
        self.assertFalse(self.d.get(''))

    def test_get_data_with_valid_label_returns_false_when_empty(self):
        valid_labels = constants.VALID_DATA_SOURCES[:3]
        for valid_label in valid_labels:
            actual = self.d.get(valid_label)
            self.assertFalse(actual)

    def test_get_all_data_returns_false_when_empty(self):
        actual = self.d.get(None)
        self.assertFalse(actual)

    def test_valid_label_returns_expected_data(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(valid_label, 'expected_data')

        actual = self.d.get(valid_label)
        self.assertEqual(actual, 'expected_data')

    def test_none_label_returns_expected_data(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(valid_label, 'expected_data')

        actual = self.d.get(None)
        expect = {valid_label: 'expected_data'}
        self.assertEqual(actual, expect)

    def test_valid_label_returns_expected_data_multiple_entries(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(valid_label, 'expected_data_a')
        self.d.add(valid_label, 'expected_data_b')

        actual = self.d.get(valid_label)
        self.assertIn('expected_data_a', actual)
        self.assertIn('expected_data_b', actual)

    def test_none_label_returns_expected_data_multiple_entries(self):
        valid_label_a = constants.VALID_DATA_SOURCES[0]
        valid_label_b = constants.VALID_DATA_SOURCES[1]
        self.d.add(valid_label_a, 'expected_data_a')
        self.d.add(valid_label_b, 'expected_data_b')

        actual = self.d.get(None)
        self.assertIn(valid_label_a, actual)
        self.assertIn(valid_label_b, actual)
        self.assertTrue(actual[valid_label_a], 'expected_data_a')
        self.assertTrue(actual[valid_label_b], 'expected_data_b')


class TestExtraction(TestCase):
    def setUp(self):
        self.e = Extraction(uu.get_mock_fileobject())
        self.sources = ['textual.py', 'metadata.py']

    def test_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_initial_results_data_len_is_zero(self):
        self.assertEqual(len(self.e.data), 0)

    def test_raises_exception_For_invalid_results(self):
        with self.assertRaises(exceptions.InvalidDataSourceError):
            self.e.collect_results(None, 'image/jpeg')
            self.e.collect_results(1, 'image/jpeg')
            self.e.collect_results(False, 'image/jpeg')

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
        extractor_classes = extractors.get_extractor_classes(self.sources)
        actual = self.e._instantiate_extractors(extractor_classes)

        self.assertTrue(isinstance(actual, list))
        for ec in actual:
            self.assertTrue(uu.is_class_instance(ec))
            self.assertTrue(issubclass(ec.__class__, extractors.BaseExtractor))

    def test_has_method__execute_run_queue(self):
        self.assertIsNotNone(self.e._execute_run_queue)


class _DummyExtractor(object):
    is_slow = False


class _DummySlowExtractor(object):
    is_slow = True


class TestKeepSlowExtractorsIfRequiredWithSlowExtractor(TestCase):
    def setUp(self):
        self.fast = _DummyExtractor
        self.slow = _DummySlowExtractor

        self.input = [self.fast, self.fast, self.slow]

    def test_keep_slow_extractors_if_required_is_defined(self):
        self.assertIsNotNone(extraction.keep_slow_extractors_if_required)

    def test_slow_extractor_are_excluded_if_not_required(self):
        actual = extraction.keep_slow_extractors_if_required(self.input, [])

        self.assertNotIn(self.slow, actual,
                         'Slow extractor class should be excluded')
        self.assertNotEqual(len(self.input), len(actual),
                            'Expect one less extractor class in the output')

    def test_slow_extractor_are_included_if_required(self):
        required = [self.slow]
        actual = extraction.keep_slow_extractors_if_required(self.input,
                                                             required)
        self.assertIn(self.slow, actual,
                      'Slow extractor class is kept when required')
        self.assertEqual(len(self.input), len(actual),
                         'Expect the same number of extractor classes')


class TestKeepSlowExtractorsIfRequired(TestCase):
    def setUp(self):
        self.fast = _DummyExtractor
        self.slow = _DummySlowExtractor

        self.input = [self.fast, self.fast, self.fast]

    def test_keep_slow_extractors_if_required_is_defined(self):
        self.assertIsNotNone(extraction.keep_slow_extractors_if_required)

    def test_slow_extractor_are_excluded_if_not_required(self):
        actual = extraction.keep_slow_extractors_if_required(self.input, [])

        self.assertNotIn(self.slow, actual,
                         'Slow extractor class should be excluded')
        self.assertEqual(len(self.input), len(actual),
                         'Expect the same number of extractor classes')

    def test_slow_extractor_are_included_if_required(self):
        required = [self.slow]
        actual = extraction.keep_slow_extractors_if_required(self.input,
                                                             required)
        self.assertNotIn(self.slow, actual,
                         'There was no slow extractor class to start with')
        self.assertEqual(len(self.input), len(actual),
                         'Expect the same number of extractor classes')
