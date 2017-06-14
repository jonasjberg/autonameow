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
from core.extraction import ExtractedData


class TestExtractedData(TestCase):
    def setUp(self):
        self.d = ExtractedData()

    def test_extracted_data_can_be_instantiated(self):
        self.assertIsNotNone(self.d)

    def test_add_data_with_invalid_label_raises_error(self):
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
