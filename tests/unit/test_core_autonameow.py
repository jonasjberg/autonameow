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

import sys
from unittest import skipIf, TestCase
from unittest.mock import MagicMock, Mock, patch

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
from core.autonameow import Autonameow
from core.autonameow import check_option_combinations


def prompt_toolkit_unavailable():
    return prompt_toolkit is None, 'Failed to import "prompt_toolkit"'


AUTONAMEOW_OPTIONS_EMPTY = dict()
MOCK_UI = Mock()


def _get_autonameow(*args, **kwargs):
    return Autonameow(
        opts=kwargs.get('opts', AUTONAMEOW_OPTIONS_EMPTY),
        ui=kwargs.get('ui', MOCK_UI),
    )


@skipIf(*prompt_toolkit_unavailable())
class TestAutonameow(TestCase):
    @patch('core.autonameow.master_provider', MagicMock())
    def test_instantiated_instance_is_not_none(self):
        instance = _get_autonameow()
        self.assertIsNotNone(instance)

    # TODO: [cleanup] This much mocking indicates poor design choices ..
    @patch('core.master_provider._initialize_master_data_provider', MagicMock())
    @patch('core.master_provider.Registry')
    @patch('core.autonameow.master_provider', MagicMock())
    def test_returns_exit_code_success(
            self, mock_registry
    ):
        mock_registry.might_be_resolvable.return_value = True

        with _get_autonameow() as a:
            exitcode = a.run()

        self.assertEqual(C.EXIT_SUCCESS, exitcode)


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
            given={'batch': False,
                   'interactive': False},
            expect={'batch': False,
                    'interactive': False}
        )
        self._check_options(
            given={'batch': True,
                   'interactive': False},
            expect={'batch': True,
                    'interactive': False}
        )
        self._check_options(
            given={'batch': False,
                   'interactive': True},
            expect={'batch': False,
                    'interactive': True}
        )

    def test_illegal_user_interaction_combination(self):
        # Only "batch" is a no-op
        self._check_options(
            given={'batch': True,
                   'interactive': False,
                   'timid': False},
            expect={'batch': True,
                    'interactive': False,
                    'timid': False}
        )
        # Mode "batch" disables "interactive"
        self._check_options(
            given={'batch': True,
                   'interactive': True,
                   'timid': False},
            expect={'batch': True,
                    'interactive': False,
                    'timid': False}
        )
        # Mode "batch" should not affect "timid"
        self._check_options(
            given={'batch': True,
                   'interactive': False,
                   'timid': True},
            expect={'batch': True,
                    'interactive': False,
                    'timid': True}
        )
        self._check_options(
            given={'batch': True,
                   'interactive': True,
                   'timid': True},
            expect={'batch': True,
                    'interactive': False,
                    'timid': True}
        )
        # Mode "interactive" is basically a superset of "timid"
        self._check_options(
            given={'batch': False,
                   'interactive': True,
                   'timid': True},
            expect={'batch': False,
                    'interactive': True,
                    'timid': False}
        )

    def test_user_interaction_and_operating_mode_combination(self):
        self._check_options(
            given={'automagic': False,
                   'batch': False},
            expect={'automagic': False,
                    'batch': False}
        )
        self._check_options(
            given={'automagic': True,
                   'batch': False},
            expect={'automagic': True,
                    'batch': False}
        )
        self._check_options(
            given={'automagic': False,
                   'batch': True},
            expect={'automagic': False,
                    'batch': True}
        )

    def test_postprocess_only(self):
        self._check_options(
            given={
                'automagic': False,
                'batch': False,
                'postprocess_only': True
            },
            expect={
                'automagic': False,
                'batch': False,
                'postprocess_only': True
            }
        )

    def test_postprocess_only_combined_with_batch_is_valid(self):
        self._check_options(
            given={
                'automagic': False,
                'batch': True,
                'postprocess_only': True
            },
            expect={
                'automagic': False,
                'batch': True,
                'postprocess_only': True
            }
        )

    def test_illegal_postprocess_only_and_automagic_combination(self):
        self._check_options(
            given={
                'automagic': True,
                'batch': False,
                'postprocess_only': True
            },
            expect={
                'automagic': False,
                'batch': False,
                'postprocess_only': True
            }
        )

    def test_illegal_batch_postprocess_only_and_automagic_combination(self):
        self._check_options(
            given={
                'automagic': True,
                'batch': True,
                'postprocess_only': True
            },
            expect={
                'automagic': False,
                'batch': True,
                'postprocess_only': True
            }
        )


class TestAutonameowHash(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.amw_A = _get_autonameow()
        cls.amw_B = _get_autonameow()

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
        self.amw = _get_autonameow()
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
