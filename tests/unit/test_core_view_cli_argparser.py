# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from core.view.cli import get_argparser


class TestGetArgparser(TestCase):
    def test_returns_something_given_no_arguments(self):
        actual = get_argparser()
        self.assertIsNotNone(actual)

    def test_returns_expected_type_given_no_arguments(self):
        import argparse
        actual = get_argparser()
        self.assertIsInstance(actual, argparse.ArgumentParser)

    def test_returns_something_given_valid_arguments(self):
        actual = get_argparser(description='foo', epilog='bar')
        self.assertIsNotNone(actual)

    def test_returns_expected_type_given_valid_arguments(self):
        import argparse
        actual = get_argparser(description='foo', epilog='bar')
        self.assertIsInstance(actual, argparse.ArgumentParser)
