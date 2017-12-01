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

import unit.unit_utils as uu
import unit.unit_utils_constants as uuconst
from core import constants as C
from core import exceptions
from core.config.configuration import Configuration
from core.config.default_config import DEFAULT_CONFIG
from util import encoding as enc


uu.init_session_repository()


def yaml_unavailable():
    return yaml is None, 'Failed to import "yaml"'


def load_yaml(path):
    if yaml is None:
        raise AssertionError('Missing required module "yaml". Install "pyyaml"')

    with open(path, 'r', encoding=C.DEFAULT_ENCODING) as fh:
        data = yaml.safe_load(fh)
    return data


def get_temporary_config_path():
    return enc.normpath(
        os.path.join(enc.syspath(uu.make_temp_dir()),
                     enc.syspath(b'test_config.yaml'))
    )


@skipIf(*yaml_unavailable())
class TestWriteConfig(TestCase):
    def setUp(self):
        self.dest_path = get_temporary_config_path()
        self.configuration = Configuration(DEFAULT_CONFIG)

    def test_setup(self):
        self.assertFalse(uu.file_exists(self.dest_path),
                         'Destination path should not already exist')

    def test_load_from_dict(self):
        self.configuration._load_from_dict(DEFAULT_CONFIG)
        self.assertIsNotNone(self.configuration.data,
                             'Configuration data should be loaded')

    def test_write_config(self):
        self.configuration.write_to_disk(self.dest_path)
        self.assertTrue(uu.file_exists(self.dest_path),
                        'Configuration file exists on disk')

    def test_write_and_verify(self):
        self.configuration.write_to_disk(self.dest_path)

        expected = load_yaml(self.dest_path)
        self.assertEqual(expected, self.configuration.data,
                         'Loaded, written and then re-read data should match')


@skipIf(*yaml_unavailable())
class TestDefaultConfig(TestCase):
    def setUp(self):
        self.configuration = Configuration(DEFAULT_CONFIG)

    def test_default_configuration_exists(self):
        self.assertIsNotNone(DEFAULT_CONFIG,
                             'Default config dict is available')

    def test_default_configuration_contain_rules(self):
        self.assertIsNotNone(self.configuration.rules)

    def test_default_configuration_contain_at_least_two_rules(self):
        self.assertGreaterEqual(len(self.configuration.rules), 2,
                                'Arbitrary rule count test')

    def test_default_configuration_contain_name_templates(self):
        self.assertIsNotNone(self.configuration.reusable_nametemplates)


@skipIf(*yaml_unavailable())
class TestDefaultConfigFromFile(TestCase):
    def setUp(self):
        self.config_path_unicode = uu.abspath_testfile(
            uuconst.DEFAULT_YAML_CONFIG_BASENAME
        )
        uu.file_exists(self.config_path_unicode)
        uu.path_is_readable(self.config_path_unicode)
        self.assertTrue(uu.is_internalstring(self.config_path_unicode))

        self.config_path_bytestring = uu.normpath(self.config_path_unicode)
        uu.file_exists(self.config_path_bytestring)
        uu.path_is_readable(self.config_path_bytestring)
        self.assertTrue(uu.is_internalbytestring(self.config_path_bytestring))

    def test_loads_default_config_from_bytestring_path(self):
        config = Configuration.from_file(self.config_path_bytestring)
        self.assertIsNotNone(config)

    def test_loading_unicode_path_raises_exception(self):
        with self.assertRaises(exceptions.EncodingBoundaryViolation):
            config = Configuration.from_file(self.config_path_unicode)


@skipIf(*yaml_unavailable())
class TestWriteDefaultConfig(TestCase):
    # Show contents of most recent temporary log on Mac OS;
    # cat "$(find /var/folders -type f -name "test_default_config.yaml" -exec stat -f %m %N {} \; 2>/dev/null | sort -n | cut -f2 -d  | tail -n 1)"

    def setUp(self):
        self.dest_path = get_temporary_config_path()
        self.configuration = Configuration(DEFAULT_CONFIG)

    def test_setup(self):
        self.assertFalse(uu.file_exists(self.dest_path),
                         'Destination path should not already exist')
        self.assertIsNotNone(self.configuration.data,
                             'Configuration data should exist')

    def test_write_default_config_to_disk(self):
        self.configuration.write_to_disk(self.dest_path)
        self.assertTrue(uu.file_exists(self.dest_path),
                        'Default configuration file exists on disk')

    def test_write_default_config_to_disk_and_verify(self):
        self.configuration.write_to_disk(self.dest_path)

        expected = load_yaml(self.dest_path)
        self.assertEqual(expected, self.configuration.data,
                         'Loaded, written and then re-read data should match')


@skipIf(*yaml_unavailable())
class TestConfigurationInit(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.configuration = Configuration(DEFAULT_CONFIG)


@skipIf(*yaml_unavailable())
class TestConfigurationDataAccess(TestCase):
    def setUp(self):
        self.configuration = Configuration(DEFAULT_CONFIG)
        self.maxDiff = None

    def test_data_does_not_return_none(self):
        self.assertIsNotNone(self.configuration.data)

    def test_rules_does_not_return_none(self):
        self.assertIsNotNone(self.configuration.rules)

    def test_rules_returns_expected_type(self):
        self.assertTrue(isinstance(self.configuration.rules, list))

    def test_rules_returns_expected_rule_count(self):
        self.assertGreaterEqual(len(self.configuration.rules), 3)

    def test_name_templates_returns_expected_type(self):
        self.assertTrue(isinstance(self.configuration.name_templates, list))
