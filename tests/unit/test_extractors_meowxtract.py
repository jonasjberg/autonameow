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
from extractors import meowxtract


# NOTE(jonas): Without patching 'extractors.meowxtract.logs', unit tests in other
#              files might fail due to some shared global state not being reset
#              after THESE tests have completed. This is related to mocking the
#              logging and is obviously a symptom of some bad design choices,
#              that might lead to even worse troubles later on..


def _get_input_paths():
    return [uu.abspath_testfile('magic_txt.txt')]


def _get_input_fileobject():
    return uu.fileobject_testfile('magic_txt.txt')


class TestMeowxtractExtract(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.input_paths = _get_input_paths()
        cls.input_fileobject = _get_input_fileobject()

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

    @patch('extractors.meowxtract.logs', MagicMock())
    def _assert_exit_success(self, options=None):
        with self.assertRaises(SystemExit) as e:
            meowxtract.main(options)
            self.assertEqual(e.type, SystemExit)
            self.assertEqual(e.value.code, C.EXIT_SUCCESS)

    def test_exits_with_exit_success_if_not_given_any_options(self):
        self._assert_exit_success()

    def test_exits_with_exit_success_if_given_empty_list_of_input_paths(self):
        options = {'input_paths': []}
        self._assert_exit_success(options)

    def test_exits_with_exit_success_if_given_input_paths_but_no_actions(self):
        options = {'input_paths': self.input_paths}
        self._assert_exit_success(options)


class TestMeowxtractExtractTextExtraction(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.input_paths = _get_input_paths()
        cls.input_fileobject = _get_input_fileobject()

    @patch('extractors.meowxtract.logs', MagicMock())
    @patch('extractors.meowxtract.do_extract_text')
    def test_extract_text(self, mock_do_extract_text):
        options = {'input_paths': self.input_paths,
                   'extract_text': True}
        meowxtract.main(options)
        mock_do_extract_text.assert_called_once_with(self.input_fileobject)

    @patch('extractors.meowxtract.logs', MagicMock())
    @patch('extractors.meowxtract.do_extract_text')
    def test_extract_text_without_input_paths(self, mock_do_extract_text):
        options = {'extract_text': True}
        with self.assertRaises(SystemExit) as e:
            meowxtract.main(options)
            self.assertEqual(e.type, SystemExit)
            self.assertEqual(e.value.code, C.EXIT_SUCCESS)
        mock_do_extract_text.assert_not_called()


class TestMeowxtractExtractMetadataExtraction(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.input_paths = _get_input_paths()
        cls.input_fileobject = _get_input_fileobject()

    @patch('extractors.meowxtract.logs', MagicMock())
    @patch('extractors.meowxtract.do_extract_metadata')
    def test_extract_metadata(self, mock_do_extract_metadata):
        options = {'input_paths': self.input_paths,
                   'extract_metadata': True}
        meowxtract.main(options)
        mock_do_extract_metadata.assert_called_once_with(self.input_fileobject)

    @patch('extractors.meowxtract.logs', MagicMock())
    @patch('extractors.meowxtract.do_extract_metadata')
    def test_extract_metadata_without_input_paths(self, mock_do_extract_metadata):
        options = {'extract_metadata': True}
        with self.assertRaises(SystemExit) as e:
            meowxtract.main(options)
            self.assertEqual(e.type, SystemExit)
            self.assertEqual(e.value.code, C.EXIT_SUCCESS)
        mock_do_extract_metadata.assert_not_called()


class TestMeowxtractExtractTextAndMetadataExtraction(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.input_paths = _get_input_paths()
        cls.input_fileobject = _get_input_fileobject()

    @patch('extractors.meowxtract.logs', MagicMock())
    @patch('extractors.meowxtract.do_extract_text')
    @patch('extractors.meowxtract.do_extract_metadata')
    def test_extract_text_and_metadata(self, mock_do_extract_metadata, mock_do_extract_text):
        options = {'input_paths': self.input_paths,
                   'extract_metadata': True,
                   'extract_text': True}
        meowxtract.main(options)
        mock_do_extract_metadata.assert_called_once_with(self.input_fileobject)
        mock_do_extract_text.assert_called_once_with(self.input_fileobject)
