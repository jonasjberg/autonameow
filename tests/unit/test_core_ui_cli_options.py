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

import argparse
from unittest import TestCase

import unit.utils as uu
from core.ui.cli.options import (
    arg_is_year,
    arg_is_readable_file,
    init_argparser,
    cli_parse_args
)


class TestArgumentValidators(TestCase):
    def test_arg_is_year_raises_exception(self):
        invalid_years = ['abc', '00', '', '19 00', ' ', None, '¡@$!']
        for y in invalid_years:
            with self.assertRaises(argparse.ArgumentTypeError) as e:
                arg_is_year(y)
            self.assertIsNotNone(e)

    def test_arg_is_year_passes_valid_years(self):
        valid_years = ['1000', '1970', '2017', '9999']
        for y in valid_years:
            self.assertTrue(arg_is_year(y))

    def test_arg_is_readable_file_raises_exception_missing_file(self):
        _file_missing = '/tmp/nopenopenopenope_no-file-here_nono'
        self.assertFalse(uu.file_exists(_file_missing))

        with self.assertRaises(argparse.ArgumentTypeError) as e:
            arg_is_readable_file(_file_missing)
        self.assertIsNotNone(e)

    def test_arg_is_readable_file_raises_exception_arg_is_dev_null(self):
        with self.assertRaises(argparse.ArgumentTypeError) as e:
            arg_is_readable_file('/dev/null')
        self.assertIsNotNone(e)

    def test_arg_is_readable_file_raises_exception_none_argument(self):
        with self.assertRaises(argparse.ArgumentTypeError) as e:
            arg_is_readable_file(None)
        self.assertIsNotNone(e)

    def test_arg_is_readable_file_raises_exception_empty_string_arg(self):
        with self.assertRaises(argparse.ArgumentTypeError) as e:
            arg_is_readable_file('')
        self.assertIsNotNone(e)

    def test_arg_is_readable_file_raises_exception_arg_is_directory(self):
        with self.assertRaises(argparse.ArgumentTypeError) as e:
            arg_is_readable_file('/tmp')
        self.assertIsNotNone(e)


class TestArgParse(TestCase):
    def test_init_argparser(self):
        self.assertIsInstance(init_argparser(), argparse.ArgumentParser)

    def test_parse_args_returns_expected_type(self):
        self.assertEqual(type(cli_parse_args('')), argparse.Namespace)
        self.assertEqual(type(cli_parse_args('--help')), argparse.Namespace)

    def test_parse_args_raises_typeerror_if_argument_missing(self):
        with self.assertRaises(TypeError):
            cli_parse_args()

    def test_parse_args_accepts_argument_help(self):
        self.assertIsNotNone(cli_parse_args('--help'))

    def test_parse_args_accepts_argument_dry_run(self):
        self.assertIsNotNone(cli_parse_args('--dry-run'))

    def test_parse_args_accepts_argument_verbose(self):
        self.assertIsNotNone(cli_parse_args('--verbose'))

    def test_parse_args_accepts_argument_debug(self):
        self.assertIsNotNone(cli_parse_args('--debug'))
