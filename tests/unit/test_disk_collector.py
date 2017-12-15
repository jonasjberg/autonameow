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

import unit.utils as uu
from core.disk.collector import (
    get_files_gen,
    PathCollector
)
from util import encoding as enc


def shorten_path(abs_path):
    parent = os.path.basename(os.path.dirname(abs_path))
    basename = os.path.basename(abs_path)
    return os.path.join(parent, basename)


def to_abspath(path_list):
    paths = [enc.bytestring_path(tf)
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

EXPECT_FILES_SUBDIR = [
    enc.bytestring_path(p) for p in FILES_SUBDIR
]
EXPECT_FILES_SUBSUBDIR_A = [
    enc.bytestring_path(p) for p in FILES_SUBSUBDIR_A
]
EXPECT_FILES_SUBSUBDIR_B = [
    enc.bytestring_path(p) for p in FILES_SUBSUBDIR_B
]


class TestTestFiles(TestCase):
    def test_all(self):
        for tf in ABSPATH_FILES_ALL:
            self.assertTrue(uu.file_exists(tf),
                            'Expected file: "{}"'.format(tf))
            self.assertTrue(uu.is_internalbytestring(tf))

        self.assertEqual(8, len(ABSPATH_FILES_ALL))

    def test_abspath_subdir(self):
        for tf in ABSPATH_FILES_SUBDIR:
            self.assertTrue(uu.file_exists(tf),
                            'Expected file: "{}"'.format(tf))
            self.assertTrue(uu.is_internalbytestring(tf))

    def test_abspath_subsubdir_a(self):
        for tf in ABSPATH_FILES_SUBSUBDIR_A:
            self.assertTrue(uu.file_exists(tf),
                            'Expected file: "{}"'.format(tf))
            self.assertTrue(uu.is_internalbytestring(tf))

    def test_abspath_subsubdir_b(self):
        for tf in ABSPATH_FILES_SUBSUBDIR_B:
            self.assertTrue(uu.file_exists(tf),
                            'Expected file: "{}"'.format(tf))
            self.assertTrue(uu.is_internalbytestring(tf))


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
        self.assertEqual(3, len(actual))

    def test_returns_expected_files_non_recursive(self):
        actual = get_files_gen(to_abspath(['subdir']))

        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(shorten_path(f), EXPECT_FILES_SUBDIR)
            self.assertNotIn(shorten_path(f), EXPECT_FILES_SUBSUBDIR_A)
            self.assertNotIn(shorten_path(f), EXPECT_FILES_SUBSUBDIR_B)
            self.assertTrue(uu.is_internalbytestring(f))

    def test_returns_expected_number_of_files_recursive(self):
        actual = list(
            get_files_gen(to_abspath(['subdir']), recurse=True)
        )
        self.assertEqual(8, len(actual))

    def test_returns_expected_files_recursive(self):
        actual = get_files_gen(to_abspath(['subdir']), recurse=True)

        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(f, ABSPATH_FILES_ALL)
            self.assertTrue(uu.is_internalbytestring(f))

    def test_returns_expected_number_of_files_recursive_from_subsubdir_a(self):
        actual = list(
            get_files_gen(to_abspath(['subdir/subsubdir_A']), recurse=True)
        )
        self.assertEqual(2, len(actual))

    def test_returns_expected_files_recursive_from_subsubdir_a(self):
        actual = list(
            get_files_gen(to_abspath(['subdir/subsubdir_A']), recurse=True)
        )

        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(f, ABSPATH_FILES_SUBSUBDIR_A)
            self.assertNotIn(f, ABSPATH_FILES_SUBSUBDIR_B)
            self.assertNotIn(f, ABSPATH_FILES_SUBDIR)
            self.assertTrue(uu.is_internalbytestring(f))

    def test_returns_expected_files_recursive_from_subsubdir_b(self):
        actual = list(
            get_files_gen(to_abspath(['subdir/subsubdir_B']), recurse=True)
        )

        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(f, ABSPATH_FILES_SUBSUBDIR_B)
            self.assertNotIn(f, ABSPATH_FILES_SUBSUBDIR_A)
            self.assertNotIn(f, ABSPATH_FILES_SUBDIR)
            self.assertTrue(uu.is_internalbytestring(f))


class TestPathCollector(TestCase):
    def setUp(self):
        self.pc = PathCollector()

    def test_raises_errors_for_invalid_paths(self):
        def _assert_raises(test_input):
            with self.assertRaises((FileNotFoundError, TypeError)):
                self.pc.get_paths(test_input)

        _assert_raises('x')
        _assert_raises(' x ')

    def test_returns_empty_list_given_invalid_paths(self):
        def _aE(test_input):
            actual = self.pc.get_paths(test_input)
            self.assertEqual([], actual)

        _aE(None)
        _aE('')
        _aE(' ')

    def test_returns_expected_number_of_files_non_recursive(self):
        _search_path = [to_abspath(['subdir'])]
        actual = self.pc.get_paths(_search_path)
        self.assertEqual(3, len(actual))

    def test_returns_expected_files_non_recursive(self):
        _search_path = [to_abspath(['subdir'])]
        actual = self.pc.get_paths(_search_path)

        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(shorten_path(f), EXPECT_FILES_SUBDIR)
            self.assertNotIn(shorten_path(f), EXPECT_FILES_SUBSUBDIR_A)
            self.assertNotIn(shorten_path(f), EXPECT_FILES_SUBSUBDIR_B)
            self.assertTrue(uu.is_internalbytestring(f))

    def test_returns_expected_number_of_files_recursive(self):
        _search_paths = [to_abspath(['subdir'])]
        pc = PathCollector(recurse=True)
        actual = pc.get_paths(_search_paths)
        self.assertEqual(8, len(actual))

    def test_returns_expected_files_recursive(self):
        _search_paths = [to_abspath(['subdir'])]
        pc = PathCollector(recurse=True)
        actual = pc.get_paths(_search_paths)

        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(f, ABSPATH_FILES_ALL)
            self.assertTrue(uu.is_internalbytestring(f))

    def test_returns_expected_number_of_files_recursive_from_subsubdir_a(self):
        _search_paths = [to_abspath(['subdir/subsubdir_A'])]
        pc = PathCollector(recurse=True)
        actual = pc.get_paths(_search_paths)
        self.assertEqual(2, len(actual))

    def test_returns_expected_files_recursive_from_subsubdir_a(self):
        _search_paths = [to_abspath(['subdir/subsubdir_A'])]
        pc = PathCollector(recurse=True)
        actual = pc.get_paths(_search_paths)

        self.assertEqual(len(ABSPATH_FILES_SUBSUBDIR_A), len(actual))
        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(f, ABSPATH_FILES_SUBSUBDIR_A)
            self.assertNotIn(f, ABSPATH_FILES_SUBSUBDIR_B)
            self.assertNotIn(f, ABSPATH_FILES_SUBDIR)
            self.assertTrue(uu.is_internalbytestring(f))

    def test_returns_expected_files_recursive_from_subsubdir_b(self):
        _search_paths = [to_abspath(['subdir/subsubdir_B'])]
        pc = PathCollector(recurse=True)
        actual = pc.get_paths(_search_paths)

        self.assertEqual(len(ABSPATH_FILES_SUBSUBDIR_B), len(actual))
        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(f, ABSPATH_FILES_SUBSUBDIR_B)
            self.assertNotIn(f, ABSPATH_FILES_SUBSUBDIR_A)
            self.assertNotIn(f, ABSPATH_FILES_SUBDIR)
            self.assertTrue(uu.is_internalbytestring(f))

    def test_returns_empty_list_for_catch_all_glob(self):
        _search_paths = [to_abspath(['subdir'])]

        pc = PathCollector(recurse=False, ignore_globs=['*'])
        a = pc.get_paths(_search_paths)
        self.assertEqual(0, len(a))

        pc = PathCollector(recurse=True, ignore_globs=['*'])
        b = pc.get_paths(_search_paths)
        self.assertEqual(0, len(b))

    def test_returns_all_for_non_matching_glob(self):
        _search_paths = [to_abspath(['subdir'])]
        pc = PathCollector(recurse=True, ignore_globs=['*foobar*'])
        actual = pc.get_paths(_search_paths)

        self.assertEqual(len(ABSPATH_FILES_ALL), len(actual))
        for f in actual:
            self.assertTrue(uu.file_exists(f))
            self.assertIn(f, ABSPATH_FILES_ALL)
            self.assertTrue(uu.is_internalbytestring(f))

    def test_returns_expected_for_glob_a(self):
        _search_paths = uu.abspath_testfile('configs')
        pc = PathCollector(ignore_globs=['*'])
        actual = pc.get_paths(_search_paths)
        self.assertEqual(0, len(actual))

    def test_returns_expected_for_glob_b(self):
        _search_paths = uu.abspath_testfile('configs')
        pc = PathCollector(ignore_globs=['*.yaml'])
        actual = pc.get_paths(_search_paths)
        self.assertEqual(0, len(actual))

    def test_returns_expected_for_glob_c(self):
        _search_paths = uu.abspath_testfile('configs')
        pc = PathCollector(ignore_globs=None)
        actual = pc.get_paths(_search_paths)
        self.assertEqual(6, len(actual))

    def test_returns_expected_for_glob_d(self):
        _search_paths = uu.abspath_testfile('configs')
        pc = PathCollector(ignore_globs=['*_filetags.yaml'])
        actual = pc.get_paths(_search_paths)
        self.assertEqual(5, len(actual))

    def test_returns_expected_for_glob_e(self):
        _search_paths = uu.abspath_testfile('configs')
        pc = PathCollector(ignore_globs=['*/integration_test_config_*a*.yaml'])
        actual = pc.get_paths(_search_paths)
        self.assertEqual(3, len(actual))


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
            uu.normpath(p) for p in _paths
        ]

    def test_setup(self):
        for path in self.input_paths:
            self.assertTrue(uu.is_internalbytestring(path))
            self.assertTrue(os.path.isabs(enc.syspath(path)))

    def test_passes_all_paths_if_no_ignore_globs_are_provided(self):
        pc = PathCollector(ignore_globs=[])
        actual = pc.filter_paths(self.input_paths)
        self.assertEqual(self.input_paths, actual)
        self.assertEqual(len(self.input_paths), len(actual))

    def _assert_filters(self, ignore_globs, remain, missing):
        # Sanity check arguments.
        self.assertEqual(len(self.input_paths),
                         len(remain) + len(missing))
        for path in missing + remain:
            self.assertIn(uu.normpath(path), self.input_paths)

        pc = PathCollector(ignore_globs=ignore_globs)
        actual = pc.filter_paths(self.input_paths)
        self.assertIsNotNone(actual)

        self.assertTrue(isinstance(actual, list))
        for p in actual:
            self.assertTrue(uu.is_internalbytestring(p))

        for m in missing:
            self.assertNotIn(uu.normpath(m), actual)
        for r in remain:
            self.assertIn(uu.normpath(r), actual)

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
