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

from core.config.rule_parsers import (
    RegexRuleParser,
    RuleParser,
    get_instantiated_parsers,
)


class TestRuleParserFunctions(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_get_instantiated_parsers_returns_list(self):
        self.assertTrue(isinstance(get_instantiated_parsers(), list))

    def test_get_instantiated_parsers_returns_3_parsers(self):
        # TODO: Likely to break; Fix or remove!
        self.assertEqual(len(get_instantiated_parsers()), 3)

    def test_get_instantiated_parsers_returns_class_objects(self):
        parsers = get_instantiated_parsers()
        for p in parsers:
            self.assertEqual(type(p), type)


class TestRegexRuleParser(TestCase):
    def test_get_validation_function(self):
        self.fail()
