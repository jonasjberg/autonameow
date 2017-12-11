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

import re
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
import unit.constants as uuconst
from core.config.config_parser import (
    ConfigurationParser,
    ConfigurationRuleParser
)
from core.exceptions import (
    ConfigurationSyntaxError,
    EncodingBoundaryViolation,
    ConfigError
)


def yaml_unavailable():
    return yaml is None, 'Failed to import "yaml"'


class TestConfigurationParser(TestCase):
    @classmethod
    def setUpClass(cls):
        uu.init_provider_registry()

    def setUp(self):
        self.p = ConfigurationParser()

    def test__load_reusable_nametemplates_returns_empty_if_missing(self):
        config_dict = dict()
        actual = self.p._load_reusable_nametemplates(config_dict)
        expect = dict()
        self.assertEqual(expect, actual)

    def test__load_reusable_nametemplates_returns_empty_if_wrong_type(self):
        config_dict = {'NAME_TEMPLATES': ['foo']}
        actual = self.p._load_reusable_nametemplates(config_dict)
        expect = dict()
        self.assertEqual(expect, actual)

    def test__load_reusable_nametemplates_returns_empty_if_none(self):
        config_dict = {'NAME_TEMPLATES': None}
        actual = self.p._load_reusable_nametemplates(config_dict)
        expect = dict()
        self.assertEqual(expect, actual)

    def test__load_reusable_nametemplates_returns_empty_if_empty_dict(self):
        config_dict = {'NAME_TEMPLATES': dict()}
        actual = self.p._load_reusable_nametemplates(config_dict)
        expect = dict()
        self.assertEqual(expect, actual)

    def test__load_reusable_nametemplates_returns_one_as_expected(self):
        config_dict = {
            'NAME_TEMPLATES': {
                'default_book': '{publisher} {title} {edition} - {author} {year}.{extension}'
            }
        }
        actual = self.p._load_reusable_nametemplates(config_dict)
        expect = {
            'default_book': '{publisher} {title} {edition} - {author} {year}.{extension}'
        }
        self.assertEqual(expect, actual)

    def test__load_reusable_nametemplates_returns_two_as_expected(self):
        config_dict = {
            'NAME_TEMPLATES': {
                'default_book': '{publisher} {title} {edition} - {author} {year}.{extension}',
                'default_photo': '{datetime} {description} -- {tags}.{extension}'
            }
        }
        actual = self.p._load_reusable_nametemplates(config_dict)
        expect = {
            'default_book': '{publisher} {title} {edition} - {author} {year}.{extension}',
            'default_photo': '{datetime} {description} -- {tags}.{extension}'
        }
        self.assertEqual(expect, actual)

    def test__load_template_fields_returns_empty_if_missing(self):
        config_dict = dict()
        actual = self.p._load_template_fields(config_dict)
        expect = dict()
        self.assertEqual(expect, actual)

    def test__load_template_fields_returns_empty_if_wrong_type(self):
        config_dict = {'NAME_TEMPLATE_FIELDS': ['foo']}
        actual = self.p._load_template_fields(config_dict)
        expect = dict()
        self.assertEqual(expect, actual)

    def test__load_template_fields_returns_empty_if_none(self):
        config_dict = {'NAME_TEMPLATE_FIELDS': None}
        actual = self.p._load_template_fields(config_dict)
        expect = dict()
        self.assertEqual(expect, actual)

    def test__load_template_fields_returns_empty_if_empty_dict(self):
        config_dict = {'NAME_TEMPLATE_FIELDS': dict()}
        actual = self.p._load_template_fields(config_dict)
        expect = dict()
        self.assertEqual(expect, actual)

    def test__load_template_fields_returns_one_as_expected(self):
        config_dict = {
            'NAME_TEMPLATE_FIELDS': {
                'publisher': {
                    'candidates': {
                        'FeedBooks': [
                            'This book is brought to you by Feedbooks',
                            'http://www.feedbooks.com'
                        ]
                    }
                }
            }
        }
        actual = self.p._load_template_fields(config_dict)
        expect = {
            'NAME_TEMPLATE_FIELDS': {
                'publisher': {
                    'candidates': {
                        'FeedBooks': [
                            re.compile('This book is brought to you by Feedbooks', re.IGNORECASE),
                            re.compile('http://www.feedbooks.com', re.IGNORECASE)
                        ]
                    }
                }
            }
        }
        self.assertEqual(expect, actual)

    def test__load_template_fields_returns_two_as_expected(self):
        config_dict = {
            'NAME_TEMPLATE_FIELDS': {
                'publisher': {
                    'candidates': {
                        'FeedBooks': [
                            'This book is brought to you by Feedbooks',
                            'http://www.feedbooks.com'
                        ],
                        'ProjectGutenberg': [
                            'Project Gutenberg',
                            'www.gutenberg.net'
                        ]
                    }
                }
            }
        }
        actual = self.p._load_template_fields(config_dict)
        expect = {
            'NAME_TEMPLATE_FIELDS': {
                'publisher': {
                    'candidates': {
                        'FeedBooks': [
                            re.compile('This book is brought to you by Feedbooks', re.IGNORECASE),
                            re.compile('http://www.feedbooks.com', re.IGNORECASE)
                        ],
                        'ProjectGutenberg': [
                            re.compile('Project Gutenberg', re.IGNORECASE),
                            re.compile('www.gutenberg.net', re.IGNORECASE)
                        ]
                    }
                }
            }
        }
        self.assertEqual(expect, actual)

    def test__load_template_fields_raises_exception_given_invalid_field(self):
        config_dict = {
            'NAME_TEMPLATE_FIELDS': {
                '______': {
                    'candidates': {
                        'foo': ['bar']
                    }
                }
            }
        }
        with self.assertRaises(ConfigurationSyntaxError):
            _ = self.p._load_template_fields(config_dict)

    def test__load_template_fields_raises_exception_given_bad_regex(self):
        config_dict = {
            'NAME_TEMPLATE_FIELDS': {
                'title': {
                    'candidates': {
                        'bad_regex': ['[[[']
                    }
                }
            }
        }
        with self.assertRaises(ConfigurationSyntaxError):
            _ = self.p._load_template_fields(config_dict)


@skipIf(*yaml_unavailable())
class TestDefaultConfigFromFile(TestCase):
    def setUp(self):
        self.config_parser = ConfigurationParser()

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
        config = self.config_parser.from_file(self.config_path_bytestring)
        self.assertIsNotNone(config)

    def test_loading_unicode_path_raises_exception(self):
        with self.assertRaises(EncodingBoundaryViolation):
            _ = self.config_parser.from_file(self.config_path_unicode)


class TestConfigurationRuleParser(TestCase):
    def test_parses_rules_from_default_config_given_all_nametemplates(self):
        from core.config.default_config import DEFAULT_CONFIG
        rules_dict = DEFAULT_CONFIG.get('RULES')
        self.assertIsNotNone(rules_dict)

        reusable_nametemplates = {
            'NAME_TEMPLATE_FIELDS': {
                'publisher': {
                    'candidates': {
                        'FeedBooks': [
                            re.compile('This book is brought to you by Feedbooks', re.IGNORECASE),
                            re.compile('http://www.feedbooks.com', re.IGNORECASE)
                        ]
                    }
                }
            }
        }
        rule_parser = ConfigurationRuleParser(reusable_nametemplates)
        actual = rule_parser.parse(rules_dict)
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, list)
        self.assertGreater(len(actual), 1)
        self.assertEqual(len(rules_dict), len(actual))

    def test_raises_exception_given_no_rules(self):
        rule_parser = ConfigurationRuleParser()
        rules_dict = dict()

        with self.assertRaises(ConfigError):
            _ = rule_parser.parse(rules_dict)
