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
import os
from unittest import TestCase

from core import options


class TestArgumentValidators(TestCase):
    def test_arg_is_year_raises_exception(self):
        invalid_years = ['abc', '00', '', '19 00', ' ', None, '¡@$!']
        for y in invalid_years:
            with self.assertRaises(argparse.ArgumentTypeError) as e:
                options.arg_is_year(y)
            self.assertIsNotNone(e)

    def test_arg_is_year_passes_valid_years(self):
        valid_years = ['1000', '1970', '2017', '9999']
        for y in valid_years:
            self.assertTrue(options.arg_is_year(y))

    def test_arg_is_readable_file_raises_exception_missing_file(self):
        _file_missing = '/tmp/nopenopenopenope_no-file-here_nono'
        self.assertFalse(os.path.exists(_file_missing))
        self.assertFalse(os.path.isfile(_file_missing))

        with self.assertRaises(argparse.ArgumentTypeError) as e:
            options.arg_is_readable_file(_file_missing)
        self.assertIsNotNone(e)

    def test_arg_is_readable_file_raises_exception_arg_is_dev_null(self):
        with self.assertRaises(argparse.ArgumentTypeError) as e:
            options.arg_is_readable_file('/dev/null')
        self.assertIsNotNone(e)

    def test_arg_is_readable_file_raises_exception_none_argument(self):
        with self.assertRaises(argparse.ArgumentTypeError) as e:
            options.arg_is_readable_file(None)
        self.assertIsNotNone(e)

    def test_arg_is_readable_file_raises_exception_empty_string_arg(self):
        with self.assertRaises(argparse.ArgumentTypeError) as e:
            options.arg_is_readable_file('')
        self.assertIsNotNone(e)

    def test_arg_is_readable_file_raises_exception_arg_is_directory(self):
        with self.assertRaises(argparse.ArgumentTypeError) as e:
            options.arg_is_readable_file('/tmp')
        self.assertIsNotNone(e)
