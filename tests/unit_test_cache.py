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
from unittest.mock import (
    MagicMock,
    patch
)

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


def mock__load(self, file_path):
    return {'mjao': 'oajm'}


def mock__dump(self, value, file_path):
    pass


class TestBaseCache(TestCase):
    def test_init_raises_exception_if_missing_required_arguments(self):
        def _aR(prefix):
            with self.assertRaises(ValueError):
                _ = cache.BaseCache(prefix)

        _aR(None)
        _aR(' ')
        _aR('  ')
        _aR(object())

        with self.assertRaises(TypeError):
            _ = cache.BaseCache()

    def test__cache_file_abspath(self):
        def _aE(prefix, key, expect):
            c = cache.BaseCache(prefix)
            actual = c._cache_file_abspath(key)
            self.assertEqual(actual, expect)

        _aE(prefix='foo', key='bar', expect=b'/tmp/autonameow_cache/foo_bar')
        _aE(prefix='_', key='my_key', expect=b'/tmp/autonameow_cache/__my_key')
        _aE(prefix='foo', key=1, expect=b'/tmp/autonameow_cache/foo_1')

    def test__cache_file_abspath_raises_exception_given_bad_key(self):
        def _aR(prefix, key, expect):
            with self.assertRaises(KeyError):
                c = cache.BaseCache(prefix)
                actual = c._cache_file_abspath(key)
                self.assertEqual(actual, expect)

        _aR(prefix='foo', key=None, expect=b'/tmp/autonameow_cache/foo_bar')
        _aR(prefix='foo', key='', expect=b'/tmp/autonameow_cache/__my_key')
        _aR(prefix='foo', key=' ', expect=b'/tmp/autonameow_cache/__my_key')

    @patch.object(cache.BaseCache, '_load', mock__load)
    def test_get(self):
        c = cache.BaseCache('foo')
        actual = c.get('key_a')
        self.assertEqual(actual, {'mjao': 'oajm'})

    @patch.object(cache.BaseCache, '_dump', mock__dump)
    def test_set(self):
        c = cache.BaseCache('foo')
        c.set('key_a', 'mjaooajm')

    @patch.object(cache.BaseCache, '_dump', mock__dump)
    def test_set_get(self):
        c = cache.BaseCache('foo')
        c.set('key_a', 'mjaooajm')

        actual = c.get('key_a')
        self.assertEqual(actual, 'mjaooajm')


class TestPickleCache(TestCase):
    CACHE_KEY = 'foo'

    def setUp(self):
        self.c = cache.PickleCache(self.CACHE_KEY)

    def tearDown(self):
        self.c.delete(self.CACHE_KEY)

    def test_delete(self):
        d = cache.PickleCache('to_be_deleted')
        d.set('dummy', 'data')

        # TODO:  FIX THIS!
        d.delete('dummy')

        # TODO:  FIX THIS!
        _cache_file_path = d._cache_file_abspath('to_be_deleted')
        self.assertFalse(uu.file_exists(_cache_file_path))

    def test_set(self):
        datakey = 'key_a'
        datavalue = 'mjaooajm'
        self.c.set(datakey, datavalue)

        # TODO:  FIX THIS!
        _cache_file_path = self.c._cache_file_abspath(datakey)
        self.assertTrue(uu.file_exists(_cache_file_path))

        actual = self.c.get(datakey)
        self.assertEqual(actual, datavalue)

    def test_get(self):
        self.c = cache.PickleCache(self.CACHE_KEY)
        actual = self.c.get('key_a')
        self.assertEqual(actual, 'mjaooajm')

    def test_set_get(self):
        c = cache.PickleCache('bar')
        c.set('key_a', {'1': 'mjaooajm', '2': 2})

        actual = c.get('key_a')
        self.assertEqual(actual, {'1': 'mjaooajm', '2': 2})
