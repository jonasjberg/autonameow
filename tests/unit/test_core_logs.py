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
    center_pad,
    deinit_logging,
    init_logging,
    log_func_runtime,
    log_previously_logged_runtimes,
    log_runtime,
    report_runtime,
)


mock_center_pad_log_entry = Mock(side_effect=lambda x: x)


class TestCenterPad(TestCase):
    def test_centers_four_character_string_with_width_ten(self):
        actual = center_pad('MEOW', maxwidth=10, fillchar=' ')
        self.assertEqual(10, len(actual))
        self.assertEqual('   MEOW   ', actual)

    def test_centers_four_character_string_with_width_six(self):
        actual = center_pad('meow', maxwidth=6, fillchar='=')
        self.assertEqual(6, len(actual))
        self.assertEqual(' meow ', actual)

    def test_centers_two_character_string_with_width_two(self):
        actual = center_pad('xx', maxwidth=2, fillchar='=')
        self.assertEqual(2, len(actual))
        self.assertEqual('xx', actual)

    def test_centers_four_character_string_with_zero_width(self):
        actual = center_pad('meow', maxwidth=0, fillchar='=')
        self.assertEqual(4, len(actual))
        self.assertEqual('meow', actual)

    def test_centers_two_character_string_with_zero_width(self):
        actual = center_pad('xx', maxwidth=0, fillchar='=')
        self.assertEqual(2, len(actual))
        self.assertEqual('xx', actual)

    def test_centers_four_character_string_with_negative_width(self):
        actual = center_pad('meow', maxwidth=-2, fillchar='=')
        self.assertEqual(4, len(actual))
        self.assertEqual('meow', actual)

    def test_centers_two_character_string_with_negative_width(self):
        actual = center_pad('xx', maxwidth=-2, fillchar='=')
        self.assertEqual(2, len(actual))
        self.assertEqual('xx', actual)

    def _assert_that_it_returns(self, expected, given_string, **kwargs):
        actual = center_pad(given_string, **kwargs)
        self.assertEqual(expected, actual)
        if 'maxwidth' in kwargs:
            # Expect length of returned string to either be unchanged
            # it it exceeds 'maxwidth' and otherwise at most 'maxwidth'.
            expected_len = max(kwargs['maxwidth'], len(given_string))
            self.assertEqual(expected_len, len(actual))

    def test_two_char_string_is_padded_if_its_length_is_less_than_width(self):
        for width, expected in [
            (10, '=== no ==='),
            (9, '=== no =='),
            (8, '== no =='),
            (7, '== no ='),
            (6, '= no ='),
            (5, '= no '),
            (4, ' no '),
            (3, ' no'),
            (2, 'no'),
            (1, 'no'),
        ]:
            with self.subTest(given_width=width):
                self._assert_that_it_returns(expected, given_string='no',
                                             maxwidth=width, fillchar='=')

    def test_ten_char_string_is_returned_as_is_for_widths_one_to_ten(self):
        expected = 'abcdefghij'
        for width in range(1, 10):
            self._assert_that_it_returns(expected, given_string='abcdefghij',
                                         maxwidth=width, fillchar='=')

    def test_ten_char_string_is_padded_for_widths_eleven_to_twenty(self):
        for width, expected in [
            (11, ' abcdefghij'),
            (12, ' abcdefghij '),
            (13, '= abcdefghij '),
            (14, '= abcdefghij ='),
            (15, '== abcdefghij ='),
            (16, '== abcdefghij =='),
            (17, '=== abcdefghij =='),
            (18, '=== abcdefghij ==='),
            (19, '==== abcdefghij ==='),
            (20, '==== abcdefghij ===='),
        ]:
            with self.subTest(given_width=width):
                self._assert_that_it_returns(expected, given_string='abcdefghij',
                                             maxwidth=width, fillchar='=')


def mock_center_pad(message, **kwargs):
    return message


class TestReportRuntime(TestCase):
    @patch('time.time')
    @patch('core.logs.center_pad', Mock(side_effect=mock_center_pad))
    def test_reporter_function_is_called_at_enter_and_exit(self, mock_time):
        mock_time.side_effect = [0, 0]
        mock_reporter = Mock()
        with report_runtime(mock_reporter, 'Foo'):
            mock_reporter.assert_called_with('Foo Started')

        mock_reporter.assert_called_with('Foo Completed in 0.000000000 seconds')

    @patch('time.time')
    def test_reporter_function_gets_decorated_str_by_default(self, mock_time):
        mock_time.side_effect = [0, 0]
        mock_reporter = Mock()
        with report_runtime(mock_reporter, 'Foo'):
            mock_reporter.assert_called_with('================================= Foo Started ==================================')

        mock_reporter.assert_called_with('===================== Foo Completed in 0.000000000 seconds =====================')

    @patch('time.time')
    def test_reporter_function_gets_undecorated_string(self, mock_time):
        mock_time.side_effect = [0, 0]
        mock_reporter = Mock()
        with report_runtime(mock_reporter, 'Foo', decorate=False):
            mock_reporter.assert_called_with('Foo Started')

        mock_reporter.assert_called_with('Foo Completed in 0.000000000 seconds')


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
    @patch('core.logs.center_pad_log_entry', mock_center_pad_log_entry)
    def test_logged_messages(self, mock_time):
        mock_time.side_effect = [0, 0]

        with log_runtime(self.mock_logger, 'Foo'):
            self.mock_logger.log.assert_called_with(
                self.LOGLEVEL_DEFAULT, 'Foo Started'
            )
        self.mock_logger.log.assert_called_with(
            self.LOGLEVEL_DEFAULT, 'Foo Completed in 0.000000000 seconds'
        )

    @patch('time.time')
    @patch('core.logs.center_pad_log_entry', mock_center_pad_log_entry)
    def test_logged_messages_with_specific_log_level(self, mock_time):
        mock_time.side_effect = [0, 0]

        with log_runtime(self.mock_logger, 'Foo', log_level='INFO'):
            self.mock_logger.log.assert_called_with(
                self.LOGLEVEL_INFO, 'Foo Started'
            )
        self.mock_logger.log.assert_called_with(
            self.LOGLEVEL_INFO, 'Foo Completed in 0.000000000 seconds'
        )

    @patch('time.time')
    @patch('core.logs.center_pad_log_entry', mock_center_pad_log_entry)
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
