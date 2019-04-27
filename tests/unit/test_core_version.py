# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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


class TestTechniqueForAccessingAttributesWithoutImporting(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.version_filepath = os.path.realpath(
            os.path.join(uuconst.PATH_AUTONAMEOW_SRCROOT, 'core', 'version.py')
        )

    def test_version_file_exists(self):
        self.assertTrue(os.path.isfile(self.version_filepath))

    def test_can_access_attributes_by_executing_the_file(self):
        # Simulates technique used in 'setup.py' for loading attributes without
        # imports.  Based on the "Python Packaging User Guide" at:
        # https://packaging.python.org/guides/single-sourcing-package-version/#single-sourcing-the-version
        projectmeta = dict()
        with open(self.version_filepath) as fp:
            exec(fp.read(), projectmeta)

        for key in [
            '__copyright__',
            '__email__',
            '__license__',
            '__title__',
            '__version__',
            '__version_info__',
            '__url__',
            '__url_repo__',
         ]:
            self.assertIn(key, projectmeta)
            self.assertIsNotNone(projectmeta[key])
