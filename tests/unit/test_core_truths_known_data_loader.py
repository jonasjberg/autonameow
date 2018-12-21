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

import os
import re
from unittest import TestCase

import unit.utils as uu
from core.truths.known_data_loader import KnownDataFileParser
from core.truths.known_data_loader import lookup_values
from core.truths.known_data_loader import literal_lookup_dict
from core.truths.known_data_loader import regex_lookup_dict


def _get_known_data_file_parser(*args, **kwargs):
    return KnownDataFileParser(*args, **kwargs)


def _load_test_data_from_yaml_file(filename):
    from util import coercers
    from util import disk
    ABSPATH_THIS_DIR = coercers.coerce_to_normalized_path(
        os.path.abspath(os.path.dirname(__file__))
    )
    bytes_basename = coercers.AW_PATHCOMPONENT(filename)
    abspath_yaml_file = disk.joinpaths(ABSPATH_THIS_DIR, bytes_basename)
    assert disk.isfile(abspath_yaml_file), (
        'File does not exist: {!s}'.format(abspath_yaml_file)
    )
    return disk.load_yaml_file(abspath_yaml_file)


class TestKnownDataFileParser(TestCase):
    # TODO: Implement 'match_any_literal_ignorecase'!
    @classmethod
    def setUpClass(cls):
        cls.SECTION_MATCH_ANY_LITERAL_CASESENSITIVE = KnownDataFileParser.CONFIG_SECTION_MATCH_ANY_LITERAL_CASESENSITIVE
        cls.SECTION_MATCH_ANY_LITERAL_IGNORECASE = KnownDataFileParser.CONFIG_SECTION_MATCH_ANY_LITERAL_IGNORECASE
        cls.SECTION_MATCH_ANY_REGEX_IGNORECASE = KnownDataFileParser.CONFIG_SECTION_MATCH_ANY_REGEX_IGNORECASE
        cls.SECTION_MATCH_ANY_REGEX_CASESENSITIVE = KnownDataFileParser.CONFIG_SECTION_MATCH_ANY_REGEX_CASESENSITIVE

    def _get_parser_from_empty_config(self):
        empty_config = dict()
        return _get_known_data_file_parser(empty_config)

    def _get_parser_from_config(self, config):
        return _get_known_data_file_parser(config)

    def _compile_regex(self, pattern):
        # NOTE: Compilation flags must match those used in the implementation.
        return re.compile(pattern, re.IGNORECASE)

    def test_filepath_config_is_expected_absolute_path(self):
        empty_config = dict()
        parser = _get_known_data_file_parser(empty_config, b'/tmp/canonical_publisher.yaml')
        actual = parser.str_lookup_dict_filepath
        self.assertIsInstance(actual, str,
                              '*not bytestring* path is stored for logging only')
        self.assertTrue(actual.endswith('canonical_publisher.yaml'))
        self.assertTrue(uu.is_abspath(actual))

    def test_can_be_instantiated_with_empty_config_dict(self):
        parser = self._get_parser_from_empty_config()
        self.assertIsNotNone(parser)

    def test_parsed_literal_lookup_is_empty_when_given_empty_config_dict(self):
        parser = self._get_parser_from_empty_config()
        self.assertEqual(dict(), parser.parsed_literal_lookup)

    def test_parsed_regex_lookup_is_empty_when_given_empty_config_dict(self):
        parser = self._get_parser_from_empty_config()
        self.assertEqual(dict(), parser.parsed_regex_lookup)

    def test_parsed_literal_lookup_is_empty_when_given_only_empty_strings(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_LITERAL_CASESENSITIVE: [
                    '',
                ],
                self.SECTION_MATCH_ANY_LITERAL_IGNORECASE: [
                    '',
                ]
            },
            'BarPub': {
                self.SECTION_MATCH_ANY_LITERAL_CASESENSITIVE: [
                    ' ',
                    '  ',
                ]
            }
        })
        self.assertEqual(dict(), parser.parsed_literal_lookup)

    def test_parsed_literal_lookup_is_empty_when_given_empty_literals(self):
        parser = self._get_parser_from_config({
            '': {
                self.SECTION_MATCH_ANY_LITERAL_CASESENSITIVE: [
                    'foo',
                ]
            },
            '  ': {
                self.SECTION_MATCH_ANY_LITERAL_CASESENSITIVE: [
                    'bar',
                ]
            }
        })
        self.assertEqual(dict(), parser.parsed_literal_lookup)

    def test_returns_expected_parsed_literal_lookup_given_config_with_one_entry(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_LITERAL_CASESENSITIVE: [
                    'Foo',
                    'foo pub',
                    'Foo',  # Duplicate that should be removed
                    '   ',  # Whitespace that should be ignored
                ]
             }
        })
        expect_parsed_literal_lookup = {
            'FooPub': {'Foo', 'foo pub'}
        }
        self.assertEqual(expect_parsed_literal_lookup, parser.parsed_literal_lookup)

    def test_returns_expected_parsed_literal_lookup_given_config_with_two_entries(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_LITERAL_CASESENSITIVE: [
                    'Foo',
                    'foo pub',
                    'Foo',  # Duplicate that should be removed
                ]
             },
            'BarPub': {
                self.SECTION_MATCH_ANY_LITERAL_CASESENSITIVE: [
                    'Bar Publishers Inc.',
                    'bar pub.',
                    '\n',  # Whitespace that should be ignored
                ]
             }
        })
        expect_parsed_literal_lookup = {
            'FooPub': {'Foo', 'foo pub'},  # set literal
            'BarPub': {'Bar Publishers Inc.', 'bar pub.'}
        }
        self.assertEqual(expect_parsed_literal_lookup, parser.parsed_literal_lookup)

    def test_parsed_regex_lookup_is_empty_when_given_only_empty_strings(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_REGEX_CASESENSITIVE: [
                    '',
                ]
            },
            'BarPub': {
                self.SECTION_MATCH_ANY_REGEX_IGNORECASE: [
                    ' ',
                    '  ',
                ]
            }
        })
        self.assertEqual(dict(), parser.parsed_regex_lookup)

    def test_parsed_regex_lookup_is_empty_when_given_empty_regex(self):
        parser = self._get_parser_from_config({
            '': {
                self.SECTION_MATCH_ANY_REGEX_CASESENSITIVE: [
                    'foo',
                ]
            },
            '  ': {
                self.SECTION_MATCH_ANY_REGEX_IGNORECASE: [
                    'bar',
                ]
            }
        })
        self.assertEqual(dict(), parser.parsed_regex_lookup)

    def test_returns_expected_parsed_regex_lookup_given_config_with_one_entry(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_REGEX_IGNORECASE: [
                    'Foo',
                    'foo pub',
                    'Foo',  # Duplicate that should be removed
                    '   ',  # Whitespace that should be ignored
                ]
             }
        })
        expect_parsed_regex_lookup = sorted({
            'FooPub': {self._compile_regex('Foo'),
                       self._compile_regex('foo pub')}
        })
        actual = sorted(parser.parsed_regex_lookup)
        self.assertEqual(expect_parsed_regex_lookup, actual)

    def test_returns_expected_parsed_regex_lookup_given_config_with_two_entries(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_REGEX_IGNORECASE: [
                    'Foo',
                    'foo pub',
                    'Foo',  # Duplicate that should be removed
                ]
             },
            'BarPub': {
                self.SECTION_MATCH_ANY_REGEX_IGNORECASE: [
                    'Bar Publishers Inc.',
                    'bar pub.',
                    '\n',  # Whitespace that should be ignored
                ]
             }
        })
        expect_parsed_regex_lookup = sorted({
            'FooPub': {self._compile_regex('Foo'),
                       self._compile_regex('foo pub')},
            'BarPub': {self._compile_regex('Bar Publishers Inc.'),
                       self._compile_regex('bar pub.')}
        })
        actual = sorted(parser.parsed_regex_lookup)
        self.assertEqual(expect_parsed_regex_lookup, actual)

    def test_parsed_regex_lookup_given_config_with_different_case_sensitivity(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_REGEX_CASESENSITIVE: [
                    'Foo',
                    'foo pub',
                    'Foo',  # Duplicate that should be removed
                ]
             },
            'BarPub': {
                self.SECTION_MATCH_ANY_REGEX_IGNORECASE: [
                    'Bar Publishers Inc.',
                    'bar pub.',
                    '\n',  # Whitespace that should be ignored
                ]
             }
        })
        expect_parsed_regex_lookup = sorted({
            'FooPub': {self._compile_regex('Foo'),
                       self._compile_regex('foo pub')},
            'BarPub': {self._compile_regex('Bar Publishers Inc.'),
                       self._compile_regex('bar pub.')}
        })
        actual = sorted(parser.parsed_regex_lookup)
        self.assertEqual(expect_parsed_regex_lookup, actual)


class TestLookupValues(TestCase):
    def test_returns_all_keys_present_in_the_regex_lookup_dict(self):
        for fieldname in ('creatortool', 'language', 'publisher'):
            regex_lookup_dict_keys = set(regex_lookup_dict(fieldname).keys())
            self.assertGreater(len(regex_lookup_dict_keys), 13,
                               'Assume greater than arbitrary non-zero count')

            actual = lookup_values(fieldname)
            self.assertGreaterEqual(len(actual), len(regex_lookup_dict_keys),
                                    'Expect sum of regex and literal keys')
            self.assertTrue(all(v in actual for v in regex_lookup_dict_keys))

    def test_returns_all_keys_present_in_the_literal_lookup_dict(self):
        for fieldname in ('creatortool', 'language', 'publisher'):
            literal_lookup_dict_keys = set(literal_lookup_dict(fieldname).keys())
            self.assertGreater(len(literal_lookup_dict_keys), 6,
                               'Assume greater than arbitrary non-zero count')

            actual = lookup_values(fieldname)
            self.assertGreaterEqual(len(actual), len(literal_lookup_dict_keys),
                                    'Expect sum of regex and literal keys')
            self.assertTrue(all(v in actual for v in literal_lookup_dict_keys))
