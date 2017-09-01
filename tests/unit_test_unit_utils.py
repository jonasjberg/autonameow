#!/usr/bin/env python3
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

import os
import types
from datetime import datetime
from unittest import TestCase

import analyzers
from analyzers import BaseAnalyzer
from core.config import rules
from core.fileobject import FileObject

import unit_utils as uu
import unit_utils_constants as uuconst


class TestUnitUtilityConstants(TestCase):
    def test_tests_dir_is_defined(self):
        self.assertIsNotNone(uuconst.TEST_FILES_DIR)

    def test_tests_dir_exists(self):
        self.assertTrue(os.path.exists(uuconst.TEST_FILES_DIR))

    def test_tests_dir_is_a_directory(self):
        self.assertTrue(os.path.isdir(uuconst.TEST_FILES_DIR))

    def test_tests_dir_is_readable(self):
        self.assertTrue(os.access(uuconst.TEST_FILES_DIR, os.R_OK))

    def test_tests_dir_is_executable(self):
        self.assertTrue(os.access(uuconst.TEST_FILES_DIR, os.X_OK))

    def test_autonameow_srcroot_dir_is_defined(self):
        self.assertIsNotNone(uuconst.AUTONAMEOW_SRCROOT_DIR)

    def test_autonameow_srcroot_dir_exists(self):
        self.assertTrue(os.path.exists(uuconst.AUTONAMEOW_SRCROOT_DIR))

    def test_autonameow_srcroot_dir_is_a_directory(self):
        self.assertTrue(os.path.isdir(uuconst.AUTONAMEOW_SRCROOT_DIR))

    def test_autonameow_srcroot_dir_is_readable(self):
        self.assertTrue(os.access(uuconst.AUTONAMEOW_SRCROOT_DIR, os.R_OK))

    def test_autonameow_srcroot_dir_is_executable(self):
        self.assertTrue(os.access(uuconst.AUTONAMEOW_SRCROOT_DIR, os.X_OK))


class TestUnitUtilityAbsPathTestFile(TestCase):
    def test_abspath_testfile_is_defined(self):
        self.assertIsNotNone(uu.abspath_testfile)

    def test_returns_expected_encoding(self):
        actual = uu.abspath_testfile('empty')
        self.assertTrue(isinstance(actual, str))

    def test_returns_absolute_paths(self):
        actual = uu.abspath_testfile('empty')
        self.assertTrue(os.path.isabs(actual))


class TestUnitUtilityFileExists(TestCase):
    def test_file_exists_is_defined(self):
        self.assertIsNotNone(uu.file_exists)

    def _check_return(self, file_to_test):
        actual = uu.file_exists(file_to_test)
        self.assertTrue(isinstance(actual, bool))

        expected = os.path.isfile(file_to_test)
        self.assertEqual(actual, expected)

    def test_returns_false_for_files_assumed_missing(self):
        _dummy_paths = [
            '/foo/bar/baz/mjao',
            '/tmp/this_isnt_a_file_right_or_huh',
            b'/tmp/this_isnt_a_file_right_or_huh'
        ]
        for df in _dummy_paths:
            self._check_return(df)

    def test_returns_true_for_files_likely_to_exist(self):
        _files = [
            __file__,
        ]
        for df in _files:
            self._check_return(df)


class TestUnitUtilityDirExists(TestCase):
    def test_dir_exists_is_defined(self):
        self.assertIsNotNone(uu.dir_exists)

    def _check_return(self, path_to_test):
        actual = uu.dir_exists(path_to_test)
        self.assertTrue(isinstance(actual, bool))

        expected = os.path.isdir(path_to_test)
        self.assertEqual(actual, expected)

    def test_returns_false_for_assumed_non_directory_paths(self):
        _dummy_paths = [
            '/foo/bar/baz/mjao',
            '/tmp/this_isnt_a_file_right_or_huh',
            b'/tmp/this_isnt_a_file_right_or_huh',
            __file__
        ]
        for df in _dummy_paths:
            self._check_return(df)

    def test_returns_true_for_likely_directory_paths(self):
        _files = [
            os.path.dirname(__file__),
            uuconst.AUTONAMEOW_SRCROOT_DIR,
            '/'
        ]
        for df in _files:
            self._check_return(df)


class TestUnitUtilityPathIsReadable(TestCase):
    def _check_return(self, path_to_test):
        actual = uu.path_is_readable(path_to_test)
        self.assertTrue(isinstance(actual, bool))

        try:
            expected = os.access(path_to_test, os.R_OK)
        except OSError:
            expected = False
        self.assertEqual(actual, expected)

    def test_returns_false_for_paths_assumed_missing(self):
        _dummy_paths = [
            '',
            b'',
            '/foo/bar/baz/mjao',
            b'/foo/bar/baz/mjao',
            '/tmp/this_isnt_a_file_right_or_huh'
        ]
        for df in _dummy_paths:
            self._check_return(df)

    def test_returns_true_for_paths_likely_to_exist(self):
        _paths = [
            __file__,
            os.path.dirname(__file__),
        ]
        for df in _paths:
            self._check_return(df)


class TestUnitUtilityMakeTempDir(TestCase):
    def test_make_temp_dir(self):
        self.assertIsNotNone(uu.make_temp_dir())
        self.assertTrue(os.path.exists(uu.make_temp_dir()))
        self.assertTrue(os.path.isdir(uu.make_temp_dir()))


class TestUnitUtilityMakeTemporaryFile(TestCase):
    def test_make_temporary_file(self):
        self.assertIsNotNone(uu.make_temporary_file)
        self.assertTrue(os.path.exists(uu.make_temporary_file()))
        self.assertTrue(os.path.isfile(uu.make_temporary_file()))
        self.assertTrue(isinstance(uu.make_temporary_file(), bytes))

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
    def test_get_mock_analyzer_is_defined(self):
        self.assertIsNotNone(uu.get_mock_analyzer)
        self.assertIsNotNone(uu.get_mock_analyzer())

    def test_get_mock_analyzer_is_generator(self):
        self.assertTrue(isinstance(uu.get_mock_analyzer(), types.GeneratorType))

    def test_get_mock_analyzer_returns_analyzers(self):
        for a in uu.get_mock_analyzer():
            self.assertIn(type(a), analyzers.get_analyzer_classes())


class TestUnitUtilityGetMockFileObject(TestCase):
    def test_get_mock_fileobject_is_defined(self):
        self.assertIsNotNone(uu.get_mock_fileobject)
        self.assertIsNotNone(uu.get_mock_fileobject())

    def test_get_mock_fileobject_returns_expected_type(self):
        self.assertTrue(isinstance(uu.get_mock_fileobject(), FileObject))

    def test_get_mock_fileobject_with_mime_type_video_mp4(self):
        actual = uu.get_mock_fileobject(mime_type='video/mp4')
        self.assertEqual(actual.mime_type, 'video/mp4')

    def test_get_mock_fileobject_with_mime_type_all_types(self):
        mime_types = ['application/pdf', 'image/gif', 'image/jpeg',
                      'image/png', 'image/x-ms-bmp', 'text/plain', 'video/mp4']

        for mt in mime_types:
            actual = uu.get_mock_fileobject(mime_type=mt)
            self.assertEqual(actual.mime_type, mt)


class TestCaptureStdout(TestCase):
    def test_capture_stdout(self):
        with uu.capture_stdout() as out:
            print('should_be_captured')

        self.assertEqual(out.getvalue().strip(), 'should_be_captured')
        self.assertEqual(out.getvalue(), 'should_be_captured\n')


class TestUnitUtilityGetInstantiatedAnalyzers(TestCase):
    def setUp(self):
        self.instances = uu.get_instantiated_analyzers()

    def test_get_instantiated_analyzers_returns_something(self):
        self.assertIsNotNone(uu.get_instantiated_analyzers())

    def test_get_instantiated_analyzers_returns_expected_type(self):
        self.assertEqual(type(self.instances), list)

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
        # TODO: [hardcoded] Likely to break; Fix or remove!
        self.assertGreaterEqual(len(self.instances), 6)


class _DummyClass(object):
    pass


class TestIsClass(TestCase):
    def test_is_class_is_defined(self):
        self.assertIsNotNone(uu.is_class)

    def _assert_not_class(self, thing):
        actual = uu.is_class(thing)
        self.assertFalse(actual)
        self.assertTrue(isinstance(actual, bool))

    def _assert_is_class(self, thing):
        actual = uu.is_class(thing)
        self.assertTrue(actual)
        self.assertTrue(isinstance(actual, bool))

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
    def test_is_class_instance_is_defined(self):
        self.assertIsNotNone(uu.is_class_instance)

    def _assert_not_class_instance(self, klass):
        actual = uu.is_class_instance(klass)
        self.assertFalse(actual)
        self.assertTrue(isinstance(actual, bool))

    def _assert_is_class_instance(self, thing):
        actual = uu.is_class_instance(thing)
        self.assertTrue(actual)
        self.assertTrue(isinstance(actual, bool))

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
    def test_str_to_datetime_is_defined(self):
        self.assertIsNotNone(uu.str_to_datetime)

    def test_returns_expected_type(self):
        actual = uu.str_to_datetime('2017-08-09 001225')
        self.assertTrue(isinstance(actual, datetime))

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
        self.assertTrue(isinstance(expect_false, bool))

        expect_true = uu.is_importable('datetime')
        self.assertTrue(isinstance(expect_true, bool))

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
        self.assertTrue(isinstance(actual, list))

    def test_returns_rule_class_instances(self):
        conditions = uu.get_dummy_rulecondition_instances()
        for condition in conditions:
            self.assertTrue(uu.is_class_instance(condition))
            self.assertTrue(isinstance(condition, rules.RuleCondition))

    def test_returns_all_rule_conditions_defined_in_unit_utils_constants(self):
        expected = len(uuconst.DUMMY_RAW_RULE_CONDITIONS)
        actual = len(uu.get_dummy_rulecondition_instances())
        self.assertEqual(actual, expected)


class TestGetDummyRawConditions(TestCase):
    def test_returns_expected_type(self):
        actual = uu.get_dummy_raw_conditions()
        self.assertTrue(isinstance(actual, list))

    def test_returns_equivalent_structure_as_yaml_config(self):
        conditions = uu.get_dummy_raw_conditions()
        for condition in conditions:
            self.assertTrue(isinstance(condition, dict))

    def test_returns_all_rule_conditions_defined_in_unit_utils_constants(self):
        expected = len(uuconst.DUMMY_RAW_RULE_CONDITIONS)
        actual = len(uu.get_dummy_rulecondition_instances())
        self.assertEqual(actual, expected)
