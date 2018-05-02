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

from core.exceptions import DependencyError


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
