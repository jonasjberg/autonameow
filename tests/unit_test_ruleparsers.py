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

from core.config.field_parsers import (
    RegexConfigFieldParser,
    ConfigFieldParser,
    get_instantiated_field_parsers,
    available_field_parsers,
    MimeTypeConfigFieldParser,
    DateTimeConfigFieldParser,
    NameFormatConfigFieldParser
)


class TestRuleParserFunctions(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_get_instantiated_parsers_returns_list(self):
        self.assertTrue(isinstance(get_instantiated_field_parsers(), list))

    def test_get_instantiated_parsers_returns_arbitrary_number(self):
        # TODO: [hardcoded] Likely to break; Fix or remove!
        self.assertGreaterEqual(len(get_instantiated_field_parsers()), 3)

    def test_get_instantiated_parsers_returns_class_objects(self):
        parsers = get_instantiated_field_parsers()
        for p in parsers:
            self.assertTrue(hasattr(p, '__class__'))

    def test_get_available_parsers(self):
        self.assertIsNotNone(available_field_parsers())

    def test_get_available_parsers_returns_list_of_strings(self):
        self.assertTrue(isinstance(available_field_parsers(), list))

        for p in available_field_parsers():
            self.assertTrue(isinstance(p, str))


class TestRuleParser(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = ConfigFieldParser()

    def test_get_validation_function_should_raise_error_if_unimplemented(self):
        with self.assertRaises(NotImplementedError):
            self.p.get_validation_function()


class TestRuleParserSubclasses(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.parsers = get_instantiated_field_parsers()

    def test_setup(self):
        self.assertIsNotNone(self.parsers)

    def test_get_validation_function_should_not_return_none(self):
        for p in self.parsers:
            self.assertIsNotNone(p.get_validation_function())

    def test_get_validation_function_should_return_function(self):
        for p in self.parsers:
            self.assertTrue(hasattr(p.get_validation_function(), '__call__'))

    def test_validation_function_should_return_booleans(self):
        for p in self.parsers:
            valfunc = p.get_validation_function()

            result = valfunc('dummy_value')
            self.assertEqual(type(result), bool,
                             'Validation function should always return boolean')

            result = valfunc(None)
            self.assertEqual(type(result), bool,
                             'Validation function should always return boolean')

            result = valfunc('123')
            self.assertEqual(type(result), bool,
                             'Validation function should always return boolean')


class TestRegexRuleParser(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = RegexConfigFieldParser()
        self.val_func = self.p.get_validation_function()

    def test_validation_function_expect_fail(self):
        self.assertFalse(self.val_func('[[['))
        self.assertFalse(self.val_func('"  |[2'))
        self.assertFalse(self.val_func(None))

    def test_validation_function_expect_pass(self):
        self.assertTrue(self.val_func('[A-Za-z]+'))
        self.assertTrue(self.val_func('.*'))


class TestMimeTypeRuleParser(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = MimeTypeConfigFieldParser()
        self.val_func = self.p.get_validation_function()

    def test_validation_function_expect_fail(self):
        self.assertFalse(self.val_func('MJAOO'))
        self.assertFalse(self.val_func(None))
        self.assertFalse(self.val_func('imaggee'))
        self.assertFalse(self.val_func('.*'))
        self.assertFalse(self.val_func('*'))

    def test_validation_function_expect_pass(self):
        self.assertTrue(self.val_func('txt'))
        self.assertTrue(self.val_func('text/plain'))
        self.assertTrue(self.val_func('jpg'))


class TestDateTimeRuleParser(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = DateTimeConfigFieldParser()
        self.val_func = self.p.get_validation_function()

    def test_validation_function_expect_fail(self):
        self.assertFalse(self.val_func(None))
        self.assertFalse(self.val_func(1))

    def test_validation_function_expect_pass(self):
        self.assertTrue(self.val_func('%Y-%m-%d %H:%M:%S'))
        self.assertTrue(self.val_func(''))
        self.assertTrue(self.val_func('_'))


class TestNameFormatRuleParser(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = NameFormatConfigFieldParser()
        self.val_func = self.p.get_validation_function()

    def test_validation_function_expect_fail(self):
        # TODO: Write tests ..
        self.assertFalse(self.val_func(None))

    def test_validation_function_expect_pass(self):
        # TODO: Write tests ..
        self.assertTrue(self.val_func('TODO'))
