# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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
from unittest.mock import Mock

from regression.regression_runner import RunResults


class TestRunResults(TestCase):
    def _get_mock_test_suite(self):
        return Mock()

    def test_len_of_all_is_the_number_of_all_stored_test_suites(self):
        def _assert_all_count(expect, _run_results):
            self.assertEqual(expect, len(_run_results.all))
            self.assertEqual(expect, len(_run_results))

        mock_test_suite_failed_A = self._get_mock_test_suite()
        mock_test_suite_failed_B = self._get_mock_test_suite()
        mock_test_suite_passed = self._get_mock_test_suite()

        run_results = RunResults()
        _assert_all_count(0, run_results)

        run_results.failed.add(mock_test_suite_failed_A)
        _assert_all_count(1, run_results)

        run_results.failed.add(mock_test_suite_failed_B)
        _assert_all_count(2, run_results)
        run_results.failed.add(mock_test_suite_failed_B)
        _assert_all_count(2, run_results)

        run_results.passed.add(mock_test_suite_passed)
        _assert_all_count(3, run_results)

    def test_all_returns_union_of_all_stored_test_suites(self):
        run_results = RunResults()
        self.assertFalse(run_results.all)

        mock_test_suite_failed = self._get_mock_test_suite()
        mock_test_suite_passed = self._get_mock_test_suite()
        mock_test_suite_skipped = self._get_mock_test_suite()
        run_results.failed.add(mock_test_suite_failed)
        run_results.passed.add(mock_test_suite_passed)
        run_results.skipped.add(mock_test_suite_skipped)

        for test_suite in [
            mock_test_suite_failed,
            mock_test_suite_passed,
            mock_test_suite_skipped
        ]:
            self.assertIn(test_suite, run_results.all)

        # Make sure nothing has been unintentionally mutated.
        self.assertNotIn(mock_test_suite_failed, run_results.passed)
        self.assertNotIn(mock_test_suite_failed, run_results.skipped)
        self.assertNotIn(mock_test_suite_passed, run_results.failed)
        self.assertNotIn(mock_test_suite_passed, run_results.skipped)
        self.assertNotIn(mock_test_suite_skipped, run_results.failed)
        self.assertNotIn(mock_test_suite_skipped, run_results.passed)
