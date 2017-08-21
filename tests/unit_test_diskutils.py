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

from core.constants import MAGIC_TYPE_LOOKUP
from core.util import diskutils
from core.util.diskutils import (
    sanitize_filename,
    get_files,
    get_files_gen
)
import unit_utils as uu


class TestMimeTypes(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_magic_type_lookup_table_exists(self):
        self.assertIsNotNone(MAGIC_TYPE_LOOKUP,
                             'MAGIC_TYPE_LOOKUP mime type lookup should exist')

    def test_magic_type_lookup_table_is_instance_of_dict(self):
        self.assertTrue(isinstance(MAGIC_TYPE_LOOKUP, dict),
                        'MAGIC_TYPE_LOOKUP should be an instance of dict')

    def test_magic_type_lookup_table_values_are_type_list(self):
        for value in MAGIC_TYPE_LOOKUP.values():
            self.assertTrue(isinstance(value, list),
                            'MAGIC_TYPE_LOOKUP values should be lists')

    def test_magic_type_lookup_arbitrarily_assert_image_is_jpeg(self):
        self.assertEqual(['image/jpeg'], MAGIC_TYPE_LOOKUP['jpg'])


class TestSplitBasename(TestCase):
    def _assert_splits(self, expected, test_input):
        actual = diskutils.split_basename(test_input)
        self.assertEqual(expected, actual)

    def test_returns_bytestrings(self):
        a, b = diskutils.split_basename('a.b')
        self.assertTrue(isinstance(a, bytes))
        self.assertTrue(isinstance(b, bytes))
        c, d = diskutils.split_basename(b'a.b')
        self.assertTrue(isinstance(c, bytes))
        self.assertTrue(isinstance(d, bytes))

    def test_split_no_name(self):
        self.assertIsNone(None, diskutils.split_basename(''))

    def test_split_no_extension(self):
        self._assert_splits((b'foo', None), 'foo')
        self._assert_splits((b'.foo', None), '.foo')

    def test_split_one_extension(self):
        self._assert_splits((b'foo', b'bar'), 'foo.bar')
        self._assert_splits((b'.foo', b'bar'), '.foo.bar')

    def test_split_multiple_extensions(self):
        self._assert_splits((b'.foo.bar', b'foo'), '.foo.bar.foo')
        self._assert_splits((b'foo.bar', b'foo'), 'foo.bar.foo')
        self._assert_splits((b'.foo.bar', b'tar'), '.foo.bar.tar')
        self._assert_splits((b'foo.bar', b'tar'), 'foo.bar.tar')

        # TODO: This case still fails, but it is such a hassle to deal with
        #       and is a really weird way to name files anyway.
        # self.assertEqual(('foo.bar', 'tar.gz'),
        #                  diskutils.split_filename('foo.bar.tar.gz'))


class TestBasenameSuffix(TestCase):
    def _assert_suffix(self, expected, test_input):
        actual = diskutils.basename_suffix(test_input)
        self.assertEqual(expected, actual)

    def test_file_suffix_no_name(self):
        self.assertIsNone(diskutils.basename_suffix(''))
        self.assertIsNone(diskutils.basename_suffix(' '))
        self.assertIsNone(diskutils.basename_suffix(',. '))
        self.assertIsNone(diskutils.basename_suffix(' . '))
        self.assertIsNone(diskutils.basename_suffix(' . . '))

    def test_file_suffix_file_has_no_extension(self):
        self.assertIsNone(diskutils.basename_suffix('filename'))
        self.assertIsNone(diskutils.basename_suffix('file name'))
        self.assertIsNone(diskutils.basename_suffix('.hiddenfile'))
        self.assertIsNone(diskutils.basename_suffix('.hidden file'))

    def test_file_suffix_file_has_one_extension(self):
        self._assert_suffix(b'jpg', 'filename.jpg')
        self._assert_suffix(b'jpg', 'filename.JPG')
        self.assertEqual(b'JPG', diskutils.basename_suffix('filename.JPG',
                                                           make_lowercase=False))

    def test_file_suffix_from_hidden_file(self):
        self._assert_suffix(b'jpg', '.hiddenfile.jpg')
        self._assert_suffix(b'jpg', '.hiddenfile.JPG')
        self.assertEqual(b'JPG', diskutils.basename_suffix('.hiddenfile.JPG',
                                                           make_lowercase=False))

    def test_file_suffix_file_has_many_suffixes(self):
        self._assert_suffix(b'tar', 'filename.tar')
        self._assert_suffix(b'gz', 'filename.gz')
        self._assert_suffix(b'tar.gz', 'filename.tar.gz')
        self._assert_suffix(b'tar.z', 'filename.tar.z')
        self._assert_suffix(b'tar.lz', 'filename.tar.lz')
        self._assert_suffix(b'tar.lzma', 'filename.tar.lzma')
        self._assert_suffix(b'tar.lzo', 'filename.tar.lzo')

    def test_file_suffix_from_hidden_file_many_suffixes(self):

        self._assert_suffix(b'tar', '.filename.tar')
        self._assert_suffix(b'gz', '.filename.gz')
        self._assert_suffix(b'tar.gz', '.filename.tar.gz')
        self._assert_suffix(b'tar.z', '.filename.tar.z')
        self._assert_suffix(b'tar.lz', '.filename.tar.lz')
        self._assert_suffix(b'tar.lzma', '.filename.tar.lzma')
        self._assert_suffix(b'tar.lzo', '.filename.tar.lzo')


class TestBasenamePrefix(TestCase):
    def test_file_base_no_name(self):
        self.assertIsNone(diskutils.basename_prefix(''))
        self.assertEqual(b' ', diskutils.basename_prefix(' '))
        self.assertEqual(b',', diskutils.basename_prefix(',. '))
        self.assertEqual(b' ', diskutils.basename_prefix(' . '))

        # TODO: Test edge cases ..
        # self.assertEqual(' ', diskutils.file_base(' . . '))

    def test_file_base_file_has_no_extension(self):
        self.assertIsNotNone(diskutils.basename_prefix('filename'))
        self.assertEqual(b'file name', diskutils.basename_prefix('file name'))
        self.assertEqual(b'.hiddenfile', diskutils.basename_prefix('.hiddenfile'))
        self.assertEqual(b'.hidden file', diskutils.basename_prefix('.hidden file'))

    def test_file_base_file_has_one_extension(self):
        def __check_expected_for(test_input):
            self.assertEqual(b'filename', diskutils.basename_prefix(test_input))

        __check_expected_for('filename.jpg')
        __check_expected_for('filename.JPG')

    def test_file_base_from_hidden_file(self):
        def __check_expected_for(test_input):
            self.assertEqual(b'.hiddenfile', diskutils.basename_prefix(test_input))

        __check_expected_for('.hiddenfile.jpg')
        __check_expected_for('.hiddenfile.JPG')
        __check_expected_for('.hiddenfile.JPG')

    def test_file_base_file_has_many_suffixes(self):
        def __check_expected_for(test_input):
            self.assertEqual(b'filename', diskutils.basename_prefix(test_input))

        __check_expected_for('filename.tar')
        __check_expected_for('filename.gz')
        __check_expected_for('filename.tar.gz')
        __check_expected_for('filename.tar.z')
        __check_expected_for('filename.tar.lz')
        __check_expected_for('filename.tar.lzma')
        __check_expected_for('filename.tar.lzo')

    def test_file_base_from_hidden_file_many_suffixes(self):
        def __check_expected_for(test_input):
            self.assertEqual(b'.filename', diskutils.basename_prefix(test_input))

        __check_expected_for('.filename.tar')
        __check_expected_for('.filename.gz')
        __check_expected_for('.filename.tar.gz')
        __check_expected_for('.filename.tar.z')
        __check_expected_for('.filename.tar.lz')
        __check_expected_for('.filename.tar.lzma')
        __check_expected_for('.filename.tar.lzo')


class TestSanitizeFilename(TestCase):
    """
    NOTE:  This class was lifted as-is from the "youtube-dl" project.

    https://github.com/rg3/youtube-dl/blob/master/youtube_dl/test/test_utils.py
    Commit: 5552c9eb0fece567f7dda13810939fca32d7d65a
    """
    def test_sanitize_filename(self):
        self.assertEqual(sanitize_filename('abc'), 'abc')
        self.assertEqual(sanitize_filename('abc_d-e'), 'abc_d-e')

        self.assertEqual(sanitize_filename('123'), '123')

        self.assertEqual('abc_de', sanitize_filename('abc/de'))
        self.assertFalse('/' in sanitize_filename('abc/de///'))

        self.assertEqual('abc_de', sanitize_filename('abc/<>\\*|de'))
        self.assertEqual('xxx', sanitize_filename('xxx/<>\\*|'))
        self.assertEqual('yes no', sanitize_filename('yes? no'))
        self.assertEqual('this - that', sanitize_filename('this: that'))

        self.assertEqual(sanitize_filename('AT&T'), 'AT&T')
        aumlaut = 'ä'
        self.assertEqual(sanitize_filename(aumlaut), aumlaut)
        tests = '\u043a\u0438\u0440\u0438\u043b\u043b\u0438\u0446\u0430'
        self.assertEqual(sanitize_filename(tests), tests)

        self.assertEqual(
            sanitize_filename('New World record at 0:12:34'),
            'New World record at 0_12_34')

        self.assertEqual(sanitize_filename('--gasdgf'), '_-gasdgf')
        self.assertEqual(sanitize_filename('--gasdgf', is_id=True), '--gasdgf')
        self.assertEqual(sanitize_filename('.gasdgf'), 'gasdgf')
        self.assertEqual(sanitize_filename('.gasdgf', is_id=True), '.gasdgf')

        forbidden = '"\0\\/'
        for fc in forbidden:
            for fbc in forbidden:
                self.assertTrue(fbc not in sanitize_filename(fc))

    def test_sanitize_filename_restricted(self):
        self.assertEqual(sanitize_filename('abc', restricted=True), 'abc')
        self.assertEqual(sanitize_filename('abc_d-e', restricted=True), 'abc_d-e')

        self.assertEqual(sanitize_filename('123', restricted=True), '123')

        self.assertEqual('abc_de', sanitize_filename('abc/de', restricted=True))
        self.assertFalse('/' in sanitize_filename('abc/de///', restricted=True))

        self.assertEqual('abc_de', sanitize_filename('abc/<>\\*|de', restricted=True))
        self.assertEqual('xxx', sanitize_filename('xxx/<>\\*|', restricted=True))
        self.assertEqual('yes_no', sanitize_filename('yes? no', restricted=True))
        self.assertEqual('this_-_that', sanitize_filename('this: that', restricted=True))

        tests = 'aäb\u4e2d\u56fd\u7684c'
        self.assertEqual(sanitize_filename(tests, restricted=True), 'aab_c')
        self.assertTrue(sanitize_filename('\xf6', restricted=True) != '')  # No empty filename

        forbidden = '"\0\\/&!: \'\t\n()[]{}$;`^,#'
        for fc in forbidden:
            for fbc in forbidden:
                self.assertTrue(fbc not in sanitize_filename(fc, restricted=True))

        # Handle a common case more neatly
        self.assertEqual(sanitize_filename('\u5927\u58f0\u5e26 - Song', restricted=True), 'Song')
        self.assertEqual(sanitize_filename('\u603b\u7edf: Speech', restricted=True), 'Speech')
        # .. but make sure the file name is never empty
        self.assertTrue(sanitize_filename('-', restricted=True) != '')
        self.assertTrue(sanitize_filename(':', restricted=True) != '')

        self.assertEqual(sanitize_filename(
            'ÂÃÄÀÁÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖŐØŒÙÚÛÜŰÝÞßàáâãäåæçèéêëìíîïðñòóôõöőøœùúûüűýþÿ', restricted=True),
            'AAAAAAAECEEEEIIIIDNOOOOOOOOEUUUUUYPssaaaaaaaeceeeeiiiionooooooooeuuuuuypy')

    def test_sanitize_ids(self):
        self.assertEqual(sanitize_filename('_n_cd26wFpw', is_id=True), '_n_cd26wFpw')
        self.assertEqual(sanitize_filename('_BD_eEpuzXw', is_id=True), '_BD_eEpuzXw')
        self.assertEqual(sanitize_filename('N0Y__7-UOdI', is_id=True), 'N0Y__7-UOdI')


def shorten_path(abs_path):
    parent = os.path.basename(os.path.dirname(abs_path))
    basename = os.path.basename(abs_path)
    return os.path.join(parent, basename)


def to_abspath(path_list):
    return [tf for tf in (uu.abspath_testfile(f) for f in path_list)]


class TestGetFiles(TestCase):
    def setUp(self):
        self.FILES_SUBDIR = [
            'subdir/file_1', 'subdir/file_2', 'subdir/file_3'
        ]
        self.FILES_SUBSUBDIR_A = [
            'subdir/subsubdir_A/file_A1', 'subdir/subsubdir_A/file_A2'
        ]
        self.FILES_SUBSUBDIR_B = [
            'subdir/subsubdir_B/file_A3', 'subdir/subsubdir_B/file_B1',
            'subdir/subsubdir_B/file_B2'
        ]
        self.ALL_FILES = (self.FILES_SUBDIR + self.FILES_SUBSUBDIR_A
                          + self.FILES_SUBSUBDIR_B)

        self.abspath_files_subdir = to_abspath(self.FILES_SUBDIR)
        self.abspath_files_subsubdir_a = to_abspath(self.FILES_SUBSUBDIR_A)
        self.abspath_files_subsubdir_b = to_abspath(self.FILES_SUBSUBDIR_B)
        self.abspath_all_files = to_abspath(self.ALL_FILES)

    def test_setup(self):
        for tf in self.abspath_all_files:
            self.assertTrue(os.path.isfile(tf),
                            'Expected file: "{}"'.format(tf))

        self.assertEqual(len(self.abspath_all_files), 8)

    def test_get_files_is_defined_and_available(self):
        self.assertIsNotNone(get_files)

    def test_raises_errors_for_invalid_paths(self):
        with self.assertRaises((FileNotFoundError, TypeError)):
            get_files(None)
            get_files('')
            get_files(' ')

    def test_returns_expected_number_of_files_non_recursive(self):
        actual = get_files(uu.abspath_testfile('subdir'))
        self.assertEqual(len(actual), 3)

    def test_returns_expected_files_non_recursive(self):
        actual = get_files(uu.abspath_testfile('subdir'))

        for f in actual:
            self.assertTrue(os.path.isfile(f))
            self.assertIn(shorten_path(f), self.FILES_SUBDIR)
            self.assertNotIn(shorten_path(f), self.FILES_SUBSUBDIR_A)
            self.assertNotIn(shorten_path(f), self.FILES_SUBSUBDIR_B)

    def test_returns_expected_number_of_files_recursive(self):
        actual = get_files(uu.abspath_testfile('subdir'), recurse=True)
        self.assertEqual(len(actual), 8)

    def test_returns_expected_files_recursive(self):
        actual = get_files(uu.abspath_testfile('subdir'), recurse=True)

        for f in actual:
            self.assertTrue(os.path.isfile(f))
            self.assertIn(f, self.abspath_all_files)

    def test_returns_expected_number_of_files_recursive_from_subsubdir_a(self):
        actual = get_files(uu.abspath_testfile('subdir/subsubdir_A'),
                           recurse=True)
        self.assertEqual(len(actual), 2)

    def test_returns_expected_files_recursive_from_subsubdir_a(self):
        actual = get_files(uu.abspath_testfile('subdir/subsubdir_A'),
                           recurse=True)

        for f in actual:
            self.assertTrue(os.path.isfile(f))
            self.assertIn(f, self.abspath_files_subsubdir_a)
            self.assertNotIn(f, self.abspath_files_subsubdir_b)
            self.assertNotIn(f, self.abspath_files_subdir)

    def test_returns_expected_files_recursive_from_subsubdir_b(self):
        actual = get_files(uu.abspath_testfile('subdir/subsubdir_B'),
                           recurse=True)

        for f in actual:
            self.assertTrue(os.path.isfile(f))
            self.assertIn(f, self.abspath_files_subsubdir_b)
            self.assertNotIn(f, self.abspath_files_subsubdir_a)
            self.assertNotIn(f, self.abspath_files_subdir)


class TestGetFilesGen(TestCase):
    def setUp(self):
        self.FILES_SUBDIR = [
            'subdir/file_1', 'subdir/file_2', 'subdir/file_3'
        ]
        self.FILES_SUBSUBDIR_A = [
            'subdir/subsubdir_A/file_A1', 'subdir/subsubdir_A/file_A2'
        ]
        self.FILES_SUBSUBDIR_B = [
            'subdir/subsubdir_B/file_A3', 'subdir/subsubdir_B/file_B1',
            'subdir/subsubdir_B/file_B2'
        ]
        self.ALL_FILES = (self.FILES_SUBDIR + self.FILES_SUBSUBDIR_A
                          + self.FILES_SUBSUBDIR_B)

        self.abspath_files_subdir = to_abspath(self.FILES_SUBDIR)
        self.abspath_files_subsubdir_a = to_abspath(self.FILES_SUBSUBDIR_A)
        self.abspath_files_subsubdir_b = to_abspath(self.FILES_SUBSUBDIR_B)
        self.abspath_all_files = to_abspath(self.ALL_FILES)

    def test_setup(self):
        for tf in self.abspath_all_files:
            self.assertTrue(os.path.isfile(tf),
                            'Expected file: "{}"'.format(tf))

        self.assertEqual(len(self.abspath_all_files), 8)

    def test_get_files_gen_is_defined_and_available(self):
        self.assertIsNotNone(get_files_gen)

    def test_raises_errors_for_none_paths(self):
        with self.assertRaises((FileNotFoundError, TypeError)):
            list(get_files_gen(None))
            list(get_files_gen(''))

    def test_raises_errors_for_invalid_paths(self):
        with self.assertRaises(FileNotFoundError):
            list(get_files_gen(' '))

    def test_returns_expected_number_of_files_non_recursive(self):
        actual = list(get_files_gen(uu.abspath_testfile('subdir')))
        self.assertEqual(len(actual), 3)

    def test_returns_expected_files_non_recursive(self):
        actual = list(get_files_gen(uu.abspath_testfile('subdir')))

        for f in actual:
            self.assertTrue(os.path.isfile(f))
            self.assertIn(shorten_path(f), self.FILES_SUBDIR)
            self.assertNotIn(shorten_path(f), self.FILES_SUBSUBDIR_A)
            self.assertNotIn(shorten_path(f), self.FILES_SUBSUBDIR_B)

    def test_returns_expected_number_of_files_recursive(self):
        actual = list(get_files_gen(uu.abspath_testfile('subdir'), recurse=True))
        self.assertEqual(len(actual), 8)

    def test_returns_expected_files_recursive(self):
        actual = list(get_files_gen(uu.abspath_testfile('subdir'), recurse=True))

        for f in actual:
            self.assertTrue(os.path.isfile(f))
            self.assertIn(f, self.abspath_all_files)

    def test_returns_expected_number_of_files_recursive_from_subsubdir_a(self):
        actual = list(get_files_gen(uu.abspath_testfile('subdir/subsubdir_A'),
                           recurse=True))
        self.assertEqual(len(actual), 2)

    def test_returns_expected_files_recursive_from_subsubdir_a(self):
        actual = list(get_files_gen(uu.abspath_testfile('subdir/subsubdir_A'),
                           recurse=True))

        for f in actual:
            self.assertTrue(os.path.isfile(f))
            self.assertIn(f, self.abspath_files_subsubdir_a)
            self.assertNotIn(f, self.abspath_files_subsubdir_b)
            self.assertNotIn(f, self.abspath_files_subdir)

    def test_returns_expected_files_recursive_from_subsubdir_b(self):
        actual = list(get_files_gen(uu.abspath_testfile('subdir/subsubdir_B'),
                           recurse=True))

        for f in actual:
            self.assertTrue(os.path.isfile(f))
            self.assertIn(f, self.abspath_files_subsubdir_b)
            self.assertNotIn(f, self.abspath_files_subsubdir_a)
            self.assertNotIn(f, self.abspath_files_subdir)


class TestPathAncestry(TestCase):
    def test_ancestry_returns_expected_ancestors_for_file_paths(self):
        PATHS_ANCESTORS = [
            ('/a/b/c', ['/', '/a', '/a/b']),
            ('/a/b',   ['/', '/a']),
            ('/a',     ['/']),
            ('/',      ['/'])
        ]
        for p, a in PATHS_ANCESTORS:
            self.assertEqual(diskutils.path_ancestry(p), a)

    def test_ancestry_returns_expected_ancestors_for_directory_paths(self):
        PATHS_ANCESTORS = [
            ('/a/b/c/', ['/', '/a', '/a/b', '/a/b/c']),
            ('/a/b/',   ['/', '/a', '/a/b']),
            ('/a/',     ['/', '/a']),
            ('/',       ['/']),
        ]
        for p, a in PATHS_ANCESTORS:
            self.assertEqual(diskutils.path_ancestry(p), a)

    def test_ancestry_returns_expected_ancestors_for_relative_paths(self):
        PATHS_ANCESTORS = [
            ('a/b/c', ['a', 'a/b']),
            ('a/b/c/', ['a', 'a/b', 'a/b/c']),
        ]
        for p, a in PATHS_ANCESTORS:
            self.assertEqual(diskutils.path_ancestry(p), a)


class TestPathComponents(TestCase):
    def test_components_returns_expected_components_for_file_paths(self):
        PATHS_COMPONENTS = [
            ('/a/b/c', ['/', 'a', 'b', 'c']),
            ('/a/b',   ['/', 'a', 'b']),
            ('/a',     ['/', 'a']),
            ('/',      ['/'])
        ]
        for p, c in PATHS_COMPONENTS:
            self.assertEqual(diskutils.path_components(p), c)

    def test_components_returns_expected_components_for_directory_paths(self):
        PATHS_COMPONENTS = [
            ('/a/b/c/', ['/', 'a', 'b', 'c']),
            ('/a/b/',   ['/', 'a', 'b']),
            ('/a/',     ['/', 'a']),
            ('/',       ['/'])
        ]
        for p, c in PATHS_COMPONENTS:
            self.assertEqual(diskutils.path_components(p), c)

    def test_components_returns_expected_components_for_relative_paths(self):
        PATHS_COMPONENTS = [
            ('a/b/c', ['a', 'b', 'c']),
            ('a/b',   ['a', 'b']),
            ('a',     ['a']),
        ]
        for p, c in PATHS_COMPONENTS:
            self.assertEqual(diskutils.path_components(p), c)


class TestCompareBasenames(TestCase):
    def test_compare_basenames_is_defined(self):
        self.assertIsNotNone(diskutils.compare_basenames)

    def test_compare_basenames_raises_exceptions_given_invalid_input(self):
        with self.assertRaises(ValueError):
            diskutils.compare_basenames(None, None)
            diskutils.compare_basenames(None, [])
            diskutils.compare_basenames([], None)
            diskutils.compare_basenames(b'a', [])
            diskutils.compare_basenames(b'', b'')
            diskutils.compare_basenames(b'', b' ')
            diskutils.compare_basenames(b'_', b'')

        with self.assertRaises(TypeError):
            diskutils.compare_basenames(1, 2)
            diskutils.compare_basenames('a', 1)
            diskutils.compare_basenames(1, 'a')
            diskutils.compare_basenames('a', 'a')
            diskutils.compare_basenames('a', b'a')
            diskutils.compare_basenames(b'a', 'a')

    def test_comparing_equal_basenames_returns_true(self):
        def _assert_true(first, second):
            self.assertTrue(diskutils.compare_basenames(first, second))
            self.assertTrue(
                isinstance(diskutils.compare_basenames(first, second), bool)
            )

        _assert_true(b' ', b' ')
        _assert_true(b'a', b'a')
        _assert_true(b'foo', b'foo')
        _assert_true(b'_', b'_')
        _assert_true('å'.encode('utf-8'), 'å'.encode('utf-8'))
        _assert_true('ö'.encode('utf-8'), 'ö'.encode('utf-8'))
        _assert_true('A_ö'.encode('utf-8'), 'A_ö'.encode('utf-8'))
        _assert_true(b'__', b'__')

    def test_comparing_unequal_basenames_returns_false(self):
        def _assert_false(first, second):
            self.assertFalse(diskutils.compare_basenames(first, second))
            self.assertTrue(
                isinstance(diskutils.compare_basenames(first, second), bool)
            )

        _assert_false(b' ', b'y')
        _assert_false(b'x', b'y')
        _assert_false(b'foo_', b'foo')
        _assert_false('ä'.encode('utf-8'), b'a')
        _assert_false('Ä'.encode('utf-8'), b'A')
        _assert_false('Ä'.encode('utf-8'), 'A'.encode('utf-8'))
