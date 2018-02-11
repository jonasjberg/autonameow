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
from unittest.mock import Mock

import unit.utils as uu
import unit.constants as uuconst
from core import exceptions
from core.repository import (
    QueryResponseFailure,
    Repository,
    RepositoryPool,
    QueryResponseSuccess
)


class TestRepositoryRetrieval(TestCase):
    def setUp(self):
        self.r = Repository()
        mock_fileobject = Mock()
        mock_fileobject.hash_partial = '123456789'
        self.fo = mock_fileobject

    def test_query_with_none_meowuri_raises_exception(self):
        with self.assertRaises(exceptions.InvalidMeowURIError):
            self.r.query(self.fo, None)

    def test_query_non_existent_data(self):
        actual = self.r.query(self.fo,
                              uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE))
        self.assertFalse(actual)


class TestRepositoryStorage(TestCase):
    def setUp(self):
        self.r = Repository()
        self.fileobject = uu.get_mock_fileobject(mime_type='text/plain')

    def test_repository_init_in_expected_state(self):
        self.assertIsInstance(self.r.data, dict)
        self.assertEqual(len(self.r), 0)

    def test_storing_data_increments_len(self):
        valid_uri = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        self.r.store(self.fileobject, valid_uri, {'value': 'foo'})
        self.assertEqual(len(self.r), 1)

    def test_storing_data_with_different_meowuris_increments_len(self):
        first_valid_uri = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        self.r.store(self.fileobject, first_valid_uri, {'value': 'foo'})
        self.assertEqual(len(self.r), 1)

        second_valid_uri = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        self.r.store(self.fileobject, second_valid_uri, {'value': 'foo'})
        self.assertEqual(len(self.r), 2)

    def test_adding_data_with_same_meowuri_increments_len(self):
        first_valid_uri = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        self.r.store(self.fileobject, first_valid_uri, {'value': 'foo'})
        self.assertEqual(len(self.r), 1)

        second_valid_uri = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        self.r.store(self.fileobject, second_valid_uri, {'value': 'foo'})
        self.assertEqual(len(self.r), 2)

    def test_adding_one_result_increments_len_once(self):
        _field = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        _results = {'value': 'foo'}
        self.r.store(self.fileobject, _field, _results)

        self.assertEqual(len(self.r), 1)

    def test_adding_two_results_increments_len_twice(self):
        _field_one = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        _field_two = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        _result_one = {'value': 'foo'}
        _result_two = {'value': 'bar'}
        self.r.store(self.fileobject, _field_one, _result_one)
        self.r.store(self.fileobject, _field_two, _result_two)

        self.assertEqual(len(self.r), 2)

    def test_adding_list_of_two_results_increments_len_twice(self):
        self.skipTest('TODO: Reimplement "Repository.__len__()"')
        _field_one = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        _result_one = {'value': ['foo', 'bar']}
        self.r.store(self.fileobject, _field_one, _result_one)

        self.assertEqual(len(self.r), 2)

    def test_adding_two_lists_of_two_results_increments_len_twice(self):
        self.skipTest('TODO: Reimplement "Repository.__len__()"')
        _field_one = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        _result_one = {'value_A': ['foo', 'bar']}
        _result_two = {'value_B': ['baz', 'BLA']}
        self.r.store(self.fileobject, _field_one, _result_one)
        self.r.store(self.fileobject, _field_one, _result_two)

        self.assertEqual(len(self.r), 2)

    def test_add_empty_does_not_increment_len(self):
        _field = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        _results = []
        self.r.store(self.fileobject, _field, _results)

        self.assertEqual(len(self.r), 0)

    def test_store_data_with_invalid_meowuri_raises_error(self):
        with self.assertRaises(AssertionError):
            self.r.store(self.fileobject, None, {'value': 'foo'})

        with self.assertRaises(AssertionError):
            self.r.store(self.fileobject, '', {'value': 'foo'})

    def test_stores_data_with_valid_meowuri(self):
        meowuris = [
            uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME),
            uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE),
            uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)
        ]
        for valid_uri in meowuris:
            self.r.store(self.fileobject, valid_uri, {'value': 'foo'})

    def test_valid_meowuri_returns_expected_data(self):
        self.skipTest('TODO: Reimplement "Repository.__len__()"')
        valid_uri = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        self.r.store(self.fileobject, valid_uri, 'expected_data')

        response = self.r.query(self.fileobject, valid_uri)
        self.assertEqual(response, 'expected_data')

    def test_none_meowuri_raises_exception(self):
        self.skipTest('TODO: Reimplement "Repository.__len__()"')
        valid_uri = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        self.r.store(self.fileobject, valid_uri, 'expected_data')

        with self.assertRaises(exceptions.InvalidMeowURIError):
            self.r.query(self.fileobject, None)

    def test_valid_meowuri_returns_expected_data_multiple_entries(self):
        self.skipTest('TODO: Reimplement "Repository.__len__()"')
        valid_uri = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        self.r.store(self.fileobject, valid_uri, 'expected_data_a')
        self.r.store(self.fileobject, valid_uri, 'expected_data_b')

        response = self.r.query(self.fileobject, valid_uri)
        self.assertIn('expected_data_a', response)
        self.assertIn('expected_data_b', response)


class TestRepositoryGenericStorage(TestCase):
    def setUp(self):
        self.r = Repository()

    def test_todo(self):
        self.skipTest('TODO: Add tests for storing "generic fields" ..')


class TestRepositoryPool(TestCase):
    DUMMY_REPOSITORY = 'IamRepository'
    DUMMY_ID_1 = 'IDOne'
    DUMMY_ID_2 = 'IDTwo'

    def test_initially_empty(self):
        p = RepositoryPool()
        self.assertEqual(len(p), 0)

    def test_get_on_empty_pool_raises_keyerror(self):
        p = RepositoryPool()

        for _id in [None, 'foo', 1, object()]:
            with self.assertRaises(KeyError):
                p.get(_id)

    def test_add_repository(self):
        p = RepositoryPool()
        p.add(repository=self.DUMMY_REPOSITORY, id_=self.DUMMY_ID_1)

        self.assertEqual(len(p), 1)

        actual = p.get(self.DUMMY_ID_1)
        self.assertEqual(actual, self.DUMMY_REPOSITORY)

    def test_uses_default_id_if_unspecified(self):
        p = RepositoryPool()
        p.add(repository=self.DUMMY_REPOSITORY)

        self.assertEqual(len(p), 1)

        actual = p.get()
        self.assertEqual(actual, self.DUMMY_REPOSITORY)

        actual = p.get(id_=None)
        self.assertEqual(actual, self.DUMMY_REPOSITORY)

    def test_get_with_bad_id_raises_keyerror(self):
        p = RepositoryPool()
        p.add(repository=self.DUMMY_REPOSITORY, id_=self.DUMMY_ID_1)

        self.assertEqual(len(p), 1)

        with self.assertRaises(KeyError):
            _ = p.get(self.DUMMY_ID_2)

        for _id in [None, 'foo', 1, object()]:
            with self.assertRaises(KeyError):
                p.get(_id)


class TestQueryResponseFailure(TestCase):
    def test_evaluates_false(self):
        response = QueryResponseFailure()
        self.assertFalse(response)
