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
    get_regressiontests_rootdir,
    RegressionTestInfo,
    regtest_abspath
)
import unit_utils as uu
import unit_utils_constants as uuconst


class TestRegressionTestUtilityFunctions(TestCase):
    def test_get_regressiontests_rootdir(self):
        actual = get_regressiontests_rootdir()
        self.assertTrue(uu.dir_exists(actual))
        self.assertTrue(uu.is_abspath(actual))
        self.assertTrue(uu.is_internalbytestring(actual))

    def test_regtest_abspath_given_valid_argument(self):
        def _ok(test_input):
            _actual = regtest_abspath(test_input)
            self.assertTrue(uu.dir_exists(_actual))
            self.assertTrue(uu.is_abspath(_actual))
            self.assertTrue(uu.is_internalbytestring(_actual))

        _ok(b'0001')
        _ok(b'0002_test')
        _ok(uuconst.REGRESSIONTEST_DIR_BASENAMES[0])
        _ok(uuconst.REGRESSIONTEST_DIR_BASENAMES[1])

    def test_regtest_abspath_given_valid_argument(self):
        def _f(test_input):
            with self.assertRaises(AssertionError):
                _ = regtest_abspath(test_input)

        _f(None)
        _f('0001')
        _f('0002_test')
        _f('1337_this_directory_should_not_exist')
        _f(b'1337_this_directory_should_not_exist')


# class TestRegressionTestInfo(TestCase):
#     def test_frompath(self):
#         _regressiontest_dir = regtest_abspath(
#             uuconst.REGRESSIONTEST_DIR_BASENAMES[0]
#         )
#         actual = RegressionTestInfo.frompath(_regressiontest_dir)
#
#         self.assertEqual(
#             actual.args,
#             ['--automagic', '--batch']
#         )
#         self.assertEqual(
#             actual.desc,
#             'Good old "test_files/gmail.pdf" integration test ..'
#         )
#         self.assertEqual(
#             actual.expect,
#             '2016-01-11T124132 gmail.pdf'
#         )
#         self.assertEqual(
#             actual.testfiles,
#             [uu.abspath_testfile('gmail.pdf')]
#         )
