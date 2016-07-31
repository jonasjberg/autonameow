# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

from unittest import TestCase
from datetime import datetime

from analyze.analyze_filesystem import FilesystemAnalyzer
from file_object import FileObject


class TestFilesystemAnalyzerWithEmptyFile(TestCase):
    def setUp(self):
        # TODO: Fix the filtering! Not completed as-is.
        self.filter = {'ignore_years': [],
                       'ignore_before_year': None,
                       'ignore_after_year': None}

        self.fo = FileObject('/home/spock/dev/projects/autoname/test_files/empty')
        self.fsa = FilesystemAnalyzer(self.fo, self.filter)

    def test_setup(self):
        self.assertIsNotNone(self.fsa)

    def test_get_datetime_does_not_return_none(self):
        dt_list = self.fsa.get_datetime()
        self.assertIsNotNone(dt_list)

    def test_get_datetime_contains_filesystem_modified(self):
        dt_modified = filter(lambda dt: dt['source'] == 'modified',
                             self.fsa.get_datetime())
        self.assertIsNotNone(dt_modified)

    def test_get_datetime_filesystem_modified_is_valid(self):
        dt_modified, = filter(lambda dt: dt['source'] == 'modified',
                              self.fsa.get_datetime())

        expected = datetime.strptime('20160628 112136', '%Y%m%d %H%M%S')
        self.assertEqual(expected, dt_modified.get('value'))

    def test_get_datetime_contains_filesystem_created(self):
        dt_created = filter(lambda dt: dt['source'] == 'created',
                            self.fsa.get_datetime())
        self.assertIsNotNone(dt_created)

    def test_get_datetime_filesystem_created_is_valid(self):
        dt_created, = filter(lambda dt: dt['source'] == 'created',
                             self.fsa.get_datetime())

        expected = datetime.strptime('20160628 112136', '%Y%m%d %H%M%S')
        self.assertEqual(expected, dt_created.get('value'))

    def test_get_datetime_contains_filesystem_accessed(self):
        dt_created = filter(lambda dt: dt['source'] == 'created',
                            self.fsa.get_datetime())
        self.assertIsNotNone(dt_created)

    def test_get_datetime_filesystem_accessed_is_valid(self):
        dt_accessed, = filter(lambda dt: dt['source'] == 'accessed',
                              self.fsa.get_datetime())

        expected = datetime.strptime('20160628 112136', '%Y%m%d %H%M%S')
        self.assertEqual(expected, dt_accessed.get('value'))

    def test_get_title(self):
        pass

    def test_get_author(self):
        pass

    def test_get_tags(self):
        pass

    def test__get_datetime_from_filesystem(self):
        pass
