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

import re
from unittest import TestCase
from unittest.mock import Mock, patch

from unit import constants as uuconst
from util.text.regexcache import (
    _RegexCache,
)


class TestRegexCache(TestCase):
    def setUp(self):
        self.rc = _RegexCache()

    def test_instantiated_regexcache_is_not_none(self):
        self.assertIsNotNone(self.rc)

    def test_regexcache_is_initially_empty(self):
        self.assertEqual(0, len(self.rc))

    def test_regexcache_stores_regex(self):
        self.rc(r'foo.*')
        self.assertEqual(1, len(self.rc))

        cached_regex = self.rc(r'foo.*')
        self.assertIsInstance(cached_regex, uuconst.BUILTIN_REGEX_TYPE)

    def test_regexcache_stores_regex_with_flags(self):
        self.rc(r'foo.*', re.IGNORECASE)
        self.assertEqual(1, len(self.rc))

        cached_regex = self.rc(r'foo.*', re.IGNORECASE)
        self.assertIsInstance(cached_regex, uuconst.BUILTIN_REGEX_TYPE)

    def test_regexcache_stores_regexes_with_and_without_flags(self):
        self.rc(r'foo.*', re.IGNORECASE)
        self.rc(r'bar.*')
        self.assertEqual(2, len(self.rc))

        cached_regex_A = self.rc(r'foo.*', re.IGNORECASE)
        self.assertIsInstance(cached_regex_A, uuconst.BUILTIN_REGEX_TYPE)

        cached_regex_B = self.rc(r'bar.*')
        self.assertIsInstance(cached_regex_B, uuconst.BUILTIN_REGEX_TYPE)

    def test_does_not_recompile_cached_regex_with_matching_patterns(self):
        self.rc(r'foo.*')
        self.assertEqual(1, len(self.rc))

        mock_re_compile = Mock()
        with patch('util.text.regexcache.re.compile', mock_re_compile):
            _ = self.rc(r'foo.*')
            mock_re_compile.assert_not_called()

    def test_does_not_recompile_cached_regex_with_matching_patterns_flags(self):
        self.rc(r'foo.*', re.IGNORECASE)

        mock_re_compile = Mock()
        with patch('util.text.regexcache.re.compile', mock_re_compile):
            _ = self.rc(r'foo.*', re.IGNORECASE)
            mock_re_compile.assert_not_called()

    def test_compiles_regex_with_matching_pattern_but_different_flags(self):
        self.rc(r'foo.*', re.IGNORECASE)

        mock_re_compile = Mock()
        with patch('util.text.regexcache.re.compile', mock_re_compile):
            _ = self.rc(r'foo.*', re.MULTILINE)
            mock_re_compile.assert_called_once()

    def test_compiles_regex_with_matching_pattern_but_first_without_flags(self):
        self.rc(r'foo.*')

        mock_re_compile = Mock()
        with patch('util.text.regexcache.re.compile', mock_re_compile):
            _ = self.rc(r'foo.*', re.MULTILINE)
            mock_re_compile.assert_called_once()
