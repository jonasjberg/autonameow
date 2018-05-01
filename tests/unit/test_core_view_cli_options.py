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

import unit.constants as uuconst
from core.view.cli.options import arg_is_readable_file
from core.view.cli.options import cli_parse_args
from core.view.cli.options import init_argparser


class TestArgumentValidatorIsReadableFile(TestCase):
    def test_raises_exception_given_none_argument(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            arg_is_readable_file(None)

    def test_raises_exception_given_non_existent_file(self):
        missing_file = uuconst.ASSUMED_NONEXISTENT_BASENAME
        with self.assertRaises(argparse.ArgumentTypeError):
            arg_is_readable_file(missing_file)

    def test_raises_exception_given_dev_null(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            arg_is_readable_file('/dev/null')

    def test_raises_exception_given_empty_string_arg(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            arg_is_readable_file('')

    def test_raises_exception_given_directory(self):
        with self.assertRaises(argparse.ArgumentTypeError):
            arg_is_readable_file('/tmp')


class TestArgParse(TestCase):
    def test_init_argparser(self):
        self.assertIsInstance(init_argparser(), argparse.ArgumentParser)

    def test_parsing_empty_string_arg_returns_expected_type(self):
        self.assertIsInstance(cli_parse_args(''), argparse.Namespace)

    def test_raises_typeerror_if_not_given_any_arguments_at_all(self):
        with self.assertRaises(TypeError):
            _ = cli_parse_args()

    def _assert_valid_argument(self, given):
        given_argument_list = [given]
        opts = cli_parse_args(given_argument_list)
        self.assertIsInstance(opts, argparse.Namespace)
        self.assertEqual(0, len(opts.input_paths),
                         'Argument mistaken for positional argument')

    def test_cli_parse_args_accepts_argument_dry_run(self):
        self._assert_valid_argument('--dry-run')
        self._assert_valid_argument('-d')

    def test_cli_parse_args_accepts_argument_help(self):
        with self.assertRaises(SystemExit):
            self._assert_valid_argument('--help')

    def test_cli_parse_args_accepts_argument_debug(self):
        self._assert_valid_argument('--debug')

    def test_cli_parse_args_accepts_argument_verbose(self):
        self._assert_valid_argument('-v')
        self._assert_valid_argument('--verbose')

    def test_cli_parse_args_accepts_argument_quiet(self):
        self._assert_valid_argument('--quiet')
        self._assert_valid_argument('-q')

    def test_cli_parse_args_accepts_argument_list_all(self):
        self._assert_valid_argument('--list-all')

    def test_cli_parse_args_accepts_argument_list_rulematch(self):
        self._assert_valid_argument('--list-rulematch')

    def test_cli_parse_args_accepts_argument_automagic(self):
        self._assert_valid_argument('--automagic')

    def test_cli_parse_args_accepts_argument_timid(self):
        self._assert_valid_argument('--timid')

    def test_cli_parse_args_accepts_argument_interactive(self):
        self._assert_valid_argument('--interactive')

    def test_cli_parse_args_accepts_argument_batch(self):
        self._assert_valid_argument('--batch')

    def test_cli_parse_args_accepts_argument_version(self):
        self._assert_valid_argument('--version')

    def test_cli_parse_args_accepts_argument_recurse(self):
        self._assert_valid_argument('--recurse')
        self._assert_valid_argument('--r')

    def test_cli_parse_args_accepts_argument_dump_options(self):
        self._assert_valid_argument('--dump-options')

    def test_cli_parse_args_accepts_argument_dump_config(self):
        self._assert_valid_argument('--dump-config')

    def test_cli_parse_args_accepts_argument_dump_meowuris(self):
        self._assert_valid_argument('--dump-meowuris')
