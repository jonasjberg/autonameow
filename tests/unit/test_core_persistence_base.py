# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from unittest import TestCase
from unittest.mock import patch

import unit.utils as uu
from core import constants as C
from core.persistence.base import BasePersistence
from core.persistence.base import get_config_persistence_path
from core.persistence.base import get_persistence
from core.persistence.base import PersistenceImplementationBackendError
from core.persistence.base import PicklePersistence
from core.persistence.base import _basename_as_key
from core.persistence.base import _key_as_filepath


class TestPersistenceDirectory(TestCase):
    def test_persistence_dir_abspath(self):
        p = get_config_persistence_path()
        self.assertIsNotNone(p)
        self.assertTrue(uu.is_internalbytestring(p))

    def test_persistence_dir_abspath_is_readable_directory(self):
        d = get_config_persistence_path()
        self.assertTrue(uu.dir_exists(d))
        self.assertTrue(uu.path_is_readable(d))

    def test_persistence_dir_abspath_is_directory(self):
        d = get_config_persistence_path()
        self.assertTrue(uu.dir_exists(d))
        self.assertTrue(uu.path_is_readable(d))


def mock__load(self, filepath):
    return {'mjao': 'oajm'}


def mock__dump(self, value, filepath):
    pass


class TestBasePersistence(TestCase):
    def test_init_raises_exception_if_missing_required_arguments(self):
        def _aR(prefix):
            with self.assertRaises(ValueError):
                _ = BasePersistence(
                    prefix,
                    persistence_dir_abspath=uu.mock_persistence_path()
                )

        _aR(None)
        _aR(' ')
        _aR('  ')
        _aR(object())

        with self.assertRaises(TypeError):
            _ = BasePersistence()

    def test__persistence_file_abspath(self):
        def _aE(prefix, key, expect):
            c = BasePersistence(
                prefix,
                persistence_dir_abspath=uu.mock_persistence_path()
            )
            actual = c._persistence_file_abspath(key)
            self.assertEqual(actual, expect)

        _aE(prefix='foo', key='bar', expect=b'/tmp/autonameow_cache/foo_bar')
        _aE(prefix='_', key='my_key', expect=b'/tmp/autonameow_cache/__my_key')
        _aE(prefix='foo', key=1, expect=b'/tmp/autonameow_cache/foo_1')

    def test__persistence_file_abspath_raises_exception_given_bad_key(self):
        def _aR(prefix, key, expect):
            with self.assertRaises(KeyError):
                c = BasePersistence(
                    prefix,
                    persistence_dir_abspath=uu.mock_persistence_path()
                )
                actual = c._persistence_file_abspath(key)
                self.assertEqual(actual, expect)

        _aR(prefix='foo', key=None, expect=b'/tmp/autonameow_cache/foo_bar')
        _aR(prefix='foo', key='', expect=b'/tmp/autonameow_cache/__my_key')
        _aR(prefix='foo', key=' ', expect=b'/tmp/autonameow_cache/__my_key')

    @patch.object(BasePersistence, '_load', mock__load)
    def test_get_raises_key_error(self):
        c = BasePersistence(
            'foo', persistence_dir_abspath=uu.mock_persistence_path()
        )

        with self.assertRaises(KeyError):
            actual = c.get('key_a')
            self.assertEqual(actual, {'mjao': 'oajm'})

    @patch.object(BasePersistence, '_dump', mock__dump)
    def test_set(self):
        c = BasePersistence(
            'foo', persistence_dir_abspath=uu.mock_persistence_path()
        )
        c.set('key_a', 'mjaooajm')

    @patch.object(BasePersistence, '_load', mock__load)
    @patch.object(BasePersistence, '_dump', mock__dump)
    def test_set_get(self):
        c = BasePersistence(
            'foo', persistence_dir_abspath=uu.mock_persistence_path()
        )
        c.set('key_a', 'mjaooajm')

        actual = c.get('key_a')
        self.assertEqual(actual, 'mjaooajm')

    @patch.object(BasePersistence, '_load', mock__load)
    @patch.object(BasePersistence, '_dump', mock__dump)
    def test_delete(self):
        c = BasePersistence(
            'foo', persistence_dir_abspath=uu.mock_persistence_path()
        )
        datakey = 'dummykey'
        datavalue = 'bardata'
        c.set(datakey, datavalue)

        actual = c.get(datakey)
        self.assertEqual(actual, datavalue)

        c.delete(datakey)
        with self.assertRaises(KeyError):
            c.get(datakey)

    def test_filesize_raises_key_error_given_invalid_keys(self):
        c = BasePersistence(
            'foo', persistence_dir_abspath=uu.mock_persistence_path()
        )

        with self.assertRaises(KeyError):
            for _invalid_key in ['key_a', None, '', ' ']:
                _ = c.filesize(_invalid_key)

    def test_empty_persistence_filesize_is_zero(self):
        c = BasePersistence(
            'foo', persistence_dir_abspath=uu.mock_persistence_path()
        )

        datakey = 'dummykey'
        actual = c.filesize(datakey)
        self.assertEqual(0, actual)


class TestBaseNameAsKey(TestCase):
    def test_returns_expected_with_prefix_foo_separator_underline(self):
        for given_basename, expect_key in [
            ('foo_dummytestkey', 'dummytestkey'),
            ('foo_dummy_testkey', 'dummy_testkey'),
            ('foo_dummy_test_key', 'dummy_test_key'),
            ('foo_foodummytestkey', 'foodummytestkey'),
            ('foo_foodummy_testkey', 'foodummy_testkey'),
            ('foo_foodummy_test_key', 'foodummy_test_key'),
            ('foo_foo_dummytestkey', 'foo_dummytestkey'),
            ('foo_foo_dummy_testkey', 'foo_dummy_testkey'),
            ('foo_foo_dummy_test_key', 'foo_dummy_test_key'),
            ('foo_a', 'a'),
            ('foo__a', '_a'),
            ('foo_a_b', 'a_b'),
            ('foo__a_b', '_a_b'),
            ('foo_a__b', 'a__b'),
            ('foo__a__b', '_a__b'),
        ]:
            with self.subTest(given_basename=given_basename):
                actual = _basename_as_key(str_basename=given_basename,
                                          persistencefile_prefix='foo',
                                          persistence_file_prefix_separator='_')
                self.assertEqual(expect_key, actual)

    def test_returns_expected_with_prefix_a_separator_dash(self):
        for given_basename, expect_key in [
            ('a-a', 'a'),
            ('a-_a', '_a'),
            ('a-a_b', 'a_b'),
            ('a-_a-b', '_a-b'),
            ('a-a--b', 'a--b'),
            ('a-_a--b', '_a--b'),
        ]:
            with self.subTest(given_basename=given_basename):
                actual = _basename_as_key(str_basename=given_basename,
                                          persistencefile_prefix='a',
                                          persistence_file_prefix_separator='-')
                self.assertEqual(expect_key, actual)

    def test_returns_none_given_basename_without_the_prefix(self):
        actual = _basename_as_key(str_basename='abc',
                                  persistencefile_prefix='foo',
                                  persistence_file_prefix_separator='_')
        self.assertIsNone(actual)


class TestKeyAsFilePath(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.TEST_PATH = b'/tmp/autonameow_cache'

    def test_returns_expected_absolute_paths(self):
        for given_key, given_prefix, given_separator, expected_path in [
            ('a', 'foo', '_', b'/tmp/autonameow_cache/foo_a'),
            ('FooOwner', 'foo', '_', b'/tmp/autonameow_cache/foo_FooOwner'),
            ('foo', 'bar', '_', b'/tmp/autonameow_cache/bar_foo'),
            ('foo', 'foo', '_', b'/tmp/autonameow_cache/foo_foo'),
            ('a', 'foo', '-', b'/tmp/autonameow_cache/foo-a'),
            ('FooOwner', 'foo', '-', b'/tmp/autonameow_cache/foo-FooOwner'),
            ('foo', 'bar', '-', b'/tmp/autonameow_cache/bar-foo'),
            ('foo', 'foo', '-', b'/tmp/autonameow_cache/foo-foo'),
        ]:
            with self.subTest(given_key=given_key):
                actual = _key_as_filepath(
                    key=given_key,
                    persistencefile_prefix=given_prefix,
                    persistence_file_prefix_separator=given_separator,
                    persistence_dir_abspath=self.TEST_PATH
                )
                self.assertTrue(uu.is_internalbytestring(actual))
                self.assertTrue(uu.is_abspath(actual))
                self.assertEqual(expected_path, actual)

    def test_raises_keyerror_given_bad_key(self):
        def _assert_raises(given):
            with self.assertRaises(KeyError):
                _ = _key_as_filepath(key=given,
                                     persistencefile_prefix='foo',
                                     persistence_file_prefix_separator='_',
                                     persistence_dir_abspath=self.TEST_PATH)
        _assert_raises(None)
        _assert_raises('')
        _assert_raises(' ')
        _assert_raises(object())
        _assert_raises([])
        _assert_raises(['foo', 'bar'])
        _assert_raises({})


class TestPicklePersistence(TestCase):
    PERSISTENCE_KEY = 'temp_unit_test_persistence'

    def setUp(self):
        self.datakey = 'fookey'
        self.datavalue = 'bardata'
        self.c = PicklePersistence(self.PERSISTENCE_KEY)

    def tearDown(self):
        self.c.flush()

    def test_delete(self):
        file_prefix = 'temp_unit_test_persistence_to_be_deleted'
        datakey = 'dummykey'
        datavalue = 'bardata'

        d = PicklePersistence(file_prefix)
        d.set(datakey, datavalue)

        _filepath = d._persistence_file_abspath(datakey)
        self.assertTrue(uu.file_exists(_filepath))

        d.delete(datakey)
        self.assertFalse(uu.file_exists(_filepath))

    def test_delete_unused_key(self):
        self.c.delete('unused_key')

    def test_delete_shared_test_persistence(self):
        self.c.set(self.datakey, self.datavalue)

        _filepath = self.c._persistence_file_abspath(self.datakey)
        self.assertTrue(uu.file_exists(_filepath))

        self.c.delete(self.datakey)
        self.assertFalse(uu.file_exists(_filepath))

    def test_set(self):
        self.c.set(self.datakey, self.datavalue)

        _filepath = self.c._persistence_file_abspath(self.datakey)
        self.assertTrue(uu.file_exists(_filepath))

        actual = self.c.get(self.datakey)
        self.assertEqual(actual, self.datavalue)

    def test_get_from_empty(self):
        random_ten_character_key = uu.random_ascii_string(10)
        c = PicklePersistence(random_ten_character_key)

        # The persistence should not have the key in 'self._data' nor should
        # the persistent data exist.  Expect a KeyError.
        with self.assertRaises(KeyError):
            _ = c.get('missing_key')

    def test_set_get(self):
        data_key = 'key_a'
        data_value = {'1': 'mjaooajm', '2': 2}
        self.c.set(data_key, data_value)

        actual = self.c.get(data_key)
        self.assertEqual(actual, data_value)

        self.c.delete(data_key)

    def test_has(self):
        self.c.set('a', 'data')
        self.assertTrue(self.c.has('a'))

        self.assertFalse(self.c.has('b'))

        self.c.set('b', 'data')
        self.assertTrue(self.c.has('b'))

    def test_keys(self):
        def _assert_has_keys(expected):
            actual = self.c.keys()
            self.assertEqual(sorted(actual), sorted(expected))

        keys = ['key_1st', 'key_2nd', 'key_3rd', '4th']
        value = 'foo'

        _assert_has_keys([])

        self.c.set(keys[0], value)
        self.c.set(keys[1], value)
        _assert_has_keys([keys[0], keys[1]])

        self.c.set(keys[2], value)
        _assert_has_keys([keys[0], keys[1], keys[2]])

        self.c.set(keys[2], 'bar')
        _assert_has_keys([keys[0], keys[1], keys[2]])

        self.c.set(keys[3], value)
        _assert_has_keys([keys[0], keys[1], keys[2], keys[3]])

    def test_keys_reset_after_flush(self):
        self.c.set('a', 'data')
        keys = self.c.keys()
        self.assertEqual(['a'], keys)

        self.c.flush()
        keys = self.c.keys()
        self.assertEqual([], keys)

    def test_initial_filesize_is_zero(self):
        actual_initial = self.c.filesize(self.datakey)
        self.assertEqual(0, actual_initial)

    def test_storing_bigger_data_increases_filesize(self):
        actual_initial = self.c.filesize(self.datakey)
        self.assertEqual(0, actual_initial)

        self.c.set(self.datakey, 'foo' * 10)
        actual_after_first_set = self.c.filesize(self.datakey)
        self.assertGreater(actual_after_first_set, 0)

        self.c.set(self.datakey, 'foo' * 20)
        actual_after_second_set = self.c.filesize(self.datakey)
        self.assertGreater(actual_after_second_set, 0)
        self.assertGreater(actual_after_second_set, actual_after_first_set)

    def test_pickle_errors_are_reraised(self):
        class Foo(object):
            def __init__(self, data):
                self.data = data

        bad_data = Foo('data')
        with self.assertRaises(PersistenceImplementationBackendError):
            # Raises 'AttributeError: Can't pickle local object'
            self.c.set('key', bad_data)


class TestGetPersistence(TestCase):
    def setUp(self):
        self.p = get_persistence(
            'foo', persistence_dir_abspath=C.DEFAULT_PERSISTENCE_DIR_ABSPATH
        )

    def tearDown(self):
        self.p.flush()

    def test_returns_persistence_class_instance(self):
        self.assertTrue(uu.is_class_instance(self.p))
        self.assertIsInstance(self.p, BasePersistence)

    def test_stores_data(self):
        data = 'dummy test data'
        key = 'dummytestkey'
        self.p.set(key, data)

        actual = self.p.get(key)
        self.assertEqual(actual, data)
