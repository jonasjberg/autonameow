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
from core.exceptions import InvalidMeowURIError
from core.util import eval_magic_glob
from core.util.misc import (
    unique_identifier,
    multiset_count,
    meowuri_list,
    flatten_dict,
    expand_meowuri_data_dict,
    nested_dict_get,
    nested_dict_set
)


DUMMY_RESULTS_DICT = {
    'filesystem': {
        'basename': {
            'full': 'a',
            'extension': 'b'
        },
        'pathname': {
            'full': 'c',
        },
        'contents': {
            'mime_type': 'd'
        }
    },
    'contents': {
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
}

DUMMY_FLATTENED_RESULTS_DICT = {
    'filesystem.basename.full': 'a',
    'filesystem.basename.extension': 'b',
    'filesystem.pathname.full': 'c',
    'filesystem.contents.mime_type': 'd',
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


class TestMeowURIList(TestCase):
    def test_raises_exception_for_none_argument(self):
        with self.assertRaises(InvalidMeowURIError):
            self.assertIsNone(meowuri_list(None))

    def test_raises_exception_for_empty_argument(self):
        with self.assertRaises(InvalidMeowURIError):
            self.assertIsNone(meowuri_list(''))

    def test_raises_exception_for_only_periods(self):
        with self.assertRaises(InvalidMeowURIError):
            self.assertIsNone(meowuri_list('.'))
            self.assertIsNone(meowuri_list('..'))
            self.assertIsNone(meowuri_list('...'))

    def test_return_value_is_type_list(self):
        self.assertTrue(isinstance(meowuri_list('a.b'), list))

    def test_valid_argument_returns_expected(self):
        self.assertEqual(meowuri_list('a'), ['a'])
        self.assertEqual(meowuri_list('a.b'), ['a', 'b'])
        self.assertEqual(meowuri_list('a.b.c'), ['a', 'b', 'c'])
        self.assertEqual(meowuri_list('a.b.c.a'), ['a', 'b', 'c', 'a'])
        self.assertEqual(meowuri_list('a.b.c.a.b'),
                         ['a', 'b', 'c', 'a', 'b'])
        self.assertEqual(meowuri_list('a.b.c.a.b.c'),
                         ['a', 'b', 'c', 'a', 'b', 'c'])

    def test_valid_argument_returns_expected_for_unexpected_input(self):
        self.assertEqual(meowuri_list('a.b.'), ['a', 'b'])
        self.assertEqual(meowuri_list('a.b..'), ['a', 'b'])
        self.assertEqual(meowuri_list('.a.b'), ['a', 'b'])
        self.assertEqual(meowuri_list('..a.b'), ['a', 'b'])
        self.assertEqual(meowuri_list('a..b'), ['a', 'b'])
        self.assertEqual(meowuri_list('.a..b'), ['a', 'b'])
        self.assertEqual(meowuri_list('..a..b'), ['a', 'b'])
        self.assertEqual(meowuri_list('...a..b'), ['a', 'b'])
        self.assertEqual(meowuri_list('a..b.'), ['a', 'b'])
        self.assertEqual(meowuri_list('a..b..'), ['a', 'b'])
        self.assertEqual(meowuri_list('a..b...'), ['a', 'b'])
        self.assertEqual(meowuri_list('a...b'), ['a', 'b'])
        self.assertEqual(meowuri_list('.a...b'), ['a', 'b'])
        self.assertEqual(meowuri_list('..a...b'), ['a', 'b'])
        self.assertEqual(meowuri_list('...a...b'), ['a', 'b'])
        self.assertEqual(meowuri_list('a...b.'), ['a', 'b'])
        self.assertEqual(meowuri_list('a...b..'), ['a', 'b'])
        self.assertEqual(meowuri_list('a...b...'), ['a', 'b'])

    def test_returns_expected(self):
        self.assertEqual(meowuri_list('filesystem.contents.mime_type'),
                         ['filesystem', 'contents', 'mime_type'])
        self.assertEqual(meowuri_list('metadata.exiftool.EXIF:Foo'),
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

        self.assertTrue(isinstance(actual, dict))

    def test_returns_expected_len(self):
        actual = len(expand_meowuri_data_dict(self.INPUT))
        expected = len(self.EXPECTED)

        self.assertEqual(actual, expected)

    def test_expanded_dict_contains_all_expected(self):
        actual = expand_meowuri_data_dict(self.INPUT)
        self.assertDictEqual(actual, self.EXPECTED)

    def test_expanded_dict_contain_expected_first_level(self):
        actual = expand_meowuri_data_dict(self.INPUT)
        self.assertIn('filesystem', actual)
        self.assertIn('contents', actual)

    def test_expanded_dict_contain_expected_second_level(self):
        actual = expand_meowuri_data_dict(self.INPUT)
        actual_filesystem = actual.get('filesystem')
        actual_contents = actual.get('contents')

        self.assertIn('basename', actual_filesystem)
        self.assertIn('pathname', actual_filesystem)
        self.assertIn('contents', actual_filesystem)
        self.assertIn('textual', actual_contents)
        self.assertIn('visual', actual_contents)
        self.assertIn('binary', actual_contents)


class TestNestedDictGet(TestCase):
    def test_nested_dict_get_is_defined(self):
        self.assertIsNotNone(nested_dict_get)

    def test_get_nested_value_returns_expected(self):
        key_list = ['filesystem', 'contents', 'mime_type']
        actual = nested_dict_get(DUMMY_RESULTS_DICT, key_list)
        self.assertEqual(actual, 'd')

    def test_get_nested_values_returns_expected(self):
        keys_expected = [(['filesystem', 'contents', 'mime_type'], 'd'),
                         (['filesystem', 'basename', 'full'], 'a'),
                         (['filesystem', 'basename', 'extension'], 'b'),
                         (['filesystem', 'pathname', 'full'], 'c'),
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
    def test_nested_dict_set_is_defined(self):
        self.assertIsNotNone(nested_dict_set)

    def test_set_single_value_in_empty_dictionary(self):
        d = {}
        nested_dict_set(d, ['a'], 2)
        expected = {'a': 2}
        self.assertEqual(d, expected)

    def test_set_single_value_modifies_dictionary_in_place(self):
        actual = {'a': 1}
        nested_dict_set(actual, ['a'], 2)
        expected = {'a': 2}
        self.assertEqual(actual, expected)

    def test_set_nested_value_modifies_dictionary_in_place(self):
        actual = {'a': 1}
        nested_dict_set(actual, ['b', 'c'], 4)
        expected = {'a': 1,
                    'b': {'c': 4}}
        self.assertEqual(actual, expected)

    def test_set_nested_values_modifies_dictionary_in_place(self):
        actual = {'a': 1}
        nested_dict_set(actual, ['b', 'c'], 4)
        nested_dict_set(actual, ['b', 'd'], 5)
        expected = {'a': 1,
                    'b': {'c': 4,
                          'd': 5}}
        self.assertEqual(actual, expected)

    def test_attempting_to_set_occupied_value_raises_key_error(self):
        actual = {'a': 1}
        with self.assertRaises(KeyError):
            nested_dict_set(actual, ['a', 'b'], 5)

    def test_passing_no_keys_raises_type_error(self):
        d = {'a': 1}

        def _assert_raises(key_list):
            with self.assertRaises(TypeError):
                nested_dict_set(d, key_list, 2)

        _assert_raises('')
        _assert_raises(None)

    def test_passing_empty_list_raises_value_error(self):
        d = {'a': 1}

        def _assert_raises(key_list):
            with self.assertRaises(ValueError):
                nested_dict_set(d, key_list, 2)

        _assert_raises([''])
        _assert_raises([None])
        _assert_raises([None, ''])
        _assert_raises(['', None])
        _assert_raises([None, 'foo'])
        _assert_raises(['foo', None])
        _assert_raises(['foo', ''])
        _assert_raises(['', 'foo'])


class TestEvalMagicGlob(TestCase):
    def test_eval_magic_blob_is_defined(self):
        self.assertIsNotNone(eval_magic_glob)

    def test_eval_magic_blob_returns_false_given_bad_arguments(self):
        self.assertIsNotNone(eval_magic_glob(None, None))
        self.assertFalse(eval_magic_glob(None, None))

    def test_eval_magic_blob_raises_exception_given_bad_arguments(self):
        with self.assertRaises(ValueError):
            self.assertTrue(eval_magic_glob('image/jpeg', ['*/*/jpeg']))

    def test_eval_magic_blob_returns_false_as_expected(self):
        self.assertFalse(eval_magic_glob('image/jpeg', []))
        self.assertFalse(eval_magic_glob('image/jpeg', ['']))
        self.assertFalse(eval_magic_glob('image/jpeg', ['application/pdf']))
        self.assertFalse(eval_magic_glob('image/jpeg', ['*/pdf']))
        self.assertFalse(eval_magic_glob('image/jpeg', ['image/pdf']))
        self.assertFalse(eval_magic_glob('image/jpeg', ['image/pdf',
                                                        'application/jpeg']))
        self.assertFalse(eval_magic_glob('image/jpeg', ['image/']))
        self.assertFalse(eval_magic_glob('image/jpeg', ['/jpeg']))
        self.assertFalse(eval_magic_glob('image/jpeg', ['*/pdf', '*/png']))
        self.assertFalse(eval_magic_glob('image/jpeg',
                                         ['*/pdf', '*/png', 'application/*']))
        self.assertFalse(eval_magic_glob('image/png',
                                         ['*/pdf', '*/jpg', 'application/*']))
        self.assertFalse(eval_magic_glob('image/png',
                                         ['*/pdf', '*/jpg', 'image/jpg']))
        self.assertFalse(eval_magic_glob('application/epub+zip',
                                         ['*/jpg']))
        self.assertFalse(eval_magic_glob('application/epub+zip',
                                         ['image/*']))
        self.assertFalse(eval_magic_glob('application/epub+zip',
                                         ['image/jpeg']))

    def test_eval_magic_blob_returns_true_as_expected(self):
        self.assertTrue(eval_magic_glob('image/jpeg', ['*/*']))
        self.assertTrue(eval_magic_glob('image/jpeg', ['*/jpeg']))
        self.assertTrue(eval_magic_glob('image/jpeg', ['image/*']))
        self.assertTrue(eval_magic_glob('image/png', ['image/*']))
        self.assertTrue(eval_magic_glob('image/jpeg', ['image/jpeg']))
        self.assertTrue(eval_magic_glob('image/jpeg', ['*/*', '*/jpeg']))
        self.assertTrue(eval_magic_glob('image/jpeg', ['image/*', '*/jpeg']))
        self.assertTrue(eval_magic_glob('image/png',
                                        ['*/pdf', '*/png', 'application/*']))
        self.assertTrue(eval_magic_glob('application/epub+zip',
                                        ['application/epub+zip']))
        self.assertTrue(eval_magic_glob('application/epub+zip',
                                        ['application/*']))
        self.assertTrue(eval_magic_glob('application/epub+zip',
                                        ['*/epub+zip']))


class TestWhichExecutable(TestCase):
    def test_returns_true_for_executable_commands(self):
        self.assertTrue(util.is_executable('python'))

    def test_returns_false_for_bogus_commands(self):
        self.assertFalse(util.is_executable('thisisntexecutablesurely'))
