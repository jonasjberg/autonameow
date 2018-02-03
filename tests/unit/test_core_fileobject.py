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
import unittest
from unittest import TestCase

import unit.constants as uuconst
import unit.utils as uu
from core.exceptions import InvalidFileArgumentError
from core.fileobject import (
    _validate_path_argument,
    FileObject
)
from util import encoding as enc


class TestFileObject(TestCase):
    def test_raises_assertion_error_given_none_path(self):
        with self.assertRaises(AssertionError):
            _ = FileObject(None)

    def test_raises_assertion_error_given_unicode_string_path(self):
        with self.assertRaises(AssertionError):
            _ = FileObject('foo')

    def test_raises_exception_given_path_to_non_existent_file(self):
        with self.assertRaises(InvalidFileArgumentError):
            _ = FileObject(uuconst.ASSUMED_NONEXISTENT_BASENAME)


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
        self.assertIsInstance(self.fo.bytesize, int)


class TestFileObject(TestCase):
    def setUp(self):
        self.fo = uu.fileobject_testfile('magic_txt.txt')

    def test_abspath(self):
        actual = self.fo.abspath
        self.assertTrue(uu.file_exists(actual))
        self.assertTrue(uu.is_abspath(uu.normpath(actual)))
        self.assertTrue(uu.is_abspath(actual))

    def test_basename_suffix(self):
        actual = self.fo.basename_suffix
        expect = b'txt'
        self.assertEqual(actual, expect)

    def test_basename_prefix(self):
        actual = self.fo.basename_prefix
        expect = b'magic_txt'
        self.assertEqual(actual, expect)

    def test_filename(self):
        actual = self.fo.filename
        expect = b'magic_txt.txt'
        self.assertEqual(actual, expect)

    def test_pathname(self):
        actual = self.fo.pathname
        expect = uu.normpath(uuconst.TEST_FILES_DIR)
        self.assertEqual(actual, expect)

    def test_pathparent(self):
        actual = self.fo.pathparent
        expect = uu.encode(os.path.basename(os.path.normpath(
            enc.syspath(uuconst.TEST_FILES_DIR)
        )))
        self.assertEqual(actual, expect)

    def test_mime_type(self):
        actual = self.fo.mime_type
        expect = 'text/plain'
        self.assertEqual(actual, expect)

    def test_bytesize(self):
        actual = self.fo.bytesize
        expect = 5
        self.assertEqual(actual, expect)

    def test_hash_partial(self):
        actual = self.fo.hash_partial
        expect = 'b9e68e1bea3e5b19ca6b2f98b73a54b73daafaa250484902e09982e07a12e733'
        self.assertEqual(actual, expect)


class TestFileObjectEquivalence(TestCase):
    def setUp(self):
        self.fo_unique = uu.get_mock_fileobject(mime_type='image/png')
        self.fo_dupe_1 = uu.get_mock_fileobject(mime_type='text/plain')
        self.fo_dupe_2 = uu.get_mock_fileobject(mime_type='text/plain')

    def test_setup(self):
        self.assertTrue(uu.file_exists(self.fo_unique.abspath))
        self.assertTrue(uu.file_exists(self.fo_dupe_1.abspath))
        self.assertTrue(uu.file_exists(self.fo_dupe_2.abspath))

    def test_equivalence_expect_unequal(self):
        self.assertNotEqual(self.fo_unique, self.fo_dupe_1)
        self.assertNotEqual(self.fo_unique, self.fo_dupe_2)

    def test_equivalence_expect_equal(self):
        self.assertEqual(self.fo_dupe_1, self.fo_dupe_2)


class TestFileObjectHash(TestCase):
    def setUp(self):
        self.fo_unique = uu.get_mock_fileobject(mime_type='image/png')
        self.fo_dupe_1 = uu.get_mock_fileobject(mime_type='text/plain')
        self.fo_dupe_2 = uu.get_mock_fileobject(mime_type='text/plain')

    def test_setup(self):
        self.assertTrue(uu.file_exists(self.fo_unique.abspath))
        self.assertTrue(uu.file_exists(self.fo_dupe_1.abspath))
        self.assertTrue(uu.file_exists(self.fo_dupe_2.abspath))

    def test_hash_expect_unequal(self):
        a = hash(self.fo_unique)
        b = hash(self.fo_dupe_1)
        c = hash(self.fo_dupe_2)
        self.assertNotEqual(a, b)
        self.assertNotEqual(a, c)

    def test_hash_expect_equal(self):
        b = hash(self.fo_dupe_1)
        c = hash(self.fo_dupe_2)
        self.assertEqual(b, c)


class TestFileObjectMembership(TestCase):
    def setUp(self):
        self.fo_unique = uu.get_mock_fileobject(mime_type='image/png')
        self.fo_dupe_1 = uu.get_mock_fileobject(mime_type='text/plain')
        self.fo_dupe_2 = uu.get_mock_fileobject(mime_type='text/plain')

    def test_setup(self):
        self.assertTrue(uu.file_exists(self.fo_unique.abspath))
        self.assertTrue(uu.file_exists(self.fo_dupe_1.abspath))
        self.assertTrue(uu.file_exists(self.fo_dupe_2.abspath))

    def test_fileobject_as_dictionary_key(self):
        d = {self.fo_unique: 'a',
             self.fo_dupe_1: 'b',
             self.fo_dupe_2: 'c'}

        self.assertEqual(len(d), 2)
        self.assertEqual(d.get(self.fo_unique), 'a')
        self.assertEqual(d.get(self.fo_dupe_1), 'c')
        self.assertEqual(d.get(self.fo_dupe_2), 'c')

    def test_membership_with_same(self):
        s = set()
        s.add(self.fo_unique)
        self.assertEqual(len(s), 1)
        s.add(self.fo_unique)
        self.assertEqual(len(s), 1)

    def test_membership_with_duplicates(self):
        s = set()
        s.add(self.fo_dupe_1)
        self.assertEqual(len(s), 1)
        s.add(self.fo_dupe_2)
        self.assertEqual(len(s), 1)

    def test_membership_with_different(self):
        s = set()
        s.add(self.fo_unique)
        self.assertEqual(len(s), 1)
        s.add(self.fo_dupe_1)
        self.assertEqual(len(s), 2)
        s.add(self.fo_dupe_2)
        self.assertEqual(len(s), 2)


@unittest.skip('TODO: [TD0026] Implement safe handling of symlinks.')
class TestFileObjectFromSymlink(TestCase):
    def setUp(self):
        self.fo_orig = uu.fileobject_testfile('empty')
        self.fo_link = uu.fileobject_testfile('empty.symlink')

    def test_setup(self):
        self.assertIsNotNone(self.fo_orig)
        self.assertIsNotNone(self.fo_link)

        self.assertTrue(uu.file_exists(self.fo_orig.abspath))
        self.assertTrue(uu.file_exists(self.fo_link.abspath))

    def test_equality(self):
        # TODO: [TD0026] Should these be considered equal or not?
        self.assertNotEqual(self.fo_orig, self.fo_link)

    def test_membership(self):
        s = set()

        s.add(self.fo_orig)
        self.assertEqual(len(s), 1)

        s.add(self.fo_link)
        # TODO: [TD0026] Expect 1 or 2?
        self.assertEqual(len(s), 2)

        # TODO: [TD0026] Should this fail or not?
        self.assertIn(self.fo_orig, s)
        self.assertIn(self.fo_link, s)


class TestFileObjectHashWithEmptyTestFile(TestCase):
    def setUp(self):
        self.fo_a = uu.fileobject_testfile('empty')
        self.fo_b = uu.fileobject_testfile('empty')

    def test_same_file_returns_same_hash(self):
        hash_fo_a = hash(self.fo_a)
        hash_fo_b = hash(self.fo_b)
        self.assertEqual(hash_fo_a, hash_fo_b)


class TestFileObjectDoesNotHandleSymlinks(TestCase):
    # TODO: [TD0026] Implement safe handling of symlinks.
    def test_raises_exception_given_symlinks(self):
        with self.assertRaises(InvalidFileArgumentError):
            _ = uu.fileobject_testfile('empty.symlink')


class TestFileObjectOrdering(TestCase):
    def setUp(self):
        self.fo_1 = uu.fileobject_testfile('magic_pdf.pdf')
        self.fo_2 = uu.fileobject_testfile('magic_png.png')
        self.some_object = 'foo'

    def test_setup(self):
        self.assertTrue(uu.file_exists(self.fo_1.abspath))
        self.assertTrue(uu.file_exists(self.fo_2.abspath))

    def test_less_than_comparison(self):
        self.assertLess(self.fo_1, self.fo_2)
        # Objects of other types are always treated the same in comparisons.
        self.assertLess(self.some_object, self.fo_1)
        self.assertLess(self.some_object, self.fo_2)

    def test_greater_than_comparison(self):
        self.assertGreater(self.fo_2, self.fo_1)
        # Objects of other types are always treated the same in comparisons.
        self.assertGreater(self.fo_1, self.some_object)
        self.assertGreater(self.fo_2, self.some_object)

    def test_sorting(self):
        sorted_list = sorted([self.fo_1, self.fo_2])
        self.assertEqual(self.fo_1, sorted_list[0])
        self.assertEqual(self.fo_2, sorted_list[1])

        # Objects of other types are always treated the same in comparisons.
        sorted_list_with_another_object = sorted([self.fo_1, self.fo_2,
                                                  self.some_object])
        self.assertEqual(self.some_object, sorted_list_with_another_object[0])
        self.assertEqual(self.fo_1, sorted_list_with_another_object[1])
        self.assertEqual(self.fo_2, sorted_list_with_another_object[2])

    def test_sorting_reverse(self):
        sorted_list = sorted([self.fo_1, self.fo_2], reverse=True)
        self.assertEqual(self.fo_2, sorted_list[0])
        self.assertEqual(self.fo_1, sorted_list[1])

        # Objects of other types are always treated the same in comparisons.
        sorted_list_with_another_object = sorted(
            [self.fo_1, self.fo_2, self.some_object], reverse=True
        )
        self.assertEqual(self.fo_2, sorted_list_with_another_object[0])
        self.assertEqual(self.fo_1, sorted_list_with_another_object[1])
        self.assertEqual(self.some_object, sorted_list_with_another_object[2])


class TestValidatePathArgument(TestCase):
    def setUp(self):
        _num_files = min(len(uu.all_testfiles()), 5)
        self.unicode_paths = uu.all_testfiles()[:_num_files]
        self.bytestr_paths = [
            uu.bytestring_path(p)
            for p in uu.all_testfiles()[:_num_files]
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
            _validate_path_argument(upath)

    def test_valid_bytes_paths(self):
        for bpath in self.bytestr_paths:
            _validate_path_argument(bpath)

    def test_invalid_paths(self):
        def _assert_raises(test_data):
            with self.assertRaises(InvalidFileArgumentError):
                _validate_path_argument(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises(' ')
        _assert_raises('  ')
        _assert_raises(b'')
        _assert_raises(b' ')
        _assert_raises(b'  ')
        _assert_raises([])
        _assert_raises({})
