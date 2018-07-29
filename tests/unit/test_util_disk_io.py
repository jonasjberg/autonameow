# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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
import stat
from unittest import TestCase
from unittest.mock import MagicMock, patch

import unit.constants as uuconst
import unit.utils as uu
from core.exceptions import FilesystemError
from util import encoding as enc
from util.disk.io import basename
from util.disk.io import delete
from util.disk.io import dirname
from util.disk.io import exists
from util.disk.io import file_bytesize
from util.disk.io import has_permissions
from util.disk.io import isabs
from util.disk.io import isdir
from util.disk.io import isfile
from util.disk.io import islink
from util.disk.io import joinpaths
from util.disk.io import listdir
from util.disk.io import makedirs
from util.disk.io import rename_file
from util.disk.io import rmdir
from util.disk.io import tempdir


class TestRenameFile(TestCase):
    @patch('os.rename', MagicMock())
    def test_raises_exception_given_unicode_string_or_none_paths(self):
        def _assert_raises(given_source_path, given_new_basename):
            with self.assertRaises(AssertionError):
                _ = rename_file(given_source_path, given_new_basename)

        _assert_raises('foo', b'bar')
        _assert_raises(b'foo', 'bar')
        _assert_raises(b'foo', b'bar')
        _assert_raises(None, b'bar')
        _assert_raises(b'foo', None)
        _assert_raises(None, None)

    @patch('os.rename', MagicMock())
    def test_raises_exception_given_relative_source_path(self):
        def _assert_raises(given_source_path):
            with self.assertRaises(AssertionError):
                _ = rename_file(given_source_path, b'bar')

        _assert_raises(b'../foo')
        _assert_raises(b'./foo')
        _assert_raises(b'foo')

    @patch('os.rename')
    @patch('util.disk.io.exists')
    def test_raises_exception_if_source_path_does_not_exist(
            self, mock_exists, mock_rename
    ):
        mock_exists.return_value = False
        with self.assertRaises(FileNotFoundError):
            rename_file(b'/tmp/foo/bar', b'baz')
        mock_rename.assert_not_called()

    @patch('os.rename')
    @patch('util.disk.io.exists')
    def test_raises_exception_if_destination_path_does_not_exist(
            self, mock_exists, mock_rename
    ):
        mock_exists.return_value = True
        with self.assertRaises(FileExistsError):
            rename_file(b'/tmp/foo/bar', b'baz')
        mock_rename.assert_not_called()

    @patch('os.rename')
    def test_renames_file_given_valid_arguments(self, mock_rename):
        test_file_path = uu.make_temporary_file()
        test_file_dir_path = os.path.realpath(os.path.dirname(test_file_path))
        expected_destpath = os.path.join(test_file_dir_path, b'baz')
        rename_file(test_file_path, b'baz')
        mock_rename.assert_called_once_with(test_file_path, expected_destpath)

    def test_raises_expected_exception_when_filename_is_too_long(self):
        test_file_path = uu.make_temporary_file()
        too_long_destination_basename = 256 * b'X'
        self.assertEqual(256, len(too_long_destination_basename))

        with self.assertRaises(FilesystemError) as cm:
            rename_file(test_file_path, too_long_destination_basename)
        # self.assertEqual(cm.exception.error_code, 36)


class TestDirname(TestCase):
    def test_returns_expected(self):
        actual = dirname(__file__)
        expect = os.path.dirname(__file__)
        self.assertEqual(expect, actual)


class TestExists(TestCase):
    def _check_return(self, file_to_test):
        actual = exists(file_to_test)
        self.assertIsInstance(actual, bool)

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
            self.assertFalse(exists(test_input))

        _aF('')
        _aF(' ')

    def test_raises_exception_given_invalid_arguments(self):
        def _aF(test_input):
            with self.assertRaises(FilesystemError):
                _ = exists(test_input)

        _aF(None)

    def test_returns_true_for_files_likely_to_exist(self):
        _files = [
            __file__,
        ]
        for df in _files:
            self._check_return(df)


class TestIsAbs(TestCase):
    def test_returns_true_given_absolute_path(self):
        given = os.path.abspath(__file__)
        actual = isabs(given)
        self.assertTrue(actual)

    def test_returns_false_given_relative_path(self):
        for given in (b'..', b'./foo'):
            with self.subTest(given=given):
                actual = isabs(given)
                self.assertFalse(actual)


class TestIsdir(TestCase):
    def _check_return(self, path_to_test):
        actual = isdir(path_to_test)
        self.assertIsInstance(actual, bool)

        if not path_to_test:
            expected = False
        else:
            try:
                expected = os.path.isdir(path_to_test)
            except (OSError, TypeError, ValueError):
                expected = False

        self.assertEqual(actual, expected)

    def test_returns_false_for_assumed_non_directory_paths(self):
        _dummy_paths = [
            __file__,
            '/foo/bar/baz/mjao',
            '/tmp/this_isnt_a_file_right_or_huh',
            b'/foo/bar/baz/mjao',
            b'/tmp/this_isnt_a_file_right_or_huh',
        ]
        for df in _dummy_paths:
            self._check_return(df)

    def test_returns_false_for_empty_argument(self):
        def _aF(test_input):
            self.assertFalse(isdir(test_input))

        _aF('')
        _aF(' ')

    def test_raises_exception_given_invalid_arguments(self):
        def _aF(test_input):
            with self.assertRaises(FilesystemError):
                _ = isdir(test_input)

        _aF(None)

    def test_returns_true_for_likely_directory_paths(self):
        _files = [
            os.path.dirname(__file__),
            uuconst.PATH_AUTONAMEOW_SRCROOT,
            '/',
            b'/',
            uu.bytestring_path(os.path.dirname(__file__)),
            uu.bytestring_path(uuconst.PATH_AUTONAMEOW_SRCROOT)
        ]
        for df in _files:
            self._check_return(df)


class TestIsfile(TestCase):
    def _check_return(self, file_to_test):
        actual = isfile(file_to_test)
        self.assertIsInstance(actual, bool)

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
            self.assertFalse(isfile(test_input))

        _aF('')
        _aF(' ')

    def test_raises_exception_given_invalid_arguments(self):
        def _aF(test_input):
            with self.assertRaises(FilesystemError):
                _ = isfile(test_input)

        _aF(None)

    def test_returns_true_for_files_likely_to_exist(self):
        _files = [
            __file__,
        ]
        for df in _files:
            self._check_return(df)


class TestIsLink(TestCase):
    def test_returns_false_given_file(self):
        f = uu.abspath_testfile('empty')
        actual = islink(f)
        self.assertFalse(actual)

    def test_returns_true_given_symlink(self):
        f = uu.abspath_testfile('empty.symlink')
        actual = islink(f)
        self.assertTrue(actual)


class TestJoinPaths(TestCase):
    def test_joins_valid_strings(self):
        actual = joinpaths('/a', 'b', 'c')
        self.assertEqual('/a/b/c', actual)

    def test_ignores_missing_elements(self):
        actual = joinpaths('/a', None, 'c')
        self.assertEqual('/a/c', actual)

        actual = joinpaths('/a', '', 'c')
        self.assertEqual('/a/c', actual)

    def test_raises_exception_given_invalid_arguments(self):
        def _assert_raises(*given):
            with self.assertRaises(FilesystemError):
                _ = joinpaths(*given)

        _assert_raises(object())
        _assert_raises([])
        _assert_raises(dict())
        _assert_raises('a', {'b': 1})
        _assert_raises('a', ['b'])


class TestListDir(TestCase):
    def test_returns_directory_contents(self):
        given = uuconst.PATH_TEST_FILES
        actual = listdir(given)
        self.assertIsNotNone(actual)
        self.assertGreater(len(actual), 1)


class TestTempdir(TestCase):
    def setUp(self):
        self.actual = tempdir()

    def test_returns_existing_directory(self):
        self.assertIsNotNone(self.actual)
        self.assertTrue(uu.dir_exists(self.actual))

    def test_returns_expected_type(self):
        self.assertTrue(uu.is_internalbytestring(self.actual))

    def test_returns_absolute_paths(self):
        self.assertTrue(uu.is_abspath(self.actual))

    def test_returns_unique_directories(self):
        NUM_DIRS = 5

        s = set()
        for _ in range(0, NUM_DIRS):
            s.add(uu.make_temp_dir())

        self.assertEqual(len(s), NUM_DIRS)


class TestMakedirs(TestCase):
    def setUp(self):
        self.parentdir = uu.make_temp_dir()

        destbase = b'foobar'
        self.destpath = uu.normpath(
            os.path.join(enc.syspath(self.parentdir),
                         enc.syspath(destbase))
        )

    def test_creates_directory(self):
        self.assertFalse(uu.dir_exists(self.destpath))
        makedirs(self.destpath)
        self.assertTrue(uu.dir_exists(self.destpath))


class TestDelete(TestCase):
    def _get_non_existent_file(self):
        _tempdir = uu.make_temp_dir()
        self.assertTrue(uu.dir_exists(_tempdir))
        self.assertTrue(uu.is_internalbytestring(_tempdir))

        not_a_file = uu.normpath(
            os.path.join(enc.syspath(_tempdir),
                         enc.syspath(uuconst.ASSUMED_NONEXISTENT_BASENAME))
        )
        self.assertFalse(uu.dir_exists(not_a_file))
        self.assertFalse(uu.file_exists(not_a_file))
        self.assertTrue(uu.is_internalbytestring(not_a_file))
        return not_a_file

    def test_deletes_existing_file(self):
        tempfile = uu.make_temporary_file()
        self.assertTrue(uu.file_exists(tempfile))
        self.assertTrue(uu.is_internalbytestring(tempfile))

        delete(tempfile)
        self.assertFalse(uu.file_exists(tempfile))

    def test_raises_exception_given_non_existent_file(self):
        not_a_file = self._get_non_existent_file()

        with self.assertRaises(FilesystemError):
            delete(not_a_file)

        with self.assertRaises(FilesystemError):
            delete(not_a_file, ignore_missing=False)

    def test_silently_ignores_non_existent_file(self):
        not_a_file = self._get_non_existent_file()
        delete(not_a_file, ignore_missing=True)


class TestRmdir(TestCase):
    def test_deletes_actual_existing_directory(self):
        _tempdir = uu.make_temp_dir()
        os.chmod(enc.syspath(_tempdir), OWNER_R | OWNER_W | OWNER_X)
        self.assertTrue(uu.is_internalbytestring(_tempdir))
        self.assertTrue(uu.dir_exists(_tempdir))
        rmdir(_tempdir)
        self.assertFalse(uu.dir_exists(_tempdir))

    @patch('os.rmdir')
    def test_deletes_directory(self, mock_rmdir):
        rmdir(b'/tmp/foo')
        mock_rmdir.assert_called_once_with(b'/tmp/foo')

    def test_raises_exception_given_non_existent_dir(self):
        with self.assertRaises(FilesystemError):
            rmdir(b'/tmp/foo/bar/does/not/exist/surely')

    def test_ignores_non_existent_dir_when_ignore_missing_is_true(self):
        rmdir(b'/tmp/foo/bar/does/not/exist/surely', ignore_missing=True)


class TestBasename(TestCase):
    def test_returns_expected_given_valid_paths(self):
        def _aE(given, expect):
            actual = basename(given)
            self.assertEqual(actual, expect)

        _aE(b'test_util_disk_io.py', b'test_util_disk_io.py')
        _aE('test_util_disk_io.py', 'test_util_disk_io.py')
        _aE(__file__, 'test_util_disk_io.py')
        _aE(os.path.abspath(__file__), 'test_util_disk_io.py')
        _aE(os.path.realpath(__file__), 'test_util_disk_io.py')


OWNER_R = stat.S_IRUSR
OWNER_W = stat.S_IWUSR
OWNER_X = stat.S_IXUSR


class TestHasPermissions(TestCase):
    def _test(self, path, perms, expected):
        actual = has_permissions(path, perms)
        self.assertEqual(actual, expected)
        self.assertIsInstance(actual, bool)

    def test_invalid_arguments(self):
        def _aR(_path, perms):
            with self.assertRaises(AssertionError):
                _ = has_permissions(_path, perms)

        path = uu.make_temporary_file()
        _aR(path, None)
        _aR(path, [])
        _aR(path, object())
        _aR(path, b'')
        _aR(path, b'foo')
        _aR(None, 'r')
        _aR([], 'r')
        _aR(object(), 'r')

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
        os.chmod(enc.syspath(path), OWNER_R | OWNER_W | OWNER_X)

        self._test(path, 'r', True)
        self._test(path, 'w', True)
        self._test(path, 'x', True)
        self._test(path, 'rw', True)
        self._test(path, 'rx', True)
        self._test(path, 'wx', True)
        self._test(path, 'rwx', True)

        os.chmod(enc.syspath(path), OWNER_R | OWNER_W)

    def test_file_perms_rw(self):
        path = uu.make_temporary_file()
        os.chmod(enc.syspath(path), OWNER_R | OWNER_W)

        self._test(path, 'r', True)
        self._test(path, 'w', True)
        self._test(path, 'x', False)
        self._test(path, 'rw', True)
        self._test(path, 'wr', True)
        self._test(path, 'rx', False)
        self._test(path, 'xr', False)
        self._test(path, 'xw', False)
        self._test(path, 'rwx', False)

        os.chmod(enc.syspath(path), OWNER_R | OWNER_W)

    def test_file_perms_r(self):
        path = uu.make_temporary_file()
        os.chmod(enc.syspath(path), OWNER_R)

        self._test(path, 'r', True)
        self._test(path, 'w', False)
        self._test(path, 'x', False)
        self._test(path, 'rw', False)
        self._test(path, 'rx', False)
        self._test(path, 'wx', False)
        self._test(path, 'rwx', False)

        os.chmod(enc.syspath(path), OWNER_R | OWNER_W)

    def test_no_file_perms(self):
        path = uu.make_temporary_file()
        os.chmod(enc.syspath(path), OWNER_R)

        self._test(path, '', True)
        self._test(path, ' ', True)

        os.chmod(enc.syspath(path), OWNER_R | OWNER_W)


class TestFileByteSize(TestCase):
    @classmethod
    def setUpClass(cls):
        # List of (path to existing file, size in bytes) tuples
        cls.test_files = [
            (uu.abspath_testfile('magic_pdf.pdf'), 10283),
            (uu.abspath_testfile('magic_jpg.jpg'), 547),
            (uu.abspath_testfile('empty'), 0)
        ]

    def test_setup_class(self):
        for test_file_path, _ in self.test_files:
            self.assertTrue(uu.file_exists(test_file_path))

    def test_returns_expected_type(self):
        for test_file_path, _ in self.test_files:
            actual = file_bytesize(test_file_path)
            self.assertIsInstance(actual, int)

    def test_returns_expected_size(self):
        for test_file_path, test_file_size in self.test_files:
            actual = file_bytesize(test_file_path)
            self.assertEqual(test_file_size, actual)

    def test_raises_exception_given_invalid_arguments(self):
        def _assert_raises(test_input):
            with self.assertRaises(FilesystemError):
                _ = file_bytesize(test_input)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises(b'')
        _assert_raises(' ')
        _assert_raises(b' ')
        _assert_raises(object())
        _assert_raises([])
        _assert_raises([''])
        _assert_raises({})
        _assert_raises({'a': 'b'})
        _assert_raises(uuconst.ASSUMED_NONEXISTENT_BASENAME)
