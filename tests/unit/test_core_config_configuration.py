#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

try:
    import yaml
except ImportError:
    yaml = None
    print('Missing required module "yaml". '
          'Make sure "pyyaml" is available before running this program.',
          file=sys.stderr)

import unit.utils as uu
from core.config.configuration import _nested_dict_get
from core.config.default_config import DEFAULT_CONFIG


def yaml_unavailable():
    return yaml is None, 'Failed to import "yaml"'


@skipIf(*yaml_unavailable())
class TestDefaultConfig(TestCase):
    @classmethod
    def setUpClass(cls):
        uu.init_provider_registry()
        cls.configuration = uu.get_default_config()

    def test_default_configuration_exists(self):
        self.assertIsNotNone(DEFAULT_CONFIG,
                             'Default config dict is available')

    def test_default_configuration_contain_rules(self):
        self.assertIsNotNone(self.configuration.rules)

    def test_default_configuration_contain_at_least_two_rules(self):
        # TODO: [hardcoded] Rework or remove ..
        self.assertGreaterEqual(len(self.configuration.rules), 2,
                                'Arbitrary rule count test')

    def test_default_configuration_contain_name_templates(self):
        self.assertIsNotNone(self.configuration.reusable_nametemplates)


@skipIf(*yaml_unavailable())
class TestConfigurationDataAccess(TestCase):
    @classmethod
    def setUpClass(cls):
        uu.init_provider_registry()

    def setUp(self):
        self.configuration = uu.get_default_config()
        self.maxDiff = None

    def test_rules_does_not_return_none(self):
        self.assertIsNotNone(self.configuration.rules)

    def test_rules_returns_expected_type(self):
        self.assertIsInstance(self.configuration.rules, list)

    def test_rules_returns_expected_rule_count(self):
        # TODO: [hardcoded] Rework or remove ..
        self.assertGreaterEqual(len(self.configuration.rules), 3)


TEST_DICTIONARY = {
    'A': {
        'A1': {
            'A1A': 'a',
            'A1B': 'b'
        },
        'A2': {
            'foo': 'c',
        },
        'A3': {
            'A3A': 'd'
        }
    },
    'B': {
        'B1': {
            'B1A': 'e',
            'B1B': 'foo',
        },
        'B2': {
            'B2A': 'g',
            'B2B': 'h'},
        'B3': {
            'B3A': True,
            'B3B': False
        }
    },
}


class TestNestedDictGet(TestCase):
    def _assert_nested_dict_get_returns(self, expected, dictionary, given_key_list):
        with self.subTest():
            actual = _nested_dict_get(dictionary.copy(), *given_key_list)
            self.assertEqual(expected, actual)

    def test_get_nested_value_returns_expected(self):
        self._assert_nested_dict_get_returns(
            'd',
            dictionary=TEST_DICTIONARY,
            given_key_list=['A', 'A3', 'A3A']
        )

    def test_get_nested_values_returns_expected(self):
        keys_expected = [(['A', 'A3', 'A3A'], 'd'),
                         (['A', 'A1', 'A1A'], 'a'),
                         (['A', 'A1', 'A1B'], 'b'),
                         (['A', 'A2', 'foo'], 'c'),
                         (['B', 'B1', 'B1A'], 'e'),
                         (['B', 'B1', 'B1B'], 'foo'),
                         (['B', 'B2', 'B2A'], 'g'),
                         (['B', 'B2', 'B2B'], 'h'),
                         (['B', 'B3', 'B3A'], True),
                         (['B', 'B3', 'B3B'], False)]

        for key_list, expected in keys_expected:
            self._assert_nested_dict_get_returns(expected, TEST_DICTIONARY, key_list)

    def test_missing_keys_raises_key_error(self):
        dictionary = {'a': {'b': {'c': 5}}}

        for given_key_list in [
            [None],
            [''],
            ['q'],
            ['a', 'q'],
            ['a', 'b', 'q'],
            ['a', 'b', 'c', 'q'],
        ]:
            with self.assertRaises(KeyError):
                _ = _nested_dict_get(dictionary, given_key_list)

    def test_none_or_empty_key_raises_key_error(self):
        dictionary = {'a': {'b': {'c': 5}}}

        for given_key_list in [
            None,
            '',
        ]:
            with self.assertRaises(KeyError):
                _ = _nested_dict_get(dictionary, given_key_list)
