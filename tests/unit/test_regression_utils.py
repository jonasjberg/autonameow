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

import inspect
import os
from unittest import TestCase

import unit.constants as uuconst
import unit.utils as uu
from core import constants as C
from util import encoding as enc
from regression.utils import (
    AutonameowWrapper,
    check_renames,
    commandline_for_testcase,
    _commandline_args_for_testcase,
    get_regressiontest_dirs,
    get_regressiontests_rootdir,
    glob_filter,
    load_regressiontests,
    MockUI,
    regexp_filter,
    RegressionTestError,
    RegressionTestLoader,
    regtest_abspath
)


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
        self.assertIsInstance(self.actual, list)

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
            'input_paths': [uuconst.PATH_TEST_FILES],
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
        self._default_config_path = uu.normpath(uu.abspath_testconfig())
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
            'config_path': self._default_config_path,
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
            'config_path': self._default_config_path,
            'mode_batch': True,
        }
        self._check(input_options, expected)

    def test_replaces_config_path_variable_testfiles(self):
        input_options = {
            'verbose': True,
            'config_path': '$TESTFILES/configs/default.yaml',
            'mode_batch': True,
        }
        expected = {
            'verbose': True,
            'config_path': self._default_config_path,
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
            enc.syspath(uu.encode('config.yaml'))
        )
        self.assertIsInstance(_expect_path, bytes)

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
        self.assertIsInstance(actual, bytes)
        self.assertTrue(uu.is_abspath(actual))

        expect = uuconst.REGRESSIONTEST_DIR_BASENAMES[1]
        self.assertTrue(actual.endswith(expect))

    def test_test_dirname(self):
        actual = self.actual.get('test_dirname')
        self.assertIsInstance(actual, bytes)

        expect = uuconst.REGRESSIONTEST_DIR_BASENAMES[1]
        self.assertEqual(actual, expect)


class TestLoadRegressiontests(TestCase):
    actual_loaded = load_regressiontests()

    def test_returns_list(self):
        self.assertIsInstance(self.actual_loaded, list)

    def test_returns_list_of_dicts(self):
        for a in self.actual_loaded:
            self.assertEqual(type(a), dict)

    def test_returns_at_least_one_test(self):
        self.assertGreaterEqual(len(self.actual_loaded), 1)


class TestMockUIInterface(TestCase):
    @classmethod
    def setUpClass(cls):
        from core.view import cli as core_view_cli
        cls.actual_cli_interface = inspect.getmembers(
            core_view_cli,
            lambda x: (inspect.isfunction(x) and not inspect.isbuiltin(x)
                       or (inspect.isclass(x) and x.__name__ == 'ColumnFormatter'))
        )

    def test_expected_interface_from_introspection(self):
        self.assertGreater(len(self.actual_cli_interface), 0)
        for name, value in self.actual_cli_interface:
            if name == 'ColumnFormatter':
                self.assertTrue(uu.is_class(value))
            else:
                self.assertTrue(callable(value), name)

    def test_expected_interface_includes_commonly_used_functions(self):
        for expected in (
            'colorize',
            'ColumnFormatter',
            'colorize_re_match',
            'colorize_quoted',
            'msg',
            'msg_possible_rename',
            'msg_rename',
            'msg_replacement',
            'print_exit_info',
            'print_start_info',
            'print_version_info',
            'silence',
            'unsilence'
        ):
            with self.subTest(expected_member=expected):
                self.assertTrue(any(
                    expected in member for member in self.actual_cli_interface
                ))

    def test_mock_implements_all_methods_exposed_by_the_cli_view(self):
        mock_ui = MockUI()
        for expected_name, _ in self.actual_cli_interface:
            self.assertTrue(hasattr(mock_ui, expected_name),
                            'Expected attribute {!s}'.format(expected_name))


class TestMockUIActualUsage(TestCase):
    def setUp(self):
        self.mock_ui = MockUI()

    def _assert_called_with_args(self, member, expect):
        self.assertIn(member, self.mock_ui.mock_call_history)
        self.assertEqual(expect, self.mock_ui.mock_call_history[member][0][0])

    def _assert_called_with_kwargs(self, member, expect):
        self.assertIn(member, self.mock_ui.mock_call_history)
        self.assertEqual(expect, self.mock_ui.mock_call_history[member][0][1])

    def test_call_colorize(self):
        self.mock_ui.colorize('foo')
        self.mock_ui.colorize('foo', fore=None)
        self.mock_ui.colorize('foo', fore=None, back=None)
        self.mock_ui.colorize('foo', fore=None, back=None, style=None)
        self.mock_ui.colorize('foo', fore='BLACK')
        self.mock_ui.colorize('foo', fore='BLACK', back='RED')
        self.mock_ui.colorize('foo', fore='BLACK', back='RED', style='NORMAL')

    def test_call_colorize_stores_passed_arguments(self):
        self.mock_ui.colorize('foo', fore='BLACK', back='RED', style='NORMAL')
        self._assert_called_with_args('colorize', ('foo', ))
        self._assert_called_with_kwargs(
            'colorize',
            {'fore': 'BLACK', 'back': 'RED', 'style': 'NORMAL'}
        )

    def test_call_colorize_re_match(self):
        self.mock_ui.colorize_re_match('foo', regex='bar')
        self.mock_ui.colorize_re_match('foo', regex='bar', color='BLACK')

    def test_call_msg(self):
        self.mock_ui.msg('foo')
        self.mock_ui.msg('foo', style='heading')
        self.mock_ui.msg('foo', add_info_log=False)
        self.mock_ui.msg('foo', ignore_quiet=False)
        self.mock_ui.msg('foo', style='heading', add_info_log=False)
        self.mock_ui.msg('foo', style='heading', ignore_quiet=False)
        self.mock_ui.msg('foo', ignore_quiet=False, add_info_log=False)
        self.mock_ui.msg('foo', style='heading', ignore_quiet=False, add_info_log=False)

    def test_call_msg_stores_passed_arguments(self):
        self.mock_ui.msg('foo', style='heading', ignore_quiet=False)
        self.assertIn('msg', self.mock_ui.mock_call_history)
        self.assertEqual('foo', self.mock_ui.mock_call_history['msg'][0][0][0])
        self._assert_called_with_args('msg', ('foo', ))

    def test_call_msg_possible_rename(self):
        self.mock_ui.msg_possible_rename('foo', 'bar')

    def test_call_msg_rename(self):
        self.mock_ui.msg_rename('foo', 'bar', False)

    def test_call_msg_replacement(self):
        self.mock_ui.msg_replacement('foo', 'bar', 'baz')

    def test_call_print_exit_info(self):
        self.mock_ui.print_exit_info(0, 1)

    def test_call_print_start_info(self):
        self.mock_ui.print_start_info()

    def test_call_print_version_info(self):
        self.mock_ui.print_version_info(False)

    def test_call_silence(self):
        self.mock_ui.silence()

    def test_call_unsilence(self):
        self.mock_ui.unsilence()


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
    @classmethod
    def setUpClass(cls):
        cls.aw = AutonameowWrapper()
        cls.aw()

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
    def _fail(self, actual, expect):
        actual = check_renames(actual, expect)
        self.assertFalse(actual)

    def _ok(self, actual, expect):
        actual = check_renames(actual, expect)
        self.assertTrue(actual)

    def test_raises_exception_given_bad_arguments(self):
        def _fail(actual, expect):
            with self.assertRaises(RegressionTestError):
                _ = check_renames(actual, expect)

        _fail(None, None)
        _fail('', None)
        _fail(None, '')
        _fail({}, '')
        _fail('', {})

    def test_returns_true_given_one_matching_rename(self):
        self._ok(actual={}, expect={})
        self._ok(actual={'A': 'A'}, expect={'A': 'A'})
        self._ok(actual={'A': 'foo'}, expect={'A': 'foo'})
        self._ok(actual={'A': 'bar'}, expect={'A': 'bar'})

    def test_returns_true_given_matching_renames(self):
        self._ok(actual={'A': 'foo', 'B': 'B'},
                 expect={'A': 'foo', 'B': 'B'})
        self._ok(actual={'A': 'foo', 'B': 'bar'},
                 expect={'A': 'foo', 'B': 'bar'})

    def test_returns_false_given_one_non_matching_rename(self):
        self._fail(actual={}, expect={'A': 'A'})
        self._fail(actual={}, expect={'A': 'B'})
        self._fail(actual={}, expect={'B': 'A'})
        self._fail(actual={'A': 'A'}, expect={})
        self._fail(actual={'A': 'B'}, expect={})
        self._fail(actual={'B': 'A'}, expect={})
        self._fail(actual={'A': 'A'}, expect={'A': 'B'})
        self._fail(actual={'A': 'A'}, expect={'B': 'A'})
        self._fail(actual={'A': 'A'}, expect={'B': 'B'})
        self._fail(actual={'A': 'B'}, expect={'A': 'A'})
        self._fail(actual={'A': 'B'}, expect={'B': 'A'})
        self._fail(actual={'A': 'B'}, expect={'B': 'B'})
        self._fail(actual={'B': 'A'}, expect={'A': 'A'})
        self._fail(actual={'B': 'A'}, expect={'A': 'B'})
        self._fail(actual={'B': 'A'}, expect={'B': 'B'})
        self._fail(actual={'B': 'B'}, expect={'A': 'A'})
        self._fail(actual={'B': 'B'}, expect={'A': 'B'})
        self._fail(actual={'B': 'B'}, expect={'B': 'A'})

    def test_returns_false_given_non_matching_renames(self):
        self._fail(actual={}, expect={'A': 'A', 'B': 'A'})
        self._fail(actual={}, expect={'A': 'A', 'B': 'B'})
        self._fail(actual={}, expect={'A': 'B', 'B': 'A'})
        self._fail(actual={}, expect={'A': 'B', 'B': 'B'})
        self._fail(actual={'A': 'A', 'B': 'A'}, expect={})
        self._fail(actual={'A': 'A', 'B': 'B'}, expect={})
        self._fail(actual={'A': 'B', 'B': 'A'}, expect={})
        self._fail(actual={'A': 'B', 'B': 'B'}, expect={})
        self._fail(actual={'A': 'A', 'B': 'A'}, expect={'A': 'A', 'B': 'B'})
        self._fail(actual={'A': 'A', 'B': 'B'}, expect={'A': 'A', 'B': 'A'})
        self._fail(actual={'A': 'B', 'B': 'B'}, expect={'A': 'A', 'B': 'B'})
        self._fail(actual={'A': 'A', 'C': 'C'}, expect={'B': 'A', 'C': 'C'})
        self._fail(actual={'A': 'A', 'C': 'D'}, expect={'B': 'A', 'C': 'C'})


SAMPLE_TESTCASE_0000 = {
    'asserts': {
        'exit_code': 0
    },
    'description': 'Dummy test used by regression runner and utilities unit tests',
    'options': {
        'config_path': b'foo/test_files/configs/default.yaml',
        'debug': False,
        'dry_run': True,
        'dump_config': False,
        'dump_meowuris': False,
        'dump_options': False,
        'list_all': False,
        'mode_automagic': True,
        'mode_batch': True,
        'mode_interactive': False,
        'quiet': False,
        'recurse_paths': False,
        'show_version': False,
        'verbose': False,
    },
    'skiptest': False,
    'test_abspath': b'foo/tests/regression/0000_unittest_dummy',
    'test_dirname': b'0000_unittest_dummy'
}
SAMPLE_TESTCASE_0006 = {
    'asserts': {
        'exit_code': 0
    },
    'description': 'All *.jpg test files with minimal settings for output and actions',
    'options': {
        'config_path': b'foo/test_files/configs/default.yaml',
        'debug': False,
        'dry_run': True,
        'dump_config': False,
        'dump_meowuris': False,
        'dump_options': False,
        'input_paths': [
            'foo/test_files/smulan.jpg',
            'foo/test_files/magic_jpg.jpg'
        ],
        'list_all': False,
        'mode_automagic': True,
        'mode_batch': True,
        'mode_interactive': False,
        'quiet': True,
        'recurse_paths': False,
        'show_version': False,
        'verbose': False,
    },
    'skiptest': False,
    'test_abspath': b'foo/tests/regression/0006_all_testfiles',
    'test_dirname': b'0006_all_testfiles'
}


class TestCommandlineArgsForTestcase(TestCase):
    def test_returns_expected_command_for_testcase_0000(self):
        expected_options = [
            '--dry-run',
            '--automagic',
            '--batch',
            "--config-path 'foo/test_files/configs/default.yaml'"
        ]
        actual = _commandline_args_for_testcase(SAMPLE_TESTCASE_0000)

        self.assertEqual(len(expected_options), len(actual))
        for expect_option in expected_options:
            self.assertIn(expect_option, actual)

    def test_returns_expected_command_for_testcase_0006(self):
        expected_options = [
            '--dry-run',
            '--automagic',
            '--batch',
            '--quiet',
            "--config-path 'foo/test_files/configs/default.yaml'",
            '--',
            "'foo/test_files/smulan.jpg'",
            "'foo/test_files/magic_jpg.jpg'"
        ]
        actual = _commandline_args_for_testcase(SAMPLE_TESTCASE_0006)

        self.assertEqual(len(expected_options), len(actual))
        for expect_option in expected_options:
            self.assertIn(expect_option, actual)


class TestCommandlineForTestcase(TestCase):
    def test_returns_expected_for_empty_testcase(self):
        actual = commandline_for_testcase({})
        expect = 'autonameow'
        self.assertEqual(actual, expect)

    def test_returns_expected_for_testcase_0000(self):
        actual = commandline_for_testcase(SAMPLE_TESTCASE_0000)
        expect = "autonameow --automagic --batch --dry-run --config-path 'foo/test_files/configs/default.yaml'"
        self.assertEqual(actual, expect)

    def test_returns_expected_for_testcase_0006(self):
        actual = commandline_for_testcase(SAMPLE_TESTCASE_0006)
        expect = "autonameow --automagic --batch --dry-run --quiet --config-path 'foo/test_files/configs/default.yaml' -- 'foo/test_files/smulan.jpg' 'foo/test_files/magic_jpg.jpg'"
        self.assertEqual(actual, expect)


class TestGlobFilter(TestCase):
    def _assert_match(self, expected, string, glob):
        actual = glob_filter(glob, string)
        self.assertIsInstance(actual, bool)
        self.assertEqual(expected, actual)

    def test_returns_false_for_non_matches(self):
        self._assert_match(False, b'foo', glob='bar')
        self._assert_match(False, b'foo', glob='foobar')
        self._assert_match(False, b'foo', glob='fooo')
        self._assert_match(False, b'foo bar', glob='bar foo')
        self._assert_match(False, b'fooxbar', glob='*xfoo')
        self._assert_match(False, b'fooxbar', glob='*x*foo')
        self._assert_match(False, b'foo', glob='!foo')
        self._assert_match(False, b'foo', glob='!*o')
        self._assert_match(False, b'foo', glob='!*')
        self._assert_match(False, b'foo x bar', glob='!foo*')
        self._assert_match(False, b'bar', glob='foo*')
        self._assert_match(False, b'9008_LOCAL_dropbox', glob='!*LOCAL*')

    def test_returns_true_for_matches(self):
        self._assert_match(True, b'foo', glob='foo')
        self._assert_match(True, b'foo', glob='fo*')
        self._assert_match(True, b'fooxbar', glob='foo*x*')
        self._assert_match(True, b'fooxbar', glob='foox*')
        self._assert_match(True, b'fooxbar', glob='*x*')
        self._assert_match(True, b'foo x bar', glob='*x*')
        self._assert_match(True, b'bar', glob='!foo')
        self._assert_match(True, b'foo bar', glob='foo bar')
        self._assert_match(True, b'foo bar', glob='foo*')
        self._assert_match(True, b'0000', glob='!0001')
        self._assert_match(True, b'9008_LOCAL_dropbox', glob='*LOCAL*')


class TestRegexpFilter(TestCase):
    def _assert_match(self, expected, string, expression):
        actual = regexp_filter(expression, string)
        self.assertIsInstance(actual, bool)
        self.assertEqual(expected, actual)

    def test_raises_exception_given_invalid_regular_expression(self):
        with self.assertRaises(RegressionTestError):
            _ = regexp_filter('*a', b'foo')

    def test_returns_false_for_non_matches(self):
        self._assert_match(False, b'foo', expression='bar')
        self._assert_match(False, b'foo', expression='foobar')
        self._assert_match(False, b'foo', expression='fooo')
        self._assert_match(False, b'foo bar', expression='bar foo')
        self._assert_match(False, b'fooxbar', expression='.*xfoo')
        self._assert_match(False, b'fooxbar', expression='.*x.*foo')

    def test_returns_true_for_matches(self):
        self._assert_match(True, b'foo', expression='foo')
        self._assert_match(True, b'foo', expression='fo?')
        self._assert_match(True, b'foo', expression='f.*')
        self._assert_match(True, b'fooxbar', expression='foo*x.*')
        self._assert_match(True, b'fooxbar', expression='foox[abr]+')
        self._assert_match(True, b'Fooxbar', expression='[fF]oox(bar|foo)')
