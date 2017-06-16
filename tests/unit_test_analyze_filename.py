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

from datetime import datetime
from unittest import TestCase

from analyzers.analyze_filename import FilenameAnalyzer
from core.fileobject import FileObject
from unit_utils import (
    make_temporary_file,
    get_named_file_object
)


def get_filename_analyzer(file_object):
    return FilenameAnalyzer(file_object, None, None)


class TestFilenameAnalyzerWithImageFile(TestCase):
    def setUp(self):
        self.fo = get_named_file_object('2010-01-31_161251.jpg')
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

    def test_get_tags_returns_empty_list(self):
        self.assertEqual([], self.fna.get_tags())

    def test_get_title_returns_empty_list(self):
        self.assertEqual([], self.fna.get_title())


class TestFilenameAnalyzerWithEmptyFile(TestCase):
    def setUp(self):
        self.fo = get_named_file_object('empty')
        self.fna = get_filename_analyzer(self.fo)

    def test_setup(self):
        self.assertIsNotNone(self.fo)
        self.assertIsNotNone(self.fna)

    def test_get_datetime_does_not_return_none(self):
        self.assertIsNotNone(self.fna.get_datetime())

    def test_get_datetime_returns_empty_list(self):
        self.assertEqual([], self.fna.get_datetime())

    def test_get_tags_does_not_return_none(self):
        self.assertIsNotNone(self.fna.get_tags())

    def test_get_tags_returns_empty_list(self):
        self.assertEqual([], self.fna.get_tags())

    def test_get_title_does_not_return_none(self):
        self.assertIsNotNone(self.fna.get_title())

    def test_get_title_return_is_valid(self):
        self.assertEqual([{'source': 'filenamepart_base',
                           'value': 'empty',
                           'weight': 0.25}], self.fna.get_title())


class TestFilenameAnalyzerWithTaggedFile(TestCase):
    def setUp(self):
        self.fo = get_named_file_object('2015-07-03_163838 Keeping notes in Vim -- dv017a dev.ogv')
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

        expected = datetime.strptime('20150703 163838', '%Y%m%d %H%M%S')
        self.assertEqual(expected, dt_special.get('value'))

    def test_get_tags_does_not_return_none(self):
        self.assertIsNotNone(self.fna.get_tags())

    def test_get_tags_return_is_valid(self):
        self.assertEqual(['dv017a', 'dev'], self.fna.get_tags())

    def test_get_title_does_not_return_none(self):
        self.assertIsNotNone(self.fna.get_title())

    def test_get_title_contains_filename(self):
        title_fn, = filter(lambda t: t['source'] == 'filenamepart_base',
                           self.fna.get_title())
        self.assertIsNotNone(title_fn)

    def test_get_title_return_is_valid(self):
        self.assertEqual([{'source': 'filenamepart_base',
                           'value': 'Keeping notes in Vim',
                           'weight': 1}], self.fna.get_title())
