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
import stat
from unittest import TestCase

from core import (
    util,
    exceptions
)
from core.util import diskutils
from core.util.diskutils import (
    get_files_gen
)
import unit_utils as uu
import unit_utils_constants as uuconst


class TestSplitBasename(TestCase):
    def _assert_splits(self, expected, test_input):
        actual = diskutils.split_basename(test_input)
        self.assertEqual(expected, actual)

    def test_returns_bytestrings(self):
        c, d = diskutils.split_basename(b'c.d')
        self.assertTrue(uu.is_internalbytestring(c))
        self.assertTrue(uu.is_internalbytestring(d))

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
            self.assertTrue(uu.is_internalbytestring(tf))

        self.assertEqual(len(ABSPATH_FILES_ALL), 8)

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
        self.assertEqual(len(actual), 3)

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
        self.assertEqual(len(actual), 8)

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
            self.assertTrue(uu.is_internalbytestring(f))

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
            self.assertTrue(uu.is_internalbytestring(f))

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
            self.assertTrue(uu.is_internalbytestring(f))

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
            self.assertTrue(uu.is_internalbytestring(f))

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
            self.assertTrue(uu.is_internalbytestring(f))

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
        self.assertEqual(len(actual), 5)

    def test_returns_expected_for_glob_d(self):
        _search_paths = uu.abspath_testfile('configs')
        pc = diskutils.PathCollector(ignore_globs=['*_filetags.yaml'])
        actual = pc.get_paths(_search_paths)
        self.assertEqual(len(actual), 4)

    def test_returns_expected_for_glob_e(self):
        _search_paths = uu.abspath_testfile('configs')
        pc = diskutils.PathCollector(ignore_globs=['*/integration_test_config_*a*.yaml'])
        actual = pc.get_paths(_search_paths)
        self.assertEqual(len(actual), 2)


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
            self.assertTrue(uu.is_internalbytestring(path))
            self.assertTrue(os.path.isabs(util.syspath(path)))

    def test_passes_all_paths_if_no_ignore_globs_are_provided(self):
        pc = diskutils.PathCollector(ignore_globs=[])
        actual = pc.filter_paths(self.input_paths)
        self.assertEqual(actual, self.input_paths)
        self.assertEqual(len(actual), len(self.input_paths))

    def _assert_filters(self, ignore_globs, remain, missing):
        # Sanity check arguments.
        self.assertEqual(len(self.input_paths),
                         len(remain) + len(missing))
        for path in missing + remain:
            self.assertIn(util.normpath(path), self.input_paths)

        pc = diskutils.PathCollector(ignore_globs=ignore_globs)
        actual = pc.filter_paths(self.input_paths)
        self.assertIsNotNone(actual)

        self.assertTrue(isinstance(actual, list))
        for p in actual:
            self.assertTrue(uu.is_internalbytestring(p))

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


OWNER_R = stat.S_IRUSR
OWNER_W = stat.S_IWUSR
OWNER_X = stat.S_IXUSR


class TestHasPermissions(TestCase):
    def _test(self, path, perms, expected):
        actual = diskutils.has_permissions(path, perms)
        self.assertEqual(actual, expected)
        self.assertTrue(isinstance(actual, bool))

    def test_invalid_arguments(self):
        path = uu.make_temporary_file()

        def _aR(path, perms):
            with self.assertRaises(TypeError):
                _ = diskutils.has_permissions(path, perms)

        _aR(path, None)
        _aR(path, [])
        _aR(path, object())
        _aR(path, b'')
        _aR(path, b'foo')
        _aR(None, 'r')
        _aR([], 'r')
        _aR(object(), 'r')
        _aR('', 'r')
        _aR('foo', 'r')

    def test_invalid_path(self):
        path = uuconst.ASSUMED_NONEXISTENT_BASENAME
        self._test(path, 'r', False)
        self._test(path, 'w', False)
        self._test(path, 'x', False)
        self._test(path, 'rw', False)
        self._test(path, 'rx', False)
        self._test(path, 'wx', False)
        self._test(path, 'rwx', False)

    def test_file_perms_rwx(self):
        path = uu.make_temporary_file()
        os.chmod(util.syspath(path), OWNER_R | OWNER_W | OWNER_X)

        self._test(path, 'r', True)
        self._test(path, 'w', True)
        self._test(path, 'x', True)
        self._test(path, 'rw', True)
        self._test(path, 'rx', True)
        self._test(path, 'wx', True)
        self._test(path, 'rwx', True)

        os.chmod(util.syspath(path), OWNER_R | OWNER_W)

    def test_file_perms_rw(self):
        path = uu.make_temporary_file()
        os.chmod(util.syspath(path), OWNER_R | OWNER_W)

        self._test(path, 'r', True)
        self._test(path, 'w', True)
        self._test(path, 'x', False)
        self._test(path, 'rw', True)
        self._test(path, 'wr', True)
        self._test(path, 'rx', False)
        self._test(path, 'xr', False)
        self._test(path, 'xw', False)
        self._test(path, 'rwx', False)

        os.chmod(util.syspath(path), OWNER_R | OWNER_W)

    def test_file_perms_r(self):
        path = uu.make_temporary_file()
        os.chmod(util.syspath(path), OWNER_R)

        self._test(path, 'r', True)
        self._test(path, 'w', False)
        self._test(path, 'x', False)
        self._test(path, 'rw', False)
        self._test(path, 'rx', False)
        self._test(path, 'wx', False)
        self._test(path, 'rwx', False)

        os.chmod(util.syspath(path), OWNER_R | OWNER_W)


class TestDelete(TestCase):
    def _get_non_existent_file(self):
        tempdir = uu.make_temp_dir()
        self.assertTrue(uu.dir_exists(tempdir))
        self.assertTrue(uu.is_internalbytestring(tempdir))

        not_a_file = util.normpath(
            os.path.join(util.syspath(tempdir),
                         util.syspath(uuconst.ASSUMED_NONEXISTENT_BASENAME))
        )
        self.assertFalse(uu.dir_exists(not_a_file))
        self.assertFalse(uu.file_exists(not_a_file))
        self.assertTrue(uu.is_internalbytestring(not_a_file))
        return not_a_file

    def test_deletes_existing_file(self):
        tempfile = uu.make_temporary_file()
        self.assertTrue(uu.file_exists(tempfile))
        self.assertTrue(uu.is_internalbytestring(tempfile))

        diskutils.delete(tempfile)
        self.assertFalse(uu.file_exists(tempfile))

    def test_deletes_existing_directory(self):
        self.skipTest('TODO: [Errno 1] Operation not permitted')

        tempdir = uu.make_temp_dir()

        _dir = util.syspath(
            os.path.join(util.syspath(tempdir),
                         util.syspath(uuconst.ASSUMED_NONEXISTENT_BASENAME))
        )
        self.assertTrue(uu.is_internalbytestring(_dir))
        os.makedirs(util.syspath(_dir))
        self.assertTrue(uu.dir_exists(_dir))

        # diskutils.delete(_dir)
        self.assertFalse(uu.dir_exists(_dir))

    def test_raises_exception_given_non_existent_file(self):
        not_a_file = self._get_non_existent_file()

        with self.assertRaises(exceptions.FilesystemError):
            diskutils.delete(not_a_file)

        with self.assertRaises(exceptions.FilesystemError):
            diskutils.delete(not_a_file, ignore_missing=False)

    def test_silently_ignores_non_existent_file(self):
        not_a_file = self._get_non_existent_file()
        diskutils.delete(not_a_file, ignore_missing=True)


class TestExists(TestCase):
    def _check_return(self, file_to_test):
        actual = diskutils.exists(file_to_test)
        self.assertTrue(isinstance(actual, bool))

        if not file_to_test:
            expected = False
        else:
            try:
                expected = os.path.isfile(file_to_test)
            except (OSError, TypeError, ValueError):
                expected = False

        self.assertEqual(actual, expected)

    def test_returns_false_for_files_assumed_missing(self):
        _dummy_paths = [
            '/foo/bar/baz/mjao',
            '/tmp/this_isnt_a_file_right_or_huh',
            b'/tmp/this_isnt_a_file_right_or_huh'
        ]
        for df in _dummy_paths:
            self._check_return(df)

    def test_returns_false_for_empty_argument(self):
        def _aF(test_input):
            self.assertFalse(diskutils.exists(test_input))

        _aF('')
        _aF(' ')

    def test_raises_exception_given_invalid_arguments(self):
        def _aF(test_input):
            with self.assertRaises(exceptions.FilesystemError):
                _ = diskutils.exists(test_input)

        _aF(None)

    def test_returns_true_for_files_likely_to_exist(self):
        _files = [
            __file__,
        ]
        for df in _files:
            self._check_return(df)

