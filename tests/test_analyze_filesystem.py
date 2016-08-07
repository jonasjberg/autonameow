# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import os
from datetime import datetime
from unittest import TestCase

from core.fileobject import FileObject
from core.analyze.analyze_filesystem import FilesystemAnalyzer


class TestFilesystemAnalyzerWithEmptyFile(TestCase):
    # Setup and sanity check:
    def setUp(self):
        # TODO: Fix the filtering! Not completed as-is.
        self.filter = {'ignore_years': [],
                       'ignore_before_year': None,
                       'ignore_after_year': None}

        # Go back one directory (..) from the location of this file.
        p_this_file = os.path.abspath(os.path.dirname(__file__))
        self.assertTrue(os.path.isdir(p_this_file))
        p_project_root = os.path.normpath(p_this_file + os.sep + os.pardir)
        self.assertTrue(os.path.isdir(p_project_root))
        p_test_file = os.path.join(
            p_project_root + os.sep + 'test_files' + os.sep + 'empty')
        self.assertTrue(os.path.isfile(p_test_file))

        self.fo = FileObject(p_test_file)
        self.fsa = FilesystemAnalyzer(self.fo, self.filter)

    def test_setup(self):
        self.assertIsNotNone(self.fo)
        self.assertIsNotNone(self.fsa)

    # Tests:
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

    def test_get_title_should_return_none(self):
        self.assertIsNone(self.fsa.get_title())

    def test_get_author_should_return_none(self):
        self.assertIsNone(self.fsa.get_author())

    def test_get_tags_returns_none(self):
        self.assertIsNone(self.fsa.get_tags())

    def test__get_datetime_from_filesystem(self):
        expect_dt_mod = datetime.strptime('20160628 112136', '%Y%m%d %H%M%S')
        expect_dt_cre = datetime.strptime('20160628 112136', '%Y%m%d %H%M%S')
        expect_dt_acc = datetime.strptime('20160628 112136', '%Y%m%d %H%M%S')
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
