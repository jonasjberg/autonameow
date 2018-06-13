#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
#   Personal site:   http://www.jonasjberg.com
#   GitHub:          https://github.com/jonasjberg
#   E-mail:          jomeganas[a]g m a i l[dot]com
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
from unittest.mock import MagicMock, patch

from util.process import ChildProcessError
from util.process import blocking_read_stdout


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
        with self.assertRaises(ChildProcessError):
            _ = blocking_read_stdout(given_args)

        self.assertIn(given_args, mock_popen.call_args[0][0])
