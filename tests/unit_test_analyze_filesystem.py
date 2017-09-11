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

from analyzers.analyze_filesystem import FilesystemAnalyzer
from core import util
from core.fileobject import FileObject
import unit_utils as uu


def get_filesystem_analyzer(file_object):
    return FilesystemAnalyzer(file_object, None, None)


class TestFilesystemAnalyzerWithEmptyFile(TestCase):
    def setUp(self):
        # TODO: [TD0034][TD0035] Fix the filtering! Not completed as-is.
        self.filter = {'ignore_years': [],
                       'ignore_before_year': None,
                       'ignore_after_year': None}

        self.fo = uu.get_mock_fileobject('inode/x-empty')
        self.fsa = get_filesystem_analyzer(self.fo)

    def get_datetime_source(self, field_name):
        return filter(lambda dt: dt['source'] == field_name,
                      self.fsa.get_datetime())

    def test_setup(self):
        self.assertIsNotNone(self.fo)
        self.assertIsNotNone(self.fsa)

    def test_get_datetime_does_not_return_none(self):
        dt_list = self.fsa.get_datetime()
        self.assertIsNotNone(dt_list)

    def test_get_datetime_contains_filesystem_modified(self):
        dt_modified = self.get_datetime_source('modified')
        self.assertIsNotNone(dt_modified)

    def test_get_datetime_filesystem_modified_is_valid(self):
        self.skipTest('Modified time might have changed between test runs.')
        dt_modified, = self.get_datetime_source('modified')

        expected = datetime.strptime('20160628 112136', '%Y%m%d %H%M%S')
        self.assertEqual(expected, dt_modified.get('value'))

    def test_get_datetime_contains_filesystem_created(self):
        dt_created = self.get_datetime_source('created')
        self.assertIsNotNone(dt_created)

    def test_get_datetime_filesystem_created_is_valid(self):
        self.skipTest('Create time might have changed. Should be set to a '
                      'known time as part of the tests setup.')

        dt_created, = filter(lambda dt: dt['source'] == 'created',
                             self.fsa.get_datetime())

        expected = datetime.strptime('20170415 025614', '%Y%m%d %H%M%S')
        self.assertEqual(expected, dt_created.get('value'))

    def test_get_datetime_contains_filesystem_accessed(self):
        dt_created = self.get_datetime_source('created')
        self.assertIsNotNone(dt_created)

    def test_get_datetime_filesystem_accessed_is_valid(self):
        self.skipTest('Access time might have changed between test runs.')

        dt_accessed, = filter(lambda dt: dt['source'] == 'accessed',
                              self.fsa.get_datetime())

        expected = datetime.strptime('20170415 025614', '%Y%m%d %H%M%S')
        self.assertEqual(expected, dt_accessed.get('value'))

    def test_get_title_raises_not_implemented_error(self):
        with self.assertRaises(AttributeError):
            self.assertIsNone(self.fsa.get_title())

    def test_get_author_raises_not_implemented_error(self):
        with self.assertRaises(AttributeError):
            self.assertIsNone(self.fsa.get_author())

    def test_get_tags_raises_not_implemented_error(self):
        with self.assertRaises(AttributeError):
            self.assertIsNone(self.fsa.get_tags())

    def test__get_datetime_from_filesystem_returns_expected_type(self):
        actual = self.fsa._get_datetime_from_filesystem()
        for entry in actual:
            self.assertTrue(isinstance(entry.get('value'), datetime))

    def test__get_datetime_from_filesystem(self):
        self.skipTest('Create and access time might have changed. Should be '
                      'set to a known state as part of the tests setup.')

        expect_dt_mod = datetime.strptime('20160628 112136', '%Y%m%d %H%M%S')
        expect_dt_cre = datetime.strptime('20170415 025614', '%Y%m%d %H%M%S')
        expect_dt_acc = datetime.strptime('20170415 025614', '%Y%m%d %H%M%S')
        expect_list = [{'value': expect_dt_mod,
                        'source': 'modified',
                        'weight': 1},
                       {'value': expect_dt_cre,
                        'source': 'created',
                        'weight': 1},
                       {'value': expect_dt_acc,
                        'source': 'accessed',
                        'weight': 0.25}]

        self.assertEqual(expect_list, self.fsa._get_datetime_from_filesystem())
