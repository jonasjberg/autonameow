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

import sys
from unittest import (
    skipIf,
    TestCase
)
from unittest.mock import (
    MagicMock,
    Mock,
    patch
)

try:
    import prompt_toolkit
except ImportError:
    prompt_toolkit = None
    print(
        'Missing required module "prompt_toolkit". '
        'Make sure "prompt_toolkit" is available before running this program.',
        file=sys.stderr
    )

from core import constants as C
from core.autonameow import (
    Autonameow,
    check_option_combinations
)


def prompt_toolkit_unavailable():
    return prompt_toolkit is None, 'Failed to import "prompt_toolkit"'


AUTONAMEOW_OPTIONS_EMPTY = dict()
MOCK_UI = Mock()


@skipIf(*prompt_toolkit_unavailable())
class TestAutonameowWithoutOptions(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.amw = Autonameow

    @patch('core.autonameow.Autonameow.exit_program', MagicMock())
    @patch('core.autonameow.master_provider', MagicMock())
    def test_instantiated_instance_is_not_none(self):
        self.assertIsNotNone(self.amw(opts=AUTONAMEOW_OPTIONS_EMPTY, ui=MOCK_UI))

    @patch('core.autonameow.Autonameow.exit_program')
    @patch('core.autonameow.master_provider', MagicMock())
    def test_instantiated_does_not_call_exit_program(self, exit_program_mock):
        _ = self.amw(opts=AUTONAMEOW_OPTIONS_EMPTY, ui=MOCK_UI)
        exit_program_mock.assert_not_called()

    # TODO: [cleanup] This much mocking indicates poor design choices ..
    @patch('core.providers.initialize', MagicMock())
    @patch('core.providers.Registry')
    @patch('core.autonameow.Autonameow.exit_program')
    @patch('core.autonameow.master_provider', MagicMock())
    def test_exit_program_called_after_running_context(
            self, exit_program_mock, mock_registry
    ):
        mock_registry.might_be_resolvable.return_value = True

        with self.amw(opts=AUTONAMEOW_OPTIONS_EMPTY, ui=MOCK_UI) as a:
            a.run()
        exit_program_mock.assert_called_with(C.EXIT_SUCCESS)


class TestCheckOptionCombinations(TestCase):
    def _check_options(self, given, expect):
        actual_options = check_option_combinations(given)
        for option, expected_value in expect.items():
            actual_value = actual_options.get(option)
            self.assertEqual(actual_value, expected_value,
                             'Expected {} to be {} but got {}'.format(
                                 option, expected_value, actual_value))

    def test_valid_user_interaction_combination(self):
        self._check_options(
            given={'mode_batch': False, 'mode_interactive': False},
            expect={'mode_batch': False, 'mode_interactive': False}
        )
        self._check_options(
            given={'mode_batch': True, 'mode_interactive': False},
            expect={'mode_batch': True, 'mode_interactive': False}
        )
        self._check_options(
            given={'mode_batch': False, 'mode_interactive': True},
            expect={'mode_batch': False, 'mode_interactive': True}
        )

    def test_illegal_user_interaction_combination(self):
        # Expect "batch" to disable all requirements of user interaction.
        self._check_options(
            given={'mode_batch': True, 'mode_interactive': True,
                   'mode_timid': False},
            expect={'mode_batch': True, 'mode_interactive': False,
                    'mode_timid': False}
        )
        self._check_options(
            given={'mode_batch': True, 'mode_interactive': False,
                   'mode_timid': True},
            expect={'mode_batch': True, 'mode_interactive': False,
                    'mode_timid': False}
        )
        self._check_options(
            given={'mode_batch': True, 'mode_interactive': True,
                   'mode_timid': True},
            expect={'mode_batch': True, 'mode_interactive': False,
                    'mode_timid': False}
        )

        # Interactive is basically a superset of timid.
        self._check_options(
            given={'mode_batch': False, 'mode_interactive': True,
                   'mode_timid': True},
            expect={'mode_batch': False, 'mode_interactive': True,
                    'mode_timid': False}
        )

    def test_valid_operating_mode_combination(self):
        self._check_options(
            given={'mode_automagic': False, 'mode_rulematch': True},
            expect={'mode_automagic': False, 'mode_rulematch': True}
        )
        self._check_options(
            given={'mode_automagic': True, 'mode_rulematch': False},
            expect={'mode_automagic': True, 'mode_rulematch': True}
        )
        self._check_options(
            given={'mode_automagic': True, 'mode_rulematch': True},
            expect={'mode_automagic': True, 'mode_rulematch': True}
        )

    def test_default_operating_mode_combination(self):
        # Always enable rule-matching for now.
        # TODO: Really enable options like this? Better to error out and exit?
        self._check_options(
            given={'mode_automagic': False, 'mode_rulematch': False},
            expect={'mode_automagic': False, 'mode_rulematch': True}
        )

    def test_user_interaction_and_operating_mode_combination(self):
        self._check_options(
            given={'mode_automagic': False, 'mode_rulematch': False,
                   'mode_batch': False},
            expect={'mode_automagic': False, 'mode_rulematch': True,
                    'mode_batch': False}
        )
        self._check_options(
            given={'mode_automagic': False, 'mode_rulematch': True,
                   'mode_batch': False},
            expect={'mode_automagic': False, 'mode_rulematch': True,
                    'mode_batch': False}
        )
        self._check_options(
            given={'mode_automagic': True, 'mode_rulematch': False,
                   'mode_batch': False},
            expect={'mode_automagic': True, 'mode_rulematch': True,
                    'mode_batch': False}
        )

    def test_illegal_user_interaction_and_operating_mode_combination(self):
        # Always enable rule-matching for now.
        # TODO: Really enable options like this? Better to error out and exit?
        self._check_options(
            given={'mode_automagic': False, 'mode_rulematch': False,
                   'mode_batch': True},
            expect={'mode_automagic': False, 'mode_rulematch': True,
                    'mode_batch': True}
        )


class TestAutonameowContextManagementProtocol(TestCase):
    # TODO: [cleanup] This much mocking indicates poor design choices ..
    @patch('core.autonameow.master_provider', MagicMock())
    @patch('core.providers.initialize', MagicMock())
    @patch('core.providers.Registry')
    def test_with_statement(self, mock_registry):
        mock_registry.might_be_resolvable.return_value = True
        Autonameow.exit_program = MagicMock()

        with Autonameow(AUTONAMEOW_OPTIONS_EMPTY, MOCK_UI) as ameow:
            ameow.run()


class TestAutonameowHash(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.amw_A = Autonameow(AUTONAMEOW_OPTIONS_EMPTY, MOCK_UI)
        cls.amw_B = Autonameow(AUTONAMEOW_OPTIONS_EMPTY, MOCK_UI)

    def test_setup_class(self):
        self.assertIsNotNone(self.amw_A)
        self.assertIsNotNone(self.amw_B)

    def test_hash(self):
        actual = hash(self.amw_A)
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, int)

    def test_instances_return_different_hashes(self):
        hash_a = hash(self.amw_A)
        hash_b = hash(self.amw_B)
        self.assertNotEqual(hash_a, hash_b)

    def test_instance_comparison(self):
        self.assertNotEqual(self.amw_A, self.amw_B)
        self.assertTrue(self.amw_A != self.amw_B)
        self.assertTrue(self.amw_A is not self.amw_B)


@skipIf(*prompt_toolkit_unavailable())
class TestSetAutonameowExitCode(TestCase):
    def setUp(self):
        self.amw = Autonameow(AUTONAMEOW_OPTIONS_EMPTY, MOCK_UI)
        self.expected_initial = C.EXIT_SUCCESS

    def test_setup(self):
        self.assertIsNotNone(self.amw)

    def test_exit_code_has_expected_type(self):
        self.assertIsInstance(self.amw.exit_code, int)

    def test_exit_code_defaults_to_expected_value(self):
        self.assertEqual(self.amw.exit_code, self.expected_initial)

    def test_exit_code_is_not_changed_when_set_to_lower_value(self):
        self.amw.exit_code = C.EXIT_WARNING
        self.assertEqual(self.amw.exit_code, C.EXIT_WARNING)

        self.amw.exit_code = C.EXIT_SUCCESS
        self.assertEqual(self.amw.exit_code, C.EXIT_WARNING)

    def test_exit_code_is_changed_when_set_to_higher_value(self):
        self.amw.exit_code = C.EXIT_WARNING
        self.assertEqual(self.amw.exit_code, C.EXIT_WARNING)

        self.amw.exit_code = C.EXIT_ERROR
        self.assertEqual(self.amw.exit_code, C.EXIT_ERROR)

    def test_exit_code_ignores_invalid_values(self):
        self.assertEqual(self.amw.exit_code, self.expected_initial)
        self.amw.exit_code = None
        self.assertEqual(self.amw.exit_code, self.expected_initial)
        self.amw.exit_code = '1'
        self.assertEqual(self.amw.exit_code, self.expected_initial)
        self.amw.exit_code = 'mjao'
        self.assertEqual(self.amw.exit_code, self.expected_initial)
