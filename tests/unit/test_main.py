#!/usr/bin/env python3
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
from unittest.mock import (
    MagicMock,
    patch
)

import unit.constants as uuconst
import unit.utils as uu
from core import constants as C
from core.main import cli_main


class TestMainFileExistsAndIsExecutable(TestCase):
    def setUp(self):
        self.main_file = os.path.normpath(os.path.join(
            uuconst.AUTONAMEOW_SRCROOT_DIR, '__main__.py'
        ))

    def test_assumed_main_source_file_exists(self):
        self.assertTrue(uu.file_exists(self.main_file))

    def test_assumed_main_source_file_is_a_file(self):
        self.assertTrue(uu.file_exists(self.main_file))

    def test_assumed_main_source_file_is_readable(self):
        self.assertTrue(os.access(self.main_file, os.R_OK))

    def test_assumed_main_source_file_is_executable(self):
        self.assertTrue(os.access(self.main_file, os.X_OK))


class TestCliMain(TestCase):
    EMPTY_COMMANDLINE_OPTIONS = []

    @patch('core.main.sys.exit', MagicMock())
    def test_prints_help_when_started_without_args(self):
        with uu.capture_stdout() as out:
            cli_main(self.EMPTY_COMMANDLINE_OPTIONS)

        # NOTE: [hardcoded] Likely to break if usage help text is changed.
        self.assertIn('"--help"', out.getvalue().strip())

    @patch('core.main.sys.exit')
    @patch('core.main.Autonameow.exit_program')
    def test_exits_with_expected_return_code_when_started_without_args(
            self, exit_program_mock, sys_exit_mock):

        cli_main(self.EMPTY_COMMANDLINE_OPTIONS)

        exit_program_mock.assert_called_with(C.EXIT_SUCCESS)
        sys_exit_mock.assert_called_with(C.EXIT_SUCCESS)
