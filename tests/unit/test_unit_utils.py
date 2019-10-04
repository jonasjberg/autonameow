#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import os
import sys
import types
from datetime import datetime
from unittest import TestCase

import unit.constants as uuconst
import unit.utils as uu
from core import FileObject
from core.model import MeowURI


class TestUnitUtilitySamplefileAbspath(TestCase):
    def test_returns_expected_encoding(self):
        actual = uu.samplefile_abspath('empty')
        self.assertIsInstance(actual, str)

    def test_returns_absolute_paths(self):
        actual = uu.samplefile_abspath('empty')
        self.assertTrue(os.path.isabs(actual))


class TestUnitUtilitySamplefileConfigAbspath(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.actual_specified = uu.samplefile_config_abspath(
            uuconst.DEFAULT_YAML_CONFIG_BASENAME
        )
        cls.actual_default = uu.samplefile_config_abspath()

    def test_returns_expected_encoding(self):
        self.assertIsInstance(self.actual_specified, str)

    def test_returns_absolute_path(self):
        self.assertTrue(os.path.isabs(self.actual_specified))

    def test_returns_existing_path(self):
        self.assertTrue(os.path.exists(self.actual_specified))

    def test_returns_path_to_existing_file(self):
        self.assertTrue(os.path.isfile(self.actual_specified))

    def test_returns_default_config_if_filename_is_unspecified(self):
        self.assertTrue(
            self.actual_default.endswith(uuconst.DEFAULT_YAML_CONFIG_BASENAME)
        )

    def test_filename_unspecified_returns_expected_encoding(self):
        self.assertIsInstance(self.actual_default, str)

    def test_filename_unspecified_returns_absolute_path(self):
        self.assertTrue(os.path.isabs(self.actual_default))

    def test_filename_unspecified_returns_existing_path(self):
        self.assertTrue(os.path.exists(self.actual_default))

    def test_filename_unspecified_returns_path_to_existing_file(self):
        self.assertTrue(os.path.isfile(self.actual_default))


class TestUnitUtilityFileobjectFromFilepath(TestCase):
    def test_returns_fileobject_given_unicode_string_path(self):
        filepath = uu.samplefile_abspath('empty')
        self.assertIsInstance(filepath, str)
        self.assertTrue(os.path.exists(filepath))

        actual = uu.fileobject_from_filepath(filepath)
        self.assertIsInstance(actual, FileObject)
        self.assertTrue(os.path.isabs(actual.abspath))

    def test_returns_fileobject_given_bytes_path(self):
        filepath = uu.samplefile_abspath('empty')

        bytes_filepath = uu.bytestring_path(filepath)
        self.assertIsInstance(bytes_filepath, bytes)
        self.assertTrue(os.path.exists(bytes_filepath))

        actual = uu.fileobject_from_filepath(bytes_filepath)
        self.assertIsInstance(actual, FileObject)
        self.assertTrue(os.path.isabs(actual.abspath))


class TestUnitUtilityFileobjectFromSamplefile(TestCase):
    def test_returns_expected_type(self):
        actual = uu.fileobject_from_samplefile('empty')
        self.assertIsInstance(actual, FileObject)
        self.assertTrue(os.path.isabs(actual.abspath))


class TestUnitUtilityAllTestFiles(TestCase):
    def test_returns_expected_encoding(self):
        actual = uu.all_samplefiles()
        self.assertIsInstance(actual, list)
        for a in actual:
            self.assertIsInstance(a, str)

    def test_returns_existing_absolute_paths(self):
        actual = uu.all_samplefiles()
        for f in actual:
            self.assertTrue(os.path.exists(f))
            self.assertTrue(os.path.isfile(f) | os.path.islink(f))
            self.assertTrue(os.path.isabs(f))

    def test_does_not_return_symbolic_links(self):
        actual = uu.all_samplefiles()
        for f in actual:
            self.assertFalse(os.path.islink(f))


class TestUnitUtilityFileExists(TestCase):
    def _check_return(self, file_to_test):
        actual = uu.file_exists(file_to_test)
        self.assertIsInstance(actual, bool)

        if not file_to_test:
            expected = False
        else:
            try:
                expected = os.path.isfile(file_to_test)
            except (OSError, TypeError, ValueError):
                expected = False

        self.assertEqual(actual, expected)

    def test_returns_false_for_files_assumed_missing(self):
        _dummy_paths = [
            '/foo/bar/baz/mjao',
            '/tmp/this_isnt_a_file_right_or_huh',
            b'/tmp/this_isnt_a_file_right_or_huh'
        ]
        for df in _dummy_paths:
            self._check_return(df)

    def test_returns_false_for_empty_argument(self):
        def _aF(test_input):
            self.assertFalse(uu.file_exists(test_input))

        _aF(None)
        _aF('')
        _aF(' ')

    def test_returns_true_for_files_likely_to_exist(self):
        _files = [
            __file__,
        ]
        for df in _files:
            self._check_return(df)


class TestUnitUtilityDirExists(TestCase):
    def _check_return(self, path_to_test):
        actual = uu.dir_exists(path_to_test)
        self.assertIsInstance(actual, bool)

        if not path_to_test:
            expected = False
        else:
            try:
                expected = os.path.isdir(path_to_test)
            except (OSError, TypeError, ValueError):
                expected = False

        self.assertEqual(actual, expected)

    def test_returns_false_for_assumed_non_directory_paths(self):
        _dummy_paths = [
            __file__,
            '/foo/bar/baz/mjao',
            '/tmp/this_isnt_a_file_right_or_huh',
            b'/foo/bar/baz/mjao',
            b'/tmp/this_isnt_a_file_right_or_huh',
        ]
        for df in _dummy_paths:
            self._check_return(df)

    def test_returns_false_for_empty_argument(self):
        def _aF(test_input):
            self.assertFalse(uu.dir_exists(test_input))

        _aF(None)
        _aF('')
        _aF(' ')

    def test_returns_true_for_likely_directory_paths(self):
        _files = [
            os.path.dirname(__file__),
            uuconst.DIRPATH_AUTONAMEOW_SRCROOT,
            '/',
            b'/',
            uu.bytestring_path(os.path.dirname(__file__)),
            uu.bytestring_path(uuconst.DIRPATH_AUTONAMEOW_SRCROOT)
        ]
        for df in _files:
            self._check_return(df)


class TestUnitUtilityPathIsReadable(TestCase):
    def _check_return(self, path_to_test):
        actual = uu.path_is_readable(path_to_test)
        self.assertIsInstance(actual, bool)

        if not path_to_test:
            expected = False
        else:
            try:
                expected = os.access(path_to_test, os.R_OK)
            except (OSError, TypeError, ValueError):
                expected = False

        self.assertEqual(actual, expected)

    def test_returns_false_for_paths_assumed_missing(self):
        _dummy_paths = [
            '',
            '/foo/bar/baz/mjao',
            '/tmp/this_isnt_a_file_right_or_huh',
            b'',
            b'/foo/bar/baz/mjao',
            b'/tmp/this_isnt_a_file_right_or_huh'
        ]
        for df in _dummy_paths:
            self._check_return(df)

    def test_returns_false_for_empty_argument(self):
        def _aF(test_input):
            self.assertFalse(uu.path_is_readable(test_input))

        _aF(None)
        _aF('')
        _aF(' ')

    def test_returns_true_for_paths_likely_to_exist(self):
        _paths = [
            __file__,
            os.path.dirname(__file__),
            uu.bytestring_path(__file__),
            uu.bytestring_path(os.path.dirname(__file__)),
        ]
        for df in _paths:
            self._check_return(df)


class TestUnitUtilityIsAbspath(TestCase):
    def test_returns_false_for_relative_paths(self):
        def _aF(test_input):
            self.assertFalse(uu.is_abspath(test_input))

        _aF(os.path.basename(os.path.dirname(__file__)))

    def test_returns_true_for_relative_paths(self):
        def _aT(test_input):
            self.assertTrue(uu.is_abspath(test_input))

        _aT(os.path.dirname(__file__))


class TestUnitUtilityMakeTempDir(TestCase):
    def setUp(self):
        self.actual = uu.make_temp_dir()

    def test_returns_existing_directory(self):
        self.assertIsNotNone(self.actual)
        self.assertTrue(os.path.exists(self.actual))
        self.assertTrue(os.path.isdir(self.actual))

    def test_returns_expected_type(self):
        self.assertTrue(uu.is_internalbytestring(self.actual))

    def test_returns_absolute_paths(self):
        self.assertTrue(os.path.isabs(self.actual))

    def test_returns_unique_directories(self):
        NUM_DIRS = 5

        s = set()
        for _ in range(0, NUM_DIRS):
            s.add(uu.make_temp_dir())

        self.assertEqual(len(s), NUM_DIRS)


class TestUnitUtilityMakeTemporaryFile(TestCase):
    def test_make_temporary_file(self):
        self.assertIsNotNone(uu.make_temporary_file)
        self.assertTrue(os.path.exists(uu.make_temporary_file()))
        self.assertTrue(os.path.isfile(uu.make_temporary_file()))
        self.assertIsInstance(uu.make_temporary_file(), bytes)

    def test_make_temporary_file_with_prefix(self):
        actual = uu.make_temporary_file(prefix='prefix_')
        self.assertTrue(os.path.exists(actual))
        self.assertTrue(os.path.isfile(actual))

        actual_basename = os.path.basename(actual)
        self.assertTrue(actual_basename.startswith(b'prefix_'))

    def test_make_temporary_file_with_suffix(self):
        actual = uu.make_temporary_file(suffix='_suffix')
        self.assertTrue(os.path.exists(actual))
        self.assertTrue(os.path.isfile(actual))
        self.assertTrue(actual.endswith(b'_suffix'))

    def test_make_temporary_file_with_prefix_and_suffix(self):
        actual = uu.make_temporary_file(prefix='mjao', suffix='.jpg')
        self.assertTrue(os.path.exists(actual))
        self.assertTrue(os.path.isfile(actual))

        actual_basename = os.path.basename(actual)
        self.assertTrue(actual_basename.endswith(b'.jpg'))
        self.assertTrue(actual_basename.startswith(b'mjao'))

    def test_make_temporary_file_with_basename(self):
        actual = uu.make_temporary_file(basename='mjao.jpg')
        self.assertTrue(os.path.exists(actual))
        self.assertTrue(os.path.isfile(actual))

        actual_basename = os.path.basename(actual)
        self.assertEqual(actual_basename, B'mjao.jpg')


class TestUnitUtilityGetMockAnalyzer(TestCase):
    def test_get_mock_analyzer_returns_something(self):
        self.assertIsNotNone(uu.get_mock_analyzer())

    def test_get_mock_analyzer_is_generator(self):
        self.assertIsInstance(uu.get_mock_analyzer(), types.GeneratorType)

    def test_get_mock_analyzer_returns_analyzers(self):
        import analyzers
        registered, _ = analyzers.get_analyzer_classes()
        for a in uu.get_mock_analyzer():
            self.assertIn(type(a), registered)


class TestUnitUtilityGetMockFileObject(TestCase):
    def test_get_mock_fileobject_returns_something(self):
        self.assertIsNotNone(uu.get_mock_fileobject())

    def test_get_mock_fileobject_returns_expected_type(self):
        self.assertIsInstance(uu.get_mock_fileobject(), FileObject)

    def test_get_mock_fileobject_with_mime_type_video_mp4(self):
        actual = uu.get_mock_fileobject(mime_type='video/mp4')
        self.assertEqual(actual.mime_type, 'video/mp4')

    def test_get_mock_fileobject_with_mime_type_all_types(self):
        mime_types = ['application/pdf', 'image/gif', 'image/jpeg',
                      'image/png', 'image/x-ms-bmp', 'text/plain', 'video/mp4']

        for mt in mime_types:
            actual = uu.get_mock_fileobject(mime_type=mt)
            self.assertEqual(actual.mime_type, mt)


class TestUnitUtilityGetMeowURI(TestCase):
    def test_returns_something(self):
        self.assertIsNotNone(uu.get_meowuri())

    def test_returns_expected_type(self):
        self.assertIsInstance(uu.get_meowuri(), MeowURI)


class TestCaptureStdout(TestCase):
    def test_capture_stdout(self):
        with uu.capture_stdout() as out:
            print('stdOUT should be captured')
            print('stdERR should NOT be captured', file=sys.stderr)

        self.assertEqual(out.getvalue().strip(), 'stdOUT should be captured')
        self.assertEqual(out.getvalue(), 'stdOUT should be captured\n')


class TestCaptureStderr(TestCase):
    def test_capture_stderr(self):
        with uu.capture_stderr() as out:
            print('stdERR should be captured', file=sys.stderr)
            print('stdOUT should NOT be captured')

        self.assertEqual(out.getvalue().strip(), 'stdERR should be captured')
        self.assertEqual(out.getvalue(), 'stdERR should be captured\n')


class TestUnitUtilityGetInstantiatedAnalyzers(TestCase):
    def setUp(self):
        self.instances = uu.get_instantiated_analyzers()

    def test_get_instantiated_analyzers_returns_something(self):
        self.assertIsNotNone(uu.get_instantiated_analyzers())

    def test_get_instantiated_analyzers_returns_expected_type(self):
        self.assertEqual(type(self.instances), list)

        from analyzers import BaseAnalyzer
        for analyzer_instance in self.instances:
            self.assertTrue(
                issubclass(analyzer_instance.__class__, BaseAnalyzer)
            )

    def test_get_analyzer_classes_does_not_return_classes(self):
        for instance in self.instances:
            self.assertFalse(uu.is_class(instance))

    def test_get_analyzer_classes_returns_class_instances(self):
        for instance in self.instances:
            self.assertTrue(uu.is_class_instance(instance))

    def test_get_instantiated_analyzers_returns_arbitrary_number(self):
        expected = len([
            f for f in
            os.listdir(
                os.path.join(uuconst.DIRPATH_AUTONAMEOW_SRCROOT, 'analyzers')
            )
            if f.startswith('analyze_') and f.endswith('.py')
        ])
        self.assertGreaterEqual(len(self.instances), expected)


class _DummyClass(object):
    pass


class TestIsClass(TestCase):
    def _assert_not_class(self, thing):
        actual = uu.is_class(thing)
        self.assertFalse(actual)
        self.assertIsInstance(actual, bool)

    def _assert_is_class(self, thing):
        actual = uu.is_class(thing)
        self.assertTrue(actual)
        self.assertIsInstance(actual, bool)

    def test_returns_true_for_classes(self):
        self._assert_is_class(_DummyClass)

    def test_returns_false_for_class_instances(self):
        self._assert_not_class(_DummyClass())

    def test_returns_false_for_none_or_empty(self):
        self._assert_not_class(None)
        self._assert_not_class('')
        self._assert_not_class([])
        self._assert_not_class([''])
        self._assert_not_class((None, None))

    def test_returns_false_for_primitive_types(self):
        self._assert_not_class(False)
        self._assert_not_class(True)
        self._assert_not_class(' ')
        self._assert_not_class([' '])
        self._assert_not_class(set())
        self._assert_not_class((None, None))
        self._assert_not_class(('foo', 'bar'))
        self._assert_not_class(1)
        self._assert_not_class(1.0)


class TestIsClassInstance(TestCase):
    def _assert_not_class_instance(self, klass):
        actual = uu.is_class_instance(klass)
        self.assertFalse(actual)
        self.assertIsInstance(actual, bool)

    def _assert_is_class_instance(self, thing):
        actual = uu.is_class_instance(thing)
        self.assertTrue(actual)
        self.assertIsInstance(actual, bool)

    def test_returns_false_for_classes(self):
        self._assert_not_class_instance(_DummyClass)

    def test_returns_true_for_class_instances(self):
        instance = _DummyClass()
        self._assert_is_class_instance(instance)
        self._assert_is_class_instance(_DummyClass())

    def test_returns_false_for_none_or_empty(self):
        self._assert_not_class_instance(None)
        self._assert_not_class_instance('')
        self._assert_not_class_instance([])
        self._assert_not_class_instance([''])
        self._assert_not_class_instance((None, None))

    def test_returns_false_for_primitive_types(self):
        self._assert_not_class_instance(False)
        self._assert_not_class_instance(True)
        self._assert_not_class_instance(' ')
        self._assert_not_class_instance([' '])
        self._assert_not_class_instance(set())
        self._assert_not_class_instance(('foo', 'bar'))
        self._assert_not_class_instance(1)
        self._assert_not_class_instance(1.0)


class TestStrToDatetime(TestCase):
    def test_returns_expected_type(self):
        actual = uu.str_to_datetime('2017-08-09 001225')
        self.assertIsInstance(actual, datetime)

    def test_returns_expected_type_with_timezone(self):
        actual = uu.str_to_datetime('2017-08-09 001225', tz='+0000')
        self.assertIsInstance(actual, datetime)

    def test_raises_exception_if_given_invalid_argument(self):
        def _assert_raises(test_data):
            with self.assertRaises((ValueError, TypeError)):
                uu.str_to_datetime(test_data)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises(' ')
        _assert_raises('2017-08-09T001225')
        _assert_raises('2017-0809 001225')
        _assert_raises('201708-09 001225')


class TestIsImportable(TestCase):
    def test_is_importable_returns_booleans(self):
        expect_false = uu.is_importable(None)
        self.assertIsInstance(expect_false, bool)

        expect_true = uu.is_importable('datetime')
        self.assertIsInstance(expect_true, bool)

    def test_is_importable_returns_false_as_expected(self):
        self.assertFalse(uu.is_importable(None))
        self.assertFalse(uu.is_importable(''))
        self.assertFalse(uu.is_importable(' '))
        self.assertFalse(uu.is_importable('foo'))

    def test_is_importable_returns_true_as_expected(self):
        self.assertTrue(uu.is_importable('datetime'))


class TestGetDummyValidatedConditions(TestCase):
    def test_returns_expected_type(self):
        actual = uu.get_dummy_rulecondition_instances()
        self.assertIsInstance(actual, list)

    def test_returns_rule_class_instances(self):
        conditions = uu.get_dummy_rulecondition_instances()

        from core.config import rules
        for condition in conditions:
            self.assertTrue(uu.is_class_instance(condition))
            self.assertIsInstance(condition, rules.RuleCondition)

    def test_returns_all_rule_conditions_defined_in_unit_utils_constants(self):
        expected = len(uuconst.DUMMY_RAW_RULE_CONDITIONS)
        actual = len(uu.get_dummy_rulecondition_instances())
        self.assertEqual(actual, expected)


class TestGetDummyRawConditions(TestCase):
    def test_returns_expected_type(self):
        actual = uu.get_dummy_raw_conditions()
        self.assertIsInstance(actual, list)

    def test_returns_equivalent_structure_as_yaml_config(self):
        conditions = uu.get_dummy_raw_conditions()
        for condition in conditions:
            self.assertIsInstance(condition, dict)

    def test_returns_all_rule_conditions_defined_in_unit_utils_constants(self):
        expected = len(uuconst.DUMMY_RAW_RULE_CONDITIONS)
        actual = len(uu.get_dummy_rulecondition_instances())
        self.assertEqual(actual, expected)


class TestIsInternalString(TestCase):
    def test_returns_false_as_expected(self):
        def _aF(test_input):
            actual = uu.is_internalstring(test_input)
            self.assertFalse(actual)
            self.assertIsInstance(actual, bool)

        _aF(None)
        _aF(object())
        _aF(b'')

    def test_returns_true_as_expected(self):
        def _aT(test_input):
            actual = uu.is_internalstring(test_input)
            self.assertTrue(actual)
            self.assertIsInstance(actual, bool)

        _aT('')
        _aT('foo')


class TestIsInternalByteString(TestCase):
    def test_returns_false_as_expected(self):
        def _aF(test_input):
            actual = uu.is_internalbytestring(test_input)
            self.assertFalse(actual)
            self.assertIsInstance(actual, bool)

        _aF(None)
        _aF(object())
        _aF('')
        _aF('foo')

    def test_returns_true_as_expected(self):
        def _aT(test_input):
            actual = uu.is_internalbytestring(test_input)
            self.assertTrue(actual)
            self.assertIsInstance(actual, bool)

        _aT(b'')
        _aT(b'foo')


class TestGetDefaultConfig(TestCase):
    @classmethod
    def setUpClass(cls):
        uu.init_session_repository()
        uu.init_provider_registry()
        cls.actual = uu.get_default_config()

    def test_does_not_return_none(self):
        self.assertIsNotNone(self.actual)

    def test_returns_an_instance_of_the_configuration_class(self):
        from core.config.configuration import Configuration
        self.assertIsInstance(self.actual, Configuration)


class TestAsMeowURI(TestCase):
    def test_returns_meowuri_instance_from_unit_utils_constants_string(self):
        expect = MeowURI(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        actual = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)

        self.assertEqual(actual, expect)
        self.assertIsInstance(actual, MeowURI)

    def test_returns_meowuri_instance_from_unit_utils_constants_strings(self):
        for given in uuconst.ALL_FULL_MEOWURIS:
            actual = uu.as_meowuri(given)
            self.assertIsInstance(actual, MeowURI)

    def test_raises_assertion_error_given_invalid_argument(self):
        for given in [None, '', ' ', {}, []]:
            with self.assertRaises(AssertionError):
                _ = uu.as_meowuri(given)


class GetExpectedTextForSamplefile(TestCase):
    def test_returns_none_when_expected_text_file_does_not_exist(self):
        actual = uu.get_expected_text_for_samplefile('magic_png.png')
        self.assertIsNone(actual)

    def test_returns_expected_text_when_expected_text_file_exists(self):
        actual = uu.get_expected_text_for_samplefile('sample.rtf')
        expect = '''Foo title
bar text


meow list

cat list

baz last line
'''
        self.assertEqual(expect, actual)


class RandomAsciiString(TestCase):
    def test_returns_empty_string(self):
        actual = uu.random_ascii_string(0)
        self.assertIsInstance(actual, str)
        self.assertEqual(0, len(actual))

    def test_returns_ten_character_string(self):
        actual = uu.random_ascii_string(10)
        self.assertIsInstance(actual, str)
        self.assertEqual(10, len(actual))

    def test_returns_string_with_only_ascii_characters(self):
        actual = uu.random_ascii_string(200)
        all_chars_are_ascii = all(ord(c) < 128 for c in actual)
        self.assertTrue(all_chars_are_ascii)
