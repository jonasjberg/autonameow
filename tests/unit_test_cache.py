# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2017 Jonas Sjöberg
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

from core import cache
import unit_utils as uu


class TestCacheConstants(TestCase):
    def test_cache_dir_abspath(self):
        p = cache.CACHE_DIR_ABSPATH
        self.assertIsNotNone(p)
        self.assertTrue(uu.is_internalbytestring(p))

    def test_default_cache_directory_root_exists(self):
        d = cache.DEFAULT_CACHE_DIRECTORY_ROOT
        self.assertTrue(uu.dir_exists(d))
        self.assertTrue(uu.path_is_readable(d))

    def test_cache_dir_abspath_is_readable_directory(self):
        d = cache.CACHE_DIR_ABSPATH
        self.assertTrue(uu.dir_exists(d))
        self.assertTrue(uu.path_is_readable(d))

    def test_cache_dir_abspath_is_directory(self):
        d = cache.CACHE_DIR_ABSPATH
        self.assertTrue(uu.dir_exists(d))
        self.assertTrue(uu.path_is_readable(d))


class TestBaseCache(TestCase):
    def test_init_raises_exception_if_missing_required_arguments(self):
        with self.assertRaises(TypeError):
            c = cache.BaseCache()

        with self.assertRaises(ValueError):
            c = cache.BaseCache(None)

    def test_cache_directory(self):
        pass

    # c = Cache('ebook_analyzer')
    # c.get('isbn_numbers')
