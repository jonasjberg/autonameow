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

import os

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


class TestReadEntireTextFileStressTest(TestCase):
    def setUp(self):
        self.sample_files = [f for f in uu.all_testfiles()
                             if os.path.basename(f).endswith('.txt')]

    def reads_all_test_files_with_txt_extension(self):
        for f in self.sample_files:
            self.assertTrue(uu.file_exists(f))
            actual = read_entire_text_file(f)
            self.assertTrue(isinstance(actual, str))


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


class TestAutoDetectsEncodingFromAlphaNumerics(TestCase):
    def setUp(self):
        self.sample_files = [
            f for f in uu.all_testfiles()
            if os.path.basename(f).startswith('text_alnum_')
            and os.path.basename(f).endswith('.txt')
        ]

        self.testfile_encoding_pairs = [
            (f,
             os.path.basename(f).replace('text_alnum_', '').replace('.txt', ''))
            for f in self.sample_files
        ]

    def test_setup(self):
        self.assertGreaterEqual(len(self.testfile_encoding_pairs), 0)
        self.assertGreaterEqual(len(self.sample_files), 0)

    def test_detects_encodings(self):
        self.skipTest('TODO: Improve auto-detecting encodings ..')
        for testfile, expected_encoding in self.testfile_encoding_pairs:
            self.assertTrue(uu.file_exists(testfile))

            if expected_encoding == 'cp1252':
                # TODO: Improve encoding detection!
                continue

            actual = autodetect_encoding(testfile)
            self.assertEqual(actual, expected_encoding)


class TestAutoDetectsEncodingFromSampleText(TestCase):
    def setUp(self):
        self.sample_files = [
            f for f in uu.all_testfiles()
            if os.path.basename(f).startswith('text_sample_')
               and os.path.basename(f).endswith('.txt')
        ]

        self.testfile_encoding_pairs = [
            (f,
             os.path.basename(f).replace('text_sample_', '').replace('.txt', '')
             )
            for f in self.sample_files
        ]

    def test_setup(self):
        self.assertGreaterEqual(len(self.testfile_encoding_pairs), 0)
        self.assertGreaterEqual(len(self.sample_files), 0)

    def test_detects_encodings(self):
        for testfile, expected_encoding in self.testfile_encoding_pairs:
            self.assertTrue(uu.file_exists(testfile))
            actual = autodetect_encoding(testfile).lower()

            if actual == 'iso-8859-9' and expected_encoding == 'cp1252':
                # TODO: Improve encoding detection!
                continue
            if actual == 'ascii':
                if expected_encoding in ('cp1252', 'cp437', 'cp858',
                                         'iso-8859-1', 'macroman', 'utf-8'):
                    # TODO: Improve encoding detection!
                    continue
            if actual == 'windows-1252' and expected_encoding == 'cp437':
                # TODO: Improve encoding detection!
                continue
            if actual == 'windows-1254' and expected_encoding == 'macroman':
                # TODO: Improve encoding detection!
                continue

            self.assertEqual(actual, expected_encoding)
