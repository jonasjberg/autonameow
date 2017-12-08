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

import unit.constants as uuconst
import unit.utils as uu
from core import constants as C
from core import exceptions
from core.config.rules import (
    get_valid_rule_condition,
    is_valid_source,
    parse_conditions,
    parse_ranking_bias,
    Rule,
    RuleCondition
)
from core.model import MeowURI


uu.init_session_repository()
uu.init_provider_registry()


class TestRuleMethods(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.rule = uu.get_dummy_rule()

    def test_rule_string(self):
        actual = str(self.rule)
        self.assertTrue(uu.is_internalstring(actual))


class TestRuleConditionFromValidInput(TestCase):
    def _is_valid(self, query, expression):
        _meowuri = MeowURI(query)
        self.assertIsInstance(_meowuri, MeowURI, 'Dependency init failed')

        actual = RuleCondition(_meowuri, expression)
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, RuleCondition)

    def test_condition_contents_mime_type(self):
        _meowuri = uuconst.MEOWURI_FS_XPLAT_MIMETYPE
        self._is_valid(_meowuri, 'text/rtf')
        self._is_valid(_meowuri, 'text/*')
        self._is_valid(_meowuri, '*/application')
        self._is_valid(_meowuri, '*/*')

    def test_condition_contents_mime_type_with_expression_list(self):
        _meowuri = uuconst.MEOWURI_FS_XPLAT_MIMETYPE
        self._is_valid(_meowuri, ['text/rtf'])
        self._is_valid(_meowuri, ['text/*'])
        self._is_valid(_meowuri, ['*/application'])
        self._is_valid(_meowuri, ['*/*'])

        self._is_valid(_meowuri, ['text/rtf', 'text/rtf'])
        self._is_valid(_meowuri, ['text/rtf', 'text/*'])
        self._is_valid(_meowuri, ['text/*', '*/rtf'])
        self._is_valid(_meowuri, ['*/application', 'pdf/application'])
        self._is_valid(_meowuri, ['*/*', '*/*'])

    def test_condition_filesystem_basename_full(self):
        _meowuri = uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL
        self._is_valid(_meowuri, 'foo.tar.gz')
        self._is_valid(_meowuri, 'foo.*')
        self._is_valid(_meowuri, '.*foo.*')
        self._is_valid(_meowuri, '.*')

    def test_condition_filesystem_basename_full_with_expression_list(self):
        self.skipTest('TODO: ..')
        _meowuri = uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL
        self._is_valid(_meowuri, ['foo.tar.gz'])
        self._is_valid(_meowuri, ['foo.*'])
        self._is_valid(_meowuri, ['.*foo.*'])
        self._is_valid(_meowuri, ['.*'])

    def test_condition_filesystem_basename_prefix(self):
        _meowuri = uuconst.MEOWURI_FS_XPLAT_BASENAME_PREFIX
        self._is_valid(_meowuri, 'foo')
        self._is_valid(_meowuri, '.*')
        self._is_valid(_meowuri, 'foo(bar)?')

    def test_condition_filesystem_basename_suffix(self):
        _meowuri = uuconst.MEOWURI_FS_XPLAT_BASENAME_SUFFIX
        self._is_valid(_meowuri, 'tar.gz')
        self._is_valid(_meowuri, 'tar.*')

    def test_condition_filesystem_extension(self):
        _meowuri = uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT
        self._is_valid(_meowuri, 'pdf')
        self._is_valid(_meowuri, '.*')
        self._is_valid(_meowuri, '.?')
        self._is_valid(_meowuri, 'pdf?')

    def test_condition_metadata_exiftool(self):
        self._is_valid(uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE, '1996')
        self._is_valid(uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATOR, 'foo')
        self._is_valid(uuconst.MEOWURI_EXT_EXIFTOOL_PDFMODIFYDATE, '1996-01-20')
        self._is_valid(uuconst.MEOWURI_EXT_EXIFTOOL_PDFPRODUCER, 'foo')
        self._is_valid(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCCREATOR, 'foo')
        self._is_valid(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCPUBLISHER, 'foo')
        self._is_valid(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCTITLE, 'foo')


class TestRuleConditionGivenInvalidExpression(TestCase):
    def _assert_raises(self, query, expression):
        with self.assertRaises(exceptions.InvalidRuleError):
            _meowuri = MeowURI(query)
            _ = get_valid_rule_condition(_meowuri, expression)

    def test_invalid_condition_contents_mime_type(self):
        _meowuri = uuconst.MEOWURI_FS_XPLAT_MIMETYPE
        self._assert_raises(_meowuri, None)
        self._assert_raises(_meowuri, '')
        self._assert_raises(_meowuri, '/')
        self._assert_raises(_meowuri, 'application/*//pdf')
        self._assert_raises(_meowuri, 'application///pdf')
        self._assert_raises(_meowuri, 'text/')

    def test_invalid_condition_filesystem_basename_full(self):
        self._assert_raises(uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL, None)
        self._assert_raises(uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL, '')

    def test_invalid_condition_filesystem_basename_prefix(self):
        self._assert_raises(uuconst.MEOWURI_FS_XPLAT_BASENAME_PREFIX, None)
        self._assert_raises(uuconst.MEOWURI_FS_XPLAT_BASENAME_PREFIX, '')

    def test_invalid_condition_filesystem_basename_suffix(self):
        self._assert_raises(uuconst.MEOWURI_FS_XPLAT_BASENAME_SUFFIX, None)
        self._assert_raises(uuconst.MEOWURI_FS_XPLAT_BASENAME_SUFFIX, '')

    def test_invalid_condition_filesystem_extension(self):
        self._assert_raises(uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT, None)
        self._assert_raises(uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT, '')


class TestRuleConditionGivenInvalidMeowURI(TestCase):
    def _assert_raises(self, meowuri, expression):
        with self.assertRaises(TypeError):
            _ = RuleCondition(meowuri, expression)

    def test_meowuri_none_expression_valid(self):
        self._assert_raises(None, 'application/pdf')

    def test_meowuri_none_expression_invalid(self):
        self._assert_raises(None, 'application///pdf')

    def test_meowuri_none_expression_none(self):
        self._assert_raises(None, None)

    def test_meowuri_empty_string_expression_valid(self):
        self._assert_raises('', 'application/pdf')

    def test_meowuri_empty_string_expression_invalid(self):
        self._assert_raises('', 'application///pdf')

    def test_meowuri_empty_string_expression_none(self):
        self._assert_raises('', None)

    def test_meowuri_not_handled_by_parser(self):
        _unhandled_meowuri = uu.as_meowuri('extractor.foo.bar')
        with self.assertRaises(ValueError):
            _ = RuleCondition(_unhandled_meowuri, 'baz')


class TestRuleConditionMethods(TestCase):
    def setUp(self):
        self.maxDiff = None
        _meowuri = MeowURI(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        self.a = RuleCondition(_meowuri, 'application/pdf')

    def test_rule___repr__(self):
        expected = 'RuleCondition("{}", "application/pdf")'.format(
            uuconst.MEOWURI_FS_XPLAT_MIMETYPE
        )
        self.assertEqual(repr(self.a), expected)

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


class TestGetValidRuleCondition(TestCase):
    def _aV(self, query, expression):
        _meowuri = MeowURI(query)
        actual = get_valid_rule_condition(_meowuri, expression)
        self.assertIsNotNone(actual)
        self.assertTrue(isinstance(actual, RuleCondition))

    def _aR(self, query, expression):
        _meowuri = MeowURI(query)
        with self.assertRaises(exceptions.InvalidRuleError):
            _ = get_valid_rule_condition(_meowuri, expression)

    def test_returns_valid_rule_condition_for_valid_query_valid_data(self):
        self._aV(uuconst.MEOWURI_FS_XPLAT_MIMETYPE, 'application/pdf')
        self._aV(uuconst.MEOWURI_FS_XPLAT_MIMETYPE, 'text/rtf')
        self._aV(uuconst.MEOWURI_FS_XPLAT_MIMETYPE, 'image/*')
        self._aV(uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT, 'pdf')
        self._aV(uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL, 'foo.pdf')
        self._aV(uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL, '~/temp/foo')

    def test_returns_false_for_valid_query_invalid_data(self):
        self._aR(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE, '')
        self._aR(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE, 'foo')
        self._aR(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE, None)
        self._aR(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE, 'application///pdf')
        self._aR(uuconst.MEOWURI_FS_XPLAT_MIMETYPE, 'application/*//pdf')
        self._aR(uuconst.MEOWURI_FS_XPLAT_MIMETYPE, 'application///pdf')
        self._aR(uuconst.MEOWURI_FS_XPLAT_MIMETYPE, 'text/')
        self._aR(uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT, '')
        self._aR(uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL, None)
        self._aR(uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL, '')


class TestIsValidSourceSpecification(TestCase):
    def test_empty_source_returns_false(self):
        def _aF(test_input):
            self.assertFalse(is_valid_source(test_input))

        _aF(None)
        _aF('')

    def test_bad_source_returns_false(self):
        def _aF(test_input):
            self.assertFalse(is_valid_source(test_input))

        _aF(None)
        _aF('')
        _aF('not.a.valid.source.surely')
        _aF('foobar')
        _aF('exiftool')
        _aF('exiftool.PDF:CreateDate')
        _aF('metadata.exiftool')
        _aF('metadata.exiftool.PDF:CreateDate')

    def test_good_source_returns_true(self):
        def _aT(test_input):
            self.assertTrue(is_valid_source(test_input))

        _aT(MeowURI(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE))
        _aT(MeowURI(uuconst.MEOWURI_GEN_CONTENTS_TEXT))
        _aT(MeowURI(uuconst.MEOWURI_GEN_METADATA_AUTHOR))
        _aT(MeowURI(uuconst.MEOWURI_GEN_METADATA_CREATOR))
        _aT(MeowURI(uuconst.MEOWURI_GEN_METADATA_PRODUCER))
        _aT(MeowURI(uuconst.MEOWURI_GEN_METADATA_SUBJECT))
        _aT(MeowURI(uuconst.MEOWURI_GEN_METADATA_TAGS))
        _aT(MeowURI(uuconst.MEOWURI_GEN_METADATA_DATECREATED))
        _aT(MeowURI(uuconst.MEOWURI_GEN_METADATA_DATEMODIFIED))
        _aT(MeowURI(uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE))
        _aT(MeowURI(uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL))
        _aT(MeowURI(uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT))
        _aT(MeowURI(uuconst.MEOWURI_FS_XPLAT_MIMETYPE))


class TestParseConditions(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_parse_condition_filesystem_pathname_is_valid(self):
        raw_conditions = {
            uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL: '~/.config'
        }
        actual = parse_conditions(raw_conditions)
        self.assertEqual(actual[0].meowuri,
                         uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL)
        self.assertEqual(actual[0].expression, '~/.config')

    def test_parse_condition_contents_mime_type_is_valid(self):
        raw_conditions = {
            uuconst.MEOWURI_FS_XPLAT_MIMETYPE: 'image/jpeg'
        }
        actual = parse_conditions(raw_conditions)
        self.assertEqual(actual[0].meowuri, uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        self.assertEqual(actual[0].expression, 'image/jpeg')

    def test_parse_condition_contents_metadata_is_valid(self):
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        raw_conditions = {
            uuconst.MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL: 'Defined',
        }
        actual = parse_conditions(raw_conditions)
        self.assertEqual(actual[0].meowuri,
                         uuconst.MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL)
        self.assertEqual(actual[0].expression, 'Defined')


class TestParseRankingBias(TestCase):
    def test_negative_value_raises_configuration_syntax_error(self):
        with self.assertRaises(exceptions.ConfigurationSyntaxError):
            parse_ranking_bias(-1)
            parse_ranking_bias(-0.1)
            parse_ranking_bias(-0.01)
            parse_ranking_bias(-0.0000000001)

    def test_value_greater_than_one_raises_configuration_syntax_error(self):
        with self.assertRaises(exceptions.ConfigurationSyntaxError):
            parse_ranking_bias(2)
            parse_ranking_bias(1.1)
            parse_ranking_bias(1.00000000001)

    def test_unexpected_type_value_raises_configuration_syntax_error(self):
        with self.assertRaises(exceptions.ConfigurationSyntaxError):
            parse_ranking_bias('')
            parse_ranking_bias(object())

    def test_none_value_returns_default_weight(self):
        self.assertEqual(parse_ranking_bias(None),
                         C.DEFAULT_RULE_RANKING_BIAS)

    def test_value_within_range_zero_to_one_returns_value(self):
        input_values = [0, 0.001, 0.01, 0.1, 0.5, 0.9, 0.99, 0.999, 1]

        for value in input_values:
            self.assertEqual(parse_ranking_bias(value), value)
