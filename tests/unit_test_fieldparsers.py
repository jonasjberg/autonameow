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
    is_valid_template_field,
    eval_query_string_glob
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

    def test_get_evaluation_function_should_raise_error_if_unimplemented(self):
        with self.assertRaises(NotImplementedError):
            self.p.get_evaluation_function()

    def test_validate_function_should_raise_error_if_unimplemented(self):
        with self.assertRaises(NotImplementedError):
            self.p.validate(None)

    def test_evaluate_function_should_raise_error_if_unimplemented(self):
        with self.assertRaises(NotImplementedError):
            self.p.evaluate(None, None)

    def test_str_returns_expected_expected_type(self):
        self.assertTrue(isinstance(str(self.p), str))


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

    def test_get_evaluation_function_should_not_return_none(self):
        for p in self.parsers:
            self.assertIsNotNone(p.get_evaluation_function())

    def test_get_evaluation_function_should_return_function(self):
        for p in self.parsers:
            self.assertTrue(hasattr(p.get_evaluation_function(), '__call__'))


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
    def __expect_parser_for(self, expected_parser, arg):
        actual = suitable_field_parser_for(arg)
        self.assertEqual(len(actual), 1)
        self.assertEqual(str(actual[0]), expected_parser)

    def test_returns_expected_type_list(self):
        actual = suitable_field_parser_for('contents.mime_type')
        self.assertTrue(isinstance(actual, list))

    def test_returns_expected_given_invalid_mime_type_field(self):
        actual = suitable_field_parser_for('contents.miiime_type')
        self.assertEqual(len(actual), 0)
        actual = suitable_field_parser_for('miiime_type')
        self.assertEqual(len(actual), 0)

    def test_expect_name_format_field_parser(self):
        self.__expect_parser_for('NameFormatConfigFieldParser', 'NAME_FORMAT')

    def test_expect_datetime_field_parser(self):
        self.__expect_parser_for('DateTimeConfigFieldParser', 'datetime')
        self.__expect_parser_for('DateTimeConfigFieldParser', 'date_accessed')
        self.__expect_parser_for('DateTimeConfigFieldParser', 'date_created')
        self.__expect_parser_for('DateTimeConfigFieldParser', 'date_modified')

    def test_expect_regex_field_parser(self):
        self.__expect_parser_for('RegexConfigFieldParser',
                                 'filesystem.pathname.full')
        self.__expect_parser_for('RegexConfigFieldParser',
                                 'filesystem.basename.full')
        self.__expect_parser_for('RegexConfigFieldParser',
                                 'filesystem.basename.extension')
        self.__expect_parser_for('RegexConfigFieldParser',
                                 'contents.textual.raw_text')

    def test_expect_mime_type_field_parser(self):
        self.__expect_parser_for('MimeTypeConfigFieldParser',
                                 'contents.mime_type')

    def test_expect_metadata_source_field_parser(self):
        # TODO: [TD0048] Fix "conflict" with 'DateTimeConfigFieldParser'.
        self.__expect_parser_for('MetadataSourceConfigFieldParser',
                                 'metadata.exiftool')
        self.__expect_parser_for('MetadataSourceConfigFieldParser',
                                 'metadata.exiftool.EXIF:DateTimeOriginal')


class TestFieldparserConstants(TestCase):
    def test_has_dummy_data_fields_constant(self):
        self.assertIsNotNone(field_parsers.DATA_FIELDS)
        self.assertTrue(isinstance(field_parsers.DATA_FIELDS, dict))


class TestIsValidTemplateField(TestCase):
    def test_invalid_fields_returns_false(self):
        self.assertFalse(is_valid_template_field(None))
        self.assertFalse(is_valid_template_field(''))
        self.assertFalse(is_valid_template_field('foo'))

    def test_valid_fields_return_true(self):
        self.assertTrue(is_valid_template_field('author'))
        self.assertTrue(is_valid_template_field('date'))
        self.assertTrue(is_valid_template_field('datetime'))
        self.assertTrue(is_valid_template_field('description'))
        self.assertTrue(is_valid_template_field('edition'))
        self.assertTrue(is_valid_template_field('extension'))
        self.assertTrue(is_valid_template_field('publisher'))
        self.assertTrue(is_valid_template_field('tags'))
        self.assertTrue(is_valid_template_field('title'))


class TestEvalQueryStringGlob(TestCase):
    def test_eval_query_string_blob_is_defined(self):
        self.assertIsNotNone(eval_query_string_glob)

    def test_eval_query_string_blob_returns_false_given_bad_arguments(self):
        self.assertIsNotNone(eval_query_string_glob(None, None))
        self.assertFalse(eval_query_string_glob(None, None))

    def test_eval_query_string_blob_returns_false_as_expected(self):
        self.assertFalse(eval_query_string_glob(
            'contents.mime_type', ['filesystem.*']
        ))
        self.assertFalse(eval_query_string_glob(
            'contents.mime_type', ['filesystem.pathname.*']
        ))
        self.assertFalse(eval_query_string_glob(
            'contents.mime_type', ['filesystem.pathname.full']
        ))
        self.assertFalse(eval_query_string_glob(
            'contents.mime_type', ['filesystem.*',
                                   'filesystem.pathname.*',
                                   'filesystem.pathname.full']
        ))
        self.assertFalse(eval_query_string_glob(
            'filesystem.pathname.extension', ['*.basename.*',
                                              '*.basename.extension',
                                              'filesystem.basename.extension']
        ))
        self.assertFalse(eval_query_string_glob(
            'filesystem.pathname.parent', ['*.pathname.full',
                                           'filesystem.*.full']
        ))

    def test_eval_query_string_blob_returns_true_as_expected(self):
        self.assertTrue(eval_query_string_glob(
            'filesystem.pathname.full', ['*']
        ))
        self.assertTrue(eval_query_string_glob(
            'filesystem.pathname.full', ['filesystem.*']
        ))
        self.assertTrue(eval_query_string_glob(
            'filesystem.pathname.full', ['filesystem.pathname.*']
        ))
        self.assertTrue(eval_query_string_glob(
            'filesystem.pathname.full', ['filesystem.pathname.full']
        ))
        self.assertTrue(eval_query_string_glob(
            'filesystem.pathname.full', ['filesystem.*',
                                         'filesystem.pathname.*',
                                         'filesystem.pathname.full']
        ))
        self.assertTrue(eval_query_string_glob(
            'filesystem.pathname.full', ['*',
                                         'filesystem.*',
                                         'filesystem.pathname.*',
                                         'filesystem.pathname.full']
        ))
        self.assertTrue(eval_query_string_glob(
            'filesystem.basename.extension', ['*.basename.*',
                                              '*.basename.extension',
                                              'filesystem.basename.extension']
        ))
        self.assertTrue(eval_query_string_glob(
            'filesystem.basename.extension', ['*',
                                              '*.basename.*',
                                              '*.basename.extension',
                                              'filesystem.basename.extension']
        ))
        self.assertTrue(eval_query_string_glob(
            'filesystem.basename.extension', ['*.extension']
        ))
        self.assertTrue(eval_query_string_glob(
            'filesystem.basename.extension', ['*',
                                              '*.extension']
        ))

    def test_eval_query_string_blob_returns_as_expected(self):
        self.assertTrue(eval_query_string_glob(
            'filesystem.basename.full', ['*.pathname.*',
                                         '*.basename.*',
                                         '*.raw_text']
        ))
