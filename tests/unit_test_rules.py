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

from core.config import rules


class TestRuleCondition(TestCase):
    def test_rulecondition_is_defined(self):
        self.assertIsNotNone(rules.RuleCondition)


class TestRuleConditionFromValidInput(TestCase):
    def _assert_valid(self, query, data):
        actual = rules.RuleCondition(query, data)
        self.assertIsNotNone(actual)
        self.assertTrue(isinstance(actual, rules.RuleCondition))

    def test_condition_contents_mime_type(self):
        self._assert_valid('contents.mime_type', 'text/rtf')
        self._assert_valid('contents.mime_type', 'text/*')
        self._assert_valid('contents.mime_type', '*/application')
        self._assert_valid('contents.mime_type', '*/*')

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
        # with self.assertRaises((ValueError, TypeError)):
        #     actual = rules.get_valid_rule_condition(query, data)
        actual = rules.get_valid_rule_condition(query, data)
        self.assertFalse(actual)

    def test_invalid_condition_contents_mime_type(self):
        self._assert_invalid('contents.mime_type', None)
        self._assert_invalid('contents.mime_type', '')
        self._assert_invalid('contents.mime_type', '/')
        self._assert_invalid('contents.mime_type', 'application/*//pdf')
        self._assert_invalid('contents.mime_type', 'application///pdf')
        self._assert_invalid('contents.mime_type', 'text/')

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


RULE_CONTENTS = {
    'description': 'First Entry in the Default Configuration',
    'exact_match': False,
    'weight': 0.5,
    'name_template': 'default_template_name',
    'conditions': {
        'filename': {
            'pathname': '~/foo',
            'basename': 'foo.bar',
            'extension': 'bar'
        },
        'contents': {
            'mime_type': '*/*'
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
}


class TestFileRuleInstantiation(TestCase):
    def setUp(self):
        self.maxDiff = None

        self.filerule = rules.FileRule()

    def test_init_description_is_str_or_none(self):
        self.assertTrue(isinstance(self.filerule.description, str) or
                        self.filerule.description is None,
                        'FileRule description should be of type string or None')

    def test_init_exact_match_is_boolean(self):
        self.assertTrue(isinstance(self.filerule.exact_match, bool),
                        'FileRule exact_match should be a boolean')


class TestFileRuleMethods(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.filerule = rules.FileRule(description='dummy',
                                       exact_match=False,
                                       weight=0.5,
                                       name_template='dummy',
                                       conditions='dummy',
                                       data_sources='dummy')

    def test_filerule_string(self):
        actual = str(self.filerule)
        self.assertTrue(isinstance(actual, str))


class TestGetValidRuleCondition(TestCase):
    def test_get_valid_rule_condition_is_defined(self):
        self.assertIsNotNone(rules.get_valid_rule_condition)

    def _assert_valid(self, query, data):
        actual = rules.get_valid_rule_condition(query, data)
        self.assertIsNotNone(actual)
        self.assertTrue(isinstance(actual, rules.RuleCondition))

    def _assert_invalid(self, query, data):
        actual = rules.get_valid_rule_condition(query, data)
        self.assertFalse(actual)

    def test_returns_valid_rule_condition_for_valid_query_valid_data(self):
        self._assert_valid('contents.mime_type', 'application/pdf')
        self._assert_valid('contents.mime_type', 'text/rtf')
        self._assert_valid('contents.mime_type', 'image/*')
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
        self._assert_invalid('contents.mime_type', 'application/*//pdf')
        self._assert_invalid('contents.mime_type', 'application///pdf')
        self._assert_invalid('contents.mime_type', 'text/')
        self._assert_invalid('filesystem.basename.extension', '')
        self._assert_invalid('filesystem.basename.full', None)
        self._assert_invalid('filesystem.pathname.full', '')

    def test_returns_false_for_invalid_query_invalid_data(self):
        self._assert_invalid('', 'application///pdf')
        self._assert_invalid('c.m', '')
        self._assert_invalid('foo', None)
        self._assert_invalid(None, 'foo')
        self._assert_invalid(None, None)
