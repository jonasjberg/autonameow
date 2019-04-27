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

import re
from unittest import TestCase
from unittest.mock import Mock, patch

from unit import constants as uuconst
from util.text.regexcache import _RegexCache


class TestRegexCache(TestCase):
    def setUp(self):
        self.rc = _RegexCache()

    def _check_cached_regex_type(self, *args):
        cached_regex = self.rc(*args)
        self.assertIsInstance(cached_regex, uuconst.BUILTIN_REGEX_TYPE)

    def _assert_does_not_recompile(self, *args):
        mock_re_compile = Mock()
        with patch('util.text.regexcache.re.compile', mock_re_compile):
            _ = self.rc(*args)
            mock_re_compile.assert_not_called()

    def _assert_compiles(self, *args):
        mock_re_compile = Mock()
        with patch('util.text.regexcache.re.compile', mock_re_compile):
            _ = self.rc(*args)
            mock_re_compile.assert_called_once_with(*args)

    def test_instantiated_regexcache_is_not_none(self):
        self.assertIsNotNone(self.rc)

    def test_instantiated_regexcache_len_is_initially_zero(self):
        self.assertEqual(0, len(self.rc))

    def test_returns_expected_len_and_cached_regex_type(self):
        self.rc(r'foo.*')
        self.assertEqual(1, len(self.rc))
        self._check_cached_regex_type(r'foo.*')

    def test_returns_expected_len_and_type_with_flags(self):
        self.rc(r'foo.*', re.IGNORECASE)
        self.assertEqual(1, len(self.rc))
        self._check_cached_regex_type(r'foo.*', re.IGNORECASE)

    def test_returns_expected_len_and_type_with_and_without_flags(self):
        self.rc(r'foo.*', re.IGNORECASE)
        self.rc(r'bar.*')
        self.assertEqual(2, len(self.rc))
        self._check_cached_regex_type(r'foo.*', re.IGNORECASE)
        self._check_cached_regex_type(r'bar.*')

    def test_compiles_first_seen_regex(self):
        self._assert_compiles(r'foo.*', re.MULTILINE)

    def test_compiles_regex_with_matching_pattern_but_different_flags(self):
        self.rc(r'foo.*', re.IGNORECASE)
        self._assert_compiles(r'foo.*', re.MULTILINE)

    def test_compiles_regex_with_matching_pattern_but_first_without_flags(self):
        self.rc(r'foo.*')
        self._assert_compiles(r'foo.*', re.MULTILINE)

    def test_does_not_recompile_cached_regex_with_matching_patterns(self):
        self.rc(r'foo.*')
        self._assert_does_not_recompile(r'foo.*')

    def test_does_not_recompile_cached_regex_with_matching_patterns_flags(self):
        self.rc(r'foo.*', re.IGNORECASE)
        self._assert_does_not_recompile(r'foo.*', re.IGNORECASE)
