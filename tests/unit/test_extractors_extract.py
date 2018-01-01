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

from unittest import TestCase
from unittest.mock import (
    MagicMock,
    patch
)

import unit.utils as uu
from core import constants as C
from extractors import extract


# NOTE(jonas): Without patching 'extractors.extract.logs', unit tests in other
#              files might fail due to some shared global state not being reset
#              after THESE tests have completed. This is related to mocking the
#              logging and is obviously a symptom of some bad design choices,
#              that might lead to even worse troubles later on..


class TestStandaloneExtract(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.input_paths = [uu.abspath_testfile('magic_txt.txt')]
        cls.input_fileobject = uu.fileobject_testfile('magic_txt.txt')

    # NOTE(jonas): Without this patch, other unit tests will fail!
    #
    # 'test_stderr_contains_no_input_files_specified' in 'test_regression_utils.py'
    #
    # Failure
    # Traceback (most recent call last):
    #   File "/usr/lib/python3.5/unittest/case.py", line 58, in testPartExecutor
    #     yield
    #   File "/usr/lib/python3.5/unittest/case.py", line 600, in run
    #     testMethod()
    #   File "/home/jonas/dev/projects/autonameow.git/tests/unit/test_regression_utils.py", line 361, in test_stderr_contains_no_input_files_specified
    #     self.assertIn('No input files specified', actual)
    #   File "/usr/lib/python3.5/unittest/case.py", line 1079, in assertIn
    #     self.fail(self._formatMessage(msg, standardMsg))
    #   File "/usr/lib/python3.5/unittest/case.py", line 665, in fail
    #     raise self.failureException(msg)
    # AssertionError: 'No input files specified' not found in ''

    @patch('extractors.extract.logs', MagicMock())
    def test_exits_with_exit_success_if_not_given_any_input_paths(self):
        with self.assertRaises(SystemExit) as e:
            extract.main()
            self.assertEqual(e.type, SystemExit)
            self.assertEqual(e.value.code, C.EXIT_SUCCESS)

    @patch('extractors.extract.logs', MagicMock())
    def test_exits_with_exit_success_if_not_specifying_actions(self):
        _options = {'input_paths': self.input_paths}
        with self.assertRaises(SystemExit) as e:
            extract.main(_options)
            self.assertEqual(e.type, SystemExit)
            self.assertEqual(e.value.code, C.EXIT_SUCCESS)

    @patch('extractors.extract.logs', MagicMock())
    @patch('extractors.extract.do_extract_text')
    def test_extract_text(self, mock_do_extract_text):
        _options = {'input_paths': self.input_paths,
                    'extract_text': True}
        extract.main(_options)
        mock_do_extract_text.assert_called_once_with(self.input_fileobject)

    @patch('extractors.extract.logs', MagicMock())
    @patch('extractors.extract.do_extract_metadata')
    def test_extract_metadata(self, mock_do_extract_metadata):
        _options = {'input_paths': self.input_paths,
                    'extract_metadata': True}
        extract.main(_options)
        mock_do_extract_metadata.assert_called_once_with(self.input_fileobject)

    @patch('extractors.extract.logs', MagicMock())
    @patch('extractors.extract.do_extract_text')
    @patch('extractors.extract.do_extract_metadata')
    def test_extract_text_and_metadata(self, mock_do_extract_metadata,
                                       mock_do_extract_text):
        _options = {'input_paths': self.input_paths,
                    'extract_metadata': True,
                    'extract_text': True}
        extract.main(_options)
        mock_do_extract_metadata.assert_called_once_with(self.input_fileobject)
        mock_do_extract_text.assert_called_once_with(self.input_fileobject)
