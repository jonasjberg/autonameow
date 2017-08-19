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
import unit_utils as uu

import yaml

from core import constants
from core.config.default_config import DEFAULT_CONFIG
from core.config.configuration import (
    Configuration,
    parse_conditions,
    parse_ranking_bias,
    is_valid_source,
)
from core.exceptions import ConfigurationSyntaxError


def load_yaml(path):
    with open(path, 'r') as file_handle:
        data = yaml.load(file_handle)
    return data


class TestWriteConfig(TestCase):
    def setUp(self):
        self.dest_path = os.path.join(uu.make_temp_dir(), 'test_config.yaml')

        self.configuration = Configuration(DEFAULT_CONFIG)

    def test_setup(self):
        self.assertFalse(os.path.exists(self.dest_path),
                         'Destination path should not already exist')

    def test_load_from_dict(self):
        self.configuration._load_from_dict(DEFAULT_CONFIG)
        self.assertIsNotNone(self.configuration.data,
                             'Configuration data should be loaded')

    def test_write_config(self):
        self.configuration.write_to_disk(self.dest_path)
        self.assertTrue(os.path.exists(self.dest_path),
                        'Configuration file exists on disk')

    def test_write_and_verify(self):
        self.configuration.write_to_disk(self.dest_path)

        expected = load_yaml(self.dest_path)
        self.assertEqual(expected, self.configuration.data,
                         'Loaded, written and then re-read data should match')


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
        self.assertIsNotNone(self.configuration.name_templates)


class TestWriteDefaultConfig(TestCase):
    # Show contents of most recent temporary log on Mac OS;
    # cat "$(find /var/folders -type f -name "test_default_config.yaml" -exec stat -f %m %N {} \; 2>/dev/null | sort -n | cut -f2 -d  | tail -n 1)"

    def setUp(self):
        self.dest_path = os.path.join(uu.make_temp_dir(),
                                      'test_default_config.yaml')

        self.configuration = Configuration(DEFAULT_CONFIG)

    def test_setup(self):
        self.assertFalse(os.path.exists(self.dest_path),
                         'Destination path should not already exist')
        self.assertIsNotNone(self.configuration.data,
                             'Configuration data should exist')

    def test_write_default_config_to_disk(self):
        self.configuration.write_to_disk(self.dest_path)
        self.assertTrue(os.path.exists(self.dest_path),
                        'Default configuration file exists on disk')

    def test_write_default_config_to_disk_and_verify(self):
        self.configuration.write_to_disk(self.dest_path)

        expected = load_yaml(self.dest_path)
        self.assertEqual(expected, self.configuration.data,
                         'Loaded, written and then re-read data should match')


class TestConfigurationInit(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.configuration = Configuration(DEFAULT_CONFIG)


class TestConfigurationDataAccess(TestCase):
    def setUp(self):
        self.configuration = Configuration(DEFAULT_CONFIG)
        self.maxDiff = None

    def test_get_data_does_not_return_none(self):
        self.assertIsNotNone(self.configuration.data)

    def test_get_file_rules_does_not_return_none(self):
        self.assertIsNotNone(self.configuration.rules)

    def test_get_file_rules_returns_expected_type(self):
        self.assertTrue(isinstance(self.configuration.rules, list))

    def test_get_file_rules_returns_expected_rule_count(self):
        self.assertGreaterEqual(len(self.configuration.rules), 3)


class TestParseConditions(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_parse_condition_filesystem_pathname_is_valid(self):
        raw_conditions = {'filesystem.pathname.full': '~/.config'}
        actual = parse_conditions(raw_conditions)
        self.assertEqual(actual[0].query_string, 'filesystem.pathname.full')
        self.assertEqual(actual[0].expression, '~/.config')

    def test_parse_condition_contents_mime_type_is_valid(self):
        raw_conditions = {'filesystem.contents.mime_type': 'image/jpeg'}
        actual = parse_conditions(raw_conditions)
        self.assertEqual(actual[0].query_string,
                         'filesystem.contents.mime_type')
        self.assertEqual(actual[0].expression,
                         'image/jpeg')

    def test_parse_condition_contents_metadata_is_valid(self):
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        raw_conditions = {
            'metadata.exiftool.EXIF:DateTimeOriginal': 'Defined',
        }
        actual = parse_conditions(raw_conditions)
        self.assertEqual(actual[0].query_string,
                         'metadata.exiftool.EXIF:DateTimeOriginal')
        self.assertEqual(actual[0].expression, 'Defined')


class TestParseRankingBias(TestCase):
    def test_negative_value_raises_configuration_syntax_error(self):
        with self.assertRaises(ConfigurationSyntaxError):
            parse_ranking_bias(-1)
            parse_ranking_bias(-0.1)
            parse_ranking_bias(-0.01)
            parse_ranking_bias(-0.0000000001)

    def test_value_greater_than_one_raises_configuration_syntax_error(self):
        with self.assertRaises(ConfigurationSyntaxError):
            parse_ranking_bias(2)
            parse_ranking_bias(1.1)
            parse_ranking_bias(1.00000000001)

    def test_unexpected_type_value_raises_configuration_syntax_error(self):
        with self.assertRaises(ConfigurationSyntaxError):
            parse_ranking_bias('')
            parse_ranking_bias(object())

    def test_none_value_returns_default_weight(self):
        self.assertEqual(parse_ranking_bias(None),
                         constants.DEFAULT_FILERULE_RANKING_BIAS)

    def test_value_within_range_zero_to_one_returns_value(self):
        input_values = [0, 0.001, 0.01, 0.1, 0.5, 0.9, 0.99, 0.999, 1]

        for value in input_values:
            self.assertEqual(parse_ranking_bias(value), value)


class TestIsValidSourceSpecification(TestCase):
    def test_empty_source_returns_false(self):
        self.assertFalse(is_valid_source(None))
        self.assertFalse(is_valid_source(''))

    def test_bad_source_returns_false(self):
        self.assertFalse(is_valid_source('not.a.valid.source.surely'))

    def test_good_source_returns_true(self):
        self.assertTrue(is_valid_source('metadata.exiftool.PDF:CreateDate'))
        self.assertTrue(is_valid_source('metadata.exiftool'))
        self.assertTrue(is_valid_source('filesystem.basename.full'))
        self.assertTrue(is_valid_source('filesystem.basename.extension'))
        self.assertTrue(is_valid_source('filesystem.contents.mime_type'))
