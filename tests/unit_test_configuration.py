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

import yaml

from core.config import rule_parsers
from core.config.config_defaults import DEFAULT_CONFIG
from core.config.configuration import Configuration
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


def load_yaml(path):
    with open(path, 'r') as file_handle:
        data = yaml.load(file_handle)
    return data


class TestWriteConfig(TestCase):
    def setUp(self):
        self.dest_path = os.path.join(make_temp_dir(), 'test_config.yaml')

        self.configuration = Configuration()
        self.configuration.load_from_dict(DEFAULT_CONFIG)

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

        expected = load_yaml(self.dest_path)
        self.assertEqual(expected, self.configuration.data,
                         'Loaded, written and then re-read data should match')


class TestDefaultConfig(TestCase):
    def setUp(self):
        self.configuration = Configuration()
        self.configuration.load_from_dict(DEFAULT_CONFIG)

    def test_default_configuration_exists(self):
        self.assertIsNotNone(DEFAULT_CONFIG,
                             'Default config dict is available')

    def test_default_configuration_contain_rules(self):
        self.assertIsNotNone(self.configuration.file_rules)

    def test_default_configuration_contain_at_least_two_rules(self):
        self.assertGreaterEqual(len(self.configuration.file_rules), 2,
                                'Arbitrary rule count test')


class TestWriteDefaultConfig(TestCase):
    # Show contents of most recent temporary log on Mac OS;
    # cat "$(find /var/folders -type f -name "test_default_config.yaml" -exec stat -f %m %N {} \; 2>/dev/null | sort -n | cut -f2 -d  | tail -n 1)"

    def setUp(self):
        self.dest_path = os.path.join(make_temp_dir(),
                                      'test_default_config.yaml')

        self.configuration = Configuration()

    def test_setup(self):
        self.assertFalse(os.path.exists(self.dest_path),
                         'Destination path should not already exist')

    def test_load_default_config_from_dict_before_write(self):
        self.configuration.load_from_dict(DEFAULT_CONFIG)
        self.assertIsNotNone(self.configuration.data,
                             'Configuration data should exist')

    def test_write_default_config_to_disk(self):
        self.configuration.load_from_dict(DEFAULT_CONFIG)
        self.configuration.write_to_disk(self.dest_path)
        self.assertTrue(os.path.exists(self.dest_path),
                        'Default configuration file exists on disk')

    def test_write_default_config_to_disk_and_verify(self):
        self.configuration.load_from_dict(DEFAULT_CONFIG)
        self.configuration.write_to_disk(self.dest_path)

        expected = load_yaml(self.dest_path)
        self.assertEqual(expected, self.configuration.data,
                         'Loaded, written and then re-read data should match')


class TestConfigurationInit(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.configuration = Configuration(DEFAULT_CONFIG)

    def test_configuration_parsers_in_not_none(self):
        self.assertIsNotNone(self.configuration.rule_parsers,
                             'Configuration should have a list of parsers.')

    def test_configuration_parsers_subclass_of_parser(self):
        for parser in self.configuration.rule_parsers:
            self.assertTrue(isinstance(parser, rule_parsers.RuleParser),
                            'Configuration should have a list of parsers that'
                            'are subclasses of (inherit from) class "Parser".')

    def test_configuration_parsers_instance_of_parser(self):
        for parser in self.configuration.rule_parsers:
            self.assertTrue(isinstance(parser, rule_parsers.RuleParser))


class TestConfigurationDataAccess(TestCase):
    def setUp(self):
        self.configuration = Configuration(DEFAULT_CONFIG)
        self.maxDiff = None

    def test_get_data_does_not_return_none(self):
        self.assertIsNotNone(self.configuration.data)

    def test_get_file_rules_does_not_return_none(self):
        self.assertIsNotNone(self.configuration.file_rules)

    def test_get_file_rules_returns_expected(self):
        self.skipTest('temporary')
        _expect_file_rules = [
        {'_description': 'First Entry in the Default Configuration',
         '_exact_match': False,
         '_weight': None,
         'name_template': 'default_template_name',
         'conditions': {
             'filename': {
                 'pathname': None,
                 'basename': None,
                 'extension': None
             },
             'contents': {
                 'mime_type': None
             }
         },
         'data_sources': {
             'datetime': None,
             'description': None,
             'title': None,
             'author': None,
             'publisher': None,
             'extension': 'filename.extension'
         }
         },
        {'_description': 'Sample Entry for Photos with strict rules',
         '_exact_match': True,
         '_weight': 1,
         'name_format': '%(datetime(%Y-%m-%dT%H%M%S))s %(description)s -- %(tags)s.%(extension)s',
         'conditions': {
             'filename': {
                 'pathname': '~/Pictures/incoming',
                 'basename': 'DCIM*',
                 'extension': 'jpg'
             },
             'contents': {
                 'mime_type': 'image/jpeg',
                 'metadata': 'exif.datetimeoriginal'
             }
         },
         'data_sources': {
             'datetime': ['metadata.exif.datetimeoriginal',
                          'metadata.exif.datetimedigitized',
                          'metadata.exif.createdate'],
             'description': 'plugin.microsoftvision.caption',
             'title': None,
             'author': None,
             'publisher': None,
             'extension': 'filename.extension',
             'tags': 'plugin.microsoftvision.tags'
         }
         },
        {'_description': 'Sample Entry for EPUB e-books',
         '_exact_match': True,
         '_weight': 1,
         'name_format': '',
         'name_template': 'default_ebook_name',
         'conditions': {
             'filename': {
                 'pathname': None,
                 'basename': None,
                 'extension': 'epub'
             },
             'contents': {
                 'mime_type': 'application/epub+zip',
                 'metadata': 'metadata.XMP-dc.***'
             }
         },
         'data_sources': {
             'datetime': ['metadata.XMP-dc.PublicationDate',
                          'metadata.XMP-dc.Date'],
             'description': None,
             'title': 'metadata.XMP-dc.Title',
             'author': ['metadata.XMP-dc.Creator',
                        'metadata.XMP-dc.CreatorFile-as'],
             'publisher': 'metadata.XMP-dc.Publisher',
             'edition': None,
             'extension': 'filename.extension',
             'tags': None
         }
         },
        {'_description': 'Sample Entry for MOBI e-books',
         '_exact_match': True,
         '_weight': 1,
         'name_format': None,
         'name_template': 'default_ebook_name',
         'conditions': {
             'filename': {
                 'pathname': None,
                 'basename': None,
                 'extension': ['mobi']
             },
             'contents': {
                 'mime_type': 'application/x-mobipocket-ebook',
                 'metadata': 'metadata.MOBI.***'
             }
         },
         'data_sources': {
             'datetime': ['metadata.MOBI.PublishDate'],
             'description': ['metadata.MOBI.Description',
                             'metadata.MOBI.Subject'],
             'title': ['metadata.MOBI.BookName',
                       'metadata.MOBI.UpdatedTitle'],
             'author': 'metadata.MOBI.Author',
             'publisher': 'metadata.MOBI.Publisher',
             'extension': 'filename.extension',
             'tags': None
         }
         }
        ]
        self.assertEqual(_expect_file_rules, self.configuration.file_rules)


