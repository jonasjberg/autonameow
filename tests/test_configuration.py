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
import yaml
from unittest import TestCase

from core.config.configuration import Configuration
from core.config_defaults import NEW_DEFAULT_CONFIG
from unit_utils import make_temp_dir

TEST_CONFIG_DATA = {'key1': 'value1',
                    'key2': ['value2', 'value3'],
                    'key3': {'key4': 'value4',
                             'key5': ['value5', 'value6']}}
TEST_CONFIG_YAML_DATA = '''
key1: value1
key2:
- value2
- value3
key3:
key4: value4
key5:
- value5
- value6
'''


class TestWriteConfig(TestCase):
    def setUp(self):
        self.dest_path = os.path.join(make_temp_dir(), 'test_config.yaml')

        self.configuration = Configuration()
        self.configuration.load_from_dict(TEST_CONFIG_DATA)

    def test_setup(self):
        self.assertFalse(os.path.exists(self.dest_path),
                         'Destination path should not already exist')

    def test_load_from_dict(self):
        self.assertIsNotNone(self.configuration.data,
                             'Configuration data should be loaded')

    def test_write_config(self):
        self.configuration.write_to_disk(self.dest_path)
        self.assertTrue(os.path.exists(self.dest_path),
                        'Configuration file exists on disk')

    def test_write_and_verify(self):
        self.configuration.write_to_disk(self.dest_path)

        def load_yaml(path):
            with open(path, 'r') as file_handle:
                data = yaml.load(file_handle)
            return data

class TestDefaultConfig(TestCase):
    def setUp(self):
        self.configuration = Configuration()
        self.configuration.load_from_dict(NEW_DEFAULT_CONFIG)

    def default_configuration_exists(self):
        self.assertIsNotNone(NEW_DEFAULT_CONFIG)


        expected = load_yaml(self.dest_path)
        self.assertEqual(expected, self.configuration.data,
                         'Loaded, written and then re-read data should match')
