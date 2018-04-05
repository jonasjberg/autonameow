# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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
from unittest import skipIf, TestCase

import unit.utils as uu
from extractors.text.plain import (
    PlainTextExtractor,
    read_entire_text_file,
    autodetect_encoding
)
from unit.case_extractors import CaseExtractorBasics


UNMET_DEPENDENCIES = (
    not PlainTextExtractor.dependencies_satisfied(),
    'Extractor dependencies not satisfied'
)
assert not UNMET_DEPENDENCIES[0], (
    'Expected extractor to not have any dependencies (always satisfied)'
)

print(UNMET_DEPENDENCIES)


@skipIf(*UNMET_DEPENDENCIES)
class TestPlainTextExtractor(CaseExtractorBasics, TestCase):
    EXTRACTOR_CLASS = PlainTextExtractor
    EXTRACTOR_NAME = 'PlainTextExtractor'


class TestReadEntireTextFileA(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_file = uu.abspath_testfile('magic_txt.txt')
        cls.actual = read_entire_text_file(cls.sample_file)

    def test_prerequisites(self):
        self.assertTrue(uu.file_exists(self.sample_file))

    def test_read_entire_text_file_returns_something(self):
        self.assertIsNotNone(self.actual)

    def test_returns_expected_encoding(self):
        self.assertTrue(uu.is_internalstring(self.actual))

    def test_returns_expected_contents(self):
        self.assertEqual('text\n', self.actual)


class TestReadEntireTextFileB(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.sample_file = uu.abspath_testfile('simplest_pdf.md.pdf.txt')
        cls.expected_text = '''Probably a title
Text following the title, probably.


Chapter One

First chapter text is missing!


Chapter Two

Second chapter depends on Chapter one ..
Test test. This file contains no digits whatsoever.




                                        1
'''

    def test_prerequisites(self):
        self.assertTrue(uu.file_exists(self.sample_file))

    def test_read_entire_text_file_returns_something(self):
        actual = read_entire_text_file(self.sample_file)
        self.assertIsNotNone(actual)

    def test_returns_expected_encoding(self):
        actual = read_entire_text_file(self.sample_file)
        self.assertTrue(uu.is_internalstring(actual))

    def test_returns_expected_contents(self):
        actual = read_entire_text_file(self.sample_file)
        self.assertEqual(actual, self.expected_text)


class TestReadEntireTextFileStressTest(TestCase):
    def setUp(self):
        self.sample_files = [f for f in uu.all_testfiles()
                             if os.path.basename(f).endswith('.txt')]

    def reads_all_test_files_with_txt_extension(self):
        for f in self.sample_files:
            self.assertTrue(uu.file_exists(f))
            actual = read_entire_text_file(f)
            self.assertTrue(uu.is_internalstring(actual))


def get_sample_text_files(prefix, suffix='.txt'):
    """
    Returns:  A list of tuples; ('absolute_path', 'expected_encoding')
    """
    _sample_files = [
        f for f in uu.all_testfiles()
        if os.path.basename(f).startswith(prefix)
        and os.path.basename(f).endswith(suffix)
    ]

    samplefile_expectedencoding = [
        (f, os.path.basename(f).replace(prefix, '').replace(suffix, ''))
        for f in _sample_files
    ]

    return samplefile_expectedencoding


class TestAutodetectEncoding(TestCase):
    def test_detects_ascii(self):
        sample = uu.abspath_testfile('magic_txt.txt')
        self.assertTrue(uu.file_exists(sample))
        actual = autodetect_encoding(sample)
        self.assertEqual(actual, 'ascii')

    def test_detects_utf8(self):
        self.skipTest('file says: "test_files/README.txt: UTF-8 Unicode text"')
        sample = uu.abspath_testfile('README.txt')
        self.assertTrue(uu.file_exists(sample))
        actual = autodetect_encoding(sample)
        self.assertEqual('utf-8', actual)

    def test_detects_encodings(self):
        testfile_encoding = get_sample_text_files(prefix='text_git_')
        self.assertGreater(len(testfile_encoding), 0)
        self.assertTrue(uu.file_exists(f) for f, _ in testfile_encoding)
        self.assertTrue(uu.is_internalstring(e)
                        for _, e in testfile_encoding)

        for testfile, expected_encoding in testfile_encoding:
            actual = autodetect_encoding(testfile).lower()

            # Two of the sample files are utf-8, remove trailing "_n".
            if expected_encoding in ('utf-8_1', 'utf-8_2'):
                expected_encoding = 'utf-8'

            if actual == 'windows-1252' and expected_encoding == 'utf16':
                # TODO: TODO: Improve auto-detecting encodings ..
                continue
            if actual == 'koi8-r' and expected_encoding == 'iso88591':
                # TODO: TODO: Improve auto-detecting encodings ..
                continue
            if actual == 'iso-8859-1' and expected_encoding == 'utf16':
                # TODO: TODO: Improve auto-detecting encodings ..
                continue

            self.assertEqual(actual, expected_encoding)

    def test_returns_none_for_non_text_files(self):
        self.skipTest('Assume non-textfiles are detected and skipped prior?')
        for test_file in ['magic_jpg.jpg', 'magic_png.png']:
            sample = uu.abspath_testfile(test_file)
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
    @classmethod
    def setUpClass(cls):
        cls.testfile_encoding = get_sample_text_files(prefix='text_alnum_')

    def test_prerequisites(self):
        self.assertGreaterEqual(len(self.testfile_encoding), 0)
        self.assertTrue(uu.file_exists(f) for f, _ in self.testfile_encoding)
        self.assertTrue(uu.is_internalstring(e)
                        for _, e in self.testfile_encoding)

    def test_detects_encodings(self):
        self.skipTest('TODO: Improve auto-detecting encodings ..')
        for testfile, expected_encoding in self.testfile_encoding:
            if expected_encoding == 'cp1252':
                # TODO: Improve encoding detection! (or not, for these samples)
                continue

            actual = autodetect_encoding(testfile)
            self.assertEqual(actual, expected_encoding)


class TestAutoDetectsEncodingFromSampleText(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.testfile_encoding = get_sample_text_files(prefix='text_sample_')

    def test_prerequisites(self):
        self.assertGreater(len(self.testfile_encoding), 0)
        self.assertTrue(uu.file_exists(f) for f, _ in self.testfile_encoding)
        self.assertTrue(uu.is_internalstring(e,)
                        for _, e in self.testfile_encoding)

    def test_detects_encodings(self):
        for testfile, expected_encoding in self.testfile_encoding:
            actual = autodetect_encoding(testfile).lower()

            if actual == 'iso-8859-1' and expected_encoding == 'cp1252':
                # TODO: TODO: Improve auto-detecting encodings ..
                continue
            if (actual == 'iso-8859-2'
                    and expected_encoding in ('iso-8859-1', 'cp437', 'cp1252',
                                              'cp858', 'macroman')):
                # TODO: TODO: Improve auto-detecting encodings ..
                continue
            if (actual == 'windows-1252'
                    and expected_encoding in ('cp858', 'cp437', 'macroman')):
                # TODO: TODO: Improve auto-detecting encodings ..
                continue

            if actual == 'utf-16le' and expected_encoding == 'utf-16':
                # TODO: TODO: Improve auto-detecting encodings ..
                continue

            self.assertEqual(actual, expected_encoding)
