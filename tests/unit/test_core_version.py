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

import unit.utils as uu
from core import version


class TestVersionModuleAttributes(TestCase):
    def _is_defined_type(self, type_, test_input):
        self.assertIsNotNone(test_input)
        self.assertIsInstance(test_input, type_)

    def _is_defined_internal_string(self, test_input):
        self.assertIsNotNone(test_input)
        self.assertTrue(uu.is_internalstring(test_input))
        self.assertNotEqual('', test_input.strip(),
                            'Expected non-empty and not all whitespace string')

    def test___title__(self):
        self._is_defined_internal_string(version.__title__)

    def test___version__(self):
        self._is_defined_internal_string(version.__version__)

    def test___version_info__(self):
        self._is_defined_type(tuple, version.__version_info__)
        for item in version.__version_info__:
            self._is_defined_type(int, item)

        # Expect semantic versioning: 0.1.2
        self.assertEqual(3, len(version.__version_info__))

    def test___author__(self):
        self._is_defined_internal_string(version.__author__)

    def test___email__(self):
        self._is_defined_internal_string(version.__email__)

    def test___url__(self):
        self._is_defined_internal_string(version.__url__)

    def test___url_repo__(self):
        self._is_defined_internal_string(version.__url_repo__)

    def test___license__(self):
        self._is_defined_internal_string(version.__license__)

    def test___copyright__(self):
        self._is_defined_internal_string(version.__copyright__)

    def test_RELEASE_DATE(self):
        # TODO: [TD0145] Add script for automating release of a new version.
        self._is_defined_internal_string(version.RELEASE_DATE)
