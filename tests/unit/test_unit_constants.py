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

import os
from unittest import TestCase

import unit.constants as uuconst
import unit.utils as uu


class TestJoinPathFromSrcroot(TestCase):
    def test_returns_absolute_path_from_unicode_string(self):
        actual = uuconst.join_path_from_srcroot('autonameow')
        self.assertTrue(os.path.isabs(actual))

    def test_returns_absolute_path_from_two_unicode_strings(self):
        actual = uuconst.join_path_from_srcroot('autonameow', 'core')
        self.assertTrue(os.path.isabs(actual))


class TestUnitUtilityConstants(TestCase):
    def _check_directory_path(self, given_path):
        self.assertIsNotNone(given_path)
        self.assertTrue(os.path.exists(given_path))
        self.assertTrue(os.path.isdir(given_path))
        self.assertTrue(os.access(given_path, os.R_OK))
        self.assertTrue(os.access(given_path, os.X_OK))

    def test_constant_path_samplefiles(self):
        self._check_directory_path(uuconst.DIRPATH_SAMPLEFILES)

    def test_constant_path_autonameow_srcroot(self):
        self._check_directory_path(uuconst.DIRPATH_AUTONAMEOW_SRCROOT)

    def test_constant_path_tests_regression(self):
        self._check_directory_path(uuconst.DIRPATH_TESTS_REGRESSION)

    def test_constant_path_tests_unit(self):
        self._check_directory_path(uuconst.DIRPATH_TESTS_UNIT)

    def test_constant_path_user_home(self):
        self._check_directory_path(uuconst.DIRPATH_USER_HOME)


class TestConstantAllFullMeowURIs(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.tested_constant = uuconst.ALL_FULL_MEOWURIS

    def test_is_not_none(self):
        self.assertIsNotNone(self.tested_constant)

    def test_is_container_type(self):
        try:
            _ = iter(self.tested_constant)
        except TypeError:
            self.fail('Expected container type. Failed test of iteration '
                      'protocol support.')

    def test_does_not_contain_none(self):
        self.assertNotIn(None, self.tested_constant)

    def test_is_immutable(self):
        with self.assertRaises(TypeError):
            _ = self.tested_constant[0]

        with self.assertRaises(AttributeError):
            _ = self.tested_constant.add(0)
            _ = self.tested_constant.append(0)
            _ = self.tested_constant.pop(0)
            _ = self.tested_constant.remove(0)

    def test_contains_all_unit_test_meowuri_constants(self):
        constant_variable_names = [
            c for c in dir(uuconst)
            if isinstance(c, str) and c.isupper() and c.startswith('MEOWURI_')
        ]
        self.assertGreater(len(constant_variable_names), 0,
                           'Unable to get variable names of actual constants.')

        actual_constants = [
            getattr(uuconst, n) for n in constant_variable_names
        ]
        self.assertGreater(len(actual_constants), 0,
                           'Unable to get the actual constants.')

        for actual_constant in actual_constants:
            self.assertIn(actual_constant, self.tested_constant)


class TestFileConstants(TestCase):
    def test_assumed_non_existent_basename(self):
        self.assertIsNotNone(uuconst.ASSUMED_NONEXISTENT_BASENAME)
        self.assertFalse(uu.file_exists(uuconst.ASSUMED_NONEXISTENT_BASENAME))


class TestConstantBuiltinRegexType(TestCase):
    def test_has_expected_type(self):
        import re
        compiled_regex = re.compile('foo')
        self.assertEqual(uuconst.BUILTIN_REGEX_TYPE, type(compiled_regex))
