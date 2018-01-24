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
from core import constants as C
from core.config.config_parser import (
    ConfigurationParser,
    ConfigurationRuleParser,
    ConfigurationOptionsParser,
    INITIAL_CONFIGURATION_OPTIONS,
    parse_versioning
)
from core.exceptions import (
    ConfigurationSyntaxError,
    EncodingBoundaryViolation,
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

        self.config_path_unicode = uu.abspath_testconfig()
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
        given_rules = DEFAULT_CONFIG.get('RULES')
        self.assertIsNotNone(given_rules)

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
        actual = rule_parser.parse(given_rules)
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, list)
        self.assertGreater(len(actual), 1)
        self.assertEqual(len(given_rules), len(actual))

    def test_returns_expected_given_empty_dict(self):
        rule_parser = ConfigurationRuleParser()
        given_rules = dict()
        expect = []
        self.assertEqual(expect, rule_parser.parse(given_rules))

    def test_raises_exception_given_non_dict(self):
        rule_parser = ConfigurationRuleParser()
        bad_rules = (['foo'], object(), 'foo')

        for given_rules in bad_rules:
            with self.assertRaises(ConfigurationSyntaxError):
                _ = rule_parser.parse(given_rules)


class TestConfigurationOptionsParserSanityChecks(TestCase):
    def setUp(self):
        self.INITIAL_OPTIONS = dict(INITIAL_CONFIGURATION_OPTIONS)
        raw_options = dict()
        self.op = ConfigurationOptionsParser(raw_options, self.INITIAL_OPTIONS)

    def test_raises_exception_given_invalid_option_section_key(self):
        with self.assertRaises(AssertionError):
            self.op.try_load_option(
                section='this_should_be_a_invalid_key',
                key='foo',
                validation_func=lambda x: True,
                default='foo'
            )

    def test_raises_exception_given_not_callable_validation_func(self):
        arbitrary_section = list(self.INITIAL_OPTIONS.keys())[-1]
        with self.assertRaises(AssertionError):
            self.op.try_load_option(
                section=arbitrary_section,
                key='foo',
                validation_func='not_callable',
                default='foo'
            )


class TestConfigurationOptionsParserTryLoadOption(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.INITIAL_OPTIONS = dict(INITIAL_CONFIGURATION_OPTIONS)

        from core.config.field_parsers import DateTimeConfigFieldParser
        cls.datetime_configfield_parser = DateTimeConfigFieldParser

    def test_valid_datetime_format_time(self):
        raw_options = {
            'DATETIME_FORMAT': {
                'date': '%Y-foo-%m-bar-%d',  # OK value
            }
        }
        op = ConfigurationOptionsParser(raw_options, self.INITIAL_OPTIONS)
        op.try_load_option(
            section='DATETIME_FORMAT',
            key='date',
            validation_func=self.datetime_configfield_parser.is_valid_datetime,
            default=C.DEFAULT_DATETIME_FORMAT_DATE
        )
        actual = op.parsed['DATETIME_FORMAT'].get('date')
        self.assertEqual('%Y-foo-%m-bar-%d', actual)

    def test_uses_default_when_given_invalid_datetime_format_time(self):
        raw_options = {
            'DATETIME_FORMAT': {
                'date': None,  # BAD value
            }
        }
        op = ConfigurationOptionsParser(raw_options, self.INITIAL_OPTIONS)
        op.try_load_option(
            section='DATETIME_FORMAT',
            key='date',
            validation_func=self.datetime_configfield_parser.is_valid_datetime,
            default=C.DEFAULT_DATETIME_FORMAT_DATE
        )
        self.assertIn('DATETIME_FORMAT', op.parsed)
        actual = op.parsed['DATETIME_FORMAT'].get('date')
        self.assertEqual(C.DEFAULT_DATETIME_FORMAT_DATE, actual)


class TestConfigurationOptionsParserTryLoadPersistenceOption(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.INITIAL_OPTIONS = dict(INITIAL_CONFIGURATION_OPTIONS)

    def test_valid_persistence_cache_directory(self):
        raw_options = {
            'PERSISTENCE': {
                'cache_directory': b'/tmp/foo/bar'
            }
        }
        op = ConfigurationOptionsParser(raw_options,
                                        initial_options=self.INITIAL_OPTIONS)
        op.try_load_persistence_option(
            'cache_directory',
            C.DEFAULT_PERSISTENCE_DIR_ABSPATH
        )
        self.assertIn('PERSISTENCE', op.parsed)
        actual = op.parsed['PERSISTENCE'].get('cache_directory')
        self.assertEqual(b'/tmp/foo/bar', actual)

    def test_uses_default_when_given_invalid_persistence_cache_directory(self):
        def _check(raw_options, expect):
            op = ConfigurationOptionsParser(raw_options, self.INITIAL_OPTIONS)
            op.try_load_persistence_option(
                'cache_directory',
                C.DEFAULT_PERSISTENCE_DIR_ABSPATH
            )
            self.assertIn('PERSISTENCE', op.parsed)
            actual = op.parsed['PERSISTENCE'].get('cache_directory')
            self.assertEqual(expect, actual)

        # TODO: [TD0160] Improve handling of setting up working directories.
        # TODO: [TD0160] This should probably fail for values like  '^' ..

        _check(raw_options={'PERSISTENCE': {'cache_directory': None}},
               expect=C.DEFAULT_PERSISTENCE_DIR_ABSPATH)
        _check(raw_options={'PERSISTENCE': {'cache_directory': ''}},
               expect=C.DEFAULT_PERSISTENCE_DIR_ABSPATH)
        _check(raw_options={'PERSISTENCE': {'cache_directory': ' '}},
               expect=C.DEFAULT_PERSISTENCE_DIR_ABSPATH)
        _check(raw_options={'PERSISTENCE': {'cache_directory': '  '}},
               expect=C.DEFAULT_PERSISTENCE_DIR_ABSPATH)
        _check(raw_options={'PERSISTENCE': {'cache_directory': b''}},
               expect=C.DEFAULT_PERSISTENCE_DIR_ABSPATH)
        _check(raw_options={'PERSISTENCE': {'cache_directory': b' '}},
               expect=C.DEFAULT_PERSISTENCE_DIR_ABSPATH)
        _check(raw_options={'PERSISTENCE': {'cache_directory': b'  '}},
               expect=C.DEFAULT_PERSISTENCE_DIR_ABSPATH)
        _check(raw_options={'PERSISTENCE': {'cache_directory': 1324}},
               expect=C.DEFAULT_PERSISTENCE_DIR_ABSPATH)


class TestValidateVersionNumber(TestCase):
    def test_valid_version_number_returns_expected(self):
        def _assert_equal(test_input, expected):
            actual = parse_versioning(test_input)
            self.assertIsInstance(actual, tuple)
            self.assertEqual(actual, expected)

        _assert_equal('0.0.0', (0, 0, 0))
        _assert_equal('0.4.6', (0, 4, 6))
        _assert_equal('1.2.3', (1, 2, 3))
        _assert_equal('9.9.9', (9, 9, 9))
        _assert_equal('10.11.12', (10, 11, 12))
        _assert_equal('1.2.34', (1, 2, 34))
        _assert_equal('1.23.4', (1, 23, 4))
        _assert_equal('12.3.4', (12, 3, 4))
        _assert_equal('12.3.45', (12, 3, 45))
        _assert_equal('12.34.5', (12, 34, 5))
        _assert_equal('12.34.56', (12, 34, 56))
        _assert_equal('1337.1337.1337', (1337, 1337, 1337))

        _assert_equal('v0.0.0', (0, 0, 0))
        _assert_equal('v0.4.6', (0, 4, 6))
        _assert_equal('v1.2.3', (1, 2, 3))
        _assert_equal('v9.9.9', (9, 9, 9))
        _assert_equal('v10.11.12', (10, 11, 12))
        _assert_equal('v1.2.34', (1, 2, 34))
        _assert_equal('v1.23.4', (1, 23, 4))
        _assert_equal('v12.3.4', (12, 3, 4))
        _assert_equal('v12.3.45', (12, 3, 45))
        _assert_equal('v12.34.5', (12, 34, 5))
        _assert_equal('v12.34.56', (12, 34, 56))
        _assert_equal('v1337.1337.1337', (1337, 1337, 1337))

    def test_invalid_version_number_returns_none(self):
        def _assert_none(test_data):
            actual = parse_versioning(test_data)
            self.assertIsNone(actual)

        _assert_none(None)
        _assert_none([])
        _assert_none({})
        _assert_none('')
        _assert_none(b'')
        _assert_none(' ')
        _assert_none(b' ')
        _assert_none('0.0')
        _assert_none('1.2')
        _assert_none('1.2.x')
        _assert_none('1.2 x')
        _assert_none('1.2 3')
        _assert_none('1 2.3')
        _assert_none('1 2 3')
        _assert_none('€.2.3')
        _assert_none('€.%.3')
        _assert_none('€.%.&')
        _assert_none(b'0.0')
        _assert_none(b'1.2')
        _assert_none(b'1.2.x')
        _assert_none(b'1.2 x')
        _assert_none(b'1.2 3')
        _assert_none(b'1 2.3')
        _assert_none(b'1 2 3')
        _assert_none('€.2.3'.encode(C.DEFAULT_ENCODING))
        _assert_none('€.%.3'.encode(C.DEFAULT_ENCODING))
        _assert_none('€.%.&'.encode(C.DEFAULT_ENCODING))
        _assert_none('v0.0')
        _assert_none('v1.2')
        _assert_none('v1.2.x')
        _assert_none('v1.2 x')
        _assert_none('v1.2 3')
        _assert_none('v1 2.3')
        _assert_none('v1 2 3')
        _assert_none('v€.2.3')
        _assert_none('v€.%.3')
        _assert_none('v€.%.&')
        _assert_none(b'v0.0')
        _assert_none(b'v1.2')
        _assert_none(b'v1.2.x')
        _assert_none(b'v1.2 x')
        _assert_none(b'v1.2 3')
        _assert_none(b'v1 2.3')
        _assert_none(b'v1 2 3')
        _assert_none('v€.2.3'.encode(C.DEFAULT_ENCODING))
        _assert_none('v€.%.3'.encode(C.DEFAULT_ENCODING))
        _assert_none('v€.%.&'.encode(C.DEFAULT_ENCODING))
