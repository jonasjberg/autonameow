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
from unittest.mock import Mock, patch

from core.logs import log_runtime


class TestLogRunTime(TestCase):
    def setUp(self):
        self.mock_logger = Mock()

    def test_logger_called_at_enter_and_exit(self):
        with log_runtime(self.mock_logger, 'Foo'):
            pass
        self.mock_logger.debug.assert_called()
        self.assertEqual(self.mock_logger.debug.call_count, 2)

    def test_logged_messages(self):
        with log_runtime(self.mock_logger, 'Foo'):
            self.assertIn('Foo Started', self.mock_logger.debug.call_args[0][0])
            pass
        self.assertIn('Foo Completed', self.mock_logger.debug.call_args[0][0])

    @patch('time.time')
    def test_timing_measurement(self, mock_time):
        mock_time.side_effect = [1511626070.045472, 1511626071.045472]
        with log_runtime(self.mock_logger, 'Foo'):
            pass
        self.assertIn('1.000000000', self.mock_logger.debug.call_args[0][0])
