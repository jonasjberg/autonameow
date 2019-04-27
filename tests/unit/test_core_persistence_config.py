#!/usr/bin/env python3
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

import os
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

import unit.utils as uu
from core.persistence.config import CONFIG_BASENAME
from core.persistence.config import config_dirpath_candidates
from core.persistence.config import config_filepath_for_platform
from core.persistence.config import load_config_from_file


class TestConfigDirpathCandidates(TestCase):
    def _assert_unicode_encoding(self, path_list):
        for path in path_list:
            self.assertTrue(uu.is_internalstring(path))

    def test_config_dirs_on_mac(self):
        with patch('platform.system', MagicMock(return_value='Darwin')):
            dirs = config_dirpath_candidates()

            self.assertIsNotNone(dirs)
            self._assert_unicode_encoding(dirs)
            self.assertIn(os.path.expanduser('~/.config'), dirs)
            self.assertIn(os.path.expanduser('~/Library/Application Support'), dirs)

    def test_config_dirs_on_windows(self):
        self.skipTest('TODO: Mock expanding "~" to "C:/Users/whatever"')
        with patch('platform.system', MagicMock(return_value='Windows')):
            dirs = config_dirpath_candidates()

            self.assertIsNotNone(dirs)
            self._assert_unicode_encoding(dirs)
            self.assertIn(os.path.expanduser('~\\AppData\\Roaming'), dirs)

    def test_config_dirs_on_linux(self):
        with patch('platform.system', MagicMock(return_value='Linux')):
            dirs = config_dirpath_candidates()

            self.assertIsNotNone(dirs)
            self._assert_unicode_encoding(dirs)
            self.assertIn(os.path.expanduser('~/.config'), dirs)

    def test_config_dirs_on_dummy_system_defaults_to_unix(self):
        with patch('platform.system', MagicMock(return_value='dummy')):
            dirs = config_dirpath_candidates()

            self.assertIsNotNone(dirs)
            self._assert_unicode_encoding(dirs)
            self.assertIn(os.path.expanduser('~/.config'), dirs)


class TestConfigFilepathForPlatform(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.expect_basename = uu.encode(CONFIG_BASENAME)

    def _check_result(self, actual):
        self.assertIsNotNone(actual)
        self.assertTrue(uu.is_internalbytestring(actual))
        actual_basename = os.path.basename(actual)
        self.assertEqual(self.expect_basename, actual_basename)

    def test_config_dirs_on_mac(self):
        with patch('platform.system', MagicMock(return_value='Darwin')):
            config_filepath = config_filepath_for_platform()
        self._check_result(config_filepath)

    def test_config_dirs_on_windows(self):
        # TODO: Mock expanding "~" to "C:/Users/whatever" ..
        with patch('platform.system', MagicMock(return_value='Windows')):
            config_filepath = config_filepath_for_platform()
        self._check_result(config_filepath)

    def test_config_dirs_on_linux(self):
        with patch('platform.system', MagicMock(return_value='Linux')):
            config_filepath = config_filepath_for_platform()
        self._check_result(config_filepath)

    def test_config_dirs_on_dummy_system_defaults_to_unix(self):
        with patch('platform.system', MagicMock(return_value='dummy')):
            config_filepath = config_filepath_for_platform()
        self._check_result(config_filepath)


MOCK_REGISTRY = Mock()
MOCK_REGISTRY.might_be_resolvable.return_value = True


class TestLoadConfigFromFile(TestCase):
    @patch('core.config.rules.master_provider.Registry', MOCK_REGISTRY)
    def test_raises_exception_given_none(self):
        with self.assertRaises(AssertionError):
            _ = load_config_from_file(None)

    @patch('core.config.rules.master_provider.Registry', MOCK_REGISTRY)
    def test_loads_valid_config_from_absolute_path(self):
        config_filepath = uu.normpath(uu.abspath_testconfig())
        actual = load_config_from_file(config_filepath)
        self.assertIsNotNone(actual)
