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
from core.metadata.canonicalize import build_string_value_canonicalizer
from core.metadata.canonicalize import CanonicalizerConfigParser
from core.metadata.canonicalize import canonicalize_creatortool
from core.metadata.canonicalize import canonicalize_language
from core.metadata.canonicalize import canonicalize_publisher
from core.metadata.canonicalize import StringValueCanonicalizer


def _canonicalize_publisher(given):
    return canonicalize_publisher(given)


def _canonicalize_language(given):
    return canonicalize_language(given)


def _canonicalize_creatortool(given):
    return canonicalize_creatortool(given)


def _build_string_value_canonicalizer(*args, **kwargs):
    return build_string_value_canonicalizer(*args, **kwargs)


def _get_canonicalizer_config_parser(*args, **kwargs):
    return CanonicalizerConfigParser(*args, **kwargs)


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


class TestCanonicalizerConfigParser(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.SECTION_MATCH_ANY_LITERAL = CanonicalizerConfigParser.CONFIG_SECTION_MATCH_ANY_LITERAL
        cls.SECTION_MATCH_ANY_REGEX = CanonicalizerConfigParser.CONFIG_SECTION_MATCH_ANY_REGEX

    def _get_parser_from_empty_config(self):
        empty_config = dict()
        return _get_canonicalizer_config_parser(empty_config)

    def _get_parser_from_config(self, config):
        return _get_canonicalizer_config_parser(config)

    def _compile_regex(self, pattern):
        # NOTE: Compilation flags must match those used in the implementation.
        return re.compile(pattern, re.IGNORECASE)

    def test_filepath_config_is_expected_absolute_path(self):
        empty_config = dict()
        parser = _get_canonicalizer_config_parser(empty_config, b'/tmp/canonical_publisher.yaml')
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
                self.SECTION_MATCH_ANY_LITERAL: [
                    '',
                ]
            },
            'BarPub': {
                self.SECTION_MATCH_ANY_LITERAL: [
                    ' ',
                    '  ',
                ]
            }
        })
        self.assertEqual(dict(), parser.parsed_literal_lookup)

    def test_parsed_literal_lookup_is_empty_when_given_empty_literals(self):
        parser = self._get_parser_from_config({
            '': {
                self.SECTION_MATCH_ANY_LITERAL: [
                    'foo',
                ]
            },
            '  ': {
                self.SECTION_MATCH_ANY_LITERAL: [
                    'bar',
                ]
            }
        })
        self.assertEqual(dict(), parser.parsed_literal_lookup)

    def test_returns_expected_parsed_literal_lookup_given_config_with_one_entry(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_LITERAL: [
                    'Foo',
                    'foo pub',
                    'Foo',  # Duplicate that should be removed
                    '   ',  # Whitespace that should be ignored
                ]
             }
        })
        expect_parsed_literal_lookup = {
            'FooPub': set([
                'Foo',
                'foo pub'
             ])
        }
        self.assertEqual(expect_parsed_literal_lookup, parser.parsed_literal_lookup)

    def test_returns_expected_parsed_literal_lookup_given_config_with_two_entries(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_LITERAL: [
                    'Foo',
                    'foo pub',
                    'Foo',  # Duplicate that should be removed
                ]
             },
            'BarPub': {
                self.SECTION_MATCH_ANY_LITERAL: [
                    'Bar Publishers Inc.',
                    'bar pub.',
                    '\n',  # Whitespace that should be ignored
                ]
             }
        })
        expect_parsed_literal_lookup = {
            'FooPub': set([
                'Foo',
                'foo pub'
             ]),
            'BarPub': set([
                'Bar Publishers Inc.',
                'bar pub.'
             ])
        }
        self.assertEqual(expect_parsed_literal_lookup, parser.parsed_literal_lookup)

    def test_parsed_regex_lookup_is_empty_when_given_only_empty_strings(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_REGEX: [
                    '',
                ]
            },
            'BarPub': {
                self.SECTION_MATCH_ANY_REGEX: [
                    ' ',
                    '  ',
                ]
            }
        })
        self.assertEqual(dict(), parser.parsed_regex_lookup)

    def test_parsed_regex_lookup_is_empty_when_given_empty_regex(self):
        parser = self._get_parser_from_config({
            '': {
                self.SECTION_MATCH_ANY_REGEX: [
                    'foo',
                ]
            },
            '  ': {
                self.SECTION_MATCH_ANY_REGEX: [
                    'bar',
                ]
            }
        })
        self.assertEqual(dict(), parser.parsed_regex_lookup)

    def test_returns_expected_parsed_regex_lookup_given_config_with_one_entry(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_REGEX: [
                    'Foo',
                    'foo pub',
                    'Foo',  # Duplicate that should be removed
                    '   ',  # Whitespace that should be ignored
                ]
             }
        })
        expect_parsed_regex_lookup = {
            'FooPub': set([
                self._compile_regex('Foo'),
                self._compile_regex('foo pub')
             ])
        }
        self.assertEqual(expect_parsed_regex_lookup, parser.parsed_regex_lookup)

    def test_returns_expected_parsed_regex_lookup_given_config_with_two_entries(self):
        parser = self._get_parser_from_config({
            'FooPub': {
                self.SECTION_MATCH_ANY_REGEX: [
                    'Foo',
                    'foo pub',
                    'Foo',  # Duplicate that should be removed
                ]
             },
            'BarPub': {
                self.SECTION_MATCH_ANY_REGEX: [
                    'Bar Publishers Inc.',
                    'bar pub.',
                    '\n',  # Whitespace that should be ignored
                ]
             }
        })
        expect_parsed_regex_lookup = {
            'FooPub': set([
                self._compile_regex('Foo'),
                self._compile_regex('foo pub')
             ]),
            'BarPub': set([
                self._compile_regex('Bar Publishers Inc.'),
                self._compile_regex('bar pub.')
             ])
        }
        self.assertEqual(expect_parsed_regex_lookup, parser.parsed_regex_lookup)


class TestBuildStringValueCanonicalizer(TestCase):
    def test_returns_given_as_is_when_used_as_callable(self):
        c = _build_string_value_canonicalizer(b'canonical_publisher.yaml')
        actual = c('Manning')
        self.assertEqual('Manning', actual)

    def test_returns_expected_when_used_as_callable(self):
        c = _build_string_value_canonicalizer(b'canonical_publisher.yaml')
        actual = c('Manning Publications')
        self.assertEqual('Manning', actual)


class CaseCanonicalizers(object):
    """
    Common functionality for classes that load test data from YAML files.
    """
    FILENAME_TESTDATA = None

    @classmethod
    def setUpClass(cls):
        assert cls.FILENAME_TESTDATA, (
            'Inheriting classes must specify the filename of an existing yaml '
            'file located in the same directory as this file.'
        )
        cls.TESTDATA = _load_test_data_from_yaml_file(cls.FILENAME_TESTDATA)

    def test_loaded_test_data_is_ok(self):
        self.assertIsInstance(self.TESTDATA, dict)
        self.assertGreater(len(self.TESTDATA), 1)


class TestCanonicalizePublisher(CaseCanonicalizers, TestCase):
    FILENAME_TESTDATA = 'test_core_metadata_canonicalize_publisher.yaml'

    def test_canonicalize_publisher(self):
        for canonical, equivalent_values in self.TESTDATA.items():
            for equivalent_value in equivalent_values:
                with self.subTest(given_expected=(equivalent_value, canonical)):
                    actual = _canonicalize_publisher(equivalent_value)
                    self.assertEqual(canonical, actual)

    def test_does_not_canonicalize_non_publishers(self):
        for given_non_publisher in [
            '',
            'foo',
            'then press real hard',
            'publishing is a thing',
            'the academic press probably applies academical weight',
        ]:
            with self.subTest(given=given_non_publisher):
                actual = _canonicalize_publisher(given_non_publisher)
                self.assertEqual(given_non_publisher, actual)


class TestCanonicalizeLanguage(CaseCanonicalizers, TestCase):
    FILENAME_TESTDATA = 'test_core_metadata_canonicalize_language.yaml'

    def test_canonicalizes_languages(self):
        for canonical, equivalent_values in self.TESTDATA.items():
            for equivalent_value in equivalent_values:
                actual = _canonicalize_language(equivalent_value)

                with self.subTest(given_expected=(equivalent_value, canonical)):
                    self.assertEqual(canonical, actual)

                with self.subTest(actual=actual):
                    self.assertTrue(actual.isupper(), 'Expected upper-case canonical form')

    def test_does_not_canonicalize_non_languages(self):
        for given_non_language in [
            '',
            'foo',
            'en katt slickade på osten',
            'ovanstående text är på svenska',
            'det var en svensk katt',
            'new english review',
            'english is a language',
        ]:
            with self.subTest(given=given_non_language):
                actual = _canonicalize_language(given_non_language)
                self.assertEqual(given_non_language, actual)


class TestCanonicalizeCreatortool(CaseCanonicalizers, TestCase):
    FILENAME_TESTDATA = 'test_core_metadata_canonicalize_creatortool.yaml'

    def test_canonicalize_creatortool(self):
        for canonical, equivalent_values in self.TESTDATA.items():
            for equivalent_value in equivalent_values:
                with self.subTest(given_expected=(equivalent_value, canonical)):
                    actual = _canonicalize_creatortool(equivalent_value)
                    self.assertEqual(canonical, actual)

    def test_does_not_canonicalize_non_creatortools(self):
        for given_non_creatortool in [
            '',
            'foo',
        ]:
            with self.subTest(given=given_non_creatortool):
                actual = _canonicalize_language(given_non_creatortool)
                self.assertEqual(given_non_creatortool, actual)


class TestStringValueCanonicalizer(TestCase):
    def _compile_regex(self, pattern):
        # NOTE: Compilation flags must match those used in the implementation.
        return re.compile(pattern, re.IGNORECASE)

    def test_returns_values_as_is_when_given_empty_lookup_data(self):
        c = StringValueCanonicalizer(literal_lookup_dict=dict(), regex_lookup_dict=dict())

        for given_and_expected in [
            '',
            'foo',
            'foo bar'
        ]:
            with self.subTest(given_and_expected=given_and_expected):
                actual = c(given_and_expected)
                self.assertEqual(given_and_expected, actual)

    def test_replaces_one_value_matching_one_regex_pattern(self):
        regex_lookup_dict = {
            'BAZ': [
                self._compile_regex('.*foo')
            ]
        }
        c = StringValueCanonicalizer(literal_lookup_dict=dict(), regex_lookup_dict=regex_lookup_dict)

        for given in [
            'foo',
            'foo foo',
            'fooo',
            'fooo foo',
            'foo fooo',
            'foo bar',
            'fooo bar',
            'bar foo',
            'bar foo',
        ]:
            with self.subTest():
                actual = c(given)
                self.assertEqual('BAZ', actual)

    def test_replaces_two_values_matching_one_regex_pattern_each(self):
        regex_lookup_dict = {
            'BAZ': [
                self._compile_regex('foo')
            ],
            'MEOW': [
                self._compile_regex('w')
            ]
        }
        c = StringValueCanonicalizer(literal_lookup_dict=dict(), regex_lookup_dict=regex_lookup_dict)

        for given, expected in [
            ('BAZ',     'BAZ'),
            ('baz',     'BAZ'),
            ('foo',     'BAZ'),
            ('foo foo', 'BAZ'),

            ('MEOW', 'MEOW'),
            ('meow', 'MEOW'),
            ('w',    'MEOW'),
            ('ww',   'MEOW'),

            # Patterns for both 'BAZ' and 'MEOW' match.
            # TODO: [incomplete] Result depends on order in 'value_lookup_dict'.. ?
            ('foow', 'BAZ'),
            ('foo w', 'BAZ'),
            ('w foo', 'BAZ'),
        ]:
            with self.subTest(given_expected=(given, expected)):
                actual = c(given)
                self.assertEqual(expected, actual)

        # Expect these to not match and be passed through as-is.
        for given_and_expected in [
            'BAZ BAZ',
            'baz baz',
        ]:
            with self.subTest():
                actual = c(given_and_expected)
                self.assertEqual(given_and_expected, given_and_expected)

    def test_uses_value_with_longest_match_in_case_of_conflicts(self):
        regex_lookup_dict = {
            'FOO': [
                self._compile_regex('F+')
            ],
            'BAR': [
                self._compile_regex('B+')
            ]
        }
        c = StringValueCanonicalizer(literal_lookup_dict=dict(), regex_lookup_dict=regex_lookup_dict)

        for given, expected in [
            ('F',     'FOO'),
            ('FF',    'FOO'),
            ('FFB',   'FOO'),
            ('BFF',   'FOO'),
            # ('FFBB',  'FOO'),  # TODO: Handle tied match lengths?
            ('B',     'BAR'),
            ('BB',    'BAR'),
            ('BBF',   'BAR'),
            ('FBB',   'BAR'),
            # ('BBFF',  'BAR'),  # TODO: Handle tied match lengths?
        ]:
            with self.subTest(given_expected=(given, expected)):
                actual = c(given)
                self.assertEqual(expected, actual)

    def test_uses_value_with_longest_match_in_case_of_conflicts_multiple_patterns(self):
        regex_lookup_dict = {
            'FOO': [
                self._compile_regex('f+'),
                self._compile_regex('x+')
            ],
            'BAR': [
                self._compile_regex('b+'),
                self._compile_regex('y+')
            ]
        }
        c = StringValueCanonicalizer(literal_lookup_dict=dict(), regex_lookup_dict=regex_lookup_dict)

        for given, expected in [
            ('f',     'FOO'),
            ('ff',    'FOO'),
            ('x',     'FOO'),
            ('xx',    'FOO'),
            ('fx',    'FOO'),
            ('xf',    'FOO'),
            ('xxff',  'FOO'),
            ('ffxx',  'FOO'),

            ('b',     'BAR'),
            ('bb',    'BAR'),
            ('y',     'BAR'),
            ('yy',    'BAR'),
            ('by',    'BAR'),
            ('yb',    'BAR'),
            ('yybb',  'BAR'),
            ('bbyy',  'BAR'),

            ('ffb',   'FOO'),
            ('bff',   'FOO'),
            ('ffy',   'FOO'),
            ('yff',   'FOO'),

            ('fbb',   'BAR'),
            ('bbf',   'BAR'),
            ('bbx',   'BAR'),
            ('xbb',   'BAR'),

            # ('ffBB',  'FOO'),  # TODO: Handle tied match lengths?
            # ('bbFF',  'BAR'),  # TODO: Handle tied match lengths?

            ('ffff bb',  'FOO'),
            ('fxfx bb',  'FOO'),
            ('fxxx bb',  'FOO'),
            ('xxxx bb',  'FOO'),

            ('bbbb ff',  'BAR'),
            ('byyy ff',  'BAR'),
            ('yyyy ff',  'BAR'),

            ('bb ffff',  'FOO'),
            ('ff ff bb', 'FOO'),
            ('bb ff ff', 'FOO'),

            ('ff bbb',  'BAR'),
            ('ff bbbb', 'BAR'),
            ('bbb ff',  'BAR'),
            ('bbbb ff', 'BAR'),

            ('ffff _ bb',   'FOO'),
            ('ffff _ bb _', 'FOO'),
            ('bb _ ffff',   'FOO'),
            ('ff _ ff bb',  'FOO'),
            ('bb _ ffff',   'FOO'),
            ('_ bb _ ffff', 'FOO'),
            ('_ fff _ bb',  'FOO'),
            ('_ bb _ ffff', 'FOO'),
        ]:
            with self.subTest(given_expected=(given, expected)):
                actual = c(given)
                self.assertEqual(expected, actual)
