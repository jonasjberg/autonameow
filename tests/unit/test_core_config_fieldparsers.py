# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from unittest import TestCase

import unit.constants as uuconst
import unit.utils as uu
from core.config import field_parsers
from core.config.field_parsers import ConfigFieldParser
from core.config.field_parsers import DateTimeConfigFieldParser
from core.config.field_parsers import MimeTypeConfigFieldParser
from core.config.field_parsers import NameTemplateConfigFieldParser
from core.config.field_parsers import RegexConfigFieldParser
from core.config.field_parsers import get_instantiated_field_parsers
from core.config.field_parsers import suitable_field_parser_for
from core.model import MeowURI


class TestGetInstantiatedFieldParsers(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual = get_instantiated_field_parsers()

    def test_returns_list(self):
        self.assertIsInstance(self.actual, list)

    def test_returns_at_least_one_element(self):
        self.assertGreaterEqual(len(self.actual), 1)

    def test_returns_at_least_two_elements(self):
        self.assertGreaterEqual(len(self.actual), 2)

    def test_returns_at_least_three_elements(self):
        self.assertGreaterEqual(len(self.actual), 3)

    def test_returns_instantiated_classes(self):
        for p in self.actual:
            self.assertTrue(uu.is_class_instance(p))

    def test_returns_subclasses_of_config_field_parser(self):
        for p in self.actual:
            self.assertIsInstance(p, field_parsers.ConfigFieldParser)


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

    def test_expect_fail_for_single_invalid_expression(self):
        self.aF('[[[')
        self.aF('"  |[2')
        self.aF(None)

    def test_expect_fail_if_one_expression_in_list_is_invalid(self):
        self.aF(['[A-Za-z]+', '[[['])
        self.aF(['.*', '"  |[2'])
        self.aF(['4123', None])
        self.aF(['[A-Za-z]+', ''])
        self.aF(['.*', ''])
        self.aF(['4123', ''])

    def test_expect_pass_for_single_valid_expression(self):
        self.aT('[A-Za-z]+')
        self.aT('.*')
        self.aT('4123')

    def test_expect_pass_for_list_with_one_valid_expression(self):
        self.aT(['[A-Za-z]+'])
        self.aT(['.*'])
        self.aT(['4123'])

    def test_expect_pass_for_list_with_two_valid_expressions(self):
        self.aT(['[A-Za-z]+', '.*'])
        self.aT(['[A-Za-z]+', '.*'])
        self.aT(['4123', '1337'])


class TestRegexFieldParserEvaluation(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.p = RegexConfigFieldParser()

    def aT(self, expression, data):
        self.assertTrue(self.p.evaluate(expression, data))

    def aF(self, expression, data):
        self.assertFalse(self.p.evaluate(expression, data))

    def test_evaluates_true_for_single_expression(self):
        self.aT('[A-Za-z]+', 'foo')
        self.aT('.*', 'foo')
        self.aT('.*', '1337')
        self.aT('4123', '4123')

    def test_evaluates_true_for_list_of_one_expression(self):
        self.aT(['[A-Za-z]+'], 'foo')
        self.aT(['.*'], 'foo')
        self.aT(['.*'], '1337')
        self.aT(['4123'], '4123')

    def test_evaluates_true_for_list_of_two_expressions(self):
        self.aT(['[A-Za-z]+', '.*'], 'foo')
        self.aT(['[A-Za-z]+', '.*'], '1337')
        self.aT(['4123', '1337'], '4123')
        self.aT(['4123', '1337'], '1337')

    def test_evaluates_false_for_single_expression(self):
        self.aF('[A-Za-z]+', '')
        self.aF('[A-Za-z]+', '1337')
        self.aF('.*', '')
        self.aF('4123', '1337')
        self.aF('4123', 'foo')

    def test_evaluates_false_for_list_of_one_expression(self):
        self.aF(['[A-Za-z]+'], '')
        self.aF(['[A-Za-z]+'], '1337')
        self.aF(['.*'], '')
        self.aF(['4123'], '1337')
        self.aF(['4123'], 'foo')

    def test_evaluates_false_for_list_of_two_expressions(self):
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

    def aT(self, expression, data):
        self.assertTrue(self.p.evaluate(expression, data))

    def aF(self, expression, data):
        self.assertFalse(self.p.evaluate(expression, data))

    def test_evaluates_true_for_single_expression(self):
        self.aT('image/jpeg', 'image/jpeg')
        self.aT('image/*', 'image/jpeg')
        self.aT('*/jpeg', 'image/jpeg')

    def test_evaluates_true_for_list_of_one_expression(self):
        self.aT(['image/jpeg'], 'image/jpeg')
        self.aT(['image/*'], 'image/jpeg')
        self.aT(['*/jpeg'], 'image/jpeg')

    def test_evaluates_true_for_list_of_two_expressions(self):
        self.aT(['*/jpeg', 'application/pdf'], 'image/jpeg')
        self.aT(['image/*', 'application/pdf'], 'image/jpeg')
        self.aT(['image/*', 'application/pdf'], 'application/pdf')
        self.aT(['image/jpeg', 'application/pdf'], 'application/pdf')
        self.aT(['image/jpeg', '*/pdf'], 'application/pdf')

    def test_evaluates_false_for_single_expression(self):
        self.aF('image/png', 'image/jpeg')
        self.aF('application/*', 'image/jpeg')
        self.aF('*/png', 'image/jpeg')

    def test_evaluates_false_for_list_of_one_expressions(self):
        self.aF(['image/png'], 'image/jpeg')
        self.aF(['application/*'], 'image/jpeg')
        self.aF(['*/png'], 'image/jpeg')

    def test_evaluates_false_for_list_of_two_expressions(self):
        self.aF(['*/png', 'application/pdf'], 'image/jpeg')
        self.aF(['application/*', 'video/quicktime'], 'image/png')
        self.aF(['image/*', 'application/pdf'], 'text/p,ain')
        self.aF(['image/jpeg', 'application/pdf'], 'image/gif')


class TestDateTimeFieldParser(TestCase):
    def setUp(self):
        self.p = DateTimeConfigFieldParser()

    def test_allow_multivalued_expression(self):
        self.assertTrue(self.p.ALLOW_MULTIVALUED_EXPRESSION)


class TestDateTimeFieldParserValidation(TestCase):
    def setUp(self):
        self.p = DateTimeConfigFieldParser()

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


class TestDateTimeFieldParserEvaluation(TestCase):
    def setUp(self):
        self.p = DateTimeConfigFieldParser()

    def test_evaluates_true_for_single_expression(self):
        self.skipTest('TODO: [TD0015] Handle expression in "condition_value"')

    def test_evaluates_true_for_list_of_one_expression(self):
        self.skipTest('TODO: [TD0015] Handle expression in "condition_value"')

    def test_evaluates_true_for_list_of_two_expressions(self):
        self.skipTest('TODO: [TD0015] Handle expression in "condition_value"')

    def test_evaluates_false_for_single_expression(self):
        self.skipTest('TODO: [TD0015] Handle expression in "condition_value"')

    def test_evaluates_false_for_list_of_one_expressions(self):
        self.skipTest('TODO: [TD0015] Handle expression in "condition_value"')

    def test_evaluates_false_for_list_of_two_expressions(self):
        self.skipTest('TODO: [TD0015] Handle expression in "condition_value"')


class TestNameTemplateFieldParser(TestCase):
    def setUp(self):
        self.p = NameTemplateConfigFieldParser()

    def test_allow_multivalued_expression(self):
        self.assertFalse(self.p.ALLOW_MULTIVALUED_EXPRESSION)


class TestNameTemplateFieldParserValidation(TestCase):
    def setUp(self):
        self.p = NameTemplateConfigFieldParser()

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


class TestNameTemplateFieldParserEvaluation(TestCase):
    def setUp(self):
        self.p = NameTemplateConfigFieldParser()

    def test_evaluates_true_for_single_expression(self):
        self.skipTest('TODO: [TD0015] Handle expression in "condition_value"')

    def test_evaluates_false_for_single_expression(self):
        self.skipTest('TODO: [TD0015] Handle expression in "condition_value"')


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
        uri = MeowURI(arg)
        actual = suitable_field_parser_for(uri)
        self.assertEqual(str(actual), expected_parser)

    def test_returns_expected_type(self):
        uri = MeowURI(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        actual = suitable_field_parser_for(uri)
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
        self.__expect_parser_for('DateTimeConfigFieldParser',
                                 uuconst.MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL)
        self.__expect_parser_for('DateTimeConfigFieldParser',
                                 uuconst.MEOWURI_GEN_METADATA_DATECREATED)
        self.__expect_parser_for('DateTimeConfigFieldParser',
                                 uuconst.MEOWURI_GEN_METADATA_DATEMODIFIED)

    def test_expect_regex_field_parser(self):
        self.__expect_parser_for('RegexConfigFieldParser',
                                 uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL)
        self.__expect_parser_for('RegexConfigFieldParser',
                                 uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL)
        self.__expect_parser_for('RegexConfigFieldParser',
                                 uuconst.MEOWURI_FS_XPLAT_EXTENSION)
        self.__expect_parser_for('RegexConfigFieldParser',
                                 uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

    def test_expect_mime_type_field_parser(self):
        self.__expect_parser_for('MimeTypeConfigFieldParser',
                                 uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        self.__expect_parser_for('MimeTypeConfigFieldParser',
                                 uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)

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
