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

import unit.constants as uuconst
import unit.utils as uu


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
