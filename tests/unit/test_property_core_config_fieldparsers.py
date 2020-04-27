# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from unittest import SkipTest, TestCase

try:
    from hypothesis import given
    from hypothesis.strategies import binary
    from hypothesis.strategies import booleans
    from hypothesis.strategies import characters
    from hypothesis.strategies import integers
    from hypothesis.strategies import text
except ImportError:
    raise SkipTest('Unable to import "hypothesis". Skipping ..')

from core.config.field_parsers import BooleanConfigFieldParser
from core.config.field_parsers import DateTimeConfigFieldParser
from core.config.field_parsers import MimeTypeConfigFieldParser
from core.config.field_parsers import RegexConfigFieldParser


class CaseFieldParserValidation(object):
    FIELD_PARSER_CLASS = None

    def setUp(self):
        assert self.FIELD_PARSER_CLASS is not None
        p = self.FIELD_PARSER_CLASS()
        self.val_func = p.get_validation_function()

    def _assert_return_type_bool(self, s):
        try:
            actual = self.val_func(s)
        except Exception as e:
            raise AssertionError('"{!s}" raised: {!s}'.format(s, e))
        else:
            self.assertIsInstance(actual, bool)

    def test_validation_function_is_callable(self):
        self.assertTrue(callable(self.val_func))

    @given(text())
    def test_text_input(self, s):
        self._assert_return_type_bool(s)

    @given(binary())
    def test_binary_input(self, s):
        self._assert_return_type_bool(s)

    @given(booleans())
    def test_boolean_input(self, s):
        self._assert_return_type_bool(s)

    @given(characters())
    def test_character_input(self, s):
        self._assert_return_type_bool(s)

    @given(integers())
    def test_integer_input(self, s):
        self._assert_return_type_bool(s)


class TestRegexFieldParserReturnsBooleans(CaseFieldParserValidation, TestCase):
    FIELD_PARSER_CLASS = RegexConfigFieldParser


class TestBooleanConfigFieldParser(CaseFieldParserValidation, TestCase):
    FIELD_PARSER_CLASS = BooleanConfigFieldParser


class TestDateTimeConfigFieldParser(CaseFieldParserValidation, TestCase):
    FIELD_PARSER_CLASS = DateTimeConfigFieldParser


class TestNameTemplateConfigFieldParser(CaseFieldParserValidation, TestCase):
    FIELD_PARSER_CLASS = MimeTypeConfigFieldParser
