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

from regression_utils import (
    get_regressiontest_dirs,
    get_regressiontests_rootdir,
    load_regressiontests,
    RegressionTestLoader,
    regtest_abspath
)
import unit_utils as uu
import unit_utils_constants as uuconst


# TODO: [TD0117] Implement automated regression tests


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

        _pass(b'0001')
        _pass(b'0001_duplicate_inputpath')
        _pass(b'0002')
        _pass(b'0003_filetags')
        _pass(b'0004_add_extension')
        _pass(uuconst.REGRESSIONTEST_DIR_BASENAMES[0])
        _pass(uuconst.REGRESSIONTEST_DIR_BASENAMES[1])

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
            self.assertTrue(uu.dir_exists(d))

    def test_returns_absolute_paths(self):
        for d in self.actual:
            self.assertTrue(uu.is_abspath(d))

    def test_returns_bytestring_paths(self):
        for d in self.actual:
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

    def test_input_paths_are_replaced(self):
        input_options = {
            'verbose': True,
            'input_paths': ['$TESTFILES/gmail.pdf'],
            'mode_batch': True,
            'mode_interactive': False,
            'dry_run': True,
            'recurse_paths': False,
        }
        expected = {
            'verbose': True,
            'input_paths': [uu.abspath_testfile('gmail.pdf')],
            'mode_batch': True,
            'mode_interactive': False,
            'dry_run': True,
            'recurse_paths': False,
        }
        actual = RegressionTestLoader._set_testfile_path(input_options)
        self.assertEqual(actual, expected)


class TestRegressionTestLoaderSetConfigPath(TestCase):
    # def test_options_without_input_paths_is_passed_through_as_is(self):
    #     input_options = {
    #         'verbose': True,
    #         'mode_batch': True,
    #         'mode_interactive': False,
    #         'dry_run': True,
    #         'recurse_paths': False,
    #     }
    #
    #     actual = RegressionTestLoader._set_testfile_path(input_options)
    #     self.assertEqual(actual, input_options)

    def test_replaces_config_path(self):
        input_options = {
            'verbose': True,
            'config_path': '$TESTFILES/default_config.yaml',
            'mode_batch': True,
            'mode_interactive': False,
            'dry_run': True,
            'recurse_paths': False,
        }
        expected = {
            'verbose': True,
            'config_path': uu.normpath(
                uu.abspath_testfile('default_config.yaml')
            ),
            'mode_batch': True,
            'mode_interactive': False,
            'dry_run': True,
            'recurse_paths': False,
        }
        actual = RegressionTestLoader._set_config_path(input_options)
        self.assertEqual(actual, expected)


class TestRegressionTestLoaderWithFirstRegressionTest(TestCase):
    def setUp(self):
        _regressiontest_dir = regtest_abspath(
            uuconst.REGRESSIONTEST_DIR_BASENAMES[0]
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
            self.assertIn(_option, actual)

        # Direct comparison won't work because "input_paths" should differ.
        for _option, _value in expected_options.items():
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
