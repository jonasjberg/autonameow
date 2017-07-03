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

from core import types


class TestBaseType(TestCase):
    def setUp(self):
        self.t = types.BaseType()

    def test_null(self):
        self.assertEqual(self.t.primitive_type(''), self.t.null)

    def test_normalize(self):
        self.assertEqual(self.t.null, self.t.normalize(None))
        self.assertEqual('foo', self.t.normalize('foo'))


class TestIntegerType(TestCase):
    def setUp(self):
        self.t = types.Integer()

    def test_null(self):
        self.assertEqual(self.t.null, 0)
        self.assertNotEqual(self.t.null, -1)

    def test_normalize(self):
        self.assertEqual(self.t.normalize(None), self.t.null)
        self.assertEqual(self.t.normalize(-1), -1)
        self.assertEqual(self.t.normalize(0), 0)
        self.assertEqual(self.t.normalize(1), 1)


class TestFloatType(TestCase):
    def setUp(self):
        self.t = types.Float()

    def test_null(self):
        self.assertEqual(self.t.null, 0)
        self.assertNotEqual(self.t.null, -1)

    def test_normalize(self):
        self.assertEqual(self.t.normalize(None), self.t.null)
        self.assertEqual(self.t.normalize(-1), -1)
        self.assertEqual(self.t.normalize(0), 0)
        self.assertEqual(self.t.normalize(1), 1)
