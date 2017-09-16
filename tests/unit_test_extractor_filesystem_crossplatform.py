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

from datetime import datetime
from unittest import TestCase

from extractors.filesystem import crossplatform
import unit_utils as uu


class TestDatetimeFromTimestamp(TestCase):
    def test_returns_expected_type(self):
        actual = crossplatform.datetime_from_timestamp(1505579505.0)
        self.assertTrue(isinstance(actual, datetime))

    def test_returns_expected_datetime(self):
        actual = crossplatform.datetime_from_timestamp(1505579505.0)
        expected = uu.str_to_datetime('2017-09-16 183145')
        self.assertEqual(actual, expected)
