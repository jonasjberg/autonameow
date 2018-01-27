# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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
    NameTemplateConfigFieldParser,
    RegexConfigFieldParser,
    available_field_parsers,
    get_instantiated_field_parsers,
    suitable_field_parser_for
)
from core.model import MeowURI
import unit.utils as uu
import unit.constants as uuconst


class TestFieldParserFunctions(TestCase):
    def setUp(self):
        self.maxDiff = None

    def test_get_instantiated_parsers_returns_list(self):
        self.assertIsInstance(get_instantiated_field_parsers(), list)

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
        self.assertIsInstance(actual, list)

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

    def test_allow_multivalued_expression_is_none_in_base_class(self):
        self.assertIsNone(self.p.ALLOW_MULTIVALUED_EXPRESSION)


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
        def __assert_returns_bool(_valfunc, given):
            actual = _valfunc(given)
            self.assertIsInstance(
                actual, bool, 'Validation function should always return boolean'
            )

        for p in self.parsers:
            valfunc = p.get_validation_function()
            __assert_returns_bool(valfunc, None)
            __assert_returns_bool(valfunc, 'foo')
            __assert_returns_bool(valfunc, [None])
            __assert_returns_bool(valfunc, ['foo'])

    def test_get_evaluation_function_should_not_return_none(self):
        for p in self.parsers:
            self.assertIsNotNone(p.get_evaluation_function())

    def test_get_evaluation_function_should_return_function(self):
        for p in self.parsers:
            self.assertTrue(hasattr(p.get_evaluation_function(), '__call__'))


class TestRegexFieldParser(TestCase):
    def setUp(self):
        self.p = RegexConfigFieldParser()

    def test_allow_multivalued_expression(self):
        self.assertTrue(self.p.ALLOW_MULTIVALUED_EXPRESSION)


class TestRegexFieldParserValidation(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = RegexConfigFieldParser()

    def aF(self, test_input):
        self.assertFalse(self.p.validate(test_input))

    def aT(self, test_input):
        self.assertTrue(self.p.validate(test_input))

    def test_validation_function_expect_fail(self):
        self.aF('[[[')
        self.aF('"  |[2')
        self.aF(None)

        # Expect validation to fail if one expression is invalid.
        self.aF(['[A-Za-z]+', '[[['])
        self.aF(['.*', '"  |[2'])
        self.aF(['4123', None])
        self.aF(['[A-Za-z]+', ''])
        self.aF(['.*', ''])
        self.aF(['4123', ''])

    def test_validation_function_expect_pass(self):
        # Single valid expression.
        self.aT('[A-Za-z]+')
        self.aT('.*')
        self.aT('4123')

        # List of one valid expression.
        self.aT(['[A-Za-z]+'])
        self.aT(['.*'])
        self.aT(['4123'])

        # List of two valid expressions.
        self.aT(['[A-Za-z]+', '.*'])
        self.aT(['[A-Za-z]+', '.*'])
        self.aT(['4123', '1337'])


class TestRegexFieldParserEvaluation(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = RegexConfigFieldParser()

    def aF(self, expression, data):
        self.assertFalse(self.p.evaluate(expression, data))

    def aT(self, expression, data):
        self.assertTrue(self.p.evaluate(expression, data))

    def test_expect_evaluates_true(self):
        # One expression.
        self.aT('[A-Za-z]+', 'foo')
        self.aT('.*', 'foo')
        self.aT('.*', '1337')
        self.aT('4123', '4123')

        self.aT(['[A-Za-z]+'], 'foo')
        self.aT(['.*'], 'foo')
        self.aT(['.*'], '1337')
        self.aT(['4123'], '4123')

        # Two expressions.
        self.aT(['[A-Za-z]+', '.*'], 'foo')
        self.aT(['[A-Za-z]+', '.*'], '1337')
        self.aT(['4123', '1337'], '4123')
        self.aT(['4123', '1337'], '1337')

    def test_expect_evaluates_false(self):
        # One expression.
        self.aF('[A-Za-z]+', '')
        self.aF('[A-Za-z]+', '1337')
        self.aF('.*', '')
        self.aF('4123', '1337')
        self.aF('4123', 'foo')

        # Two expressions.
        self.aF(['[A-Za-z]+', 'foo'], '')
        self.aF(['[A-Za-z]+', 'foo'], '1337')
        self.aF(['4123', '1337'], 'foo')


class TestMimeTypeFieldParser(TestCase):
    def setUp(self):
        self.p = MimeTypeConfigFieldParser()

    def test_allow_multivalued_expression(self):
        self.assertTrue(self.p.ALLOW_MULTIVALUED_EXPRESSION)


class TestMimeTypeFieldParserValidation(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = MimeTypeConfigFieldParser()

    def aF(self, test_input):
        self.assertFalse(self.p.validate(test_input))

    def aT(self, test_input):
        self.assertTrue(self.p.validate(test_input))

    def test_expect_fail_for_invalid_mime_types(self):
        self.aF('')
        self.aF(None)
        self.aF('invalid_mime_surely')

    def test_expect_fail_for_invalid_globs(self):
        self.aF('.*')
        self.aF('*')
        self.aF('image/')
        self.aF('/jpeg')
        self.aF('image/*/*')

    def test_expect_fail_for_list_of_invalid_mime_types(self):
        self.aF([''])
        self.aF([None])
        self.aF(['invalid_mime_surely'])
        self.aF([None, None])
        self.aF([None, ''])
        self.aF([None, '', 'invalid_mime_surely'])
        self.aF([[]])
        self.aF([None, []])
        self.aF([None, [None]])

    def test_expect_fail_for_list_of_invalid_globs(self):
        self.aF(['.*'])
        self.aF(['*'])
        self.aF(['image/'])
        self.aF(['/jpeg'])
        self.aF(['image/*/*'])
        self.aF(['.*', '.*'])
        self.aF(['*', '.*'])
        self.aF([None, '.*'])
        self.aF([[], '.*'])

    def test_expect_pass_for_valid_mime_types_no_globs(self):
        self.aT('image/x-ms-bmp')
        self.aT('image/gif')
        self.aT('image/jpeg')
        self.aT('video/quicktime')
        self.aT('video/mp4')
        self.aT('video/ogg')
        self.aT('application/pdf')
        self.aT('image/png')
        self.aT('text/plain')
        self.aT('inode/x-empty')
        self.aT('application/epub+zip')
        self.aT('image/vnd.djvu')

    def test_expect_pass_for_valid_globs(self):
        self.aT('*/*')
        self.aT('image/*')
        self.aT('*/jpeg')
        self.aT('inode/*')
        self.aT('*/x-empty')
        self.aT('*/x-ms-bmp')
        self.aT('image/*')
        self.aT('*/epub+zip')
        self.aT('application/*')

    def test_expect_pass_for_list_of_valid_mime_types_with_globs(self):
        self.aT(['*/*'])
        self.aT(['image/*'])
        self.aT(['*/jpeg'])
        self.aT(['inode/*'])
        self.aT(['*/x-empty'])
        self.aT(['*/x-ms-bmp'])
        self.aT(['image/*'])
        self.aT(['*/epub+zip'])
        self.aT(['application/*'])
        self.aT(['*/*', '*/*'])
        self.aT(['*/*', '*/jpeg'])
        self.aT(['image/*', '*/jpeg'])
        self.aT(['*/jpeg', 'image/*'])
        self.aT(['*/jpeg', 'application/*'])

    def test_expect_pass_for_list_of_valid_mime_types_no_globs(self):
        self.aT(['image/x-ms-bmp'])
        self.aT(['image/gif'])
        self.aT(['image/jpeg'])
        self.aT(['video/quicktime'])
        self.aT(['video/mp4'])
        self.aT(['video/ogg'])
        self.aT(['application/pdf'])
        self.aT(['image/png'])
        self.aT(['text/plain'])
        self.aT(['inode/x-empty'])
        self.aT(['application/epub+zip'])
        self.aT(['image/gif', 'image/jpeg'])
        self.aT(['image/jpeg', 'image/gif'])
        self.aT(['video/quicktime', 'image/jpeg'])


class TestMimeTypeFieldParserEvaluation(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = MimeTypeConfigFieldParser()

    def aF(self, expression, data):
        actual = self.p.evaluate(expression, data)
        self.assertIsInstance(actual, bool)
        self.assertFalse(actual)

    def aT(self, expression, data):
        actual = self.p.evaluate(expression, data)
        self.assertIsInstance(actual, bool)
        self.assertTrue(actual)

    def test_expect_evaluates_true(self):
        self.aT('image/jpeg', 'image/jpeg')
        self.aT('image/*', 'image/jpeg')
        self.aT('*/jpeg', 'image/jpeg')
        self.aT(['*/jpeg', 'application/pdf'], 'image/jpeg')
        self.aT(['image/*', 'application/pdf'], 'image/jpeg')
        self.aT(['image/*', 'application/pdf'], 'application/pdf')
        self.aT(['image/jpeg', 'application/pdf'], 'application/pdf')
        self.aT(['image/jpeg', '*/pdf'], 'application/pdf')

    def test_expect_evaluates_false(self):
        self.aF('image/png', 'image/jpeg')
        self.aF('application/*', 'image/jpeg')
        self.aF('*/png', 'image/jpeg')
        self.aF(['*/png', 'application/pdf'], 'image/jpeg')
        self.aF(['application/*', 'video/quicktime'], 'image/png')
        self.aF(['image/*', 'application/pdf'], 'text/p,ain')
        self.aF(['image/jpeg', 'application/pdf'], 'image/gif')


class TestDateTimeFieldParser(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = DateTimeConfigFieldParser()

    def test_allow_multivalued_expression(self):
        self.assertTrue(self.p.ALLOW_MULTIVALUED_EXPRESSION)

    def test_validation_function_expect_fail(self):
        def _aF(test_input):
            self.assertFalse(self.p.validate(test_input))

        _aF(None)
        _aF(1)
        _aF('')

    def test_validation_function_expect_pass(self):
        def _aT(test_input):
            self.assertTrue(self.p.validate(test_input))

        _aT('%Y-%m-%d %H:%M:%S')
        _aT('%Y-%m-%d')
        _aT('%Y')
        _aT('_')
        _aT('foo')


class TestNameTemplateFieldParser(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = NameTemplateConfigFieldParser()

    def test_allow_multivalued_expression(self):
        self.assertFalse(self.p.ALLOW_MULTIVALUED_EXPRESSION)

    def test_validation_function_expect_fail(self):
        def _aF(test_input):
            self.assertFalse(self.p.validate(test_input))

        _aF(None)
        _aF('')
        _aF('{bad_field}')
        _aF('{datetime} {bad_field}')

    def test_validation_function_expect_pass(self):
        def _aT(test_input):
            self.assertTrue(self.p.validate(test_input))

        _aT('{datetime}')
        _aT('{publisher} "abc" {tags}')
        _aT('{datetime} {title}.{extension}')
        _aT('{datetime} {title} -- {tags}.{extension}')


class TestInstantiatedFieldParsers(TestCase):
    def test_field_parsers_in_not_none(self):
        self.assertIsNotNone(field_parsers.FieldParserInstances)

    def test_field_parsers_subclass_config_field_parser(self):
        for parser in field_parsers.FieldParserInstances:
            self.assertIsInstance(parser, field_parsers.ConfigFieldParser)
            self.assertTrue(issubclass(parser.__class__,
                                       field_parsers.ConfigFieldParser))

    def test_field_parsers_are_instantiated_classes(self):
        for parser in field_parsers.FieldParserInstances:
            self.assertTrue(uu.is_class_instance(parser))


class TestSuitableFieldParserFor(TestCase):
    def __expect_parser_for(self, expected_parser, arg):
        _meowuri = MeowURI(arg)
        actual = suitable_field_parser_for(_meowuri)
        self.assertEqual(str(actual), expected_parser)

    def test_returns_expected_type(self):
        _meowuri = MeowURI(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        actual = suitable_field_parser_for(_meowuri)
        self.assertNotIsInstance(actual, list)
        self.assertIsInstance(actual, field_parsers.ConfigFieldParser)
        self.assertTrue(issubclass(actual.__class__,
                                   field_parsers.ConfigFieldParser))

    def test_returns_expected_given_invalid_mime_type_field(self):
        actual = suitable_field_parser_for(
            MeowURI('generic.contents.miiime_type')
        )
        self.assertIsNone(actual)

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

    def test_raises_exception_given_none_meowuri(self):
        with self.assertRaises(AssertionError):
            suitable_field_parser_for(None)

    def test_raises_exception_given_string_meowuri(self):
        with self.assertRaises(AssertionError):
            suitable_field_parser_for(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)


class TestFieldParserConstants(TestCase):
    def test_has_dummy_data_fields_constant(self):
        self.assertIsNotNone(field_parsers.NAMETEMPLATEFIELDS_DUMMYDATA)
        self.assertIsInstance(field_parsers.NAMETEMPLATEFIELDS_DUMMYDATA, dict)
