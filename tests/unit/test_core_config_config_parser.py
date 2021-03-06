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
from core.config.config_parser import _nested_dict_set
from core.config.config_parser import ConfigurationOptionsParser
from core.config.config_parser import ConfigurationParser
from core.config.config_parser import ConfigurationRuleParser
from core.config.config_parser import INITIAL_CONFIGURATION_OPTIONS
from core.config.config_parser import parse_rule_conditions
from core.config.config_parser import parse_rule_ranking_bias
from core.config.config_parser import parse_versioning
from core.config.default_config import DEFAULT_CONFIG
from core.exceptions import ConfigError
from core.exceptions import ConfigurationSyntaxError


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
        for section in (
            'DATETIME_FORMAT',
            'FILESYSTEM',
            'FILETAGS_OPTIONS',
            'PERSISTENCE',
            'POST_PROCESSING'
        ):
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


@skipIf(*yaml_unavailable())
class TestDefaultConfigFromFile(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.config_path_unicode = uu.samplefile_config_abspath()
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
        with self.assertRaises(AssertionError):
            _ = self.config_parser.from_file(self.config_path_unicode)

    def test_raises_config_error_if_given_path_to_empty_file(self):
        filepath_empty_file = uu.normpath(uu.samplefile_abspath('empty'))
        with self.assertRaises(ConfigError):
            _ = self.config_parser.from_file(filepath_empty_file)

    def test_raises_config_error_if_given_path_to_png_image_file(self):
        filepath_empty_file = uu.normpath(uu.samplefile_abspath('empty'))
        with self.assertRaises(ConfigError):
            _ = self.config_parser.from_file(filepath_empty_file)


class TestConfigurationRuleParser(TestCase):
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
    def _assert_parsed_result(self, given, expect_uri, expect_expression):
        actual = parse_rule_conditions(given)
        self.assertEqual(expect_uri, actual[0].meowuri)
        self.assertEqual(expect_expression, actual[0].expression)

    def test_parse_condition_filesystem_pathname_is_valid(self):
        self._assert_parsed_result(
            given={uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL: '~/.config'},
            expect_uri=uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL,
            expect_expression='~/.config',
        )

    def test_parse_condition_contents_mime_type_is_valid(self):
        self._assert_parsed_result(
            given={uuconst.MEOWURI_FS_XPLAT_MIMETYPE: 'image/jpeg'},
            expect_uri=uuconst.MEOWURI_FS_XPLAT_MIMETYPE,
            expect_expression='image/jpeg',
        )

    def test_parse_condition_contents_metadata_is_valid(self):
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        self._assert_parsed_result(
            given={uuconst.MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL: 'Defined'},
            expect_uri=uuconst.MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL,
            expect_expression='Defined',
        )

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
        for given in [
            None,
            [],
            {},
            '',
            b'',
            ' ',
            b' ',
            '0.0',
            '1.2',
            '1.2.x',
            '1.2 x',
            '1.2 3',
            '1 2.3',
            '1 2 3',
            '€.2.3',
            '€.%.3',
            '€.%.&',
            b'0.0',
            b'1.2',
            b'1.2.x',
            b'1.2 x',
            b'1.2 3',
            b'1 2.3',
            b'1 2 3',
            '€.2.3'.encode(C.DEFAULT_ENCODING),
            '€.%.3'.encode(C.DEFAULT_ENCODING),
            '€.%.&'.encode(C.DEFAULT_ENCODING),
            'v0.0',
            'v1.2',
            'v1.2.x',
            'v1.2 x',
            'v1.2 3',
            'v1 2.3',
            'v1 2 3',
            'v€.2.3',
            'v€.%.3',
            'v€.%.&',
            b'v0.0',
            b'v1.2',
            b'v1.2.x',
            b'v1.2 x',
            b'v1.2 3',
            b'v1 2.3',
            b'v1 2 3',
            'v€.2.3'.encode(C.DEFAULT_ENCODING),
            'v€.%.3'.encode(C.DEFAULT_ENCODING),
            'v€.%.&'.encode(C.DEFAULT_ENCODING),
        ]:
            with self.subTest(given=given):
                actual = parse_versioning(given)
                self.assertIsNone(actual)


class TestNestedDictSet(TestCase):
    def _assert_sets(self, dictionary, list_of_keys, value, expected):
        _ = _nested_dict_set(dictionary, list_of_keys, value)
        self.assertIsNone(_)
        self.assertDictEqual(dictionary, expected)
        self.assertTrue(key in dictionary for key in expected.keys())

    def test_set_value_in_empty_dictionary(self):
        self._assert_sets(
            dictionary={},
            list_of_keys=['a'],
            value=1,
            expected={'a': 1}
        )
        self._assert_sets(
            dictionary={},
            list_of_keys=['a', 'b'],
            value=2,
            expected={'a': {'b': 2}}
        )
        self._assert_sets(
            dictionary={},
            list_of_keys=['a', 'b', 'c'],
            value=3,
            expected={'a': {'b': {'c': 3}}}
        )

    def test_set_value_in_empty_dictionary_with_fileobject_key(self):
        keys = [uu.get_mock_fileobject()]
        self._assert_sets(
            dictionary={},
            list_of_keys=keys,
            value=1,
            expected={keys[0]: 1}
        )

        keys = [uu.get_mock_fileobject(), uu.get_mock_fileobject()]
        self._assert_sets(
            dictionary={},
            list_of_keys=keys,
            value='foo',
            expected={keys[0]: {keys[1]: 'foo'}}
        )

    def test_set_value_modifies_dictionary_in_place(self):
        d = {'a': 1}
        self._assert_sets(
            dictionary=d,
            list_of_keys=['a'],
            value=2,
            expected={'a': 2}
        )
        self._assert_sets(
            dictionary=d,
            list_of_keys=['b'],
            value={},
            expected={'a': 2,
                      'b': {}}
        )
        self._assert_sets(
            dictionary=d,
            list_of_keys=['b', 'c'],
            value=4,
            expected={'a': 2,
                      'b': {'c': 4}}
        )
        self._assert_sets(
            dictionary=d,
            list_of_keys=['b', 'foo'],
            value=6,
            expected={'a': 2,
                      'b': {'c': 4,
                            'foo': 6}}
        )
        self._assert_sets(
            dictionary=d,
            list_of_keys=['b', 'foo'],
            value=8,
            expected={'a': 2,
                      'b': {'c': 4,
                            'foo': 8}}
        )

    def test_attempting_to_set_occupied_value_raises_key_error(self):
        with self.assertRaises(KeyError):
            self._assert_sets(
                dictionary={'a': 1},
                list_of_keys=['a', 'b'],
                value=5,
                expected={'a': 2}
            )

    def test_passing_invalid_list_of_keys_raises_assertion_error(self):
        for given_key_list in [
            '',
            None,
            (),
            {},
            {'a': None},
            {'a': 'b'},
        ]:
            with self.assertRaises(AssertionError):
                self._assert_sets(
                    dictionary={'a': 1},
                    list_of_keys=given_key_list,
                    value=2,
                    expected={'expect_exception': 0}
                )

    def test_passing_empty_list_raises_value_error(self):
        for given_key_list in [
            [''],
            [None],
            [None, ''],
            ['', None],
            [None, 'foo'],
            ['foo', None],
            ['foo', ''],
            ['', 'foo'],
            [None, 'foo', ''],
            [None, '', 'foo'],
            ['foo', None, ''],
            ['', None, 'foo'],
            ['foo', None, '', None],
            ['', None, 'foo', None],
            ['foo', None, 'a', 'b'],
            ['', 'a', 'b', None],
            ['', 'a', 'b', 'foo'],
        ]:
            with self.assertRaises(ValueError):
                self._assert_sets(
                    dictionary={'a': 1},
                    list_of_keys=given_key_list,
                    value=2,
                    expected={'expect_exception': 0}
                )
