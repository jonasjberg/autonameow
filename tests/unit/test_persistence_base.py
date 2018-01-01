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
from unittest.mock import patch

from core import constants as C
from util import unique_identifier
from core.persistence.base import (
    get_config_persistence_path,
    get_persistence,
    BasePersistence,
    PicklePersistence
)
import unit.utils as uu


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


def mock__load(self, file_path):
    return {'mjao': 'oajm'}


def mock__dump(self, value, file_path):
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

        _file_path = d._persistence_file_abspath(datakey)
        self.assertTrue(uu.file_exists(_file_path))

        d.delete(datakey)
        self.assertFalse(uu.file_exists(_file_path))

    def test_delete_shared_test_persistence(self):
        self.c.set(self.datakey, self.datavalue)

        _file_path = self.c._persistence_file_abspath(self.datakey)
        self.assertTrue(uu.file_exists(_file_path))

        self.c.delete(self.datakey)
        self.assertFalse(uu.file_exists(_file_path))

    def test_set(self):
        self.c.set(self.datakey, self.datavalue)

        _file_path = self.c._persistence_file_abspath(self.datakey)
        self.assertTrue(uu.file_exists(_file_path))

        actual = self.c.get(self.datakey)
        self.assertEqual(actual, self.datavalue)

    def test_get_from_empty(self):
        random_key = unique_identifier()
        c = PicklePersistence(random_key)

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

    def test_keys(self):
        data_keys = ['key_1st', 'key_2nd', 'key_3rd']
        data_value = 'foo'
        self.c.set(data_keys[0], data_value)
        self.c.set(data_keys[1], data_value)

        actual = self.c.keys()
        expect = [data_keys[0], data_keys[1]]
        self.assertEqual(sorted(actual), sorted(expect))

        self.c.set(data_keys[2], data_value)
        actual = self.c.keys()
        expect = [data_keys[0], data_keys[1], data_keys[2]]
        self.assertEqual(sorted(actual), sorted(expect))

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
