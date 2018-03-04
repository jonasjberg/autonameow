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
from unittest.mock import (
    Mock,
    patch
)

from core.logs import (
    deinit_logging,
    init_logging,
    log_previously_logged_runtimes,
    log_func_runtime,
    log_runtime,
)


mock__decorate_log_entry_section = Mock(side_effect=lambda x: x)


class TestLogRunTime(TestCase):
    def setUp(self):
        self.mock_logger = Mock()
        self.LOGLEVEL_DEFAULT = 10
        self.LOGLEVEL_INFO = 20

    def test_logger_called_at_enter_and_exit(self):
        with log_runtime(self.mock_logger, 'Foo'):
            pass

        self.assertEqual(self.mock_logger.log.call_count, 2)

    def test_logger_called_at_enter_and_exit_with_specific_log_level(self):
        with log_runtime(self.mock_logger, 'Foo', log_level='INFO'):
            pass

        self.assertEqual(self.mock_logger.log.call_count, 2)

    @patch('time.time')
    @patch('core.logs._decorate_log_entry_section', mock__decorate_log_entry_section)
    def test_logged_messages(self, mock_time):
        mock_time.side_effect = [0, 0]

        with log_runtime(self.mock_logger, 'Foo'):
            pass

            self.mock_logger.log.assert_called_with(
                self.LOGLEVEL_DEFAULT, 'Foo Started'
            )
        self.mock_logger.log.assert_called_with(
            self.LOGLEVEL_DEFAULT, 'Foo Completed in 0.000000000 seconds'
        )

    @patch('time.time')
    @patch('core.logs._decorate_log_entry_section', mock__decorate_log_entry_section)
    def test_logged_messages_with_specific_log_level(self, mock_time):
        mock_time.side_effect = [0, 0]

        with log_runtime(self.mock_logger, 'Foo', log_level='INFO'):
            pass

            self.mock_logger.log.assert_called_with(
                self.LOGLEVEL_INFO, 'Foo Started'
            )
        self.mock_logger.log.assert_called_with(
            self.LOGLEVEL_INFO, 'Foo Completed in 0.000000000 seconds'
        )

    @patch('time.time')
    @patch('core.logs._decorate_log_entry_section', mock__decorate_log_entry_section)
    def test_timing_measurement(self, mock_time):
        mock_time.side_effect = [1511626070.045472, 1511626071.045472]
        with log_runtime(self.mock_logger, 'Foo'):
            pass

        self.mock_logger.log.assert_called_with(
            self.LOGLEVEL_DEFAULT, 'Foo Completed in 1.000000000 seconds'
        )


class TestLogFuncRuntime(TestCase):
    def setUp(self):
        self.mock_logger = Mock()

    def test_assume_running_with___debug__(self):
        # The function under test is a no-op when running in optimized mode,
        # I.E. when __debug__ == False
        self.assertTrue(__debug__)

    def test_logger_called_at_exit(self):
        @log_func_runtime(self.mock_logger)
        def dummy_func():
            pass

        dummy_func()
        self.assertEqual(self.mock_logger.debug.call_count, 1)

    def test_logged_messages(self):
        @log_func_runtime(self.mock_logger)
        def dummy_func():
            pass

        dummy_func()
        self.assertIn('dummy_func Completed',
                      self.mock_logger.debug.call_args[0][0])

    @patch('time.time')
    def test_timing_measurement(self, mock_time):
        mock_time.side_effect = [1511626070.045472, 1511626071.045472]

        @log_func_runtime(self.mock_logger)
        def dummy_func():
            pass

        dummy_func()

        self.assertIn('dummy_func Completed in 1.000000000 seconds',
                      self.mock_logger.debug.call_args[0][0])


class TestLogAllLoggedRuntimes(TestCase):
    @classmethod
    def setUpClass(cls):
        # TODO: [cleanup] Do not use global to store logged run-times
        deinit_logging()

    def setUp(self):
        opts = dict()
        init_logging(opts)
        self.mock_logger = Mock()

    def tearDown(self):
        deinit_logging()

    def test_nothing_is_logged_when_no_runtimes_have_been_logged(self):
        log_previously_logged_runtimes(self.mock_logger)
        self.assertEqual(self.mock_logger.debug.call_count, 0)

    def test_calls_debug_with_one_logged_runtime(self):
        mock_runtime_logger = Mock()
        with log_runtime(mock_runtime_logger, 'Foo'):
            pass
        log_previously_logged_runtimes(self.mock_logger)
        self.assertEqual(self.mock_logger.debug.call_count, 1)


class TestInitLogging(TestCase):
    def tearDown(self):
        deinit_logging()

    def test_init_logging_empty_opts(self):
        opts = dict()
        init_logging(opts)

    def test_init_logging_debug(self):
        opts = {'debug': True}
        init_logging(opts)

    def test_init_logging_verbose(self):
        opts = {'verbose': True}
        init_logging(opts)

    def test_init_logging_quiet(self):
        opts = {'quiet': True}
        init_logging(opts)
