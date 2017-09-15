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
from extractors import ExtractedData


class TestExtractedData(TestCase):
    def test_wraps_primitives(self):
        a = ExtractedData(wrapper=types.AW_BOOLEAN)
        a('true')
        self.assertEqual(a.value, True)

        b = ExtractedData(wrapper=types.AW_BOOLEAN)
        b(True)
        self.assertEqual(b.value, True)

        c = ExtractedData(wrapper=types.AW_INTEGER)
        c('1.0')
        self.assertEqual(c.value, 1)

    def test_autodetects_wrapper_given_primitives(self):
        a = ExtractedData(wrapper=None)
        a(True)
        self.assertEqual(a.value, True)
        self.assertTrue(isinstance(a.wrapper, types.Boolean))
        self.assertEqual(a.wrapper, types.AW_BOOLEAN)

        b = ExtractedData(wrapper=None)
        b('foo')
        self.assertEqual(b.value, 'foo')
        self.assertTrue(isinstance(b.wrapper, types.String))
        self.assertEqual(b.wrapper, types.AW_STRING)

    def test_todo(self):
        self.skipTest('TODO: ..')
        d = ExtractedData(
            wrapper=types.AW_EXIFTOOLTIMEDATE,
            # mapped_fields=[
            #     fields.WeightedMapping(fields.datetime, probability=1),
            #     fields.WeightedMapping(fields.date, probability=1)
            # ],
            # generic_field=fields.GenericDateCreated
        )
