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
    RegressionTestInfo,
    regtest_abspath,
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
        _pass(b'0002_test')
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


class TestRegressionTestInfoFromPath(TestCase):
    def test_description(self):
        _regressiontest_dir = regtest_abspath(
            uuconst.REGRESSIONTEST_DIR_BASENAMES[0]
        )
        actual = RegressionTestInfo.frompath(_regressiontest_dir)
        self.assertEqual(
            actual.description,
            'Good old "test_files/gmail.pdf" integration test ..'
        )
