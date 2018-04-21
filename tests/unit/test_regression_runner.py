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
from unittest.mock import patch

import unit.utils as uu
from regression.regression_runner import (
    _get_persistence,
    load_failed_testsuites,
    write_failed_testsuites,
)
from regression.utils import RegressionTestSuite


class TestLoadAndWriteFailedTestsuites(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.TEMP_DIR = uu.make_temp_dir()

    def _mock_get_persistence(self):
        return _get_persistence(file_prefix='test_regression_runner',
                                persistence_dir_abspath=self.TEMP_DIR)

    def test_write_failed_testsuites_empty_list(self):
        suites = list()
        with patch('regression.regression_runner._get_persistence',
                   self._mock_get_persistence):
            write_failed_testsuites(suites)

    def test_write_and_read_with_two_actual_suites(self):
        a = RegressionTestSuite(
            abspath=b'/tmp/bar',
            dirname=b'bar',
            asserts=None,
            options=None,
            skip=False,
            description='bar'
        )
        b = RegressionTestSuite(
            abspath=b'/tmp/foo',
            dirname=b'foo',
            asserts=None,
            options=None,
            skip=False,
            description='foo'
        )
        suites = [a, b]
        with patch('regression.regression_runner._get_persistence',
                   self._mock_get_persistence):
            write_failed_testsuites(suites)
            loaded = load_failed_testsuites()

        self.assertEqual(len(loaded), len(suites))
        self.assertEqual(sorted(loaded), sorted(suites))
