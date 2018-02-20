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

from util.misc import (
    contains_none,
    count_dict_recursive,
    expand_meowuri_data_dict,
    flatten_dict,
    flatten_sequence_type,
    git_commit_hash,
    is_executable,
    multiset_count,
    nested_dict_get,
    nested_dict_set,
    unique_identifier
)
import unit.utils as uu


DUMMY_RESULTS_DICT = {
    'A': {
        'A1': {
            'A1A': 'a',
            'A1B': 'b'
        },
        'A2': {
            'foo': 'c',
        },
        'A3': {
            'A3A': 'd'
        }
    },
    'B': {
        'B1': {
            'B1A': 'e',
            'B1B': 'foo',
        },
        'B2': {
            'B2A': 'g',
            'B2B': 'h'},
        'B3': {
            'B3A': True,
            'B3B': False
        }
    },
}

DUMMY_FLATTENED_RESULTS_DICT = {
    'A.A1.A1A': 'a',
    'A.A1.A1B': 'b',
    'A.A2.foo': 'c',
    'A.A3.A3A': 'd',
    'B.B1.B1A': 'e',
    'B.B1.B1B': 'foo',
    'B.B2.B2A': 'g',
    'B.B2.B2B': 'h',
    'B.B3.B3A': True,
    'B.B3.B3B': False,
}


class TestUniqueIdentifier(TestCase):
    def test_unique_identifier_returns_not_none(self):
        self.assertIsNotNone(unique_identifier())

    def test_unique_identifier_returns_string(self):
        uuid = unique_identifier()
        self.assertTrue(uu.is_internalstring(uuid))

    def test_unique_identifier_returns_100_unique_values(self):
        seen = set()
        count = 100

        for i in range(0, count):
            seen.add(unique_identifier())

        self.assertEqual(len(seen), count)


class TestMultisetCount(TestCase):
    def test_list_duplicate_count_returns_empty_dict_for_empty_list(self):
        self.assertEqual(multiset_count([]), {})

    def test_list_duplicate_count_returns_none_for_none(self):
        self.assertIsNone(multiset_count(None))

    def _check(self, given, expect):
        self.assertEqual(expect, multiset_count(given))

    def test_list_duplicate_count_returns_expected_no_duplicates(self):
        self._check(given=['a', 'b', 'c'], expect={'a': 1, 'b': 1, 'c': 1})

    def test_list_duplicate_count_returns_expected_one_duplicate(self):
        self._check(given=['a', 'a', 'c'], expect={'a': 2, 'c': 1})

    def test_list_duplicate_count_returns_expected_only_duplicates(self):
        self._check(given=['a', 'a', 'a'], expect={'a': 3})

    def test_list_duplicate_count_returns_expected_no_duplicate_one_none(self):
        self._check(given=['a', None, 'b'], expect={None: 1, 'a': 1, 'b': 1})

    def test_list_duplicate_count_returns_expected_one_duplicate_one_none(self):
        self._check(given=['b', None, 'b'], expect={None: 1, 'b': 2})

    def test_list_duplicate_count_returns_expected_no_duplicate_two_none(self):
        self._check(given=['a', None, 'b', None], expect={None: 2, 'a': 1, 'b': 1})


class TestFlattenSequenceType(TestCase):
    def test_returns_values_that_are_not_lists_or_tuples_as_is(self):
        self.assertEqual(None, flatten_sequence_type(None))
        self.assertEqual('foo', flatten_sequence_type('foo'))
        self.assertEqual(1, flatten_sequence_type(1))

    def test_returns_flat_list_as_is(self):
        actual = flatten_sequence_type(['foo', 1])
        self.assertEqual(['foo', 1], actual)

    def _check(self, given, expect):
        actual = flatten_sequence_type(given)
        self.assertEqual(expect, actual)

    def test_returns_flat_tuple_as_is(self):
        self._check(given=('foo', 1),
                    expect=('foo', 1))

    def test_flattens_nested_list(self):
        self._check(given=['foo', 1, [2, 3]],
                    expect=['foo', 1, 2, 3])

    def test_flattens_nested_tuple(self):
        self._check(given=('foo', 1, (2, 3)),
                    expect=('foo', 1, 2, 3))

    def test_flattens_list_nested_in_tuple(self):
        self._check(given=('foo', 1, [2, 3]),
                    expect=('foo', 1, 2, 3))

    def test_flattens_tuple_nested_in_list(self):
        self._check(given=['foo', 1, (2, 3)],
                    expect=['foo', 1, 2, 3])

    def test_flattens_multiple_nested_tuples(self):
        self._check(given=('foo', 1, (2, 3), (4, (5, 6, (7, 8)))),
                    expect=('foo', 1, 2, 3, 4, 5, 6, 7, 8))

    def test_flattens_multiple_nested_tuples_and_lists(self):
        self._check(given=('foo', 1, [2, 3], (4, [5, 6, (7, 8)])),
                    expect=('foo', 1, 2, 3, 4, 5, 6, 7, 8))


class TestFlattenDict(TestCase):
    def setUp(self):
        self.INPUT = DUMMY_RESULTS_DICT
        self.EXPECTED = DUMMY_FLATTENED_RESULTS_DICT

    def test_raises_type_error_for_invalid_input(self):
        for bad_arg in (None, [], ''):
            with self.subTest(given=bad_arg):
                with self.assertRaises(TypeError):
                    flatten_dict(bad_arg)

    def test_returns_expected_type(self):
        self.assertIsInstance(flatten_dict(self.INPUT), dict)

    def test_returns_expected_len(self):
        self.assertEqual(len(flatten_dict(self.INPUT)), 10)

    def test_flattened_dict_contains_expected(self):
        actual = flatten_dict(self.INPUT)
        self.assertEqual(self.EXPECTED, actual)


class TestFlattenDictWithRawMetadata(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.INPUT = {
            'A': {
                '1': 'A1a',
                '2': 'A2b',
                '3': 'A2c',
                '4': 'A2d',
                '5': False,
                '6': 100,
                '7': True
            }
        }
        self.EXPECTED = {
            'A.1': 'A1a',
            'A.2': 'A2b',
            'A.3': 'A2c',
            'A.4': 'A2d',
            'A.5': False,
            'A.6': 100,
            'A.7': True,
        }

    def test_returns_expected_type(self):
        actual = flatten_dict(self.INPUT)
        self.assertIsInstance(actual, dict)

    def test_returns_expected_len(self):
        actual = flatten_dict(self.INPUT)
        self.assertEqual(len(actual), 7)

    def test_flattened_dict_contains_expected(self):
        actual = flatten_dict(self.INPUT)
        self.assertEqual(self.EXPECTED, actual)


class TestCountDictRecursive(TestCase):
    def test_raises_exception_for_invalid_input(self):
        with self.assertRaises(TypeError):
            count_dict_recursive([])
            count_dict_recursive([{}])
            count_dict_recursive([{'foo': []}])

    def test_returns_zero_given_none_or_false(self):
        self.assertEqual(count_dict_recursive(None), 0)
        self.assertEqual(count_dict_recursive(False), 0)

    def test_returns_zero_given_empty_dictionary(self):
        self.assertEqual(count_dict_recursive({}), 0)
        self.assertEqual(count_dict_recursive({'foo': {}}), 0)
        self.assertEqual(count_dict_recursive({'foo': {'bar': {}}}), 0)

    def test_returns_zero_given_empty_containers(self):
        def _assert_zero_count(test_data):
            self.assertEqual(count_dict_recursive(test_data), 0)

        _assert_zero_count({'a': []})
        _assert_zero_count({'a': [[]]})
        _assert_zero_count({'a': [None]})
        _assert_zero_count({'a': [None, None]})
        _assert_zero_count({'a': {'b': []}})
        _assert_zero_count({'a': {'b': [[]]}})
        _assert_zero_count({'a': {'b': [None]}})
        _assert_zero_count({'a': {'b': [None, None]}})
        _assert_zero_count({'a': {'b': {'c': []}}})
        _assert_zero_count({'a': {'b': {'c': [[]]}}})
        _assert_zero_count({'a': {'b': {'c': [None]}}})
        _assert_zero_count({'a': {'b': {'c': [None, None]}}})

    def test_returns_expected_count(self):
        def _assert_count_is(expected, given):
            self.assertEqual(expected, count_dict_recursive(given))

        _assert_count_is(1, given={'a': 'foo'})
        _assert_count_is(1, given={'a': 'foo', 'b': None})
        _assert_count_is(1, given={'a': 'foo', 'b': []})
        _assert_count_is(2, given={'a': 'foo', 'b': 'bar'})
        _assert_count_is(2, given={'a': 'foo', 'b': ['bar']})
        _assert_count_is(3, given={'a': 'foo', 'b': ['c', 'd']})
        _assert_count_is(3, given={'a': 'foo', 'b': ['c', 'd', None]})
        _assert_count_is(3, given={'a': 'foo', 'b': ['c', 'd', []]})
        _assert_count_is(4, given={'a': 'foo', 'b': ['c', 'd', 'e']})
        _assert_count_is(4, given={'a': 'foo', 'b': ['c', 'd', 'e'], 'foo': None})
        _assert_count_is(4, given={'a': 'foo', 'b': ['c', 'd', 'e'], 'foo': []})
        _assert_count_is(4, given={'a': 'foo', 'b': ['c', 'd', 'e'], 'foo': ['']})
        _assert_count_is(5, given={'a': 'foo', 'b': ['c', 'd', 'e'], 'foo': ['g']})
        _assert_count_is(6, given={'a': 'foo', 'b': ['c', 'd', 'e'], 'foo': ['g', 'h']})


class TestExpandMeowURIDataDict(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.EXPECTED = DUMMY_RESULTS_DICT
        self.INPUT = DUMMY_FLATTENED_RESULTS_DICT

    def test_raises_type_error_for_invalid_input(self):
        with self.assertRaises(TypeError):
            expand_meowuri_data_dict(None)
            expand_meowuri_data_dict([])
            expand_meowuri_data_dict('')

    def test_returns_expected_type(self):
        actual = expand_meowuri_data_dict(self.INPUT)

        self.assertIsInstance(actual, dict)

    def test_returns_expected_len(self):
        actual = len(expand_meowuri_data_dict(self.INPUT))
        expected = len(self.EXPECTED)

        self.assertEqual(actual, expected)

    def test_expanded_dict_contains_all_expected(self):
        actual = expand_meowuri_data_dict(self.INPUT)
        self.assertDictEqual(actual, self.EXPECTED)

    def test_expanded_dict_contain_expected_first_level(self):
        actual = expand_meowuri_data_dict(self.INPUT)
        self.assertIn('A', actual)
        self.assertIn('B', actual)

    def test_expanded_dict_contain_expected_second_level(self):
        actual = expand_meowuri_data_dict(self.INPUT)
        actual_A = actual.get('A')
        actual_contents = actual.get('B')

        self.assertIn('A1', actual_A)
        self.assertIn('A2', actual_A)
        self.assertIn('A3', actual_A)
        self.assertIn('B1', actual_contents)
        self.assertIn('B2', actual_contents)
        self.assertIn('B3', actual_contents)


class TestNestedDictGet(TestCase):
    def test_get_nested_value_returns_expected(self):
        key_list = ['A', 'A3', 'A3A']
        actual = nested_dict_get(DUMMY_RESULTS_DICT, key_list)
        self.assertEqual(actual, 'd')

    def test_get_nested_values_returns_expected(self):
        keys_expected = [(['A', 'A3', 'A3A'], 'd'),
                         (['A', 'A1', 'A1A'], 'a'),
                         (['A', 'A1', 'A1B'], 'b'),
                         (['A', 'A2', 'foo'], 'c'),
                         (['B', 'B1', 'B1A'], 'e'),
                         (['B', 'B1', 'B1B'], 'foo'),
                         (['B', 'B2', 'B2A'], 'g'),
                         (['B', 'B2', 'B2B'], 'h'),
                         (['B', 'B3', 'B3A'], True),
                         (['B', 'B3', 'B3B'], False)]

        for key_list, expected in keys_expected:
            actual = nested_dict_get(DUMMY_RESULTS_DICT, key_list)
            self.assertEqual(actual, expected)

    def test_missing_keys_raises_key_error(self):
        d = {'a': {'b': {'c': 5}}}

        def _assert_raises(key_list):
            with self.assertRaises(KeyError):
                nested_dict_get(d, key_list)

        _assert_raises([None])
        _assert_raises([''])
        _assert_raises(['q'])
        _assert_raises(['a', 'q'])
        _assert_raises(['a', 'b', 'q'])
        _assert_raises(['a', 'b', 'c', 'q'])

    def test_passing_no_keys_raises_type_error(self):
        d = {'a': {'b': {'c': 5}}}

        def _assert_raises(key_list):
            with self.assertRaises(TypeError):
                nested_dict_get(d, key_list)

        _assert_raises('')
        _assert_raises(None)


class TestNestedDictSet(TestCase):
    def _assert_sets(self, dictionary, list_of_keys, value, expected):
        _ = nested_dict_set(dictionary, list_of_keys, value)
        self.assertIsNone(_)
        self.assertDictEqual(dictionary, expected)
        self.assertTrue(key in dictionary for key in expected.keys())

    def test_set_value_in_empty_dictionary(self):
        self._assert_sets(dictionary={}, list_of_keys=['a'],
                          value=1, expected={'a': 1})
        self._assert_sets(dictionary={}, list_of_keys=['a', 'b'],
                          value=2, expected={'a': {'b': 2}})
        self._assert_sets(dictionary={}, list_of_keys=['a', 'b', 'c'],
                          value=3, expected={'a': {'b': {'c': 3}}})

    def test_set_value_in_empty_dictionary_with_fileobject_key(self):
        keys = [uu.get_mock_fileobject()]
        self._assert_sets(dictionary={}, list_of_keys=keys, value=1,
                          expected={keys[0]: 1})

        keys = [uu.get_mock_fileobject(), uu.get_mock_fileobject()]
        self._assert_sets(dictionary={}, list_of_keys=keys, value='foo',
                          expected={keys[0]: {keys[1]: 'foo'}})

    def test_set_value_modifies_dictionary_in_place(self):
        d = {'a': 1}
        self._assert_sets(dictionary=d, list_of_keys=['a'], value=2,
                          expected={'a': 2})
        self._assert_sets(dictionary=d, list_of_keys=['b'], value={},
                          expected={'a': 2,
                                    'b': {}})
        self._assert_sets(dictionary=d, list_of_keys=['b', 'c'], value=4,
                          expected={'a': 2,
                                    'b': {'c': 4}})
        self._assert_sets(dictionary=d, list_of_keys=['b', 'foo'], value=6,
                          expected={'a': 2,
                                    'b': {'c': 4,
                                          'foo': 6}})
        self._assert_sets(dictionary=d, list_of_keys=['b', 'foo'], value=8,
                          expected={'a': 2,
                                    'b': {'c': 4,
                                          'foo': 8}})

    def test_attempting_to_set_occupied_value_raises_key_error(self):
        with self.assertRaises(KeyError):
            self._assert_sets(dictionary={'a': 1}, list_of_keys=['a', 'b'],
                              value=5, expected={'a': 2})

    def test_passing_invalid_list_of_keys_raises_type_error(self):
        def _assert_raises(key_list):
            with self.assertRaises(TypeError):
                self._assert_sets(dictionary={'a': 1}, list_of_keys=key_list,
                                  value=2, expected={'expect_exception': 0})

        _assert_raises(key_list='')
        _assert_raises(key_list=None)
        _assert_raises(key_list=())
        _assert_raises(key_list={})
        _assert_raises(key_list={'a': None})
        _assert_raises(key_list={'a': 'b'})

    def test_passing_empty_list_raises_value_error(self):
        def _assert_raises(key_list):
            with self.assertRaises(ValueError):
                self._assert_sets(dictionary={'a': 1}, list_of_keys=key_list,
                                  value=2, expected={'expect_exception': 0})

        _assert_raises(key_list=[''])
        _assert_raises(key_list=[None])
        _assert_raises(key_list=[None, ''])
        _assert_raises(key_list=['', None])
        _assert_raises(key_list=[None, 'foo'])
        _assert_raises(key_list=['foo', None])
        _assert_raises(key_list=['foo', ''])
        _assert_raises(key_list=['', 'foo'])
        _assert_raises(key_list=[None, 'foo', ''])
        _assert_raises(key_list=[None, '', 'foo'])
        _assert_raises(key_list=['foo', None, ''])
        _assert_raises(key_list=['', None, 'foo'])
        _assert_raises(key_list=['foo', None, '', None])
        _assert_raises(key_list=['', None, 'foo', None])
        _assert_raises(key_list=['foo', None, 'a', 'b'])
        _assert_raises(key_list=['', 'a', 'b', None])
        _assert_raises(key_list=['', 'a', 'b', 'foo'])


class TestNestedDictSetRetrieveLists(TestCase):
    def test_stores_empty_list(self):
        d = dict()
        nested_dict_set(d, ['a', 'b'], [])
        actual = nested_dict_get(d, ['a', 'b'])
        self.assertEqual(actual, [])

    def test_stores_list_one_element(self):
        d = dict()
        nested_dict_set(d, ['a', 'b'], [1])
        actual = nested_dict_get(d, ['a', 'b'])
        self.assertEqual(actual, [1])

    def test_stores_list_two_elements(self):
        d = dict()
        nested_dict_set(d, ['a', 'b'], [1, 2])
        actual = nested_dict_get(d, ['a', 'b'])
        self.assertEqual(actual, [1, 2])


class TestWhichExecutable(TestCase):
    def test_returns_true_for_executable_commands(self):
        self.assertTrue(is_executable('python'))

    def test_returns_false_for_bogus_commands(self):
        self.assertFalse(is_executable('thisisntexecutablesurely'))


class TestContainsNone(TestCase):
    def _assert_false(self, test_data):
        actual = contains_none(test_data)
        self.assertFalse(actual)
        self.assertIsInstance(actual, bool)

    def _assert_true(self, test_data):
        actual = contains_none(test_data)
        self.assertTrue(actual)
        self.assertIsInstance(actual, bool)

    def test_returns_true_as_expected(self):
        self._assert_true([])
        self._assert_true([None])
        self._assert_true([None, None])
        self._assert_true(['', None])
        self._assert_true([None, ''])
        self._assert_true([None, '', None])
        self._assert_true(['', None, ''])
        self._assert_true([None, 'a'])
        self._assert_true(['a', None])
        self._assert_true([None, 'a', None])
        self._assert_true(['a', None, 'a'])
        self._assert_true(['a', None, ''])

    def test_returns_false_as_expected(self):
        self._assert_false([''])
        self._assert_false([' '])
        self._assert_false(['a', ''])
        self._assert_false([' ', 'a'])
        self._assert_false([' ', 'a', ''])


class TestGitCommitHash(TestCase):
    def test_returns_expected_type(self):
        actual = git_commit_hash()
        self.assertTrue(uu.is_internalstring(actual))

    def test_resets_curdir(self):
        curdir_before = os.path.curdir
        _ = git_commit_hash()
        curdir_after = os.path.curdir

        self.assertEqual(curdir_before, curdir_after)

    def _setup_mock_popen(self, mock_popen, return_code=None, stdout=None, stderr=None):
        def __communicate():
            return stdout, stderr

        if return_code is None:
            return_code = 0
        if stdout is None:
            stdout = b''

        mock_popen.return_value = MagicMock(returncode=return_code)
        mock_popen_instance = mock_popen.return_value
        mock_popen_instance.communicate = __communicate

    @patch('util.misc.subprocess.Popen')
    def test_returns_none_if_repository_not_found(self, mock_popen):
        self._setup_mock_popen(
            mock_popen,
            stdout=b'fatal: Not a git repository (or any of the parent directories): .git\n',
            stderr=None
        )

        actual = git_commit_hash()
        self.assertIsNone(actual)
