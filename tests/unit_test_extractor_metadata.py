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
from datetime import datetime

from extractors.metadata import (
    MetadataExtractor,
    to_datetime
)
from unit_utils import make_temporary_file


class TestMetadataExtractor(TestCase):
    def setUp(self):
        self.e = MetadataExtractor(make_temporary_file())

    def test_metadata_extractor_class_is_available(self):
        self.assertIsNotNone(MetadataExtractor)

    def test_metadata_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_method__get_raw_metadata_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e._get_raw_metadata()

    def test_query_returns_false_without__get_raw_metadata_implemented(self):
        self.assertFalse(self.e.query())
        self.assertFalse(self.e.query(field='some_field'))


class TestToDatetime(TestCase):
    def test_to_datetime_is_defined_and_reachable(self):
        self.assertIsNotNone(to_datetime)

    def test_to_datetime_raises_exception_given_bad_input(self):
        with self.assertRaises(ValueError):
            to_datetime(None)
            to_datetime('')

    def test_to_datetime_raises_exception_for_invalid_datetime_strings(self):
        with self.assertRaises(ValueError):
            to_datetime('foo bar')
            to_datetime('foo 123 bar')

    def test_to_datetime_returns_datetime_objects_given_valid_input(self):
        self.assertTrue(isinstance(to_datetime("D:20121225235237 +05'30'"),
                                   datetime))
        self.assertTrue(isinstance(to_datetime("D:20160111124132+00'00'"),
                                   datetime))

    def test_to_datetime_returns_expected_given_valid_input(self):
        DT_FMT = '%Y-%m-%dT%H:%M:%S'
        input_output = [
            ("D:20121225235237 +05'30'",
             datetime.strptime('2012-12-25T23:52:37', DT_FMT)),
            ("D:20160111124132+00'00'",
             datetime.strptime('2016-01-11T12:41:32', DT_FMT))
        ]

        for input_value, expected_output in input_output:
            self.assertEqual(to_datetime(input_value), expected_output)
