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

from core import (
    constants,
    exceptions,
    container
)
import unit_utils as uu


class TestSessionDataPool(TestCase):
    def setUp(self):
        self.d = container.SessionDataPool()
        self.file_object = uu.get_mock_fileobject(mime_type='text/plain')

    def test_extracted_data_can_be_instantiated(self):
        self.assertIsNotNone(self.d)

    def test_results_init_in_expected_state(self):
        self.assertTrue(isinstance(self.d._data, dict))
        self.assertEqual(len(self.d), 0)

    def test_add_data_with_invalid_label_raises_error(self):
        with self.assertRaises(exceptions.InvalidDataSourceError):
            self.d.add(self.file_object, None, 'data')
        with self.assertRaises(exceptions.InvalidDataSourceError):
            self.d.add(self.file_object, '', 'data')

    def test_adds_data_with_valid_label(self):
        valid_labels = constants.VALID_DATA_SOURCES[:3]
        for valid_label in valid_labels:
            self.d.add(self.file_object, valid_label, 'data')

    def test_adding_data_increments_len(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(self.file_object, valid_label, 'data')
        self.assertEqual(len(self.d), 1)

    def test_adding_data_with_different_labels_increments_len(self):
        first_valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(self.file_object, first_valid_label, 'data')
        self.assertEqual(len(self.d), 1)

        second_valid_label = constants.VALID_DATA_SOURCES[1]
        self.d.add(self.file_object, second_valid_label, 'data')
        self.assertEqual(len(self.d), 2)

    def test_adding_data_with_same_label_increments_len(self):
        first_valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(self.file_object, first_valid_label, 'data')
        self.assertEqual(len(self.d), 1)

        second_valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(self.file_object, second_valid_label, 'data')
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
        self.d.add(self.file_object, valid_label, 'expected_data')

        actual = self.d.get(self.file_object).get(valid_label)
        self.assertEqual(actual, 'expected_data')

    def test_none_label_returns_expected_data(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(self.file_object, valid_label, 'expected_data')

        actual = self.d.get(None)
        expect = {self.file_object: {valid_label: 'expected_data'}}
        self.assertEqual(actual, expect)

    def test_valid_label_returns_expected_data_multiple_entries(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.d.add(self.file_object, valid_label, 'expected_data_a')
        self.d.add(self.file_object, valid_label, 'expected_data_b')

        actual = self.d.get(self.file_object).get(valid_label)
        self.assertIn('expected_data_a', actual)
        self.assertIn('expected_data_b', actual)

    def test_none_label_returns_expected_data_multiple_entries(self):
        valid_label_a = constants.VALID_DATA_SOURCES[0]
        valid_label_b = constants.VALID_DATA_SOURCES[1]
        self.d.add(self.file_object, valid_label_a, 'expected_data_a')
        self.d.add(self.file_object, valid_label_b, 'expected_data_b')

        actual = self.d.get(None)
        self.assertIn(valid_label_a, actual[self.file_object])
        self.assertIn(valid_label_b, actual[self.file_object])
        self.assertTrue(actual[self.file_object][valid_label_a],
                        'expected_data_a')
        self.assertTrue(actual[self.file_object][valid_label_b],
                        'expected_data_b')

    def test_add(self):
        _field = constants.ANALYSIS_RESULTS_FIELDS[0]
        _results = []
        self.d.add(self.file_object, _field, _results)

    def test_adding_one_result_increments_len_once(self):
        _field = constants.ANALYSIS_RESULTS_FIELDS[0]
        _results = ['foo']
        self.d.add(self.file_object, _field, _results)

        self.assertEqual(len(self.d), 1)

    def test_adding_two_results_increments_len_twice(self):
        _field_one = constants.ANALYSIS_RESULTS_FIELDS[0]
        _field_two = constants.ANALYSIS_RESULTS_FIELDS[1]
        _result_one = ['foo']
        _result_two = ['bar']
        self.d.add(self.file_object, _field_one, _result_one)
        self.d.add(self.file_object, _field_two, _result_two)

        self.assertEqual(len(self.d), 2)

    def test_adding_list_of_two_results_increments_len_twice(self):
        _field_one = constants.ANALYSIS_RESULTS_FIELDS[0]
        _result_one = ['foo', 'bar']
        self.d.add(self.file_object, _field_one, _result_one)

        self.assertEqual(len(self.d), 2)

    def test_adding_dict_of_two_results_increments_len_twice(self):
        _field_one = constants.ANALYSIS_RESULTS_FIELDS[0]
        _result_one = {'baz': ['foo', 'bar']}
        self.d.add(self.file_object, _field_one, _result_one)

        self.assertEqual(len(self.d), 2)

    def test_add_empty_does_not_increment_len(self):
        _field = constants.ANALYSIS_RESULTS_FIELDS[0]
        _results = []
        self.d.add(self.file_object, _field, _results)

        self.assertEqual(len(self.d), 0)
