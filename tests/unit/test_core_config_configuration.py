#!/usr/bin/env python3
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

try:
    import yaml
except ImportError:
    yaml = None
    print('Missing required module "yaml". '
          'Make sure "pyyaml" is available before running this program.',
          file=sys.stderr)

import unit.utils as uu
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

    def test_name_templates_returns_expected_type(self):
        self.assertIsInstance(self.configuration.name_templates, list)
