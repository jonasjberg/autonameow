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

from unittest import TestCase

from core import (
    exceptions,
    constants
)
from core.config import rules
import unit_utils as uu


class TestRuleCondition(TestCase):
    def test_rulecondition_is_defined(self):
        self.assertIsNotNone(rules.RuleCondition)


class TestRuleConditionFromValidInput(TestCase):
    def _assert_valid(self, query, data):
        actual = rules.RuleCondition(query, data)
        self.assertIsNotNone(actual)
        self.assertTrue(isinstance(actual, rules.RuleCondition))

    def test_condition_contents_mime_type(self):
        self._assert_valid('filesystem.contents.mime_type', 'text/rtf')
        self._assert_valid('filesystem.contents.mime_type', 'text/*')
        self._assert_valid('filesystem.contents.mime_type', '*/application')
        self._assert_valid('filesystem.contents.mime_type', '*/*')

    def test_condition_filesystem_basename_full(self):
        self._assert_valid('filesystem.basename.full', 'foo.tar.gz')
        self._assert_valid('filesystem.basename.full', 'foo.*')
        self._assert_valid('filesystem.basename.full', '.*foo.*')
        self._assert_valid('filesystem.basename.full', '.*')

    def test_condition_filesystem_basename_prefix(self):
        self._assert_valid('filesystem.basename.prefix', 'foo')
        self._assert_valid('filesystem.basename.prefix', '.*')
        self._assert_valid('filesystem.basename.prefix', 'foo(bar)?')

    def test_condition_filesystem_basename_suffix(self):
        self._assert_valid('filesystem.basename.suffix', 'tar.gz')
        self._assert_valid('filesystem.basename.suffix', 'tar.*')

    def test_condition_filesystem_extension(self):
        self._assert_valid('filesystem.basename.extension', 'pdf')
        self._assert_valid('filesystem.basename.extension', '.*')
        self._assert_valid('filesystem.basename.extension', '.?')
        self._assert_valid('filesystem.basename.extension', 'pdf?')

    def test_condition_metadata_exiftool(self):
        self._assert_valid('metadata.exiftool.PDF:CreateDate', '1996')
        self._assert_valid('metadata.exiftool.PDF:Creator', 'foo')
        self._assert_valid('metadata.exiftool.PDF:ModifyDate', '1996-01-20')
        self._assert_valid('metadata.exiftool.PDF:Producer', 'foo')
        self._assert_valid('metadata.exiftool.XMP-dc:Creator', 'foo')
        self._assert_valid('metadata.exiftool.XMP-dc:Publisher', 'foo')
        self._assert_valid('metadata.exiftool.XMP-dc:Title', 'foo')


class TestRuleConditionFromInvalidInput(TestCase):
    def _assert_invalid(self, query, data):
        with self.assertRaises(exceptions.InvalidRuleError):
            _ = rules.get_valid_rule_condition(query, data)

    def test_invalid_condition_contents_mime_type(self):
        self._assert_invalid('filesystem.contents.mime_type', None)
        self._assert_invalid('filesystem.contents.mime_type', '')
        self._assert_invalid('filesystem.contents.mime_type', '/')
        self._assert_invalid('filesystem.contents.mime_type', 'application/*//pdf')
        self._assert_invalid('filesystem.contents.mime_type', 'application///pdf')
        self._assert_invalid('filesystem.contents.mime_type', 'text/')

    def test_invalid_condition_filesystem_basename_full(self):
        self._assert_invalid('filesystem.basename.full', None)
        self._assert_invalid('filesystem.basename.full', '')

    def test_invalid_condition_filesystem_basename_prefix(self):
        self._assert_invalid('filesystem.basename.prefix', None)
        self._assert_invalid('filesystem.basename.prefix', '')

    def test_invalid_condition_filesystem_basename_suffix(self):
        self._assert_invalid('filesystem.basename.suffix', None)
        self._assert_invalid('filesystem.basename.suffix', '')

    def test_invalid_condition_filesystem_extension(self):
        self._assert_invalid('filesystem.basename.extension', None)
        self._assert_invalid('filesystem.basename.extension', '')


class TestRuleConditionMethods(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.a = rules.RuleCondition('filesystem.contents.mime_type',
                                     'application/pdf')

    def test_rule___repr__(self):
        self.assertEqual(
            repr(self.a),
            'RuleCondition("filesystem.contents.mime_type", "application/pdf")'
        )

    def test_rule___repr__exhaustive(self):
        expected_reprs = []

        for raw_condition in uu.get_dummy_raw_conditions():
            for meowuri, expression in raw_condition.items():
                expected_reprs.append(
                    'RuleCondition("{}", "{}")'.format(meowuri, expression)
                )

        for condition, expect in zip(uu.get_dummy_rulecondition_instances(),
                                     expected_reprs):
            self.assertEqual(repr(condition), expect)


RULE_CONTENTS = {
    'description': 'First Entry in the Default Configuration',
    'exact_match': False,
    'weight': 0.5,
    'name_template': 'default_template_name',
    'conditions': {
        'filesystem': {
            'basename': {
                'extension': 'bar',
                'full': 'foo.bar',
                'prefix': 'foo',
                'suffix': 'bar',
            },
            'pathname': {
                'full': '~/foo',
                'parent': '~',
            },
            'contents': {
                'mime_type': '*/*'
            }
        },
    },
    'data_sources': {
        'datetime': None,
        'description': None,
        'title': None,
        'author': None,
        'publisher': None,
        'extension': 'filename.extension'
    }
}


class TestRuleMethods(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.rule = uu.get_dummy_rule()

    def test_rule_string(self):
        actual = str(self.rule)
        self.assertTrue(isinstance(actual, str))


class TestGetValidRuleCondition(TestCase):
    def test_get_valid_rule_condition_is_defined(self):
        self.assertIsNotNone(rules.get_valid_rule_condition)

    def _assert_valid(self, query, data):
        actual = rules.get_valid_rule_condition(query, data)
        self.assertIsNotNone(actual)
        self.assertTrue(isinstance(actual, rules.RuleCondition))

    def _assert_invalid(self, query, data):
        with self.assertRaises(exceptions.InvalidRuleError):
            _ = rules.get_valid_rule_condition(query, data)

    def test_returns_valid_rule_condition_for_valid_query_valid_data(self):
        self._assert_valid('filesystem.contents.mime_type', 'application/pdf')
        self._assert_valid('filesystem.contents.mime_type', 'text/rtf')
        self._assert_valid('filesystem.contents.mime_type', 'image/*')
        self._assert_valid('filesystem.basename.extension', 'pdf')
        self._assert_valid('filesystem.basename.full', 'foo.pdf')
        self._assert_valid('filesystem.pathname.full', '~/temp/foo')

    def test_returns_false_for_invalid_query_valid_data(self):
        self._assert_invalid('', 'application/pdf')
        self._assert_invalid('c.m', 'text/rtf')
        self._assert_invalid(None, 'pdf')
        self._assert_invalid('None', 'pdf')
        self._assert_invalid('filesystem..full', 'foo.pdf')
        self._assert_invalid('foo', '~/temp/foo')

    def test_returns_false_for_valid_query_invalid_data(self):
        self._assert_invalid('filesystem.contents.mime_type', 'application/*//pdf')
        self._assert_invalid('filesystem.contents.mime_type', 'application///pdf')
        self._assert_invalid('filesystem.contents.mime_type', 'text/')
        self._assert_invalid('filesystem.basename.extension', '')
        self._assert_invalid('filesystem.basename.full', None)
        self._assert_invalid('filesystem.pathname.full', '')

    def test_returns_false_for_invalid_query_invalid_data(self):
        self._assert_invalid('', 'application///pdf')
        self._assert_invalid('c.m', '')
        self._assert_invalid('foo', None)
        self._assert_invalid(None, 'foo')
        self._assert_invalid(None, None)


class TestIsValidSourceSpecification(TestCase):
    def test_empty_source_returns_false(self):
        self.assertFalse(rules.is_valid_source(None))
        self.assertFalse(rules.is_valid_source(''))

    def test_bad_source_returns_false(self):
        self.assertFalse(rules.is_valid_source('not.a.valid.source.surely'))
        self.assertFalse(rules.is_valid_source('foobar'))

    def test_good_source_returns_true(self):
        self.assertTrue(rules.is_valid_source('metadata.exiftool.PDF:CreateDate'))
        self.assertTrue(rules.is_valid_source('metadata.exiftool'))
        self.assertTrue(rules.is_valid_source('filesystem.basename.full'))
        self.assertTrue(rules.is_valid_source('filesystem.basename.extension'))
        self.assertTrue(rules.is_valid_source('filesystem.contents.mime_type'))


class TestParseConditions(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_parse_condition_filesystem_pathname_is_valid(self):
        raw_conditions = {'filesystem.pathname.full': '~/.config'}
        actual = rules.parse_conditions(raw_conditions)
        self.assertEqual(actual[0].meowuri, 'filesystem.pathname.full')
        self.assertEqual(actual[0].expression, '~/.config')

    def test_parse_condition_contents_mime_type_is_valid(self):
        raw_conditions = {'filesystem.contents.mime_type': 'image/jpeg'}
        actual = rules.parse_conditions(raw_conditions)
        self.assertEqual(actual[0].meowuri,
                         'filesystem.contents.mime_type')
        self.assertEqual(actual[0].expression,
                         'image/jpeg')

    def test_parse_condition_contents_metadata_is_valid(self):
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        raw_conditions = {
            'metadata.exiftool.EXIF:DateTimeOriginal': 'Defined',
        }
        actual = rules.parse_conditions(raw_conditions)
        self.assertEqual(actual[0].meowuri,
                         'metadata.exiftool.EXIF:DateTimeOriginal')
        self.assertEqual(actual[0].expression, 'Defined')


class TestParseRankingBias(TestCase):
    def test_negative_value_raises_configuration_syntax_error(self):
        with self.assertRaises(exceptions.ConfigurationSyntaxError):
            rules.parse_ranking_bias(-1)
            rules.parse_ranking_bias(-0.1)
            rules.parse_ranking_bias(-0.01)
            rules.parse_ranking_bias(-0.0000000001)

    def test_value_greater_than_one_raises_configuration_syntax_error(self):
        with self.assertRaises(exceptions.ConfigurationSyntaxError):
            rules.parse_ranking_bias(2)
            rules.parse_ranking_bias(1.1)
            rules.parse_ranking_bias(1.00000000001)

    def test_unexpected_type_value_raises_configuration_syntax_error(self):
        with self.assertRaises(exceptions.ConfigurationSyntaxError):
            rules.parse_ranking_bias('')
            rules.parse_ranking_bias(object())

    def test_none_value_returns_default_weight(self):
        self.assertEqual(rules.parse_ranking_bias(None),
                         constants.DEFAULT_RULE_RANKING_BIAS)

    def test_value_within_range_zero_to_one_returns_value(self):
        input_values = [0, 0.001, 0.01, 0.1, 0.5, 0.9, 0.99, 0.999, 1]

        for value in input_values:
            self.assertEqual(rules.parse_ranking_bias(value), value)
