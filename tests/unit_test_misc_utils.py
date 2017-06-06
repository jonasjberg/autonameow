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

from core.exceptions import InvalidQueryStringError
from core.util.misc import (
    unique_identifier,
    multiset_count,
    query_string_list,
    flatten_dict
)


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
        self.assertEqual(query_string_list('a.b'), ['a', 'b'])



class TestFlattenDict(TestCase):
    def setUp(self):
        self.maxDiff = None
        self.INPUT = {
            'filesystem': {
                'basename': None,
                'extension': None,
                'pathname': None,
            },
            'contents': {
                'mime_type': None,
                'textual': {
                    'raw_text': None,
                    'number_pages': None,
                },
                'visual': {
                    'ocr_text': None,
                    'ocr_tags': None
                },
                'binary': {

                }
            },
            'metadata': {
                'exiftool': {}
            }
        }
        self.EXPECTED = {
            'filesystem.basename': None,
            'filesystem.extension': None,
            'filesystem.pathname': None,
            'contents.mime_type': None,
            'contents.textual.raw_text': None,
            'contents.textual.number_pages': None,
            'contents.visual.ocr_text': None,
            'contents.visual.ocr_tags': None,
            'contents.binary': None,
            'metadata.exiftool': None
        }

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
        self.assertEqual(len(actual), 8)

    def test_returns_expected(self):
        actual = flatten_dict(self.INPUT)

        for k, v in actual.items():
            self.assertTrue(k in self.EXPECTED)
            self.assertEqual(actual[k], self.EXPECTED[k])
