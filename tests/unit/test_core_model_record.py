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
from core.model.fields import Title
from core.model.record import Record
from core.model.record import RecordComparator


# From 'notes/metadata_processing.md':
#
#     r1 = Record(Author('Gibson'), Title('Meow'), ISBN('123456789'))
#     r2 = Record(Author('Gibson'), Title('Meow'))
#     r3 = Record(Author('G.'), Title('Meow'))
#     assert r1.weight > r2.weight > r3.weight
#
# HOWEVER, I don't think this is such a good idea..


FIELD_1 = Author('Gibson')
FIELD_2 = Title('Meow')


class TestRecordInit(TestCase):
    def test_instantiated_record_is_not_none_given_one_field(self):
        r1 = Record(FIELD_1)
        self.assertIsNotNone(r1)

    def test_instantiated_record_is_not_none_given_two_fields(self):
        r2 = Record(FIELD_1, FIELD_2)
        self.assertIsNotNone(r2)


class TestRecordBasics(TestCase):
    def setUp(self):
        self.r1 = Record(FIELD_1)
        self.r2 = Record(FIELD_1, FIELD_2)

    def test_len(self):
        self.assertEqual(len(self.r1), 1)
        self.assertEqual(len(self.r2), 2)

    def test_contains(self):
        self.assertIn(FIELD_1, self.r1)
        self.assertNotIn(FIELD_2, self.r1)

        self.assertIn(FIELD_1, self.r2)
        self.assertIn(FIELD_2, self.r2)


class TestRecordComparator(TestCase):
    def setUp(self):
        self.c = RecordComparator()

    def _check(self, *records, expect=None):
        actual = self.c.weigh(*records)
        self.assertEqual(actual, expect)

    def test_prefer_record_with_more_fields(self):
        r1 = Record(Author('Gibson'))
        r2 = Record(Author('Gibson'), Title('Meow'))
        self._check(r1, r2, expect=r2)

    def test_prefer_record_with_complete_fields(self):
        r1 = Record(Author(''))
        r2 = Record(Author('Gibson'))
        self._check(r1, r2, expect=r2)

    def test_prefer_record_with_more_complete_field(self):
        r1 = Record(Author('Gibson Sjöberg'))
        r2 = Record(Author('Gibson'))
        self._check(r1, r2, expect=r1)

        r3 = Record(Author('Gibso'))
        r4 = Record(Author('Gibson'))
        self._check(r3, r4, expect=r4)
