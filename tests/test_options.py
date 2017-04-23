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

import argparse
from unittest import TestCase

from core import options


class TestArgumentValidators(TestCase):
    def test_arg_is_year_raises_exception(self):
        invalid_years = ['abc', '00', '', '19 00', ' ', None, '¡@$!']
        for y in invalid_years:
            with self.assertRaises(argparse.ArgumentTypeError) as e:
                options.arg_is_year(y)
            self.assertIsNotNone(e)
            # self.assertIn('"{}" is not a valid year'.format(y), e.exception)
