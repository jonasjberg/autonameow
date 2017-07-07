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

from core.config import field_parsers
from core.config.field_parsers import (
    RegexConfigFieldParser,
    ConfigFieldParser,
    get_instantiated_field_parsers,
    available_field_parsers,
    MimeTypeConfigFieldParser,
    DateTimeConfigFieldParser,
    NameFormatConfigFieldParser,
    MetadataSourceConfigFieldParser,
    suitable_field_parser_for,
    suitable_parser_for_querystr
)


class TestFieldParserFunctions(TestCase):
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


class TestFieldParser(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = ConfigFieldParser()

    def test_get_validation_function_should_raise_error_if_unimplemented(self):
        with self.assertRaises(NotImplementedError):
            self.p.get_validation_function()


class TestFieldParserSubclasses(TestCase):
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


class TestRegexFieldParser(TestCase):
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


class TestMimeTypeFieldParser(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = MimeTypeConfigFieldParser()
        self.val_func = self.p.get_validation_function()

    def test_expect_fail_for_invalid_mime_types(self):
        self.assertFalse(self.val_func(''))
        self.assertFalse(self.val_func(None))
        self.assertFalse(self.val_func('invalid_mime_surely'))

    def test_expect_fail_for_invalid_globs(self):
        self.assertFalse(self.val_func('.*'))
        self.assertFalse(self.val_func('*'))
        self.assertFalse(self.val_func('image/'))
        self.assertFalse(self.val_func('/jpeg'))
        self.assertFalse(self.val_func('image/*/*'))

    def test_expect_pass_for_valid_mime_types_no_globs(self):
        self.assertTrue(self.val_func('image/x-ms-bmp'))
        self.assertTrue(self.val_func('image/gif'))
        self.assertTrue(self.val_func('image/jpeg'))
        self.assertTrue(self.val_func('video/quicktime'))
        self.assertTrue(self.val_func('video/mp4'))
        self.assertTrue(self.val_func('video/ogg'))
        self.assertTrue(self.val_func('application/pdf'))
        self.assertTrue(self.val_func('image/png'))
        self.assertTrue(self.val_func('text/plain'))
        self.assertTrue(self.val_func('inode/x-empty'))
        self.assertTrue(self.val_func('application/epub+zip'))

    def test_expect_pass_for_valid_globs(self):
        self.assertTrue(self.val_func('*/*'))
        self.assertTrue(self.val_func('image/*'))
        self.assertTrue(self.val_func('*/jpeg'))
        self.assertTrue(self.val_func('inode/*'))
        self.assertTrue(self.val_func('*/x-empty'))
        self.assertTrue(self.val_func('*/x-ms-bmp'))
        self.assertTrue(self.val_func('image/*'))
        self.assertTrue(self.val_func('*/epub+zip'))
        self.assertTrue(self.val_func('application/*'))

    def test_expect_pass_for_valid_mime_types_with_globs(self):
        self.assertTrue(self.val_func('*/jpeg'))
        self.assertTrue(self.val_func('image/*'))


class TestDateTimeFieldParser(TestCase):
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


class TestNameFormatFieldParser(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = NameFormatConfigFieldParser()
        self.val_func = self.p.get_validation_function()

    def test_validation_function_expect_fail(self):
        self.assertFalse(self.val_func(None))
        self.assertFalse(self.val_func(''))
        self.assertFalse(self.val_func('{bad_field}'))
        self.assertFalse(self.val_func('{datetime} {bad_field}'))

    def test_validation_function_expect_pass(self):
        self.assertTrue(self.val_func('{datetime}'))
        self.assertTrue(self.val_func('{publisher} "abc" {tags}'))
        self.assertTrue(self.val_func('{datetime} {title}.{extension}'))


class TestMetadataSourceConfigFieldParser(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = MetadataSourceConfigFieldParser()
        self.val_func = self.p.get_validation_function()

    def test_validation_function_expect_fail(self):
        self.assertFalse(self.val_func(None))
        self.assertFalse(self.val_func(''))

    def test_validation_function_expect_pass(self):
        self.assertTrue(self.val_func('exiftool.EXIF:DateTimeOriginal'))
        self.assertTrue(self.val_func('pypdf.CreationDate'))

        # TODO: Implement proper (?) validation of metadata source!
        self.assertTrue(self.val_func('exiftool'))


class TestInstantiatedFieldParsers(TestCase):
    def test_field_parsers_in_not_none(self):
        self.assertIsNotNone(field_parsers.FieldParsers)

    def test_configuration_field_parsers_subclass_of_config_field_parser(self):
        for parser in field_parsers.FieldParsers:
            self.assertTrue(isinstance(parser, field_parsers.ConfigFieldParser))

    def test_configuration_field_parsers_instance_of_config_field_parser(self):
        for parser in field_parsers.FieldParsers:
            self.assertTrue(isinstance(parser, field_parsers.ConfigFieldParser))


class TestSuitableFieldParserFor(TestCase):
    def test_returns_expected_type(self):
        actual = suitable_field_parser_for('mime_type')
        self.assertTrue(isinstance(actual, list))

    def test_returns_expected_given_valid_mime_type_field(self):
        actual = suitable_field_parser_for('mime_type')
        self.assertEqual(len(actual), 1)
        self.assertEqual(str(actual[0]), 'MimeTypeConfigFieldParser')

    def test_returns_expected_given_invalid_mime_type_field(self):
        actual = suitable_field_parser_for('miiime_type')
        self.assertEqual(len(actual), 0)

    def test_returns_expected_given_valid_name_format_field(self):
        actual = suitable_field_parser_for('NAME_FORMAT')
        self.assertEqual(len(actual), 1)
        self.assertEqual(str(actual[0]), 'NameFormatConfigFieldParser')

    def test_datetime_field_parser_handles_multiple_fields(self):
        for field in ['datetime', 'date_accessed',
                      'date_created', 'date_modified']:
            actual = suitable_field_parser_for(field)
            self.assertEqual(len(actual), 1)
            self.assertEqual(str(actual[0]), 'DateTimeConfigFieldParser')

    def test_regex_field_parser_handles_multiple_fields(self):
        for field in ['pathname', 'basename', 'extension', 'raw_text']:
            actual = suitable_field_parser_for(field)
            self.assertEqual(len(actual), 1)
            self.assertEqual(str(actual[0]), 'RegexConfigFieldParser')


class TestSuitableParserForQueryString(TestCase):
    def test_returns_expected_type(self):
        actual = suitable_parser_for_querystr('mime_type')
        self.assertTrue(isinstance(actual, list))

    def test_returns_expected_given_valid_mime_type_field(self):
        actual = suitable_parser_for_querystr('contents.mime_type')
        self.assertEqual(len(actual), 1)
        self.assertEqual(str(actual[0]), 'MimeTypeConfigFieldParser')

    def test_returns_expected_given_invalid_mime_type_field(self):
        actual = suitable_parser_for_querystr('miiime_type')
        self.assertEqual(len(actual), 0)

    def test_returns_expected_given_valid_name_format_field(self):
        actual = suitable_parser_for_querystr('NAME_FORMAT')
        self.assertEqual(len(actual), 1)

    def test_datetime_field_parser_handles_multiple_fields(self):
        for field in ['datetime', 'date_accessed',
                      'date_created', 'date_modified']:
            actual = suitable_parser_for_querystr(field)
            self.assertEqual(len(actual), 1)
            self.assertEqual(str(actual[0]), 'DateTimeConfigFieldParser')

    def test_regex_field_parser_handles_multiple_fields(self):
        for field in ['filesystem.pathname', 'filesystem.basename',
                      'filesystem.extension', 'contents.textual.raw_text']:
            actual = suitable_parser_for_querystr(field)
            self.assertEqual(len(actual), 1)
            self.assertEqual(str(actual[0]), 'RegexConfigFieldParser')
