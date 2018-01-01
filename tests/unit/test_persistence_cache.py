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
from core.persistence import cache


class TestBaseCache(TestCase):
    def test_init_raises_exception_if_missing_required_arguments(self):
        def _aR(prefix):
            with self.assertRaises(ValueError):
                _ = cache.BaseCache(
                    prefix,
                    cache_dir_abspath=uu.mock_cache_path()
                )

        _aR(None)
        _aR(' ')
        _aR('  ')
        _aR(object())

        with self.assertRaises(TypeError):
            _ = cache.BaseCache()


class TestBaseCacheStorage(TestCase):
    def setUp(self):
        owner = 'test_owner'
        self.data_key = 'key_foo'
        self.data_value = 'value_bar'
        self.c = cache.BaseCache(owner=owner)

    def tearDown(self):
        self.c.flush()

    def test_cache_set(self):
        self.c.set(self.data_key, self.data_value)

    def test_cache_set_get(self):
        self.c.set(self.data_key, self.data_value)

        retrieved = self.c.get(self.data_key)
        self.assertEqual(retrieved, self.data_value)

    def test_cache_get_from_empty_cache_returns_none(self):
        actual = self.c.get(self.data_key)
        self.assertIsNone(actual)

    def test_keys_initially_empty(self):
        expect = []
        actual = self.c.keys()
        self.assertEqual(actual, expect)

    def test_keys_returns_expected(self):
        self.c.set(self.data_key, self.data_value)

        expect = [self.data_key]
        actual = self.c.keys()
        self.assertEqual(actual, expect)

    def test_empty_cache_filesize_is_zero(self):
        actual = self.c.filesize()
        self.assertEqual(0, actual)

    def test_caching_data_increases_filesize(self):
        actual_initial = self.c.filesize()
        self.assertEqual(0, actual_initial)

        self.c.set('key', 'data' * 10)
        actual_after_first_set = self.c.filesize()
        self.assertGreater(actual_after_first_set, 0)

        self.c.set('key', 'data' * 20)
        actual_after_second_set = self.c.filesize()
        self.assertGreater(actual_after_second_set, 0)
        self.assertGreater(actual_after_second_set, actual_after_first_set)

    def test_caching_continuously_increases_filesize(self):
        previous_size = 0
        for data_size in range(100, 2000, 100):
            self.c.set('key', 'data' * data_size)

            current_size = self.c.filesize()
            self.assertGreater(current_size, previous_size)
            previous_size = current_size


class TestBaseCacheMaxFilesize(TestCase):
    def setUp(self):
        owner = 'test_owner'
        self.c = cache.BaseCache(owner, max_filesize=500)

    def tearDown(self):
        self.c.flush()

    def test_cache_does_not_exceed_max_filesize(self):
        data = 'data' * 10

        # Allow exceeding the limit (size of recently cached data)
        failing_limit = self.c.max_filesize + len(data)

        for data_size in range(10, 1000, 10):
            key = str(data_size)
            self.c.set(key, data)

            current_size = self.c.filesize()
            self.assertLess(current_size, failing_limit)


class CacheInterface(TestCase):
    def test_get_cache(self):
        actual = cache.get_cache('foo')
        self.assertTrue(uu.is_class_instance(actual))
        self.assertIsInstance(actual, cache.BaseCache)
