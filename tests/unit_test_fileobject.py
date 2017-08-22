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

from core import (
    fileobject,
    constants
)


class TestFileObjectTypes(TestCase):
    def setUp(self):
        self.fo = uu.get_named_file_object('20160722 Descriptive name.txt')

    def test_internal_bytestring_path_type_abspath(self):
        self.assertTrue(isinstance(self.fo.abspath, bytes))

    def test_internal_bytestring_path_type_suffix(self):
        self.assertTrue(isinstance(self.fo.basename_suffix, bytes))

    def test_internal_bytestring_path_type_filename(self):
        self.assertTrue(isinstance(self.fo.filename, bytes))

    def test_internal_bytestring_path_type_basename_prefix(self):
        self.assertTrue(isinstance(self.fo.basename_prefix, bytes))

    def test_internal_bytestring_path_type_pathname(self):
        self.assertTrue(isinstance(self.fo.pathname, bytes))

    def test_internal_bytestring_path_type_pathparent(self):
        self.assertTrue(isinstance(self.fo.pathparent, bytes))

    def test_internal_type_mime_type(self):
        self.assertTrue(isinstance(self.fo.mime_type, str))

    def test_internal_type_str(self):
        self.assertTrue(isinstance(str(self.fo), str))


class TestFileObjectEquivalence(TestCase):
    def setUp(self):
        self.fo_unique = uu.get_mock_fileobject(mime_type='image/png')
        self.fo_dupe_1 = uu.get_mock_fileobject(mime_type='text/plain')
        self.fo_dupe_2 = uu.get_mock_fileobject(mime_type='text/plain')

    def test_setup(self):
        self.assertTrue(os.path.isfile(self.fo_unique.abspath))
        self.assertTrue(os.path.isfile(self.fo_dupe_1.abspath))

    def test_equivalence_expect_unequal(self):
        self.assertFalse(self.fo_unique == self.fo_dupe_1)
        self.assertFalse(self.fo_unique == self.fo_dupe_2)

    def test_equivalence_expect_equal(self):
        self.assertTrue(self.fo_dupe_1 == self.fo_dupe_2)

    def test_hash_expect_unequal(self):
        hash_a = hash(self.fo_unique)
        hash_b = hash(self.fo_dupe_1)
        self.assertNotEqual(hash_a, hash_b)

    def test_hash_expect_equal(self):
        hash_b = hash(self.fo_dupe_1)
        hash_c = hash(self.fo_dupe_2)
        self.assertEqual(hash_b, hash_c)

    def test_file_object_as_dictionary_key(self):
        d = {self.fo_unique: 'a',
             self.fo_dupe_1: 'b',
             self.fo_dupe_2: 'c'}

        self.assertEqual(len(d), 2)
        self.assertEqual(d.get(self.fo_unique), 'a')
        self.assertEqual(d.get(self.fo_dupe_1), 'c')
        self.assertEqual(d.get(self.fo_dupe_2), 'c')


class TestFileTypeMagic(TestCase):
    def setUp(self):
        TEST_FILES = [('magic_bmp.bmp', 'image/x-ms-bmp'),
                      ('magic_gif.gif', 'image/gif'),
                      ('magic_jpg.jpg', 'image/jpeg'),
                      ('magic_mp4.mp4', 'video/mp4'),
                      ('magic_pdf.pdf', 'application/pdf'),
                      ('magic_png.png', 'image/png'),
                      ('magic_txt',     'text/plain'),
                      ('magic_txt.md',  'text/plain'),
                      ('magic_txt.txt', 'text/plain')]
        self.test_files = [(uu.abspath_testfile(f), e) for f, e in TEST_FILES]

    def test_test_files_defined(self):
        for fname, fmagic in self.test_files:
            self.assertIsNotNone(fname)
            self.assertIsNotNone(fmagic)
            self.assertTrue(len(fname) > 0)
            self.assertTrue(len(fmagic) > 0)

    def test_test_files_exist(self):
        for fname, _ in self.test_files:
            self.assertTrue(os.path.isfile(fname))

    def test_test_files_are_readable(self):
        for fname, _ in self.test_files:
            self.assertTrue(os.access(fname, os.R_OK))

    def test_filetype_magic(self):
        for fname, fmagic in self.test_files:
            self.assertIsNotNone(fileobject.filetype_magic(fname))
            self.assertEqual(fmagic, fileobject.filetype_magic(fname))

    def test_filetype_magic_with_invalid_args(self):
        self.assertEqual(fileobject.filetype_magic(None),
                         constants.MAGIC_TYPE_UNKNOWN)
