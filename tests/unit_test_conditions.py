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

from core.config.conditions import RuleCondition


class TestRuleCondition(TestCase):
    def test_rulecondition_is_defined(self):
        self.assertIsNotNone(RuleCondition)


class TestRuleConditionFromValidInput(TestCase):
    def test_contents_mime_type_condition(self):
        self.rc = RuleCondition('contents.mime_type', 'text/rtf')
        self.assertIsNotNone(self.rc)

    def test_filesystem_basename_condition(self):
        self.rc = RuleCondition('filesystem.basename', 'gmail.pdf')
        self.assertIsNotNone(self.rc)

    def test_filesystem_extension_condition(self):
        self.rc = RuleCondition('filesystem.extension', 'pdf')
        self.assertIsNotNone(self.rc)


class TestRuleConditionFromInvalidInput(TestCase):
    def test_invalid_contents_mime_type_condition(self):
        with self.assertRaises(ValueError):
            self.rc = RuleCondition('contents.mime_type', '/')

    def test_invalid_filesystem_basename_condition(self):
        with self.assertRaises(ValueError):
            self.rc = RuleCondition('filesystem.basename', None)

    def test_invalid_filesystem_extension_condition(self):
        with self.assertRaises(ValueError):
            self.rc = RuleCondition('filesystem.extension', None)
