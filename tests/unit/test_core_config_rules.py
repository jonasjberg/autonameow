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

from unittest import TestCase

import unit.constants as uuconst
import unit.utils as uu
from core import constants as C
from core.config.rules import (
    is_valid_source,
    InvalidRuleConditionError,
    Rule,
    RuleCondition
)
from core.model import MeowURI


uu.init_provider_registry()


def _get_rule(*args, **kwargs):
    test_default_conditions = kwargs.get('conditions') or list()
    test_default_data_sources = kwargs.get('data_sources') or dict()
    test_default_name_template = kwargs.get('name_template') or 'dummy'
    kwargs.update({
        'conditions': test_default_conditions,
        'data_sources': test_default_data_sources,
        'name_template': test_default_name_template
    })
    return Rule(*args, **kwargs)


MOCK_CONDITIONS_A = ['a']
MOCK_CONDITIONS_B = ['b']
MOCK_DATA_SOURCES_A = {'a': 'foo'}
MOCK_DATA_SOURCES_B = {'b': 'bar'}


class TestRule(TestCase):
    def setUp(self):
        self.default_rule = _get_rule()

    def test_required_arguments_no_conditions_no_data_sources(self):
        self.assertEqual([], self.default_rule.conditions)
        self.assertEqual(dict(), self.default_rule.data_sources)
        self.assertEqual('dummy', self.default_rule.name_template)

    def test_required_arguments_no_data_sources(self):
        rule = _get_rule(conditions=MOCK_CONDITIONS_A)
        self.assertEqual(MOCK_CONDITIONS_A, rule.conditions)
        self.assertEqual(dict(), rule.data_sources)
        self.assertEqual('dummy', rule.name_template)

    def test_required_arguments(self):
        rule = _get_rule(
            conditions=MOCK_CONDITIONS_A,
            data_sources=MOCK_DATA_SOURCES_A,
        )
        self.assertEqual(MOCK_CONDITIONS_A, rule.conditions)
        self.assertEqual(len(MOCK_DATA_SOURCES_A), len(rule.data_sources))
        self.assertEqual('dummy', rule.name_template)

    def test_exact_match_coerces_to_false_if_none(self):
        rule = _get_rule(exact_match=None)
        self.assertEqual(rule.exact_match, False)

    def test_exact_match_uses_default_value_if_left_unspecified(self):
        self.assertEqual(self.default_rule.exact_match, False)

    def test_ranking_bias_uses_default_value_if_none(self):
        a = _get_rule(ranking_bias=None)
        self.assertEqual(C.DEFAULT_RULE_RANKING_BIAS, a.ranking_bias)

    def test_ranking_bias_uses_default_value_if_left_unspecified(self):
        self.assertEqual(C.DEFAULT_RULE_RANKING_BIAS, self.default_rule.ranking_bias)

    def test_description_ses_default_value_if_none(self):
        a = _get_rule(description=None)
        self.assertEqual(C.DEFAULT_RULE_DESCRIPTION, a.description)

    def test_description_uses_default_value_if_left_unspecified(self):
        self.assertEqual(C.DEFAULT_RULE_DESCRIPTION, self.default_rule.description)


class TestRuleComparison(TestCase):
    def test_should_not_be_equal_to_objects_of_another_type(self):
        a = _get_rule()
        for b in [None, False, object(), {}, [], 'foo']:
            self.assertNotEqual(a, b)

    def test_should_be_equal_to_itself(self):
        a = _get_rule()
        self.assertEqual(a, a)

    def test_hashable_for_set_membership(self):
        container = set()

        a = _get_rule(data_sources={'foo': 'bar'})
        container.add(a)
        self.assertEqual(1, len(container))

        b = _get_rule(data_sources={'baz': 'bar'})
        container.add(b)
        container.add(b)
        self.assertEqual(2, len(container))

        c = _get_rule(name_template='meow')
        container.add(c)
        container.add(c)
        self.assertEqual(3, len(container))

        # Descriptions are ignored.
        d = _get_rule(name_template='meow', description='MEOW MEOW')
        container.add(d)
        self.assertEqual(3, len(container))

    def test_equality_only_required_arguments(self):
        a = _get_rule(name_template='dummy')
        b = _get_rule(name_template='dummy')
        self.assertEqual(a, b)

    def test_equality_required_arguments_no_data_sources(self):
        a = _get_rule()
        b = _get_rule(
            conditions=MOCK_CONDITIONS_A,
        )
        c = _get_rule(
            conditions=MOCK_CONDITIONS_A,
        )
        d = _get_rule(
            conditions=MOCK_CONDITIONS_A,
            name_template='foo',
        )
        self.assertNotEqual(a, b)
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, d)
        self.assertNotEqual(b, d)
        self.assertNotEqual(c, d)
        self.assertEqual(b, c)

    def test_equality_required_arguments(self):
        a = _get_rule(
            conditions=MOCK_CONDITIONS_A,
            data_sources=MOCK_DATA_SOURCES_A,
        )
        b = _get_rule(
            conditions=MOCK_CONDITIONS_A,
            data_sources=MOCK_DATA_SOURCES_A,
        )
        c = _get_rule(
            conditions=MOCK_CONDITIONS_A,
            data_sources=MOCK_DATA_SOURCES_B,
        )
        d = _get_rule(
            conditions=MOCK_CONDITIONS_B,
            data_sources=MOCK_DATA_SOURCES_A,
        )
        e = _get_rule(
            description='meow',
            conditions=MOCK_CONDITIONS_B,
            data_sources=MOCK_DATA_SOURCES_B,
        )
        f = _get_rule(
            description='MEOW MEOW',
            conditions=MOCK_CONDITIONS_B,
            data_sources=MOCK_DATA_SOURCES_B,
        )
        # Rules should equal themselves.
        self.assertEqual(a, a)
        self.assertEqual(b, b)
        self.assertEqual(c, c)
        self.assertEqual(d, d)
        self.assertEqual(e, e)
        self.assertEqual(f, f)

        # Equality based on conditions and data sources.
        self.assertEqual(a, b)
        # Descriptions are ignored.
        self.assertEqual(e, f)

        # Inequality based on conditions and data sources.
        self.assertNotEqual(a, c)
        self.assertNotEqual(a, d)
        self.assertNotEqual(a, e)
        self.assertNotEqual(a, f)
        self.assertNotEqual(b, c)
        self.assertNotEqual(b, d)
        self.assertNotEqual(b, e)
        self.assertNotEqual(b, f)
        self.assertNotEqual(c, d)
        self.assertNotEqual(c, e)
        self.assertNotEqual(c, f)
        self.assertNotEqual(d, e)
        self.assertNotEqual(d, f)


class TestDummyRule(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.rule = uu.get_dummy_rule()

    def test_rule_string(self):
        actual = str(self.rule)
        self.assertTrue(uu.is_internalstring(actual))

    def test_rule_hash(self):
        actual = hash(self.rule)
        self.assertIsNotNone(actual)

    def test_stringify_dummy_rule(self):
        s = self.rule.stringify()
        self.assertIsInstance(s, str)


class TestRuleConditionComparison(TestCase):
    @staticmethod
    def _get_rule_condition(meowuri, expression):
        return RuleCondition(MeowURI(meowuri), expression)

    def test_not_equal_to_objects_of_another_type(self):
        a = self._get_rule_condition(
            meowuri=uuconst.MEOWURI_FS_XPLAT_MIMETYPE,
            expression='text/plain'
        )
        for b in [None, {}, [], 'foo', object()]:
            self.assertNotEqual(a, b)

    def test_is_equal_to_itself(self):
        a = self._get_rule_condition(
            meowuri=uuconst.MEOWURI_FS_XPLAT_MIMETYPE,
            expression='text/plain'
        )
        self.assertEqual(a, a)

    def test_hashable_for_set_membership(self):
        # NOTE(jonas): Assumes dummy rule conditions are unique.
        all_ruleconditions = uu.get_dummy_rulecondition_instances()
        container = set(all_ruleconditions)
        self.assertEqual(len(all_ruleconditions), len(container))

    def test_equal_for_same_meowuri_identical_expression(self):
        a = self._get_rule_condition(
            meowuri=uuconst.MEOWURI_FS_XPLAT_MIMETYPE,
            expression='text/plain'
        )
        b = self._get_rule_condition(
            meowuri=uuconst.MEOWURI_FS_XPLAT_MIMETYPE,
            expression='text/plain'
        )
        self.assertEqual(a, b)

    def test_not_equal_for_same_meowuri_different_expressions(self):
        a = self._get_rule_condition(
            meowuri=uuconst.MEOWURI_FS_XPLAT_MIMETYPE,
            expression='text/plain'
        )
        b = self._get_rule_condition(
            meowuri=uuconst.MEOWURI_FS_XPLAT_MIMETYPE,
            expression='application/pdf'
        )
        self.assertNotEqual(a, b)

    def test_not_equal_for_different_meowuris_identical_expression(self):
        a = self._get_rule_condition(
            meowuri=uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL,
            expression='.*'
        )
        b = self._get_rule_condition(
            meowuri=uuconst.MEOWURI_FS_XPLAT_BASENAME_PREFIX,
            expression='.*'
        )
        self.assertNotEqual(a, b)

    def test_not_equal_for_different_meowuris_different_expressions(self):
        a = self._get_rule_condition(
            meowuri=uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL,
            expression='foo'
        )
        b = self._get_rule_condition(
            meowuri=uuconst.MEOWURI_FS_XPLAT_BASENAME_PREFIX,
            expression='bar'
        )
        self.assertNotEqual(a, b)


def _get_rule_condition(meowuri, expression):
    assert isinstance(meowuri, MeowURI)
    return RuleCondition(meowuri, expression)


class TestRuleConditionFromValidInput(TestCase):
    def _is_valid(self, query, expression):
        uri = MeowURI(query)
        self.assertIsInstance(uri, MeowURI, 'Dependency init failed')

        actual = _get_rule_condition(uri, expression)
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, RuleCondition)

    def test_condition_contents_mime_type(self):
        uri = uuconst.MEOWURI_FS_XPLAT_MIMETYPE
        self._is_valid(uri, 'text/rtf')
        self._is_valid(uri, 'text/*')
        self._is_valid(uri, '*/application')
        self._is_valid(uri, '*/*')

    def test_condition_contents_mime_type_with_expression_list(self):
        uri = uuconst.MEOWURI_FS_XPLAT_MIMETYPE
        self._is_valid(uri, ['text/rtf'])
        self._is_valid(uri, ['text/*'])
        self._is_valid(uri, ['*/application'])
        self._is_valid(uri, ['*/*'])

        self._is_valid(uri, ['text/rtf', 'text/rtf'])
        self._is_valid(uri, ['text/rtf', 'text/*'])
        self._is_valid(uri, ['text/*', '*/rtf'])
        self._is_valid(uri, ['*/application', 'pdf/application'])
        self._is_valid(uri, ['*/*', '*/*'])

    def test_condition_filesystem_basename_full(self):
        uri = uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL
        self._is_valid(uri, 'foo.tar.gz')
        self._is_valid(uri, 'foo.*')
        self._is_valid(uri, '.*foo.*')
        self._is_valid(uri, '.*')

    def test_condition_filesystem_basename_full_with_expression_list(self):
        self.skipTest('TODO: ..')
        uri = uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL
        self._is_valid(uri, ['foo.tar.gz'])
        self._is_valid(uri, ['foo.*'])
        self._is_valid(uri, ['.*foo.*'])
        self._is_valid(uri, ['.*'])

    def test_condition_filesystem_basename_prefix(self):
        uri = uuconst.MEOWURI_FS_XPLAT_BASENAME_PREFIX
        self._is_valid(uri, 'foo')
        self._is_valid(uri, '.*')
        self._is_valid(uri, 'foo(bar)?')

    def test_condition_filesystem_basename_suffix(self):
        uri = uuconst.MEOWURI_FS_XPLAT_BASENAME_SUFFIX
        self._is_valid(uri, 'tar.gz')
        self._is_valid(uri, 'tar.*')

    def test_condition_filesystem_extension(self):
        uri = uuconst.MEOWURI_FS_XPLAT_EXTENSION
        self._is_valid(uri, 'pdf')
        self._is_valid(uri, '.*')
        self._is_valid(uri, '.?')
        self._is_valid(uri, 'pdf?')

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
        with self.assertRaises(InvalidRuleConditionError):
            uri = MeowURI(query)
            _ = _get_rule_condition(uri, expression)

    def test_invalid_condition_contents_mime_type(self):
        uri = uuconst.MEOWURI_FS_XPLAT_MIMETYPE
        self._assert_raises(uri, None)
        self._assert_raises(uri, '')
        self._assert_raises(uri, '/')
        self._assert_raises(uri, 'application/*//pdf')
        self._assert_raises(uri, 'application///pdf')
        self._assert_raises(uri, 'text/')

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
        self._assert_raises(uuconst.MEOWURI_FS_XPLAT_EXTENSION, None)
        self._assert_raises(uuconst.MEOWURI_FS_XPLAT_EXTENSION, '')


class TestRuleConditionGivenInvalidMeowURI(TestCase):
    def _assert_raises(self, meowuri, expression):
        with self.assertRaises(AssertionError):
            _ = _get_rule_condition(meowuri, expression)

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
        unhandled_meowuri = uu.as_meowuri('extractor.foo.bar')
        with self.assertRaises(InvalidRuleConditionError):
            _ = _get_rule_condition(unhandled_meowuri, 'baz')


class TestRuleConditionMethods(TestCase):
    def setUp(self):
        self.maxDiff = None
        uri = MeowURI(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        self.a = RuleCondition(uri, 'application/pdf')

    def test_rule___repr__(self):
        expected = 'RuleCondition({}, application/pdf)'.format(
            uuconst.MEOWURI_FS_XPLAT_MIMETYPE
        )
        self.assertEqual(expected, repr(self.a))

    def test_rule___repr__exhaustive(self):
        expected_reprs = []

        for raw_condition in uu.get_dummy_raw_conditions():
            for meowuri, expression in raw_condition.items():
                expected_reprs.append(
                    'RuleCondition({}, {})'.format(meowuri, expression)
                )

        for condition, expect in zip(uu.get_dummy_rulecondition_instances(),
                                     expected_reprs):
            self.assertEqual(expect, repr(condition))


class TestGetValidRuleCondition(TestCase):
    def _aV(self, query, expression):
        uri = MeowURI(query)
        actual = _get_rule_condition(uri, expression)
        self.assertIsNotNone(actual)
        self.assertIsInstance(actual, RuleCondition)

    def _aR(self, query, expression):
        uri = MeowURI(query)
        with self.assertRaises(InvalidRuleConditionError):
            _ = _get_rule_condition(uri, expression)

    def test_returns_valid_rule_condition_for_valid_query_valid_data(self):
        self._aV(uuconst.MEOWURI_FS_XPLAT_MIMETYPE, 'application/pdf')
        self._aV(uuconst.MEOWURI_FS_XPLAT_MIMETYPE, 'text/rtf')
        self._aV(uuconst.MEOWURI_FS_XPLAT_MIMETYPE, 'image/*')
        self._aV(uuconst.MEOWURI_FS_XPLAT_EXTENSION, 'pdf')
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
        self._aR(uuconst.MEOWURI_FS_XPLAT_EXTENSION, '')
        self._aR(uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL, None)
        self._aR(uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL, '')


class TestIsValidSourceSpecification(TestCase):
    def test_returns_false_given_none_or_empty_source(self):
        for given in [None, '']:
            self.assertFalse(is_valid_source(given))

    def test_returns_false_given_invalid_source(self):
        for given in [
            ' ',
            'not.a.valid.source.surely',
            'foo',
            'foo.bar',
            'foo.bar.baz.',
        ]:
            self.assertFalse(is_valid_source(given))

    def test_returns_true_given_valid_source(self):
        for given_str in [
            # Generic sources
            uuconst.MEOWURI_GEN_CONTENTS_TEXT,
            uuconst.MEOWURI_GEN_METADATA_AUTHOR,

            # Extractor sources
            uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE,
            uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL,
            uuconst.MEOWURI_FS_XPLAT_MIMETYPE
        ]:
            with self.subTest(given=given_str):
                given = uu.as_meowuri(given_str)
                self.assertTrue(is_valid_source(given))
