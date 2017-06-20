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
from core.evaluate.rulematcher import (
    all_template_fields_defined,
    RuleMatcher
)


class TestRuleMatcher(TestCase):
    def setUp(self):
        self.rm = RuleMatcher(None, None, None)

    def test_rule_matcher_can_be_instantiated(self):
        self.assertIsNotNone(self.rm)


class TestAllTemplateFieldsDefined(TestCase):
    def setUp(self):
        self.template = '{datetime} {title} -- tag.{extension}'
        self.data_sources_ok = {'datetime': 'dummy',
                                'extension': 'dummy',
                                'title': 'dummy'}
        self.data_sources_missing = {'datetime': 'dummy',
                                     'extension': 'dummy'}

    def test_return_false_if_sources_does_not_include_all_template_fields(self):
        self.assertFalse(all_template_fields_defined(self.template,
                                                     self.data_sources_missing))

    def test_return_true_if_sources_contain_all_template_fields(self):
        self.assertTrue(all_template_fields_defined(self.template,
                                                    self.data_sources_ok))
