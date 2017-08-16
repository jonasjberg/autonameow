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
    exceptions,
    constants
)
from core.repository import Repository

import unit_utils as uu


class TestRepository(TestCase):
    def setUp(self):
        self.r = Repository()

    def test_setup(self):
        self.r.initialize()
        self.assertTrue(isinstance(self.r._query_string_source_map, dict))


class TestRepositoryMethodStore(TestCase):
    def setUp(self):
        self.r = Repository()
        self.r.initialize()
        self.file_object = uu.get_mock_fileobject(mime_type='text/plain')

    def test_repository_init_in_expected_state(self):
        self.assertTrue(isinstance(self.r.data, dict))
        self.assertEqual(len(self.r), 0)

    def test_storing_data_increments_len(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.r.store(self.file_object, valid_label, 'data')
        self.assertEqual(len(self.r), 1)

    def test_storing_data_with_different_labels_increments_len(self):
        first_valid_label = constants.VALID_DATA_SOURCES[0]
        self.r.store(self.file_object, first_valid_label, 'data')
        self.assertEqual(len(self.r), 1)

        second_valid_label = constants.VALID_DATA_SOURCES[1]
        self.r.store(self.file_object, second_valid_label, 'data')
        self.assertEqual(len(self.r), 2)

    def test_adding_data_with_same_label_increments_len(self):
        first_valid_label = constants.VALID_DATA_SOURCES[0]
        self.r.store(self.file_object, first_valid_label, 'data')
        self.assertEqual(len(self.r), 1)

        second_valid_label = constants.VALID_DATA_SOURCES[0]
        self.r.store(self.file_object, second_valid_label, 'data')
        self.assertEqual(len(self.r), 2)

    def test_adding_one_result_increments_len_once(self):
        _field = constants.ANALYSIS_RESULTS_FIELDS[0]
        _results = ['foo']
        self.r.store(self.file_object, _field, _results)

        self.assertEqual(len(self.r), 1)

    def test_adding_two_results_increments_len_twice(self):
        _field_one = constants.ANALYSIS_RESULTS_FIELDS[0]
        _field_two = constants.ANALYSIS_RESULTS_FIELDS[1]
        _result_one = ['foo']
        _result_two = ['bar']
        self.r.store(self.file_object, _field_one, _result_one)
        self.r.store(self.file_object, _field_two, _result_two)

        self.assertEqual(len(self.r), 2)

    def test_adding_list_of_two_results_increments_len_twice(self):
        _field_one = constants.ANALYSIS_RESULTS_FIELDS[0]
        _result_one = ['foo', 'bar']
        self.r.store(self.file_object, _field_one, _result_one)

        self.assertEqual(len(self.r), 2)

    def test_adding_dict_of_two_results_increments_len_twice(self):
        _field_one = constants.ANALYSIS_RESULTS_FIELDS[0]
        _result_one = {'baz': ['foo', 'bar']}
        self.r.store(self.file_object, _field_one, _result_one)

        self.assertEqual(len(self.r), 2)

    def test_add_empty_does_not_increment_len(self):
        _field = constants.ANALYSIS_RESULTS_FIELDS[0]
        _results = []
        self.r.store(self.file_object, _field, _results)

        self.assertEqual(len(self.r), 0)

    def test_store_data_with_invalid_label_raises_error(self):
        with self.assertRaises(exceptions.InvalidDataSourceError):
            self.r.store(self.file_object, None, 'data')
        with self.assertRaises(exceptions.InvalidDataSourceError):
            self.r.store(self.file_object, '', 'data')

    def test_stores_data_with_valid_label(self):
        valid_labels = constants.VALID_DATA_SOURCES[:3]
        for valid_label in valid_labels:
            self.r.store(self.file_object, valid_label, 'data')

    def test_valid_label_returns_expected_data(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.r.store(self.file_object, valid_label, 'expected_data')

        actual = self.r.resolve(self.file_object, valid_label)
        self.assertEqual(actual, 'expected_data')

    def test_none_label_returns_expected_data(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.r.store(self.file_object, valid_label, 'expected_data')

        actual = self.r.resolve(self.file_object, None)
        expect = {self.file_object: {valid_label: 'expected_data'}}
        self.assertEqual(actual, expect)

    def test_valid_label_returns_expected_data_multiple_entries(self):
        valid_label = constants.VALID_DATA_SOURCES[0]
        self.r.store(self.file_object, valid_label, 'expected_data_a')
        self.r.store(self.file_object, valid_label, 'expected_data_b')

        actual = self.r.resolve(self.file_object, valid_label)
        self.assertIn('expected_data_a', actual)
        self.assertIn('expected_data_b', actual)

    def test_none_label_returns_expected_data_multiple_entries(self):
        valid_label_a = constants.VALID_DATA_SOURCES[0]
        valid_label_b = constants.VALID_DATA_SOURCES[1]
        self.r.store(self.file_object, valid_label_a, 'expected_data_a')
        self.r.store(self.file_object, valid_label_b, 'expected_data_b')

        actual = self.r.resolve(self.file_object, None)
        self.assertIn(valid_label_a, actual[self.file_object])
        self.assertIn(valid_label_b, actual[self.file_object])
        self.assertTrue(actual[self.file_object][valid_label_a],
                        'expected_data_a')
        self.assertTrue(actual[self.file_object][valid_label_b],
                        'expected_data_b')


class TestRepositoryMethodResolvable(TestCase):
    def setUp(self):
        self.r = Repository()
        self.r.initialize()

    def test_empty_query_string_returns_false(self):
        self.assertFalse(self.r.resolvable(None))
        self.assertFalse(self.r.resolvable(''))

    def test_bad_query_string_returns_false(self):
        self.assertFalse(self.r.resolvable('not.a.valid.source.surely'))

    def test_good_query_string_returns_true(self):
        self.assertTrue(self.r.resolvable('metadata.exiftool.PDF:CreateDate'))
        self.assertTrue(self.r.resolvable('metadata.exiftool'))
        self.assertTrue(self.r.resolvable('filesystem.basename.full'))
        self.assertTrue(self.r.resolvable('filesystem.basename.extension'))
        self.assertTrue(self.r.resolvable('filesystem.contents.mime_type'))
