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

from core import (
    fields,
    types
)
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
            mapped_fields=[
                fields.WeightedMapping('foo_field_a', probability=1.0),
                fields.WeightedMapping('foo_field_b', probability=0.8)
            ])

        self.assertIsNotNone(m)
