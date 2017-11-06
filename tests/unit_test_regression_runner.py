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

from unittest import TestCase

from core import constants as C
from regression_runner import AutonameowWrapper


class TestTemporaryStuff(TestCase):
    # from core.config import write_yaml_file
    # def test_temporary_write_testdata(self):
    #     _test_data = {
    #         '../../gmail.pdf': {
    #             'basename': '2016-01-11T124132 gmail.pdf'
    #         }
    #     }
    #     write_yaml_file(b'/tmp/test.yaml', _test_data)
    #
    # def test_temporary_write_options(self):
    #     _opts = {'debug': False, 'verbose': True, 'quiet': False, 'show_version': False, 'dump_config': False, 'dump_options': False, 'dump_meowuris': False, 'list_all': True, 'list_datetime': False, 'list_title': False, 'mode_batch': True, 'mode_automagic': True, 'mode_interactive': False, 'config_path': None, 'dry_run': True, 'recurse_paths': False, 'input_paths': ['/Users/jonas/PycharmProjects/autonameow.git/test_files/gmail.pdf']}
    #     write_yaml_file(b'/tmp/test_options.yaml', _opts)

    def test_noop(self):
        self.assertTrue(True)


class TestAutonameowWrapper(TestCase):
    def setUp(self):
        self.aw = AutonameowWrapper()

    def test_call(self):
        self.aw()

    def test_captured_exit_code_type(self):
        self.aw()
        actual = self.aw.exit_code
        self.assertIsNotNone(actual)
        self.assertTrue(type(actual), int)

    def test_captured_stdout_type(self):
        self.aw()
        actual = self.aw.captured_stdout
        self.assertIsNotNone(actual)
        self.assertTrue(type(actual), str)

    def test_captured_stderr_type(self):
        self.aw()
        actual = self.aw.captured_stderr
        self.assertIsNotNone(actual)
        self.assertTrue(type(actual), str)


class TestAutonameowWrapperWithDefaultOptions(TestCase):
    def setUp(self):
        self.aw = AutonameowWrapper()
        self.aw()

    def test_exit_code_is_exit_success(self):
        actual = self.aw.exit_code
        self.assertEqual(actual, C.EXIT_SUCCESS)

    def test_stderr_contains_no_input_files_specified(self):
        actual = self.aw.captured_stderr
        self.assertIn('No input files specified', actual)

    def test_stdout_is_empty(self):
        actual = self.aw.captured_stdout
        self.assertIn('', actual)
