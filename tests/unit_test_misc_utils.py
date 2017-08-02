#!/usr/bin/env python3
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

from core import util
from core.exceptions import InvalidQueryStringError
from core.util.misc import (
    unique_identifier,
    multiset_count,
    query_string_list,
    flatten_dict,
    expand_query_string_dict,
    dict_lookup,
    nested_dict_get
)


DUMMY_RESULTS_DICT = {
    'filesystem': {
        'basename': {
            'full': 'a',
            'extension': 'b'
        },
        'pathname': {
            'full': 'c',
        }
    },
    'contents': {
        'mime_type': 'd',
        'textual': {
            'raw_text': 'e',
            'number_pages': 'f',
        },
        'visual': {
            'ocr_text': 'g',
            'ocr_tags': 'h'},
        'binary': {
            'boolean_true': True,
            'boolean_false': False
        }
    },
    'metadata': {
        'exiftool': {}
    }
}

DUMMY_FLATTENED_RESULTS_DICT = {
    'filesystem.basename.full': 'a',
    'filesystem.basename.extension': 'b',
    'filesystem.pathname.full': 'c',
    'contents.mime_type': 'd',
    'contents.textual.raw_text': 'e',
    'contents.textual.number_pages': 'f',
    'contents.visual.ocr_text': 'g',
    'contents.visual.ocr_tags': 'h',
    'contents.binary.boolean_true': True,
    'contents.binary.boolean_false': False,
}


class TestUniqueIdentifier(TestCase):
    def test_unique_identifier_returns_not_none(self):
        self.assertIsNotNone(unique_identifier())

    def test_unique_identifier_returns_string(self):
        uuid = unique_identifier()
        self.assertTrue(isinstance(uuid, str))

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

    def test_list_duplicate_count_returns_expected_no_duplicates(self):
        self.assertEqual(multiset_count(['a', 'b', 'c']),
                         {'a': 1, 'b': 1, 'c': 1})

    def test_list_duplicate_count_returns_expected_one_duplicate(self):
        self.assertEqual(multiset_count(['a', 'a', 'c']),
                         {'a': 2, 'c': 1})

    def test_list_duplicate_count_returns_expected_only_duplicates(self):
        self.assertEqual(multiset_count(['a', 'a', 'a']),
                         {'a': 3})

    def test_list_duplicate_count_returns_expected_no_duplicate_one_none(self):
        self.assertEqual(multiset_count(['a', None, 'b']),
                         {None: 1, 'a': 1, 'b': 1})

    def test_list_duplicate_count_returns_expected_one_duplicate_one_none(self):
        self.assertEqual(multiset_count(['b', None, 'b']),
                         {None: 1, 'b': 2})

    def test_list_duplicate_count_returns_expected_no_duplicate_two_none(self):
        self.assertEqual(multiset_count(['a', None, 'b', None]),
                         {None: 2, 'a': 1, 'b': 1})


class TestQueryStringList(TestCase):
    def test_raises_exception_for_none_argument(self):
        with self.assertRaises(InvalidQueryStringError):
            self.assertIsNone(query_string_list(None))

    def test_raises_exception_for_empty_argument(self):
        with self.assertRaises(InvalidQueryStringError):
            self.assertIsNone(query_string_list(''))

    def test_raises_exception_for_only_periods(self):
        with self.assertRaises(InvalidQueryStringError):
            self.assertIsNone(query_string_list('.'))
            self.assertIsNone(query_string_list('..'))
            self.assertIsNone(query_string_list('...'))

    def test_return_value_is_type_list(self):
        self.assertTrue(isinstance(query_string_list('a.b'), list))

    def test_valid_argument_returns_expected(self):
        self.assertEqual(query_string_list('a'), ['a'])
        self.assertEqual(query_string_list('a.b'), ['a', 'b'])
        self.assertEqual(query_string_list('a.b.c'), ['a', 'b', 'c'])
        self.assertEqual(query_string_list('a.b.c.a'), ['a', 'b', 'c', 'a'])
        self.assertEqual(query_string_list('a.b.c.a.b'),
                         ['a', 'b', 'c', 'a', 'b'])
        self.assertEqual(query_string_list('a.b.c.a.b.c'),
                         ['a', 'b', 'c', 'a', 'b', 'c'])

    def test_valid_argument_returns_expected_for_unexpected_input(self):
        self.assertEqual(query_string_list('a.b.'), ['a', 'b'])
        self.assertEqual(query_string_list('a.b..'), ['a', 'b'])
        self.assertEqual(query_string_list('.a.b'), ['a', 'b'])
        self.assertEqual(query_string_list('..a.b'), ['a', 'b'])
        self.assertEqual(query_string_list('a..b'), ['a', 'b'])
        self.assertEqual(query_string_list('.a..b'), ['a', 'b'])
        self.assertEqual(query_string_list('..a..b'), ['a', 'b'])
        self.assertEqual(query_string_list('...a..b'), ['a', 'b'])
        self.assertEqual(query_string_list('a..b.'), ['a', 'b'])
        self.assertEqual(query_string_list('a..b..'), ['a', 'b'])
        self.assertEqual(query_string_list('a..b...'), ['a', 'b'])
        self.assertEqual(query_string_list('a...b'), ['a', 'b'])
        self.assertEqual(query_string_list('.a...b'), ['a', 'b'])
        self.assertEqual(query_string_list('..a...b'), ['a', 'b'])
        self.assertEqual(query_string_list('...a...b'), ['a', 'b'])
        self.assertEqual(query_string_list('a...b.'), ['a', 'b'])
        self.assertEqual(query_string_list('a...b..'), ['a', 'b'])
        self.assertEqual(query_string_list('a...b...'), ['a', 'b'])

    def test_returns_expected(self):
        self.assertEqual(query_string_list('contents.mime_type'),
                         ['contents', 'mime_type'])
        self.assertEqual(query_string_list('metadata.exiftool.EXIF:Foo'),
                         ['metadata', 'exiftool', 'EXIF:Foo'])


class TestFlattenDict(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.INPUT = DUMMY_RESULTS_DICT
        self.EXPECTED = DUMMY_FLATTENED_RESULTS_DICT

    def test_raises_type_error_for_invalid_input(self):
        with self.assertRaises(TypeError):
            flatten_dict(None)
            flatten_dict([])
            flatten_dict('')

    def test_returns_expected_type(self):
        actual = flatten_dict(self.INPUT)

        self.assertTrue(isinstance(actual, dict))

    def test_returns_expected_len(self):
        actual = flatten_dict(self.INPUT)
        self.assertEqual(len(actual), 10)

    def test_flattened_dict_contains_expected(self):
        actual = flatten_dict(self.INPUT)

        for k, v in self.EXPECTED.items():
            self.assertEqual(actual[k], self.EXPECTED[k])


class TestFlattenDictWithRawMetadata(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.INPUT = {
            '_raw_metadata': {
                'CreationDate': '2016-01-11',
                'Creator': 'Chromium',
                'ModDate': '2016-01-11 12:41:32',
                'Producer': 'Skia/PDF',
                'encrypted': False,
                'number_pages': 2,
                'paginated': True
            }
        }
        self.EXPECTED = {
            '_raw_metadata.CreationDate': '2016-01-11',
            '_raw_metadata.Creator': 'Chromium',
            '_raw_metadata.ModDate': '2016-01-11 12:41:32',
            '_raw_metadata.Producer': 'Skia/PDF',
            '_raw_metadata.encrypted': False,
            '_raw_metadata.number_pages': 2,
            '_raw_metadata.paginated': True,
        }

    def test_returns_expected_type(self):
        actual = flatten_dict(self.INPUT)
        self.assertTrue(isinstance(actual, dict))

    def test_returns_expected_len(self):
        actual = flatten_dict(self.INPUT)
        self.assertEqual(len(actual), 7)

    def test_flattened_dict_contains_expected(self):
        actual = flatten_dict(self.INPUT)

        for k, v in self.EXPECTED.items():
            self.assertEqual(actual[k], self.EXPECTED[k])


class TestCountDictRecursive(TestCase):
    def test_count_dict_recursive_function_is_defined(self):
        self.assertIsNotNone(util.count_dict_recursive)

    def test_raises_exception_for_invalid_input(self):
        with self.assertRaises(TypeError):
            util.count_dict_recursive([])
            util.count_dict_recursive([{}])
            util.count_dict_recursive([{'foo': []}])

    def test_returns_zero_given_none_or_false(self):
        self.assertEqual(util.count_dict_recursive(None), 0)
        self.assertEqual(util.count_dict_recursive(False), 0)

    def test_returns_zero_given_empty_dictionary(self):
        self.assertEqual(util.count_dict_recursive({}), 0)
        self.assertEqual(util.count_dict_recursive({'foo': {}}), 0)
        self.assertEqual(util.count_dict_recursive({'foo': {'bar': {}}}), 0)

    def test_returns_zero_given_empty_containers(self):
        def _assert_zero(test_data):
            self.assertEqual(util.count_dict_recursive(test_data), 0)

        _assert_zero({'a': []})
        _assert_zero({'a': [[]]})
        _assert_zero({'a': [None]})
        _assert_zero({'a': [None, None]})
        _assert_zero({'a': {'b': []}})
        _assert_zero({'a': {'b': [[]]}})
        _assert_zero({'a': {'b': [None]}})
        _assert_zero({'a': {'b': [None, None]}})
        _assert_zero({'a': {'b': {'c': []}}})
        _assert_zero({'a': {'b': {'c': [[]]}}})
        _assert_zero({'a': {'b': {'c': [None]}}})
        _assert_zero({'a': {'b': {'c': [None, None]}}})

    def test_returns_expected_count(self):
        def _assert_count(test_data, expect_count):
            self.assertEqual(util.count_dict_recursive(test_data), expect_count)

        _assert_count({'a': 'foo'}, 1)
        _assert_count({'a': 'foo', 'b': None}, 1)
        _assert_count({'a': 'foo', 'b': []}, 1)
        _assert_count({'a': 'foo', 'b': 'bar'}, 2)
        _assert_count({'a': 'foo', 'b': ['bar']}, 2)
        _assert_count({'a': 'foo', 'b': ['c', 'd']}, 3)
        _assert_count({'a': 'foo', 'b': ['c', 'd', None]}, 3)
        _assert_count({'a': 'foo', 'b': ['c', 'd', []]}, 3)
        _assert_count({'a': 'foo', 'b': ['c', 'd', 'e']}, 4)
        _assert_count({'a': 'foo', 'b': ['c', 'd', 'e'], 'f': None}, 4)
        _assert_count({'a': 'foo', 'b': ['c', 'd', 'e'], 'f': []}, 4)
        _assert_count({'a': 'foo', 'b': ['c', 'd', 'e'], 'f': ['']}, 4)
        _assert_count({'a': 'foo', 'b': ['c', 'd', 'e'], 'f': ['g']}, 5)
        _assert_count({'a': 'foo', 'b': ['c', 'd', 'e'], 'f': ['g', 'h']}, 6)


class TestDictLookup(TestCase):
    def test_passing_none_argument_returns_none(self):
        d = {'a': 5}
        actual = dict_lookup(d, None)
        self.assertIsNone(actual)

    def test_lookup_missing_key_returns_none(self):
        d = {'a': 5}
        actual = dict_lookup(d, 'b')
        self.assertIsNone(actual)

    def test_lookup_single_argument_returns_expected(self):
        d = {'a': 5}
        actual = dict_lookup(d, 'a')
        self.assertEqual(actual, 5)

    def test_nested_lookup_multiple_arguments_returns_expected(self):
        d = {'a': {'b': {'c': 5}}}
        actual = dict_lookup(d, 'a', 'b', 'c')
        self.assertEqual(actual, 5)

        arguments_expected = [((d, 'a', 'b', 'c'), 5),
                              ((d, 'a', 'b'),      {'c': 5}),
                              ((d, 'a'),           {'b': {'c': 5}})]
        for arguments, expected in arguments_expected:
            self.assertEqual(dict_lookup(*arguments), expected)

    def test_nested_lookup_argument_list_returns_expected(self):
        d = {'a': {'b': {'c': 5}}}
        actual = dict_lookup(d, *['a', 'b', 'c'])
        self.assertEqual(actual, 5)


class TestNestedDictGet(TestCase):
    def test_nested_dict_get_is_defined(self):
        self.assertIsNotNone(nested_dict_get)

    def test_get_nested_value_returns_expected(self):
        key_list = ['contents', 'mime_type']
        actual = nested_dict_get(DUMMY_RESULTS_DICT, key_list)
        self.assertEqual(actual, 'd')

    def test_get_nested_values_returns_expected(self):
        keys_expected = [(['contents', 'mime_type'], 'd'),
                         (['filesystem', 'basename', 'full'], 'a'),
                         (['filesystem', 'basename', 'extension'], 'b'),
                         (['filesystem', 'pathname', 'full'], 'c'),
                         (['contents', 'mime_type'], 'd'),
                         (['contents', 'textual', 'raw_text'], 'e'),
                         (['contents', 'textual', 'number_pages'], 'f'),
                         (['contents', 'visual', 'ocr_text'], 'g'),
                         (['contents', 'visual', 'ocr_tags'], 'h'),
                         (['contents', 'binary', 'boolean_true'], True),
                         (['contents', 'binary', 'boolean_false'], False)]

        for key_list, expected in keys_expected:
            actual = nested_dict_get(DUMMY_RESULTS_DICT, key_list)
            self.assertEqual(actual, expected)

    def test_missing_keys_raises_key_error(self):
        def _assert_raises(key_list):
            d = {'a': {'b': {'c': 5}}}
            with self.assertRaises(KeyError):
                nested_dict_get(d, key_list)

        _assert_raises([None])
        _assert_raises([''])
        _assert_raises(['q'])
        _assert_raises(['a', 'q'])
        _assert_raises(['a', 'b', 'q'])
        _assert_raises(['a', 'b', 'c', 'q'])

    def test_passing_no_keys_raises_type_error(self):
        def _assert_raises(key_list):
            d = {'a': {'b': {'c': 5}}}
            with self.assertRaises(TypeError):
                nested_dict_get(d, key_list)

        _assert_raises('')
        _assert_raises(None)
