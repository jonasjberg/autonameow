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

from core import (
    fileobject,
    util
)
from core import constants as C
from core.exceptions import InvalidFileArgumentError
import unit_utils as uu


class TestFileObjectTypes(TestCase):
    def setUp(self):
        self.fo = uu.get_named_fileobject('20160722 Descriptive name.txt')

    def test_internal_bytestring_path_type_abspath(self):
        self.assertTrue(uu.is_internalbytestring(self.fo.abspath))

    def test_internal_bytestring_path_type_suffix(self):
        self.assertTrue(uu.is_internalbytestring(self.fo.basename_suffix))

    def test_internal_bytestring_path_type_filename(self):
        self.assertTrue(uu.is_internalbytestring(self.fo.filename))

    def test_internal_bytestring_path_type_basename_prefix(self):
        self.assertTrue(uu.is_internalbytestring(self.fo.basename_prefix))

    def test_internal_bytestring_path_type_pathname(self):
        self.assertTrue(uu.is_internalbytestring(self.fo.pathname))

    def test_internal_bytestring_path_type_pathparent(self):
        self.assertTrue(uu.is_internalbytestring(self.fo.pathparent))

    def test_internal_type_mime_type(self):
        self.assertTrue(uu.is_internalstring(self.fo.mime_type))

    def test_internal_type_str(self):
        self.assertTrue(uu.is_internalstring(str(self.fo)))

    def test_bytesize_is_integer(self):
        self.assertTrue(isinstance(self.fo.bytesize, int))


class TestFileObjectEquivalence(TestCase):
    def setUp(self):
        self.fo_unique = uu.get_mock_fileobject(mime_type='image/png')
        self.fo_dupe_1 = uu.get_mock_fileobject(mime_type='text/plain')
        self.fo_dupe_2 = uu.get_mock_fileobject(mime_type='text/plain')

    def test_setup(self):
        self.assertTrue(uu.file_exists(self.fo_unique.abspath))
        self.assertTrue(uu.file_exists(self.fo_dupe_1.abspath))

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

    def test_fileobject_as_dictionary_key(self):
        d = {self.fo_unique: 'a',
             self.fo_dupe_1: 'b',
             self.fo_dupe_2: 'c'}

        self.assertEqual(len(d), 2)
        self.assertEqual(d.get(self.fo_unique), 'a')
        self.assertEqual(d.get(self.fo_dupe_1), 'c')
        self.assertEqual(d.get(self.fo_dupe_2), 'c')


class TestFileTypeMagic(TestCase):
    TEST_FILES = [('magic_bmp.bmp', 'image/x-ms-bmp'),
                  ('magic_gif.gif', 'image/gif'),
                  ('magic_jpg.jpg', 'image/jpeg'),
                  ('magic_mp4.mp4', 'video/mp4'),
                  ('magic_pdf.pdf', 'application/pdf'),
                  ('magic_png.png', 'image/png'),
                  ('magic_txt',     'text/plain'),
                  ('magic_txt.md',  'text/plain'),
                  ('magic_txt.txt', 'text/plain')]

    def setUp(self):
        self.test_files = [
            (uu.abspath_testfile(basename), expect_mime)
            for basename, expect_mime in self.TEST_FILES
        ]

    def test_test_files_exist_and_are_readable(self):
        for test_file, _ in self.test_files:
            self.assertTrue(uu.file_exists(test_file))
            self.assertTrue(uu.path_is_readable(test_file))

    def test_filetype_magic(self):
        for test_file, expected_mime in self.test_files:
            actual = fileobject.filetype_magic(test_file)
            self.assertEqual(expected_mime, actual)

    def test_filetype_magic_with_invalid_args(self):
        self.assertEqual(fileobject.filetype_magic(None),
                         C.MAGIC_TYPE_UNKNOWN)


class TestValidatePathArgument(TestCase):
    def setUp(self):
        _num_files = min(len(uu.all_testfiles()), 5)
        self.unicode_paths = uu.all_testfiles()[:_num_files]
        self.bytestr_paths = [
            util.bytestring_path(p) for p in uu.all_testfiles()[:_num_files]
        ]

    def test_setup(self):
        for upath in self.unicode_paths:
            self.assertTrue(uu.file_exists(upath))
            self.assertTrue(uu.is_internalstring(upath))

        for bpath in self.bytestr_paths:
            self.assertTrue(uu.file_exists(bpath))
            self.assertTrue(uu.is_internalbytestring(bpath))

    def test_valid_unicode_paths(self):
        for upath in self.unicode_paths:
            fileobject.validate_path_argument(upath)

    def test_valid_bytes_paths(self):
        for bpath in self.bytestr_paths:
            fileobject.validate_path_argument(bpath)

    def test_invalid_paths(self):
        def _assert_raises(test_data):
            with self.assertRaises(InvalidFileArgumentError):
                fileobject.validate_path_argument(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises(' ')
        _assert_raises('  ')
        _assert_raises(b'')
        _assert_raises(b' ')
        _assert_raises(b'  ')
        _assert_raises([])
        _assert_raises({})
