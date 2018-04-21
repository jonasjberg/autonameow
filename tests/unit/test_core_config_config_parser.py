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
from unittest import skipIf, TestCase
from unittest.mock import Mock, patch

try:
    import yaml
except ImportError:
    yaml = None
    print('Missing required module "yaml". '
          'Make sure "pyyaml" is available before running this program.',
          file=sys.stderr)

import unit.utils as uu
import unit.constants as uuconst
from core import constants as C
from core.config.config_parser import (
    ConfigurationParser,
    ConfigurationRuleParser,
    ConfigurationOptionsParser,
    INITIAL_CONFIGURATION_OPTIONS,
    parse_rule_conditions,
    parse_rule_ranking_bias,
    parse_versioning,
)
from core.config.default_config import DEFAULT_CONFIG
from core.exceptions import (
    ConfigError,
    ConfigurationSyntaxError,
    EncodingBoundaryViolation,
)


MOCK_REGISTRY = Mock()
MOCK_REGISTRY.might_be_resolvable.return_value = True


def yaml_unavailable():
    return yaml is None, 'Failed to import "yaml"'


class TestConfigurationParser(TestCase):
    def setUp(self):
        self.p = ConfigurationParser()

    @patch('core.config.rules.master_provider.Registry', MOCK_REGISTRY)
    def test_parsed_default_config_is_not_none(self):
        actual = self.p.parse(DEFAULT_CONFIG)
        self.assertIsNotNone(actual)

    @patch('core.config.rules.master_provider.Registry', MOCK_REGISTRY)
    def test_parsed_default_config_has_expected_options(self):
        actual = self.p.parse(DEFAULT_CONFIG)
        actual_options = actual.options
        self.assertIsInstance(actual_options, dict)
        for section in [
            'DATETIME_FORMAT', 'FILESYSTEM', 'FILETAGS_OPTIONS',
            'NAME_TEMPLATE_FIELDS', 'PERSISTENCE', 'POST_PROCESSING'
        ]:
            self.assertIn(section, actual_options)
            self.assertIsInstance(actual_options[section], dict)


class TestConfigurationParserLoadReusableNameTemplates(TestCase):
    def setUp(self):
        self.p = ConfigurationParser()

    def _assert_returns(self, expected, given):
        actual = self.p._load_reusable_name_templates(given)
        self.assertEqual(expected, actual)

    def test_returns_empty_if_given_config_dict_is_none(self):
        self._assert_returns(dict(), given=dict())

    def test_returns_empty_if_given_config_dict_is_empty_dict(self):
        self._assert_returns(dict(), given=dict())

    def test_returns_empty_if_given_name_templates_is_none(self):
        self._assert_returns(dict(), given={'NAME_TEMPLATES': None})

    def test_returns_empty_if_given_name_templates_dict_is_empty(self):
        self._assert_returns(dict(), given={'NAME_TEMPLATES': dict()})

    def test_raises_exception_if_given_name_templates_is_not_type_dict(self):
        for given in [
            object(),
            [None], ['foo'], [1],
            True,
        ]:
            with self.assertRaises(ConfigurationSyntaxError):
                _ = self.p._load_reusable_name_templates({'NAME_TEMPLATES': given})

    def test_returns_one_as_expected(self):
        self._assert_returns(
            expected={
                'default_book': '{publisher} {title} {edition} - {author} {year}.{extension}'
            },
            given={
                'NAME_TEMPLATES': {
                    'default_book': '{publisher} {title} {edition} - {author} {year}.{extension}'
                }
            }
        )

    def test_returns_two_as_expected(self):
        self._assert_returns(
            expected={
                'default_book': '{publisher} {title} {edition} - {author} {year}.{extension}',
                'default_photo': '{datetime} {description} -- {tags}.{extension}'
            },
            given={
                'NAME_TEMPLATES': {
                    'default_book': '{publisher} {title} {edition} - {author} {year}.{extension}',
                    'default_photo': '{datetime} {description} -- {tags}.{extension}'
                }
            }
        )


class TestConfigurationParserLoadPlaceholderFieldOptions(TestCase):
    def setUp(self):
        self.p = ConfigurationParser()

    def _assert_returns(self, expected, given):
        actual = self.p._load_placeholder_field_options(given)
        self.assertEqual(expected, actual)

    def test_returns_empty_if_missing(self):
        self._assert_returns(dict(), given=dict())

    def test_returns_empty_if_wrong_type(self):
        self._assert_returns(dict(), given={'NAME_TEMPLATE_FIELDS': ['foo']})

    def test_returns_empty_if_none(self):
        self._assert_returns(dict(), given={'NAME_TEMPLATE_FIELDS': None})

    def test_returns_empty_if_empty_dict(self):
        self._assert_returns(dict(), given={'NAME_TEMPLATE_FIELDS': dict()})

    def test_returns_one_as_expected(self):
        self._assert_returns(
            expected={
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
                },
            given={
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
        )

    def test_returns_two_as_expected(self):
        self._assert_returns(
            expected={
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
            },
            given={
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
        )

    def test_raises_exception_given_invalid_field(self):
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
            _ = self.p._load_placeholder_field_options(config_dict)

    def test_raises_exception_given_bad_regex(self):
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
            _ = self.p._load_placeholder_field_options(config_dict)


@skipIf(*yaml_unavailable())
class TestDefaultConfigFromFile(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_path_unicode = uu.abspath_testconfig()
        cls.config_path_bytestring = uu.normpath(cls.config_path_unicode)

    def setUp(self):
        self.config_parser = ConfigurationParser()

    def _assert_valid_existing_file(self, filepath):
        self.assertTrue(uu.file_exists(filepath))
        self.assertTrue(uu.path_is_readable(filepath))

    def test_setup(self):
        self._assert_valid_existing_file(self.config_path_unicode)
        self.assertTrue(uu.is_internalstring(self.config_path_unicode))
        self._assert_valid_existing_file(self.config_path_bytestring)
        self.assertTrue(uu.is_internalbytestring(self.config_path_bytestring))

    @patch('core.config.rules.master_provider.Registry', MOCK_REGISTRY)
    def test_loads_default_config_from_bytestring_path(self):
        config = self.config_parser.from_file(self.config_path_bytestring)
        self.assertIsNotNone(config)

    def test_raises_exception_given_unicode_path(self):
        with self.assertRaises(EncodingBoundaryViolation):
            _ = self.config_parser.from_file(self.config_path_unicode)

    def test_raises_config_error_if_given_path_to_empty_file(self):
        filepath_empty_file = uu.normpath(uu.abspath_testfile('empty'))
        with self.assertRaises(ConfigError):
            _ = self.config_parser.from_file(filepath_empty_file)

    def test_raises_config_error_if_given_path_to_png_image_file(self):
        filepath_empty_file = uu.normpath(uu.abspath_testfile('empty'))
        with self.assertRaises(ConfigError):
            _ = self.config_parser.from_file(filepath_empty_file)


class TestConfigurationRuleParser(TestCase):
    @patch('core.config.rules.master_provider.Registry', MOCK_REGISTRY)
    def test_parses_rules_from_default_config_given_all_nametemplates(self):
        from core.config.default_config import DEFAULT_CONFIG
        given_rules = DEFAULT_CONFIG.get('RULES')
        self.assertIsNotNone(given_rules)

        reusable_name_templates = {
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
        rule_parser = ConfigurationRuleParser(reusable_name_templates)
        actual = rule_parser.parse(given_rules)
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, list)
        self.assertGreater(len(actual), 1)
        self.assertEqual(len(given_rules), len(actual))

    def test_returns_expected_given_empty_dict(self):
        rule_parser = ConfigurationRuleParser()
        given_rules = dict()
        expect = list()
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


class TestParseRuleConditions(TestCase):
    def _assert_parsed_result(self, expect_uri, expect_expression, given):
        actual = parse_rule_conditions(given)
        self.assertEqual(expect_uri, actual[0].meowuri)
        self.assertEqual(expect_expression, actual[0].expression)

    def test_parse_condition_filesystem_pathname_is_valid(self):
        raw_conditions = {
            uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL: '~/.config'
        }
        actual = parse_rule_conditions(raw_conditions)
        self.assertEqual(uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL,
                         actual[0].meowuri)
        self.assertEqual('~/.config',
                         actual[0].expression)

        self._assert_parsed_result(
            expect_uri=uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL,
            expect_expression='~/.config',
            given={uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL: '~/.config'}
        )

    def test_parse_condition_contents_mime_type_is_valid(self):
        raw_conditions = {
            uuconst.MEOWURI_FS_XPLAT_MIMETYPE: 'image/jpeg'
        }
        actual = parse_rule_conditions(raw_conditions)
        self.assertEqual(uuconst.MEOWURI_FS_XPLAT_MIMETYPE, actual[0].meowuri)
        self.assertEqual('image/jpeg', actual[0].expression)

    def test_parse_condition_contents_metadata_is_valid(self):
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        raw_conditions = {
            uuconst.MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL: 'Defined',
        }
        actual = parse_rule_conditions(raw_conditions)
        self.assertEqual(uuconst.MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL,
                         actual[0].meowuri)
        self.assertEqual('Defined',
                         actual[0].expression)

    def test_parse_empty_conditions_is_allowed(self):
        raw_conditions = dict()
        _ = parse_rule_conditions(raw_conditions)


class TestParseRuleRankingBias(TestCase):
    def test_negative_value_raises_configuration_syntax_error(self):
        for given in [-1, -0.1, -0.01, -0.0000000001]:
            with self.assertRaises(ConfigurationSyntaxError):
                _ = parse_rule_ranking_bias(given)

    def test_value_greater_than_one_raises_configuration_syntax_error(self):
        for given in [2, 1.1, 1.00000000001]:
            with self.assertRaises(ConfigurationSyntaxError):
                _ = parse_rule_ranking_bias(given)

    def test_unexpected_type_value_raises_configuration_syntax_error(self):
        for given in ['', object()]:
            with self.assertRaises(ConfigurationSyntaxError):
                _ = parse_rule_ranking_bias(given)

    def test_none_value_returns_default_weight(self):
        actual = parse_rule_ranking_bias(None)
        self.assertEqual(C.DEFAULT_RULE_RANKING_BIAS, actual)

    def test_value_within_range_zero_to_one_returns_value(self):
        for given in [0, 0.001, 0.01, 0.1, 0.5, 0.9, 0.99, 0.999, 1]:
            self.assertEqual(given, parse_rule_ranking_bias(given))


class TestValidateVersionNumber(TestCase):
    def test_valid_version_number_returns_expected(self):
        def _assert_equal(test_input, expected):
            actual = parse_versioning(test_input)
            self.assertIsInstance(actual, tuple)
            self.assertEqual(expected, actual)

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
