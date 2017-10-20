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

from core import util
from core.exceptions import FilesystemError
from core.util.disk import (
    isdir,
    isfile,
    tempdir
)
import unit_utils as uu
import unit_utils_constants as uuconst


class TestIsdir(TestCase):
    def _check_return(self, path_to_test):
        actual = isdir(path_to_test)
        self.assertTrue(isinstance(actual, bool))

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
            uuconst.AUTONAMEOW_SRCROOT_DIR,
            '/',
            b'/',
            util.bytestring_path(os.path.dirname(__file__)),
            util.bytestring_path(uuconst.AUTONAMEOW_SRCROOT_DIR)
        ]
        for df in _files:
            self._check_return(df)


class TestIsfile(TestCase):
    def _check_return(self, file_to_test):
        actual = isfile(file_to_test)
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
