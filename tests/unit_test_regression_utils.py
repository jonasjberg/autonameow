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
from unittest import TestCase

from core import constants as C
from util import encoding as enc
from regression_utils import (
    AutonameowWrapper,
    check_renames,
    get_regressiontest_dirs,
    get_regressiontests_rootdir,
    load_regressiontests,
    RegressionTestError,
    RegressionTestLoader,
    regtest_abspath
)
import unit_utils as uu
import unit_utils_constants as uuconst


class TestGetRegressiontestsRootdir(TestCase):
    def test_returns_absolute_bytestring_path(self):
        actual = get_regressiontests_rootdir()
        self.assertTrue(uu.dir_exists(actual))
        self.assertTrue(uu.is_abspath(actual))
        self.assertTrue(uu.is_internalbytestring(actual))


class TestRegtestAbspath(TestCase):
    def test_valid_argument_returns_absolute_bytestring_path(self):
        def _pass(test_input):
            _actual = regtest_abspath(test_input)
            self.assertTrue(uu.dir_exists(_actual))
            self.assertTrue(uu.is_abspath(_actual))
            self.assertTrue(uu.is_internalbytestring(_actual))

        _pass(uuconst.REGRESSIONTEST_DIR_BASENAMES[0])
        _pass(uuconst.REGRESSIONTEST_DIR_BASENAMES[1])
        _pass(uuconst.REGRESSIONTEST_DIR_BASENAMES[2])
        _pass(uuconst.REGRESSIONTEST_DIR_BASENAMES[3])
        _pass(uuconst.REGRESSIONTEST_DIR_BASENAMES[4])

    def test_bad_argument_raises_exception(self):
        def _fail(test_input):
            with self.assertRaises(AssertionError):
                _ = regtest_abspath(test_input)

        _fail(None)
        _fail('0001')
        _fail('0002_test')
        _fail('1337_this_directory_should_not_exist')
        _fail(b'1337_this_directory_should_not_exist')


class TestGetRegressiontestDirs(TestCase):
    def setUp(self):
        self.actual = get_regressiontest_dirs()

    def test_returns_list(self):
        self.assertTrue(isinstance(self.actual, list))

    def test_returns_at_least_one_test(self):
        self.assertGreaterEqual(len(self.actual), 1)

    def test_returns_existing_directories(self):
        for d in self.actual:
            with self.subTest(directory=d):
                self.assertTrue(uu.dir_exists(d))

    def test_returns_absolute_paths(self):
        for d in self.actual:
            with self.subTest(directory=d):
                self.assertTrue(uu.is_abspath(d))

    def test_returns_bytestring_paths(self):
        for d in self.actual:
            with self.subTest(directory=d):
                self.assertTrue(uu.is_internalbytestring(d))


class TestRegressionTestLoaderSetTestfilePath(TestCase):
    def test_options_without_input_paths_is_passed_through_as_is(self):
        input_options = {
            'verbose': True,
            'mode_batch': True,
            'mode_interactive': False,
            'dry_run': True,
            'recurse_paths': False,
        }

        actual = RegressionTestLoader._set_testfile_path(input_options)
        self.assertEqual(actual, input_options)

    def test_input_path_is_replaced(self):
        input_options = {
            'verbose': True,
            'input_paths': ['$TESTFILES/gmail.pdf'],
            'mode_batch': True,
        }
        expected = {
            'verbose': True,
            'input_paths': [uu.abspath_testfile('gmail.pdf')],
            'mode_batch': True,
        }
        actual = RegressionTestLoader._set_testfile_path(input_options)
        self.assertEqual(actual, expected)

    def test_input_paths_are_replaced(self):
        input_options = {
            'input_paths': ['$TESTFILES/gmail.pdf',
                            '$TESTFILES/magic_txt.txt'],
        }
        expected = {
            'input_paths': [uu.abspath_testfile('gmail.pdf'),
                            uu.abspath_testfile('magic_txt.txt')],
        }
        actual = RegressionTestLoader._set_testfile_path(input_options)
        self.assertEqual(actual, expected)

    def test_testfiles_directory_only_is_replaced(self):
        input_options = {
            'input_paths': ['$TESTFILES'],
        }
        expected = {
            'input_paths': [uuconst.TEST_FILES_DIR],
        }
        actual = RegressionTestLoader._set_testfile_path(input_options)
        self.assertEqual(actual, expected)

    def test_paths_are_normalized(self):
        input_options = {
            'input_paths': ['~/foo/temp'],
        }

        user_home = os.path.expanduser('~')
        _expected = os.path.join(user_home, 'foo', 'temp')
        expected = {
            'input_paths': [_expected],
        }
        actual = RegressionTestLoader._set_testfile_path(input_options)
        self.assertEqual(actual, expected)


class TestRegressionTestLoaderSetConfigPath(TestCase):
    def setUp(self):
        self._regressiontest_dir = regtest_abspath(
            uuconst.REGRESSIONTEST_DIR_BASENAMES[0]
        )
        self.rtl = RegressionTestLoader(self._regressiontest_dir)

    def _check(self, input_options, expected):
        actual = self.rtl._set_config_path(input_options)
        self.assertEqual(actual, expected)

    def test_uses_default_config_if_config_path_unspecified(self):
        input_options = {
            'verbose': True,
            'mode_batch': True,
        }
        expected = {
            'verbose': True,
            'config_path': uu.normpath(
                uu.abspath_testfile('default_config.yaml')
            ),
            'mode_batch': True,
        }
        self._check(input_options, expected)

    def test_uses_default_config_if_config_path_is_none(self):
        input_options = {
            'verbose': True,
            'config_path': None,
            'mode_batch': True,
        }
        expected = {
            'verbose': True,
            'config_path': uu.normpath(
                uu.abspath_testfile('default_config.yaml')
            ),
            'mode_batch': True,
        }
        self._check(input_options, expected)

    def test_replaces_config_path_variable_testfiles(self):
        input_options = {
            'verbose': True,
            'config_path': '$TESTFILES/default_config.yaml',
            'mode_batch': True,
        }
        expected = {
            'verbose': True,
            'config_path': uu.normpath(
                uu.abspath_testfile('default_config.yaml')
            ),
            'mode_batch': True,
        }
        self._check(input_options, expected)

    def test_replaces_config_path_variable_thistest(self):
        input_options = {
            'verbose': True,
            'config_path': '$THISTEST/config.yaml',
            'mode_batch': True,
        }

        _expect_path = os.path.join(
            enc.syspath(self._regressiontest_dir),
            enc.syspath(enc.encode_('config.yaml'))
        )
        self.assertTrue(isinstance(_expect_path, bytes))

        expected = {
            'verbose': True,
            'config_path': _expect_path,
            'mode_batch': True,
        }
        self._check(input_options, expected)


class TestRegressionTestLoaderWithFirstRegressionTest(TestCase):
    def setUp(self):
        _regressiontest_dir = regtest_abspath(
            uuconst.REGRESSIONTEST_DIR_BASENAMES[1]
        )
        b = RegressionTestLoader(_regressiontest_dir)
        self.actual = b.load()

    def test_description(self):
        self.assertEqual(
            self.actual.get('description'),
            'Good old "test_files/gmail.pdf" integration test ..'
        )

    def test_options(self):
        # NOTE(jonas): Omitted environment-dependant option "input_paths".
        expected_options = {
            'debug': False,
            'verbose': True,
            'quiet': False,
            'show_version': False,
            'dump_config': False,
            'dump_options': False,
            'dump_meowuris': False,
            'list_all': True,
            'list_datetime': False,
            'list_title': False,
            'mode_batch': True,
            'mode_automagic': True,
            'mode_interactive': False,
            'dry_run': True,
            'recurse_paths': False,
        }
        actual = self.actual.get('options')
        for _option in expected_options:
            with self.subTest(expected_option=_option):
                self.assertIn(_option, actual)

        # Direct comparison won't work because "input_paths" should differ.
        for _option, _value in expected_options.items():
            with self.subTest():
                self.assertEqual(_value, actual.get(_option))

    def test_asserts(self):
        expected_asserts = {
            'exit_code': 0,
            'renames': {
                'gmail.pdf': '2016-01-11T124132 gmail.pdf',
            }
        }
        actual = self.actual.get('asserts')
        for _option in expected_asserts:
            self.assertIn(_option, actual)

        self.assertEqual(actual, expected_asserts)

    def test_test_abspath(self):
        actual = self.actual.get('test_abspath')
        self.assertTrue(isinstance(actual, bytes))
        self.assertTrue(uu.is_abspath(actual))

        expect = uuconst.REGRESSIONTEST_DIR_BASENAMES[1]
        self.assertTrue(actual.endswith(expect))

    def test_test_dirname(self):
        actual = self.actual.get('test_dirname')
        self.assertTrue(isinstance(actual, bytes))

        expect = uuconst.REGRESSIONTEST_DIR_BASENAMES[1]
        self.assertEqual(actual, expect)


class TestLoadRegressiontests(TestCase):
    def setUp(self):
        self.actual = load_regressiontests()

    def test_returns_list(self):
        self.assertTrue(isinstance(self.actual, list))

    def test_returns_list_of_dicts(self):
        for a in self.actual:
            self.assertEqual(type(a), dict)

    def test_returns_at_least_one_test(self):
        self.assertGreaterEqual(len(self.actual), 1)


class TestAutonameowWrapper(TestCase):
    def setUp(self):
        self.aw = AutonameowWrapper()

    def test_call(self):
        self.aw()

    def test_captured_exitcode_type(self):
        self.aw()
        actual = self.aw.captured_exitcode
        self.assertIsNotNone(actual)
        self.assertTrue(type(actual), int)

    def test_captured_stdout_type(self):
        self.aw()
        actual = self.aw.captured_stdout
        self.assertIsNotNone(actual)
        self.assertTrue(type(actual), str)

    def test_captured_stderr_type(self):
        self.aw()
        actual = self.aw.captured_stderr
        self.assertIsNotNone(actual)
        self.assertTrue(type(actual), str)


class TestAutonameowWrapperWithDefaultOptions(TestCase):
    def setUp(self):
        self.aw = AutonameowWrapper()
        self.aw()

    def test_exitcode_is_exit_success(self):
        actual = self.aw.captured_exitcode
        self.assertEqual(actual, C.EXIT_SUCCESS)

    def test_stderr_contains_no_input_files_specified(self):
        actual = self.aw.captured_stderr
        self.assertIn('No input files specified', actual)

    def test_stdout_is_empty(self):
        actual = self.aw.captured_stdout
        self.assertIn('', actual)


class TestRenames(TestCase):
    def _fail(self, actual_renames, expect_renames):
        actual = check_renames(actual_renames, expect_renames)
        self.assertFalse(actual)

    def _ok(self, actual_renames, expect_renames):
        actual = check_renames(actual_renames, expect_renames)
        self.assertTrue(actual)

    def test_raises_exception_given_bad_arguments(self):
        def _fail(actual_renames, expect_renames):
            with self.assertRaises(RegressionTestError):
                _ = check_renames(actual_renames, expect_renames)

        _fail(None, None)
        _fail('', None)
        _fail(None, '')
        _fail({}, '')
        _fail('', {})

    def test_returns_true_given_one_matching_rename(self):
        self._ok(actual_renames={}, expect_renames={})
        self._ok(actual_renames={'A': 'A'}, expect_renames={'A': 'A'})
        self._ok(actual_renames={'A': 'foo'}, expect_renames={'A': 'foo'})
        self._ok(actual_renames={'A': 'bar'}, expect_renames={'A': 'bar'})

    def test_returns_true_given_matching_renames(self):
        self._ok(actual_renames={'A': 'foo', 'B': 'B'},
                 expect_renames={'A': 'foo', 'B': 'B'})
        self._ok(actual_renames={'A': 'foo', 'B': 'bar'},
                 expect_renames={'A': 'foo', 'B': 'bar'})

    def test_returns_false_given_one_non_matching_rename(self):
        self._fail(actual_renames={}, expect_renames={'A': 'A'})
        self._fail(actual_renames={}, expect_renames={'A': 'B'})
        self._fail(actual_renames={}, expect_renames={'B': 'A'})
        self._fail(actual_renames={'A': 'A'}, expect_renames={})
        self._fail(actual_renames={'A': 'B'}, expect_renames={})
        self._fail(actual_renames={'B': 'A'}, expect_renames={})
        self._fail(actual_renames={'A': 'A'}, expect_renames={'A': 'B'})
        self._fail(actual_renames={'A': 'A'}, expect_renames={'B': 'A'})
        self._fail(actual_renames={'A': 'A'}, expect_renames={'B': 'B'})
        self._fail(actual_renames={'A': 'B'}, expect_renames={'A': 'A'})
        self._fail(actual_renames={'A': 'B'}, expect_renames={'B': 'A'})
        self._fail(actual_renames={'A': 'B'}, expect_renames={'B': 'B'})
        self._fail(actual_renames={'B': 'A'}, expect_renames={'A': 'A'})
        self._fail(actual_renames={'B': 'A'}, expect_renames={'A': 'B'})
        self._fail(actual_renames={'B': 'A'}, expect_renames={'B': 'B'})
        self._fail(actual_renames={'B': 'B'}, expect_renames={'A': 'A'})
        self._fail(actual_renames={'B': 'B'}, expect_renames={'A': 'B'})
        self._fail(actual_renames={'B': 'B'}, expect_renames={'B': 'A'})

    def test_returns_false_given_non_matching_renames(self):
        self._fail(actual_renames={}, expect_renames={'A': 'A', 'B': 'A'})
        self._fail(actual_renames={}, expect_renames={'A': 'A', 'B': 'B'})
        self._fail(actual_renames={}, expect_renames={'A': 'B', 'B': 'A'})
        self._fail(actual_renames={}, expect_renames={'A': 'B', 'B': 'B'})
        self._fail(actual_renames={'A': 'A', 'B': 'A'}, expect_renames={})
        self._fail(actual_renames={'A': 'A', 'B': 'B'}, expect_renames={})
        self._fail(actual_renames={'A': 'B', 'B': 'A'}, expect_renames={})
        self._fail(actual_renames={'A': 'B', 'B': 'B'}, expect_renames={})

        self._fail(actual_renames={'A': 'A', 'B': 'A'},
                   expect_renames={'A': 'A', 'B': 'B'})
        self._fail(actual_renames={'A': 'A', 'B': 'B'},
                   expect_renames={'A': 'A', 'B': 'A'})
        self._fail(actual_renames={'A': 'B', 'B': 'B'},
                   expect_renames={'A': 'A', 'B': 'B'})
        self._fail(actual_renames={'A': 'A', 'C': 'C'},
                   expect_renames={'B': 'A', 'C': 'C'})
        self._fail(actual_renames={'A': 'A', 'C': 'D'},
                   expect_renames={'B': 'A', 'C': 'C'})
