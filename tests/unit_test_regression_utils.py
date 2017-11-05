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


# TODO: [TD0117] Implement automated regression tests
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
