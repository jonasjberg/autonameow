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

from core.config.rules import FileRule

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

        self.filerule = FileRule()

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
        self.filerule = FileRule(description='dummy',
                                 exact_match=False,
                                 weight=0.5,
                                 name_template='dummy',
                                 conditions='dummy',
                                 data_sources='dummy')

    def test_filerule_string(self):
        actual = str(self.filerule)
        self.assertTrue(isinstance(actual, str))
