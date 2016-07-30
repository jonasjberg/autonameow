# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

from unittest import TestCase
from datetime import datetime

from analyze.analyze_filename import FilenameAnalyzer
from file_object import FileObject


class TestFilenameAnalyzerWithImageFile(TestCase):
    def setUp(self):
        # TODO: Fix the filtering! Not completed as-is.
        self.filter = {'ignore_years': [],
                       'ignore_before_year': None,
                       'ignore_after_year': None}

        self.fo = FileObject('~/dev/projects/autonameow/test_files/2010-01-31_161251.jpg')
        self.fna = FilenameAnalyzer(self.fo, self.filter)

    def test_setup(self):
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
        self.assertEqual(expected, dt_special.get('datetime'))


class TestFilenameAnalyzerWithEmptyFile(TestCase):
    def setUp(self):
        # TODO: Fix the filtering! Not completed as-is.
        self.filter = {'ignore_years': [],
                       'ignore_before_year': None,
                       'ignore_after_year': None}

        self.fo = FileObject('~/dev/projects/autonameow/test_files/empty')
        self.fna = FilenameAnalyzer(self.fo, self.filter)

    def test_setup(self):
        self.assertIsNotNone(self.fna)

    def test_get_datetime_does_not_return_none(self):
        self.assertIsNotNone(self.fna.get_datetime())

    def test_get_datetime_returns_empty_list(self):
        self.assertEqual([], self.fna.get_datetime())
