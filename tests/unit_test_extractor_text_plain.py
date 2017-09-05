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

import unit_utils as uu
from extractors.text.plain import (
    read_entire_text_file,
    autodetect_encoding
)


class TestReadEntireTextFile(TestCase):
    def setUp(self):
        self.sample_file = uu.abspath_testfile('magic_txt.txt')
        self.assertTrue(uu.file_exists(self.sample_file))

    def test_read_entire_text_file(self):
        actual = read_entire_text_file(self.sample_file)
        self.assertIsNotNone(actual)

    def test_returns_expected_encoding(self):
        actual = read_entire_text_file(self.sample_file)
        self.assertTrue(isinstance(actual, str))

    def test_returns_expected_contents(self):
        actual = read_entire_text_file(self.sample_file)
        self.assertEqual(actual, 'text\n')


class TestAutodetectEncoding(TestCase):
    def test_detects_ascii(self):
        sample = uu.abspath_testfile('magic_txt.txt')
        self.assertTrue(uu.file_exists(sample))
        actual = autodetect_encoding(sample)
        self.assertEqual(actual, 'ascii')

    def test_detects_utf8(self):
        sample = uu.abspath_testfile('README.txt')
        self.assertTrue(uu.file_exists(sample))
        actual = autodetect_encoding(sample)
        self.assertEqual(actual, 'utf-8')

    def test_detects_encodings(self):
        testfile_encoding_pairs = [
            ('text_eucjp.txt', 'EUC-JP'),
            ('text_iso2022jp.txt', 'ISO-2022-JP'),
            # ('text_iso88591.txt', 'ISO-8859-1'),
            ('text_utf16.txt', 'ISO-8859-1'),
            ('text_utf8_1.txt', 'utf-8'),
            ('text_utf8_2.txt', 'utf-8'),
        ]

        for testfile, expected_encoding in testfile_encoding_pairs:
            sample = uu.abspath_testfile(testfile)
            self.assertTrue(uu.file_exists(sample))

            actual = autodetect_encoding(sample)
            self.assertEqual(actual, expected_encoding)

    def test_returns_none_for_non_text_files(self):
        sample = uu.abspath_testfile('magic_png.png')
        self.assertTrue(uu.file_exists(sample))
        actual = autodetect_encoding(sample)
        self.assertIsNone(actual)

    def test_returns_none_for_empty_files(self):
        sample = uu.abspath_testfile('empty')
        self.assertTrue(uu.file_exists(sample))
        actual = autodetect_encoding(sample)
        self.assertIsNone(actual)

    def test_returns_none_for_non_existing_files(self):
        sample = '/tmp/this_isnt_a_file_right_or_huh'
        self.assertFalse(uu.file_exists(sample))
        actual = autodetect_encoding(sample)
        self.assertIsNone(actual)
