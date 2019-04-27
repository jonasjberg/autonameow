# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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
from extractors.text.extractor_plain import PlainTextExtractor
from extractors.text.extractor_plain import read_entire_text_file
from unit.case_extractors_text import CaseTextExtractorBasics


UNMET_DEPENDENCIES = (
    not PlainTextExtractor.dependencies_satisfied(),
    'Extractor dependencies not satisfied'
)
assert not UNMET_DEPENDENCIES[0], (
    'Expected extractor to not have any dependencies (always satisfied)'
)

print(UNMET_DEPENDENCIES)


@skipIf(*UNMET_DEPENDENCIES)
class TestPlainTextExtractor(CaseTextExtractorBasics, TestCase):
    EXTRACTOR_CLASS = PlainTextExtractor
    EXTRACTOR_NAME = 'PlainTextExtractor'


class TestPlainTextExtractorCanHandle(TestCase):
    def setUp(self):
        self.e = PlainTextExtractor()

        class DummyFileObject(object):
            def __init__(self, mime, basename_suffix):
                self.mime_type = mime
                self.basename_suffix = basename_suffix

        self.fo_image = DummyFileObject(mime='image/jpeg',
                                        basename_suffix=b'jpg')
        self.fo_pdf = DummyFileObject(mime='application/pdf',
                                      basename_suffix=b'pdf')
        self.fo_text = DummyFileObject(mime='text/plain',
                                       basename_suffix=b'txt')

    def test_class_method_can_handle_returns_false(self):
        self.assertFalse(self.e.can_handle(self.fo_image))
        self.assertFalse(self.e.can_handle(self.fo_pdf))

    def test_class_method_can_handle_returns_true(self):
        self.assertTrue(self.e.can_handle(self.fo_text))


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
