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

from analyzers.analyze_filename import (
    FilenameAnalyzer,
    _find_edition
)
import unit_utils as uu


def get_filename_analyzer(file_object):
    return FilenameAnalyzer(file_object,
                            add_results_callback=uu.mock_add_results_callback,
                            request_data_callback=uu.mock_request_data_callback)


class TestFilenameAnalyzerWithImageFile(TestCase):
    def setUp(self):
        self.fo = uu.get_named_file_object('2010-01-31_161251.jpg')
        self.fna = get_filename_analyzer(self.fo)

    def test_setup(self):
        self.assertIsNotNone(self.fo)
        self.assertIsNotNone(self.fna)

    def test_get_datetime_does_not_return_none(self):
        dt_list = self.fna.get_datetime()
        self.assertIsNotNone(dt_list)

    def test_get_datetime_contains_special_case(self):
        dt_special, = filter(lambda dt: dt['source'] == 'very_special_case',
                             self.fna.get_datetime())
        self.assertIsNotNone(dt_special)

    def test_get_datetime_special_case_is_valid(self):
        dt_special, = filter(lambda dt: dt['source'] == 'very_special_case',
                             self.fna.get_datetime())

        expected = datetime.strptime('20100131 161251', '%Y%m%d %H%M%S')
        self.assertEqual(expected, dt_special.get('value'))

    def test_get_tags_does_not_return_none(self):
        self.assertIsNotNone(self.fna.get_tags())

    def test_get_tags_returns_expected(self):
        expected = [{'source': 'filenamepart_tags', 'value': [], 'weight': 0.1}]
        self.assertEqual(expected, self.fna.get_tags())

    def test_get_title_returns_empty_list(self):
        self.skipTest('TODO')
        self.assertEqual([], self.fna.get_title())


class TestFilenameAnalyzerWithEmptyFile(TestCase):
    def setUp(self):
        self.fo = uu.get_named_file_object('gmail.pdf')
        self.fna = get_filename_analyzer(self.fo)

    def test_setup(self):
        self.assertIsNotNone(self.fo)
        self.assertIsNotNone(self.fna)

    def test_get_datetime_does_not_return_none(self):
        self.skipTest('TODO')
        self.assertIsNotNone(self.fna.get_datetime())

    def test_get_datetime_returns_empty_list(self):
        self.skipTest('TODO')
        self.assertEqual([], self.fna.get_datetime())

    def test_get_tags_does_not_return_none(self):
        self.assertIsNotNone(self.fna.get_tags())

    def test_get_tags_returns_expected(self):
        expected = [{'source': 'filenamepart_tags', 'value': [], 'weight': 0.1}]
        self.assertEqual(expected, self.fna.get_tags())

    def test_get_title_does_not_return_none(self):
        self.assertIsNotNone(self.fna.get_title())

    def test_get_title_return_is_valid(self):
        self.assertEqual([{'source': 'filetags',
                           'value': 'gmail',
                           'weight': 0.25}], self.fna.get_title())


class TestFindEdition(TestCase):
    def test_returns_expected_edition(self):
        self.assertEqual(_find_edition('Foo, Bar - Baz._5th'), 5)
        self.assertEqual(_find_edition('Foo,Bar-_Baz_-_3ed_2002'), 3)
        self.assertEqual(_find_edition('Foo,Bar-_Baz_-_4ed_2003'), 4)
        self.assertEqual(_find_edition('Embedded_Systems_6th_.2011'), 6)
        self.assertEqual(_find_edition('Networking_4th'), 4)
        self.assertEqual(_find_edition('Foo 2E - Bar B. 2001'), 2)

    def test_returns_none_for_unavailable_editions(self):
        self.assertIsNone(_find_edition('Foo, Bar - Baz._'))
        self.assertIsNone(_find_edition('Foo, Bar 5 - Baz._'))
