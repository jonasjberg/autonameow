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

from core.model.fields import Author


# From 'notes/metadata_processing.md':
#
#     f1 = Field('AUTHOR', 'Gibson Sjöberg')
#     f2 = Field('AUTHOR', 'Gibson')
#     f3 = Field('AUTHOR', 'G.S.')
#     f4 = Field('AUTHOR', 'G')
#     assert f1 == f2
#     assert f1 != f3
#     assert f1 != f4
#     assert f1.weight == f2.weight > f3.weight > f4.weight
#
#
# Alternatively:
#
#     f1 = Author('Gibson Sjöberg')
#     f2 = Author('Gibson')
#     f3 = Author('G.S.')
#     f4 = Author('G')
#     assert f1 == f2
#     assert f1 != f3
#     assert f1 != f4
#     assert f1.weight == f2.weight > f3.weight > f4.weight


# class TestTitleFieldComparison(TestCase):
#     EQUIVALENT_TITLES = [
#         'AI Algorithms, Data Structures, And Idioms In Prolog, Lisp, And Java',
#         'AI Algorithms Data Structures and Idioms in Prolog Lisp and Java',
#         'ai algorithms data structures and idioms in prolog lisp and java'
#     ]


class TestAuthorFieldComparison(TestCase):
    def setUp(self):
        self.f1 = Author('Gibson Sjöberg')
        self.f1b = Author('Gibson Sjöberg')
        self.f1c = Author('Gibson  Sjöberg')
        self.f1d = Author('gibson  sjöberg')
        self.f2 = Author('Gibson')
        self.f3 = Author('G.S.')
        self.f4 = Author('G')

    def test_identical_full_names_are_equal(self):
        self.assertEqual(self.f1, self.f1b)

    def test_trivially_different_full_names_are_equal(self):
        self.assertEqual(self.f1, self.f1c)
        self.assertEqual(self.f1, self.f1d)

    def test_full_name_not_equal_only_first_name(self):
        self.assertNotEqual(self.f1, self.f3)

    def test_full_name_not_equal_to_abbreviation_only_first_name(self):
        self.assertNotEqual(self.f1, self.f3)

    def test_single_character_not_equal_to_any_other_field(self):
        self.assertNotEqual(self.f1, self.f4)
        self.assertNotEqual(self.f2, self.f4)
        self.assertNotEqual(self.f3, self.f4)
