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

from core.util.misc import (
    unique_identifier,
    multiset_count
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
