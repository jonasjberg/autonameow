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
    ConfigFieldParser,
    DateTimeConfigFieldParser,
    MimeTypeConfigFieldParser,
    NameFormatConfigFieldParser,
    RegexConfigFieldParser,
    available_field_parsers,
    get_instantiated_field_parsers,
    parse_versioning,
    suitable_field_parser_for
)
from core.model import MeowURI
import unit_utils as uu
import unit_utils_constants as uuconst


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

    def test_get_available_parsers_returns_expected_type(self):
        actual = available_field_parsers()
        self.assertTrue(isinstance(actual, list))

        for p in actual:
            self.assertTrue(uu.is_class(p))

    def test_get_available_parsers_returns_arbitrary_number(self):
        # TODO: [hardcoded] Likely to break; Fix or remove!
        self.assertGreaterEqual(len(available_field_parsers()), 4)


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
        self.assertTrue(uu.is_internalstring(str(self.p)))


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

    def test__normalize_returns_expected(self):
        self.assertEqual(self.p._normalize('foo'), 'foo')
        self.assertEqual(self.p._normalize('ö'), 'ö')


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

    def test_expect_fail_for_list_of_invalid_mime_types(self):
        self.assertFalse(self.val_func(['']))
        self.assertFalse(self.val_func([None]))
        self.assertFalse(self.val_func(['invalid_mime_surely']))
        self.assertFalse(self.val_func([None, None]))
        self.assertFalse(self.val_func([None, '']))
        self.assertFalse(self.val_func([None, '', 'invalid_mime_surely']))
        self.assertFalse(self.val_func([[]]))
        self.assertFalse(self.val_func([None, []]))
        self.assertFalse(self.val_func([None, [None]]))

    def test_expect_fail_for_list_of_invalid_globs(self):
        self.assertFalse(self.val_func(['.*']))
        self.assertFalse(self.val_func(['*']))
        self.assertFalse(self.val_func(['image/']))
        self.assertFalse(self.val_func(['/jpeg']))
        self.assertFalse(self.val_func(['image/*/*']))
        self.assertFalse(self.val_func(['.*', '.*']))
        self.assertFalse(self.val_func(['*', '.*']))
        self.assertFalse(self.val_func([None, '.*']))
        self.assertFalse(self.val_func([[], '.*']))

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
        self.assertTrue(self.val_func('image/vnd.djvu'))

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

    def test_expect_pass_for_list_of_valid_mime_types_with_globs(self):
        self.assertTrue(self.val_func(['*/*']))
        self.assertTrue(self.val_func(['image/*']))
        self.assertTrue(self.val_func(['*/jpeg']))
        self.assertTrue(self.val_func(['inode/*']))
        self.assertTrue(self.val_func(['*/x-empty']))
        self.assertTrue(self.val_func(['*/x-ms-bmp']))
        self.assertTrue(self.val_func(['image/*']))
        self.assertTrue(self.val_func(['*/epub+zip']))
        self.assertTrue(self.val_func(['application/*']))
        self.assertTrue(self.val_func(['*/*', '*/*']))
        self.assertTrue(self.val_func(['*/*', '*/jpeg']))
        self.assertTrue(self.val_func(['image/*', '*/jpeg']))
        self.assertTrue(self.val_func(['*/jpeg', 'image/*']))
        self.assertTrue(self.val_func(['*/jpeg', 'application/*']))

    def test_expect_pass_for_list_of_valid_mime_types_no_globs(self):
        self.assertTrue(self.val_func(['image/x-ms-bmp']))
        self.assertTrue(self.val_func(['image/gif']))
        self.assertTrue(self.val_func(['image/jpeg']))
        self.assertTrue(self.val_func(['video/quicktime']))
        self.assertTrue(self.val_func(['video/mp4']))
        self.assertTrue(self.val_func(['video/ogg']))
        self.assertTrue(self.val_func(['application/pdf']))
        self.assertTrue(self.val_func(['image/png']))
        self.assertTrue(self.val_func(['text/plain']))
        self.assertTrue(self.val_func(['inode/x-empty']))
        self.assertTrue(self.val_func(['application/epub+zip']))
        self.assertTrue(self.val_func(['image/gif', 'image/jpeg']))
        self.assertTrue(self.val_func(['image/jpeg', 'image/gif']))
        self.assertTrue(self.val_func(['video/quicktime', 'image/jpeg']))

    def test_expect_mime_type_globs_to_evaluate_true(self):
        def _assert_eval_true(expression, data):
            actual = self.p.evaluate_mime_type_globs(expression, data)
            self.assertTrue(isinstance(actual, bool))
            self.assertTrue(actual)

        _assert_eval_true('image/jpeg', 'image/jpeg')
        _assert_eval_true('image/*', 'image/jpeg')
        _assert_eval_true('*/jpeg', 'image/jpeg')
        _assert_eval_true(['*/jpeg', 'application/pdf'], 'image/jpeg')
        _assert_eval_true(['image/*', 'application/pdf'], 'image/jpeg')
        _assert_eval_true(['image/*', 'application/pdf'], 'application/pdf')
        _assert_eval_true(['image/jpeg', 'application/pdf'], 'application/pdf')
        _assert_eval_true(['image/jpeg', '*/pdf'], 'application/pdf')

    def test_expect_mime_type_globs_to_evaluate_false(self):
        def _assert_eval_false(expression, data):
            actual = self.p.evaluate_mime_type_globs(expression, data)
            self.assertTrue(isinstance(actual, bool))
            self.assertFalse(actual)

        _assert_eval_false('image/png', 'image/jpeg')
        _assert_eval_false('application/*', 'image/jpeg')
        _assert_eval_false('*/png', 'image/jpeg')
        _assert_eval_false(['*/png', 'application/pdf'], 'image/jpeg')
        _assert_eval_false(['application/*', 'video/quicktime'], 'image/png')
        _assert_eval_false(['image/*', 'application/pdf'], 'text/p,ain')
        _assert_eval_false(['image/jpeg', 'application/pdf'], 'image/gif')


class TestDateTimeFieldParser(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = DateTimeConfigFieldParser()
        self.val_func = self.p.get_validation_function()

    def test_validation_function_expect_fail(self):
        self.assertFalse(self.val_func(None))
        self.assertFalse(self.val_func(1))
        self.assertFalse(self.val_func(''))

    def test_validation_function_expect_pass(self):
        self.assertTrue(self.val_func('%Y-%m-%d %H:%M:%S'))
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
        self.assertFalse(self.val_func('{datetime} {bad_field}'))

    def test_validation_function_expect_pass(self):
        self.assertTrue(self.val_func('{datetime}'))
        self.assertTrue(self.val_func('{publisher} "abc" {tags}'))
        self.assertTrue(self.val_func('{datetime} {title}.{extension}'))


class TestInstantiatedFieldParsers(TestCase):
    def test_field_parsers_in_not_none(self):
        self.assertIsNotNone(field_parsers.FieldParserInstances)

    def test_field_parsers_subclass_config_field_parser(self):
        for parser in field_parsers.FieldParserInstances:
            self.assertTrue(isinstance(parser, field_parsers.ConfigFieldParser))
            self.assertTrue(issubclass(parser.__class__,
                                       field_parsers.ConfigFieldParser))

    def test_field_parsers_are_instantiated_classes(self):
        for parser in field_parsers.FieldParserInstances:
            self.assertTrue(uu.is_class_instance(parser))


class TestSuitableFieldParserFor(TestCase):
    def __expect_parser_for(self, expected_parser, arg):
        _meowuri = MeowURI(arg)
        actual = suitable_field_parser_for(_meowuri)
        self.assertEqual(len(actual), 1)
        self.assertEqual(str(actual[0]), expected_parser)

    def test_returns_expected_type_list(self):
        _meowuri = MeowURI(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        actual = suitable_field_parser_for(_meowuri)
        self.assertTrue(isinstance(actual, list))

    def test_returns_expected_given_invalid_mime_type_field(self):
        actual = suitable_field_parser_for(MeowURI('generic.contents.miiime_type'))
        self.assertEqual(len(actual), 0)
        actual = suitable_field_parser_for(MeowURI('generic.contents.miiime_type'))
        self.assertEqual(len(actual), 0)

    def test_expect_datetime_field_parser(self):
        # TODO: [cleanup] Is this still relevant?
        # self.__expect_parser_for('DateTimeConfigFieldParser', 'datetime')
        # self.__expect_parser_for('DateTimeConfigFieldParser', 'date_accessed')
        # self.__expect_parser_for('DateTimeConfigFieldParser', 'date_created')
        # self.__expect_parser_for('DateTimeConfigFieldParser', 'date_modified')

        self.__expect_parser_for('DateTimeConfigFieldParser',
                                 uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE)
        self.__expect_parser_for(
            'DateTimeConfigFieldParser',
            uuconst.MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL
        )

    def test_expect_regex_field_parser(self):
        self.__expect_parser_for('RegexConfigFieldParser',
                                 uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL)
        self.__expect_parser_for('RegexConfigFieldParser',
                                 uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL)
        self.__expect_parser_for('RegexConfigFieldParser',
                                 uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT)
        self.__expect_parser_for('RegexConfigFieldParser',
                                 uuconst.MEOWURI_GEN_CONTENTS_TEXT)
        self.__expect_parser_for('DateTimeConfigFieldParser',
                                 uuconst.MEOWURI_GEN_METADATA_DATECREATED)
        self.__expect_parser_for('DateTimeConfigFieldParser',
                                 uuconst.MEOWURI_GEN_METADATA_DATEMODIFIED)
        self.__expect_parser_for('MimeTypeConfigFieldParser',
                                 uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)

    def test_expect_mime_type_field_parser(self):
        self.__expect_parser_for('MimeTypeConfigFieldParser',
                                 uuconst.MEOWURI_FS_XPLAT_MIMETYPE)


class TestFieldParserConstants(TestCase):
    def test_has_dummy_data_fields_constant(self):
        self.assertIsNotNone(field_parsers.DATA_FIELDS)
        self.assertTrue(isinstance(field_parsers.DATA_FIELDS, dict))


class TestValidateVersionNumber(TestCase):
    def test_valid_version_number_returns_expected(self):
        def _assert_equal(test_input, expected):
            actual = parse_versioning(test_input)
            self.assertTrue(isinstance(actual, tuple))
            self.assertEqual(actual, expected)

        _assert_equal('0.0.0', (0, 0, 0))
        _assert_equal('0.4.6', (0, 4, 6))
        _assert_equal('1.2.3', (1, 2, 3))
        _assert_equal('9.9.9', (9, 9, 9))
        _assert_equal('10.11.12', (10, 11, 12))
        _assert_equal('1337.1337.1337', (1337, 1337, 1337))
        _assert_equal('v0.0.0', (0, 0, 0))
        _assert_equal('v0.4.6', (0, 4, 6))
        _assert_equal('v1.2.3', (1, 2, 3))
        _assert_equal('v9.9.9', (9, 9, 9))
        _assert_equal('v10.11.12', (10, 11, 12))
        _assert_equal('v1337.1337.1337', (1337, 1337, 1337))

    def test_invalid_version_number_returns_none(self):
        def _assert_none(test_data):
            actual = parse_versioning(test_data)
            self.assertIsNone(actual)

        _assert_none(None)
        _assert_none([])
        _assert_none({})
        _assert_none('')
        _assert_none(b'')
        _assert_none(' ')
        _assert_none(b' ')
        _assert_none('0.0')
        _assert_none('1.2')
        _assert_none('1.2.x')
        _assert_none('1.2 x')
        _assert_none('1.2 3')
        _assert_none('1 2.3')
        _assert_none('1 2 3')
        _assert_none('€.2.3')
        _assert_none('€.%.3')
        _assert_none('€.%.&')
        _assert_none(b'0.0')
        _assert_none(b'1.2')
        _assert_none(b'1.2.x')
        _assert_none(b'1.2 x')
        _assert_none(b'1.2 3')
        _assert_none(b'1 2.3')
        _assert_none(b'1 2 3')
        _assert_none('€.2.3'.encode('utf-8'))
        _assert_none('€.%.3'.encode('utf-8'))
        _assert_none('€.%.&'.encode('utf-8'))
        _assert_none('v0.0')
        _assert_none('v1.2')
        _assert_none('v1.2.x')
        _assert_none('v1.2 x')
        _assert_none('v1.2 3')
        _assert_none('v1 2.3')
        _assert_none('v1 2 3')
        _assert_none('v€.2.3')
        _assert_none('v€.%.3')
        _assert_none('v€.%.&')
        _assert_none(b'v0.0')
        _assert_none(b'v1.2')
        _assert_none(b'v1.2.x')
        _assert_none(b'v1.2 x')
        _assert_none(b'v1.2 3')
        _assert_none(b'v1 2.3')
        _assert_none(b'v1 2 3')
        _assert_none('v€.2.3'.encode('utf-8'))
        _assert_none('v€.%.3'.encode('utf-8'))
        _assert_none('v€.%.&'.encode('utf-8'))
