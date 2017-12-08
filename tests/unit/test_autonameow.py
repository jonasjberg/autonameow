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

import sys
from unittest import (
    skipIf,
    TestCase
)
from unittest.mock import (
    MagicMock,
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

from core import config
from core import constants as C
from core.autonameow import Autonameow
from core.config.configuration import Configuration


def prompt_toolkit_unavailable():
    return prompt_toolkit is None, 'Failed to import "prompt_toolkit"'


AUTONAMEOW_OPTIONS_EMPTY = {}


@skipIf(*prompt_toolkit_unavailable())
class TestAutonameowWithoutOptions(TestCase):
    # @classmethod
    # def setUpClass(cls):
    #     from core.autonameow import Autonameow
    #     cls.A = Autonameow

    @patch('core.autonameow.Autonameow.exit_program', MagicMock())
    def test_instantiated_instance_is_not_none(self):
        self.assertIsNotNone(Autonameow(opts=AUTONAMEOW_OPTIONS_EMPTY))

    @patch('core.autonameow.Autonameow.exit_program')
    def test_instantiated_does_not_call_exit_program(self, exit_program_mock):
        _ = Autonameow(opts=AUTONAMEOW_OPTIONS_EMPTY)
        exit_program_mock.assert_not_called()

    @patch('core.autonameow.Autonameow.exit_program')
    def test_exit_program_called_after_running(self, exit_program_mock):
        a = Autonameow(opts=AUTONAMEOW_OPTIONS_EMPTY)
        a.run()
        exit_program_mock.assert_called_with(C.EXIT_SUCCESS)

    @patch('core.autonameow.Autonameow.exit_program')
    def test_exit_program_called_after_running_context(self, exit_program_mock):
        with Autonameow(opts=AUTONAMEOW_OPTIONS_EMPTY) as a:
            a.run()
        exit_program_mock.assert_called_with(C.EXIT_SUCCESS)


class TestAutonameowOptionCombinations(TestCase):
    def setUp(self):
        from core.autonameow import Autonameow
        self.a = Autonameow

    def _check_options(self, given, expect):
        actual = self.a.check_option_combinations(given)
        for k, v in expect.items():
            self.assertEqual(actual.get(k), v)

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
        # Expect the "safer" option to take precedence.
        self._check_options(
            given={'mode_batch': True, 'mode_interactive': True,
                   'mode_timid': False},
            expect={'mode_batch': False, 'mode_interactive': True,
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
    def test_with_statement(self):
        from core.autonameow import Autonameow
        Autonameow.exit_program = MagicMock()

        with Autonameow(AUTONAMEOW_OPTIONS_EMPTY) as ameow:
            ameow.run()


class TestAutonameowHash(TestCase):
    def setUp(self):
        from core.autonameow import Autonameow
        self.a = Autonameow(AUTONAMEOW_OPTIONS_EMPTY)
        self.b = Autonameow(AUTONAMEOW_OPTIONS_EMPTY)

    def test_hash(self):
        actual = hash(self.a)
        self.assertIsNotNone(actual)
        self.assertTrue(isinstance(actual, int))

    def test_instances_return_different_hashes(self):
        hash_a = hash(self.a)
        hash_b = hash(self.b)
        self.assertNotEqual(hash_a, hash_b)

    def test_instance_comparison(self):
        self.assertNotEqual(self.a, self.b)
        self.assertTrue(self.a != self.b)
        self.assertTrue(self.a is not self.b)


@skipIf(*prompt_toolkit_unavailable())
class TestSetAutonameowExitCode(TestCase):
    def setUp(self):
        from core.autonameow import Autonameow
        self.amw = Autonameow(AUTONAMEOW_OPTIONS_EMPTY)
        self.expected_initial = C.EXIT_SUCCESS

    def test_exit_code_has_expected_type(self):
        self.assertTrue(isinstance(self.amw.exit_code, int))

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


@skipIf(*prompt_toolkit_unavailable())
class TestDoRename(TestCase):
    def setUp(self):
        from core.autonameow import Autonameow
        self.amw = Autonameow(AUTONAMEOW_OPTIONS_EMPTY)
        self.assertIsNotNone(self.amw)

        _config = Configuration(config.DEFAULT_CONFIG)
        self.amw.active_config = _config

    @patch('core.disk.rename_file')
    def test_dry_run_true_will_not_call_diskutils_rename_file(self, mockrename):
        self.amw.do_rename(b'/tmp/dummy/path', 'mjaopath', dry_run=True)
        mockrename.assert_not_called()

    @patch('core.disk.rename_file')
    def test_dry_run_false_calls_diskutils_rename_file(self, mockrename):
        self.amw.do_rename(b'/tmp/dummy/path', 'mjaopath', dry_run=False)
        mockrename.assert_called_with(b'/tmp/dummy/path', b'mjaopath')

    @patch('core.disk.rename_file')
    def test_skip_rename_if_new_name_equals_old_name(self, mockrename):
        self.amw.do_rename(b'/tmp/dummy/foo', 'foo', dry_run=False)
        mockrename.assert_not_called()

    @patch('core.disk.rename_file')
    def test_skip_rename_if_new_name_equals_old_name_dry_run(self, mockrename):
        self.amw.do_rename(b'/tmp/dummy/foo', 'foo', dry_run=True)
        mockrename.assert_not_called()
