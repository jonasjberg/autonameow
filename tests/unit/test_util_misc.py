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
from unittest.mock import MagicMock, patch

import unit.utils as uu
from util.misc import count_dict_recursive
from util.misc import flatten_sequence_type
from util.misc import git_commit_hash


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
        # Call 'cache_clear()' added by the 'functools.lru_cache' decorator.
        git_commit_hash.cache_clear()

        actual = git_commit_hash()
        self.assertIsNone(actual)
