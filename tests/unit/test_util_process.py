#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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
from unittest import TestCase
from unittest.mock import MagicMock, patch

import unit.utils as uu
from util.process import blocking_read_stdout
from util.process import ChildProcessFailure
from util.process import current_process_id
from util.process import git_commit_hash
from util.process import is_executable


class TestBlockingReadStdout(TestCase):
    def _setup_mock_popen(self, mock_popen, return_code=0, stdout=b'', stderr=b''):
        def __communicate():
            return stdout, stderr

        mock_popen.return_value = MagicMock(returncode=return_code)
        mock_popen_instance = mock_popen.return_value
        mock_popen_instance.communicate = __communicate

    def test_returns_stdout_of_arbitrary_process_whoami(self):
        actual = blocking_read_stdout('whoami')
        self.assertIsInstance(actual, bytes)
        self.assertTrue(actual, 'stdout should not be empty')

    def test_returns_stdout_of_arbitrary_process_file_dev_null(self):
        actual = blocking_read_stdout('file', '-b', '/dev/null')
        self.assertIsInstance(actual, bytes)
        self.assertIn(b'character special', actual)

    @patch('util.process.subprocess.Popen')
    def test_raises_expected_exception(self, mock_popen):
        self._setup_mock_popen(mock_popen, return_code=-1)

        given_args = 'expect this to fail'
        with self.assertRaises(ChildProcessFailure):
            _ = blocking_read_stdout(given_args)

        self.assertIn(given_args, mock_popen.call_args[0][0])


class TestIsExecutable(TestCase):
    def test_returns_true_for_executable_commands(self):
        self.assertTrue(is_executable('python'))

    def test_returns_false_for_bogus_commands(self):
        self.assertFalse(is_executable('thisisntexecutablesurely'))


class TestGitCommitHash(TestCase):
    def test_returns_expected_type(self):
        actual = git_commit_hash()
        self.assertTrue(uu.is_internalstring(actual))

    def test_resets_curdir(self):
        curdir_before = os.path.curdir
        _ = git_commit_hash()
        curdir_after = os.path.curdir

        self.assertEqual(curdir_before, curdir_after)

    def _setup_mock_popen(self, mock_popen, return_code=None, stdout=None, stderr=None):
        def __communicate():
            return stdout, stderr

        if return_code is None:
            return_code = 0
        if stdout is None:
            stdout = b''

        mock_popen.return_value = MagicMock(returncode=return_code)
        mock_popen_instance = mock_popen.return_value
        mock_popen_instance.communicate = __communicate

    @patch('util.process.subprocess.Popen')
    def test_returns_none_if_repository_not_found(self, mock_popen):
        self._setup_mock_popen(
            mock_popen,
            stdout=b'fatal: Not a git repository (or any of the parent directories): .git\n',
            stderr=None
        )
        # Call 'cache_clear()' added by the 'functools.lru_cache' decorator.
        git_commit_hash.cache_clear()

        actual = git_commit_hash()
        self.assertIsNone(actual)


class TestCurrentProcessId(TestCase):
    def test_returns_expected_type(self):
        self.assertIsInstance(current_process_id(), int)
