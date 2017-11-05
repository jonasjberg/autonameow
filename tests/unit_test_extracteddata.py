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
from core.model import ExtractedData


class TestExtractedData(TestCase):
    def test_wraps_primitives(self):
        a = ExtractedData(coercer=types.AW_BOOLEAN)
        a('true')
        self.assertEqual(a.value, True)

        b = ExtractedData(coercer=types.AW_BOOLEAN)
        b(True)
        self.assertEqual(b.value, True)

        c = ExtractedData(coercer=types.AW_INTEGER)
        c('1.0')
        self.assertEqual(c.value, 1)

    def test_autodetects_coercer_given_primitives(self):
        a = ExtractedData(coercer=None)
        a(True)
        self.assertEqual(a.value, True)
        self.assertTrue(isinstance(a.coercer, types.Boolean))
        self.assertEqual(a.coercer, types.AW_BOOLEAN)

        b = ExtractedData(coercer=None)
        b('foo')
        self.assertEqual(b.value, 'foo')
        self.assertTrue(isinstance(b.coercer, types.String))
        self.assertEqual(b.coercer, types.AW_STRING)

    def test_call(self):
        m = ExtractedData(
            coercer=types.AW_STRING,
            multivalued=False
        )
        self.assertIsNotNone(m)

    def test_from_raw(self):
        e = ExtractedData(
            coercer=types.AW_STRING,
        )
        given = 'foo'
        expect = 'foo'
        d = ExtractedData.from_raw(e, given)
        self.assertEqual(d.value, expect)

    def test_from_raw_multivalued(self):
        e = ExtractedData(
            coercer=types.AW_STRING,
            multivalued=True
        )
        given = ['foo', 'bar']
        expect = ['foo', 'bar']
        d = ExtractedData.from_raw(e, given)
        self.assertEqual(d.value, expect)

    def test_from_raw_multivalued_coercion(self):
        e = ExtractedData(
            coercer=types.AW_STRING,
            multivalued=True
        )
        given = [1, 1.337]
        expect = ['1', '1.337']
        d = ExtractedData.from_raw(e, given)
        self.assertEqual(d.value, expect)

    def test_call_not_multivalued(self):
        with self.assertRaises(types.AWTypeError):
            _ = ExtractedData(
                coercer=types.AW_STRING,
                multivalued=False
            )(['foo', 'bar'])

    def test_call_not_multivalued_coercion(self):
        with self.assertRaises(types.AWTypeError):
            _ = ExtractedData(
                coercer=types.AW_STRING,
                multivalued=False
            )([1, 1.337])

    def test_from_raw_not_multivalued(self):
        e = ExtractedData(
            coercer=types.AW_STRING,
            multivalued=False
        )
        given = ['foo', 'bar']
        d = ExtractedData.from_raw(e, given)
        self.assertIsNone(d)

    def test_from_raw_not_multivalued_coercion(self):
        e = ExtractedData(
            coercer=types.AW_STRING,
            multivalued=False
        )
        given = [1, 1.337]
        d = ExtractedData.from_raw(e, given)
        self.assertIsNone(d)
