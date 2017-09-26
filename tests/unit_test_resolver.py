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

from core.evaluate.resolver import (
    all_template_fields_defined,
    has_data_for_placeholder_fields
)
import unit_utils as uu


class TestAllTemplateFieldsDefined(TestCase):
    def setUp(self):
        self.template = '{datetime} {title} -- tag.{extension}'
        self.data_sources_ok = {'datetime': 'dummy',
                                'extension': 'dummy',
                                'title': 'dummy'}
        self.data_sources_missing = {'datetime': 'dummy',
                                     'extension': 'dummy'}

    def test_return_false_if_sources_does_not_include_all_template_fields(self):
        self.assertFalse(
            all_template_fields_defined(self.template,
                                        self.data_sources_missing)
        )

    def test_return_true_if_sources_contain_all_template_fields(self):
        self.assertTrue(
            all_template_fields_defined(self.template, self.data_sources_ok)
        )


class TestHasDataForPlaceholderFields(TestCase):
    def test_data_for_template_fields_present_returns_true(self):
        data = {
            'datetime': uu.str_to_datetime('2016-01-11 124132'),
            'extension': 'pdf',
            'title': 'Meow Gibson Rules Meow'
        }
        template = '{datetime} {title}.{extension}'

        actual = has_data_for_placeholder_fields(template, data)
        self.assertTrue(isinstance(actual, bool))
        self.assertTrue(actual)

    def test_field_data_missing_returns_false(self):
        data = {
            'extension': 'pdf',
            'title': 'Meow Gibson Rules Meow'
        }
        template = '{datetime} {title}.{extension}'

        actual = has_data_for_placeholder_fields(template, data)
        self.assertTrue(isinstance(actual, bool))
        self.assertFalse(actual)

    def test_none_field_data_returns_false(self):
        data = {
            'datetime': uu.str_to_datetime('2016-01-11 124132'),
            'extension': None,
            'title': 'Meow Gibson Rules Meow'
        }
        template = '{datetime} {title}.{extension}'

        actual = has_data_for_placeholder_fields(template, data)
        self.assertTrue(isinstance(actual, bool))
        self.assertFalse(actual)

    def test_field_data_but_no_placeholder_fields_return_true(self):
        data = {
            'datetime': uu.str_to_datetime('2016-01-11 124132'),
            'extension': None,
            'title': 'Meow Gibson Rules Meow'
        }
        template = 'foo bar'
        actual = has_data_for_placeholder_fields(template, data)
        self.assertTrue(isinstance(actual, bool))
        self.assertTrue(actual)

    def test_empty_data_and_no_placeholder_fields_return_true(self):
        data = {
        }
        template = 'foo bar'
        actual = has_data_for_placeholder_fields(template, data)
        self.assertTrue(isinstance(actual, bool))
        self.assertTrue(actual)
