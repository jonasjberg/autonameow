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

from core.exceptions import DependencyError
from core.exceptions import ignored


class TestIgnored(TestCase):
    def setUp(self):
        self.original_value = 'original value'
        self.modified_value = 'modified value'

    def test_code_before_ignored_exception_is_executed(self):
        a = 'original_value'

        with ignored(ValueError):
            a = self.modified_value
            _ = int('x')

        self.assertEqual(self.modified_value, a)

    def test_code_after_ignored_exception_is_not_executed(self):
        a = self.original_value

        with ignored(ValueError):
            _ = int('x')
            a = self.modified_value

        self.assertEqual(self.original_value, a)

    def test_only_one_specified_exception_are_ignored(self):
        with ignored(TypeError):
            _ = float([])

        with self.assertRaises(ValueError):
            with ignored(TypeError):
                _ = int('x')

    def test_all_of_the_specified_exceptions_are_ignored(self):
        with ignored(TypeError, ValueError):
            _ = float([])
            _ = int('x')

        with self.assertRaises(ZeroDivisionError):
            with ignored(TypeError, ValueError):
                _ = 1 / 0


def _raise_and_capture_dependency_error(*args, **kwargs):
    try:
        raise DependencyError(*args, **kwargs)
    except DependencyError as e:
        return e


class TestDependencyError(TestCase):
    def test_exception_without_any_additional_arguments(self):
        e = _raise_and_capture_dependency_error()
        self.assertIsNotNone(e)

    def test_string_contains_unspecified_missing_module(self):
        e = _raise_and_capture_dependency_error()
        self.assertEqual('Missing required module(s): (unspecified)', str(e))

    def test_string_contains_one_missing_module_as_str(self):
        e = _raise_and_capture_dependency_error(missing_modules='foo')
        self.assertEqual('Missing required module(s): "foo"', str(e))

    def test_string_contains_one_missing_module_as_list_of_str(self):
        e = _raise_and_capture_dependency_error(missing_modules=['foo'])
        self.assertEqual('Missing required module(s): "foo"', str(e))

    def test_string_contains_multiple_missing_modules(self):
        e = _raise_and_capture_dependency_error(missing_modules=['foo', 'bar', 'baz'])
        self.assertEqual('Missing required module(s): "bar" "baz" "foo"', str(e))
