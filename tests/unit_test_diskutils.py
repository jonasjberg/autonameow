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

from core import (
    util,
    exceptions
)
from core.exceptions import EncodingBoundaryViolation
from core.util import diskutils
from core.util.diskutils import (
    sanitize_filename,
    get_files_gen
)
import unit_utils as uu


class TestSplitBasename(TestCase):
    def _assert_splits(self, expected, test_input):
        actual = diskutils.split_basename(test_input)
        self.assertEqual(expected, actual)

    def test_returns_bytestrings(self):
        c, d = diskutils.split_basename(b'c.d')
        self.assertTrue(isinstance(c, bytes))
        self.assertTrue(isinstance(d, bytes))

    def test_passing_unicode_strings_raises_assertion_error(self):
        with self.assertRaises(exceptions.EncodingBoundaryViolation):
            _, _ = diskutils.split_basename('a.b')

    def test_split_no_name(self):
        self.assertIsNone(None, diskutils.split_basename(b''))

    def test_split_no_extension(self):
        self._assert_splits((b'foo', None), b'foo')
        self._assert_splits((b'.foo', None), b'.foo')

    def test_split_one_extension(self):
        self._assert_splits((b'foo', b'bar'), b'foo.bar')
        self._assert_splits((b'.foo', b'bar'), b'.foo.bar')

    def test_split_multiple_extensions(self):
        self._assert_splits((b'.foo.bar', b'foo'), b'.foo.bar.foo')
        self._assert_splits((b'foo.bar', b'foo'), b'foo.bar.foo')
        self._assert_splits((b'.foo.bar', b'tar'), b'.foo.bar.tar')
        self._assert_splits((b'foo.bar', b'tar'), b'foo.bar.tar')

        # TODO: This case still fails, but it is such a hassle to deal with
        #       and is a really weird way to name files anyway.
        # self.assertEqual(('foo.bar', 'tar.gz'),
        #                  diskutils.split_filename('foo.bar.tar.gz'))


class TestBasenameSuffix(TestCase):
    def _assert_suffix(self, expected, test_input):
        actual = diskutils.basename_suffix(test_input)
        self.assertEqual(expected, actual)

    def test_no_name(self):
        self.assertIsNone(diskutils.basename_suffix(b''))
        self.assertIsNone(diskutils.basename_suffix(b' '))
        self.assertIsNone(diskutils.basename_suffix(b',. '))
        self.assertIsNone(diskutils.basename_suffix(b' . '))
        self.assertIsNone(diskutils.basename_suffix(b' . . '))

    def test_no_extension(self):
        self.assertIsNone(diskutils.basename_suffix(b'filename'))
        self.assertIsNone(diskutils.basename_suffix(b'file name'))
        self.assertIsNone(diskutils.basename_suffix(b'.hiddenfile'))
        self.assertIsNone(diskutils.basename_suffix(b'.hidden file'))

    def test_one_extension(self):
        self._assert_suffix(b'jpg', b'filename.jpg')
        self._assert_suffix(b'jpg', b'filename.JPG')
        self.assertEqual(
            b'JPG', diskutils.basename_suffix(b'filename.JPG',
                                              make_lowercase=False)
        )

    def test_hidden_file(self):
        self._assert_suffix(b'jpg', b'.hiddenfile.jpg')
        self._assert_suffix(b'jpg', b'.hiddenfile.JPG')
        self.assertEqual(
            b'JPG', diskutils.basename_suffix(b'.hiddenfile.JPG',
                                              make_lowercase=False)
        )

    def test_many_suffixes(self):
        self._assert_suffix(b'tar', b'filename.tar')
        self._assert_suffix(b'gz', b'filename.gz')
        self._assert_suffix(b'tar.gz', b'filename.tar.gz')
        self._assert_suffix(b'tar.z', b'filename.tar.z')
        self._assert_suffix(b'tar.lz', b'filename.tar.lz')
        self._assert_suffix(b'tar.lzma', b'filename.tar.lzma')
        self._assert_suffix(b'tar.lzo', b'filename.tar.lzo')

    def test_hidden_with_many_suffixes(self):
        self._assert_suffix(b'tar', b'.filename.tar')
        self._assert_suffix(b'gz', b'.filename.gz')
        self._assert_suffix(b'tar.gz', b'.filename.tar.gz')
        self._assert_suffix(b'tar.z', b'.filename.tar.z')
        self._assert_suffix(b'tar.lz', b'.filename.tar.lz')
        self._assert_suffix(b'tar.lzma', b'.filename.tar.lzma')
        self._assert_suffix(b'tar.lzo', b'.filename.tar.lzo')


class TestBasenamePrefix(TestCase):
    def test_no_name(self):
        self.assertIsNone(diskutils.basename_prefix(b''))
        self.assertEqual(b' ', diskutils.basename_prefix(b' '))
        self.assertEqual(b',', diskutils.basename_prefix(b',. '))
        self.assertEqual(b' ', diskutils.basename_prefix(b' . '))

        # TODO: Test edge cases ..
        # self.assertEqual(' ', diskutils.file_base(' . . '))

    def test_no_extension(self):
        self.assertIsNotNone(diskutils.basename_prefix(b'filename'))
        self.assertEqual(b'file name',
                         diskutils.basename_prefix(b'file name'))
        self.assertEqual(b'.hiddenfile',
                         diskutils.basename_prefix(b'.hiddenfile'))
        self.assertEqual(b'.hidden file',
                         diskutils.basename_prefix(b'.hidden file'))

    def test_one_extension(self):
        def __check_expected_for(test_input):
            self.assertEqual(b'filename', diskutils.basename_prefix(test_input))

        __check_expected_for(b'filename.jpg')
        __check_expected_for(b'filename.JPG')

    def test_hidden_file(self):
        def __check_expected_for(test_input):
            self.assertEqual(b'.hiddenfile',
                             diskutils.basename_prefix(test_input))

        __check_expected_for(b'.hiddenfile.jpg')
        __check_expected_for(b'.hiddenfile.JPG')
        __check_expected_for(b'.hiddenfile.JPG')

    def test_many_suffixes(self):
        def __check_expected_for(test_input):
            self.assertEqual(b'filename',
                             diskutils.basename_prefix(test_input))

        __check_expected_for(b'filename.tar')
        __check_expected_for(b'filename.gz')
        __check_expected_for(b'filename.tar.gz')
        __check_expected_for(b'filename.tar.z')
        __check_expected_for(b'filename.tar.lz')
        __check_expected_for(b'filename.tar.lzma')
        __check_expected_for(b'filename.tar.lzo')

    def test_hidden_with_many_suffixes(self):
        def __check_expected_for(test_input):
            self.assertEqual(b'.filename',
                             diskutils.basename_prefix(test_input))

        __check_expected_for(b'.filename.tar')
        __check_expected_for(b'.filename.gz')
        __check_expected_for(b'.filename.tar.gz')
        __check_expected_for(b'.filename.tar.z')
        __check_expected_for(b'.filename.tar.lz')
        __check_expected_for(b'.filename.tar.lzma')
        __check_expected_for(b'.filename.tar.lzo')


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
    paths = [util.bytestring_path(tf)
             for tf in (uu.abspath_testfile(f)
             for f in path_list)]
    if len(paths) == 1:
        return paths[0]
    else:
        return paths


FILES_SUBDIR = [
    'subdir/file_1', 'subdir/file_2', 'subdir/file_3'
]
FILES_SUBSUBDIR_A = [
    'subdir/subsubdir_A/file_A1', 'subdir/subsubdir_A/file_A2'
]
FILES_SUBSUBDIR_B = [
    'subdir/subsubdir_B/file_A3', 'subdir/subsubdir_B/file_B1',
    'subdir/subsubdir_B/file_B2'
]
FILES_ALL = (FILES_SUBDIR + FILES_SUBSUBDIR_A + FILES_SUBSUBDIR_B)
ABSPATH_FILES_SUBDIR = to_abspath(FILES_SUBDIR)
ABSPATH_FILES_SUBSUBDIR_A = to_abspath(FILES_SUBSUBDIR_A)
ABSPATH_FILES_SUBSUBDIR_B = to_abspath(FILES_SUBSUBDIR_B)
ABSPATH_FILES_ALL = to_abspath(FILES_ALL)
EXPECT_FILES_SUBDIR = [util.bytestring_path(p) for p in FILES_SUBDIR]
EXPECT_FILES_SUBSUBDIR_A = [util.bytestring_path(p) for p in FILES_SUBSUBDIR_A]
EXPECT_FILES_SUBSUBDIR_B = [util.bytestring_path(p) for p in FILES_SUBSUBDIR_B]


class TestTestFiles(TestCase):
    def test_all(self):
        for tf in ABSPATH_FILES_ALL:
            self.assertTrue(uu.file_exists(tf),
                            'Expected file: "{}"'.format(tf))
            self.assertTrue(isinstance(tf, bytes))

        self.assertEqual(len(ABSPATH_FILES_ALL), 8)

    def test_abspath_subdir(self):
        for tf in ABSPATH_FILES_SUBDIR:
            self.assertTrue(uu.file_exists(tf),
                            'Expected file: "{}"'.format(tf))
            self.assertTrue(isinstance(tf, bytes))

    def test_abspath_subsubdir_a(self):
        for tf in ABSPATH_FILES_SUBSUBDIR_A:
            self.assertTrue(uu.file_exists(tf),
                            'Expected file: "{}"'.format(tf))
            self.assertTrue(isinstance(tf, bytes))

    def test_abspath_subsubdir_b(self):
        for tf in ABSPATH_FILES_SUBSUBDIR_B:
            self.assertTrue(uu.file_exists(tf),
                            'Expected file: "{}"'.format(tf))
            self.assertTrue(isinstance(tf, bytes))


class TestGetFilesGen(TestCase):
    def test_raises_errors_for_none_paths(self):
        with self.assertRaises(FileNotFoundError):
            _ = list(get_files_gen(None))

    def test_raises_errors_for_invalid_paths(self):
        def _aR(test_input):
            with self.assertRaises(FileNotFoundError):
                _ = list(get_files_gen(test_input))

        _aR(b'')
        _aR(b' ')
        _aR(b'  ')
        _aR(b'x')
        _aR(b' x ')

    def test_returns_expected_number_of_files_non_recursive(self):
        actual = list(get_files_gen(to_abspath(['subdir'])))
        self.assertEqual(len(actual), 3)

    def test_returns_expected_files_non_recursive(self):
        actual = get_files_gen(to_abspath(['subdir']))

        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(shorten_path(f), EXPECT_FILES_SUBDIR)
            self.assertNotIn(shorten_path(f), EXPECT_FILES_SUBSUBDIR_A)
            self.assertNotIn(shorten_path(f), EXPECT_FILES_SUBSUBDIR_B)
            self.assertTrue(isinstance(f, bytes))

    def test_returns_expected_number_of_files_recursive(self):
        actual = list(
            get_files_gen(to_abspath(['subdir']), recurse=True)
        )
        self.assertEqual(len(actual), 8)

    def test_returns_expected_files_recursive(self):
        actual = get_files_gen(to_abspath(['subdir']), recurse=True)

        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(f, ABSPATH_FILES_ALL)
            self.assertTrue(isinstance(f, bytes))

    def test_returns_expected_number_of_files_recursive_from_subsubdir_a(self):
        actual = list(
            get_files_gen(to_abspath(['subdir/subsubdir_A']), recurse=True)
        )
        self.assertEqual(len(actual), 2)

    def test_returns_expected_files_recursive_from_subsubdir_a(self):
        actual = list(
            get_files_gen(to_abspath(['subdir/subsubdir_A']), recurse=True)
        )

        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(f, ABSPATH_FILES_SUBSUBDIR_A)
            self.assertNotIn(f, ABSPATH_FILES_SUBSUBDIR_B)
            self.assertNotIn(f, ABSPATH_FILES_SUBDIR)
            self.assertTrue(isinstance(f, bytes))

    def test_returns_expected_files_recursive_from_subsubdir_b(self):
        actual = list(
            get_files_gen(to_abspath(['subdir/subsubdir_B']), recurse=True)
        )

        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(f, ABSPATH_FILES_SUBSUBDIR_B)
            self.assertNotIn(f, ABSPATH_FILES_SUBSUBDIR_A)
            self.assertNotIn(f, ABSPATH_FILES_SUBDIR)
            self.assertTrue(isinstance(f, bytes))


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
        def _raises(exception_, a, b):
            with self.assertRaises(exception_):
                diskutils.compare_basenames(a, b)

        _raises(ValueError, None, None)
        _raises(ValueError, None, None)
        _raises(ValueError, None, [])
        _raises(ValueError, [], None)
        _raises(EncodingBoundaryViolation, 1, 2)
        _raises(EncodingBoundaryViolation, [], [])
        _raises(EncodingBoundaryViolation, object(), object())
        _raises(EncodingBoundaryViolation, 'a', 'b')
        _raises(EncodingBoundaryViolation, 'a', [])
        _raises(EncodingBoundaryViolation, '', '')
        _raises(EncodingBoundaryViolation, '', ' ')
        _raises(EncodingBoundaryViolation, '_', '')
        _raises(EncodingBoundaryViolation, 'a', 2)
        _raises(EncodingBoundaryViolation, 1, 'b')
        _raises(EncodingBoundaryViolation, 'a', b'a')
        _raises(EncodingBoundaryViolation, b'a', 'a')

    def test_comparing_equal_basenames_returns_true(self):
        def _assert_true(first, second):
            self.assertTrue(diskutils.compare_basenames(first, second))
            self.assertTrue(
                isinstance(diskutils.compare_basenames(first, second), bool)
            )

        _assert_true(b'', b'')
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

        # Looks identical but the second string contains character '\xc2\xa0'
        # between the last timestamp digit and 'W' instead of a simple space.
        _assert_false(
            '2017-08-14T015051 Working on autonameow -- dev projects.png'.encode('utf-8'),
            '2017-08-14T015051 Working on autonameow -- dev projects.png'.encode('utf-8')
        )


class TestPathCollector(TestCase):
    def setUp(self):
        self.pc = diskutils.PathCollector()

    def test_raises_errors_for_invalid_paths(self):
        def _assert_raises(test_input):
            with self.assertRaises((FileNotFoundError, TypeError)):
                self.pc.get_paths(test_input)

        _assert_raises('x')
        _assert_raises(' x ')

    def test_returns_empty_list_given_invalid_paths(self):
        def _aE(test_input):
            actual = self.pc.get_paths(test_input)
            self.assertEqual(actual, [])

        _aE(None)
        _aE('')
        _aE(' ')

    def test_returns_expected_number_of_files_non_recursive(self):
        _search_path = [to_abspath(['subdir'])]
        actual = self.pc.get_paths(_search_path)
        self.assertEqual(len(actual), 3)

    def test_returns_expected_files_non_recursive(self):
        _search_path = [to_abspath(['subdir'])]
        actual = self.pc.get_paths(_search_path)

        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(shorten_path(f), EXPECT_FILES_SUBDIR)
            self.assertNotIn(shorten_path(f), EXPECT_FILES_SUBSUBDIR_A)
            self.assertNotIn(shorten_path(f), EXPECT_FILES_SUBSUBDIR_B)
            self.assertTrue(isinstance(f, bytes))

    def test_returns_expected_number_of_files_recursive(self):
        _search_paths = [to_abspath(['subdir'])]
        pc = diskutils.PathCollector(recurse=True)
        actual = pc.get_paths(_search_paths)
        self.assertEqual(len(actual), 8)

    def test_returns_expected_files_recursive(self):
        _search_paths = [to_abspath(['subdir'])]
        pc = diskutils.PathCollector(recurse=True)
        actual = pc.get_paths(_search_paths)

        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(f, ABSPATH_FILES_ALL)
            self.assertTrue(isinstance(f, bytes))

    def test_returns_expected_number_of_files_recursive_from_subsubdir_a(self):
        _search_paths = [to_abspath(['subdir/subsubdir_A'])]
        pc = diskutils.PathCollector(recurse=True)
        actual = pc.get_paths(_search_paths)
        self.assertEqual(len(actual), 2)

    def test_returns_expected_files_recursive_from_subsubdir_a(self):
        _search_paths = [to_abspath(['subdir/subsubdir_A'])]
        pc = diskutils.PathCollector(recurse=True)
        actual = pc.get_paths(_search_paths)

        self.assertEqual(len(actual), len(ABSPATH_FILES_SUBSUBDIR_A))
        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(f, ABSPATH_FILES_SUBSUBDIR_A)
            self.assertNotIn(f, ABSPATH_FILES_SUBSUBDIR_B)
            self.assertNotIn(f, ABSPATH_FILES_SUBDIR)
            self.assertTrue(isinstance(f, bytes))

    def test_returns_expected_files_recursive_from_subsubdir_b(self):
        _search_paths = [to_abspath(['subdir/subsubdir_B'])]
        pc = diskutils.PathCollector(recurse=True)
        actual = pc.get_paths(_search_paths)

        self.assertEqual(len(actual), len(ABSPATH_FILES_SUBSUBDIR_B))
        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(f, ABSPATH_FILES_SUBSUBDIR_B)
            self.assertNotIn(f, ABSPATH_FILES_SUBSUBDIR_A)
            self.assertNotIn(f, ABSPATH_FILES_SUBDIR)
            self.assertTrue(isinstance(f, bytes))

    def test_returns_empty_list_for_catch_all_glob(self):
        _search_paths = [to_abspath(['subdir'])]

        pc = diskutils.PathCollector(recurse=False, ignore_globs=['*'])
        a = pc.get_paths(_search_paths)
        self.assertEqual(len(a), 0)

        pc = diskutils.PathCollector(recurse=True, ignore_globs=['*'])
        b = pc.get_paths(_search_paths)
        self.assertEqual(len(b), 0)

    def test_returns_all_for_non_matching_glob(self):
        _search_paths = [to_abspath(['subdir'])]
        pc = diskutils.PathCollector(recurse=True, ignore_globs=['*foobar*'])
        actual = pc.get_paths(_search_paths)

        self.assertEqual(len(actual), len(ABSPATH_FILES_ALL))
        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(f, ABSPATH_FILES_ALL)
            self.assertTrue(isinstance(f, bytes))

    def test_returns_expected_for_glob_a(self):
        _search_paths = uu.abspath_testfile('configs')
        pc = diskutils.PathCollector(ignore_globs=['*'])
        actual = pc.get_paths(_search_paths)
        self.assertEqual(len(actual), 0)

    def test_returns_expected_for_glob_b(self):
        _search_paths = uu.abspath_testfile('configs')
        pc = diskutils.PathCollector(ignore_globs=['*.yaml'])
        actual = pc.get_paths(_search_paths)
        self.assertEqual(len(actual), 0)

    def test_returns_expected_for_glob_c(self):
        _search_paths = uu.abspath_testfile('configs')
        pc = diskutils.PathCollector(ignore_globs=None)
        actual = pc.get_paths(_search_paths)
        self.assertEqual(len(actual), 3)

    def test_returns_expected_for_glob_d(self):
        _search_paths = uu.abspath_testfile('configs')
        pc = diskutils.PathCollector(ignore_globs=['*_filetags.yaml'])
        actual = pc.get_paths(_search_paths)
        self.assertEqual(len(actual), 2)

    def test_returns_expected_for_glob_e(self):
        _search_paths = uu.abspath_testfile('configs')
        pc = diskutils.PathCollector(ignore_globs=['*/integration_test_config_*a*.yaml'])
        actual = pc.get_paths(_search_paths)
        self.assertEqual(len(actual), 1)


class UnitTestIgnorePaths(TestCase):
    def setUp(self):
        _paths = [
            '~/dummy/foo.txt',
            '~/dummy/d/foo.txt',
            '~/dummy/bar.jpg',
            '~/dummy/.DS_Store',
            '~/foo/bar',
            '~/foo/.DS_Store'
        ]
        self.input_paths = [
           util.normpath(p) for p in _paths
        ]

    def test_setup(self):
        for path in self.input_paths:
            self.assertTrue(isinstance(path, bytes))
            self.assertTrue(os.path.isabs(util.syspath(path)))

    def test_passes_all_paths_if_no_ignore_globs_are_provided(self):
        actual = diskutils.filter_paths(self.input_paths, [])
        self.assertEqual(actual, self.input_paths)
        self.assertEqual(len(actual), len(self.input_paths))

    def _assert_filters(self, ignore_globs, remain, missing):
        # Sanity check arguments.
        self.assertEqual(len(self.input_paths),
                         len(remain) + len(missing))
        for path in missing + remain:
            self.assertIn(util.normpath(path), self.input_paths)

        actual = diskutils.filter_paths(self.input_paths, ignore_globs)
        self.assertIsNotNone(actual)

        self.assertTrue(isinstance(actual, list))
        for p in actual:
            self.assertTrue(isinstance(p, bytes))

        for m in missing:
            self.assertNotIn(util.normpath(m), actual)
        for r in remain:
            self.assertIn(util.normpath(r), actual)

    def test_ignores_txt_extensions(self):
        self._assert_filters(
            ignore_globs=['*.txt'],
            remain=['~/dummy/.DS_Store', '~/dummy/bar.jpg', '~/foo/bar',
                    '~/foo/.DS_Store'],
            missing=['~/dummy/foo.txt', '~/dummy/d/foo.txt']
        )

    def test_ignores_ds_store(self):
        self._assert_filters(
            ignore_globs=['*.DS_Store'],
            remain=['~/dummy/bar.jpg', '~/dummy/foo.txt', '~/dummy/d/foo.txt',
                    '~/foo/bar'],
            missing=['~/dummy/.DS_Store', '~/foo/.DS_Store']
        )

    def test_ignores_single_file(self):
        self._assert_filters(
            ignore_globs=['*/bar.jpg'],
            remain=['~/dummy/.DS_Store', '~/foo/.DS_Store', '~/dummy/foo.txt',
                    '~/dummy/d/foo.txt', '~/foo/bar'],
            missing=['~/dummy/bar.jpg']
        )

    def test_ignores_all_files(self):
        self._assert_filters(
            ignore_globs=['*'],
            remain=[],
            missing=['~/dummy/.DS_Store', '~/dummy/bar.jpg', '~/dummy/foo.txt',
                     '~/dummy/d/foo.txt', '~/foo/.DS_Store', '~/foo/bar']
       )

    def test_ignores_path(self):
        self._assert_filters(
            ignore_globs=['*/dummy/*'],
            remain=['~/foo/bar', '~/foo/.DS_Store'],
            missing=['~/dummy/.DS_Store', '~/dummy/bar.jpg', '~/dummy/foo.txt',
                     '~/dummy/d/foo.txt']
        )
