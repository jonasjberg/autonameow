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
from unittest.mock import MagicMock

from core import constants
from core.autonameow import (
    Autonameow,
)
from unit_utils import capture_stdout


class TestAutonameowWithoutOptions(TestCase):
    def setUp(self):
        self.autonameow = Autonameow('')
        self.autonameow.exit_program = MagicMock()

    def test_autonameow_can_be_instantiated_without_opts(self):
        self.assertIsNotNone(self.autonameow)

    def test_prints_help_when_started_without_opts(self):
        with capture_stdout() as out:
            self.autonameow.run()

        # NOTE: [hardcoded] Likely to break if usage help text is changed.
        self.assertIn('"--help"', out.getvalue().strip())

    def test_exits_program_successfully_when_started_without_opts(self):
        self.autonameow.run()
        self.autonameow.exit_program.assert_called_with(constants.EXIT_SUCCESS)


class TestSetAutonameowExitCode(TestCase):
    def setUp(self):
        self.amw = Autonameow('')
        self.expected_initial = constants.EXIT_SUCCESS

    def test_exit_code_has_expected_type(self):
        self.assertTrue(isinstance(self.amw.exit_code, int))

    def test_exit_code_defaults_to_expected_value(self):
        self.assertEqual(self.expected_initial, self.amw.exit_code)

    def test_exit_code_is_not_changed_when_set_to_lower_value(self):
        self.amw.exit_code = constants.EXIT_WARNING
        self.assertEqual(self.amw.exit_code, constants.EXIT_WARNING)

        self.amw.exit_code = constants.EXIT_SUCCESS
        self.assertEqual(self.amw.exit_code, constants.EXIT_WARNING)

    def test_exit_code_is_changed_when_set_to_higher_value(self):
        self.amw.exit_code = constants.EXIT_WARNING
        self.assertEqual(self.amw.exit_code, constants.EXIT_WARNING)

        self.amw.exit_code = constants.EXIT_ERROR
        self.assertEqual(self.amw.exit_code, constants.EXIT_ERROR)

    def test_exit_code_ignores_invalid_values(self):
        self.assertEqual(self.expected_initial, self.amw.exit_code)
        self.amw.exit_code = None
        self.assertEqual(self.expected_initial, self.amw.exit_code)
        self.amw.exit_code = '1'
        self.assertEqual(self.expected_initial, self.amw.exit_code)
        self.amw.exit_code = 'mjao'
        self.assertEqual(self.expected_initial, self.amw.exit_code)
