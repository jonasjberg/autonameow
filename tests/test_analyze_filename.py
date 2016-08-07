# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

from datetime import datetime
from unittest import TestCase

from core.analyze.analyze_filename import FilenameAnalyzer
from core.fileobject import FileObject


class TestFilenameAnalyzerWithImageFile(TestCase):
    # Setup and sanity check:
    def setUp(self):
        # TODO: Fix the filtering! Not completed as-is.
        self.filter = {'ignore_years': [],
                       'ignore_before_year': None,
                       'ignore_after_year': None}

        self.fo = FileObject('~/dev/projects/autonameow/test_files/2010-01-31_161251.jpg')
        self.fna = FilenameAnalyzer(self.fo, self.filter)

    def test_setup(self):
        self.assertIsNotNone(self.fo)
        self.assertIsNotNone(self.fna)

    # Tests:
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
    # Setup and sanity check:
    def setUp(self):
        # TODO: Fix the filtering! Not completed as-is.
        self.filter = {'ignore_years': [],
                       'ignore_before_year': None,
                       'ignore_after_year': None}

        self.fo = FileObject('~/dev/projects/autonameow/test_files/empty')
        self.fna = FilenameAnalyzer(self.fo, self.filter)

    def test_setup(self):
        self.assertIsNotNone(self.fo)
        self.assertIsNotNone(self.fna)

    # Tests:
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
                           'title': 'empty',
                           'weight': 0.25}], self.fna.get_title())


class TestFilenameAnalyzerWithTaggedFile(TestCase):
    # Setup and sanity check:
    def setUp(self):
        # TODO: Fix the filtering! Not completed as-is.
        self.filter = {'ignore_years': [],
                       'ignore_before_year': None,
                       'ignore_after_year': None}

        self.fo = FileObject('~/dev/projects/autonameow/test_files/2015-07-03_163838 Keeping notes in Vim -- dv017a dev.ogv')
        self.fna = FilenameAnalyzer(self.fo, self.filter)

    def test_setup(self):
        self.assertIsNotNone(self.fo)
        self.assertIsNotNone(self.fna)

    # Tests:
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
                           'title': 'Keeping notes in Vim',
                           'weight': 1}], self.fna.get_title())
