#!/usr/bin/env python3
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

import os
from unittest import TestCase
from unittest.mock import (
    MagicMock,
    patch
)

import unit.utils as uu
from core.config import (
    CONFIG_BASENAME,
    config_dirs,
    config_file_path,
    load_config_from_file
)


class TestConfigDirs(TestCase):
    def _assert_unicode_encoding(self, path_list):
        for path in path_list:
            self.assertTrue(uu.is_internalstring(path))

    def test_config_dirs_on_mac(self):
        with patch('platform.system', MagicMock(return_value='Darwin')):
            dirs = config_dirs()

            self.assertIsNotNone(dirs)
            self._assert_unicode_encoding(dirs)
            self.assertIn(os.path.expanduser('~/.config'), dirs)
            self.assertIn(os.path.expanduser('~/Library/Application Support'), dirs)

    def test_config_dirs_on_windows(self):
        self.skipTest('TODO: Mock expanding "~" to "C:/Users/whatever"')
        with patch('platform.system', MagicMock(return_value='Windows')):
            dirs = config_dirs()

            self.assertIsNotNone(dirs)
            self._assert_unicode_encoding(dirs)
            self.assertIn(os.path.expanduser('~\\AppData\\Roaming'), dirs)

    def test_config_dirs_on_linux(self):
        with patch('platform.system', MagicMock(return_value='Linux')):
            dirs = config_dirs()

            self.assertIsNotNone(dirs)
            self._assert_unicode_encoding(dirs)
            self.assertIn(os.path.expanduser('~/.config'), dirs)

    def test_config_dirs_on_dummy_system_defaults_to_unix(self):
        with patch('platform.system', MagicMock(return_value='dummy')):
            dirs = config_dirs()

            self.assertIsNotNone(dirs)
            self._assert_unicode_encoding(dirs)
            self.assertIn(os.path.expanduser('~/.config'), dirs)


class TestConfigFilePath(TestCase):
    def _assert_expected_basename(self, config_path):
        actual_basename = os.path.basename(config_path)
        expect_basename = uu.encode(CONFIG_BASENAME)
        self.assertEqual(expect_basename, actual_basename)

    def _assert_expected_encoding(self, config_path):
        self.assertTrue(uu.is_internalbytestring(config_path))

    def test_config_dirs_on_mac(self):
        with patch('platform.system', MagicMock(return_value='Darwin')):
            config_path = config_file_path()

            self.assertIsNotNone(config_path)
            self._assert_expected_encoding(config_path)
            self._assert_expected_basename(config_path)

    def test_config_dirs_on_windows(self):
        # TODO: Mock expanding "~" to "C:/Users/whatever" ..
        with patch('platform.system', MagicMock(return_value='Windows')):
            config_path = config_file_path()

            self.assertIsNotNone(config_path)
            self._assert_expected_encoding(config_path)
            self._assert_expected_basename(config_path)

    def test_config_dirs_on_linux(self):
        with patch('platform.system', MagicMock(return_value='Linux')):
            config_path = config_file_path()

            self.assertIsNotNone(config_path)
            self._assert_expected_encoding(config_path)
            self._assert_expected_basename(config_path)

    def test_config_dirs_on_dummy_system_defaults_to_unix(self):
        with patch('platform.system', MagicMock(return_value='dummy')):
            config_path = config_file_path()

            self.assertIsNotNone(config_path)
            self._assert_expected_encoding(config_path)
            self._assert_expected_basename(config_path)


class TestLoadConfigFromFile(TestCase):
    @classmethod
    def setUpClass(cls):
        uu.init_provider_registry()

    def test_raises_exception_given_none(self):
        with self.assertRaises(AssertionError):
            _ = load_config_from_file(None)

    def test_loads_valid_config_from_absolute_path(self):
        _config_path = uu.normpath(uu.abspath_testconfig())
        actual = load_config_from_file(_config_path)
        self.assertIsNotNone(actual)
