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
    types,
    fields
)
from extractors import ExtractedData


class TestExtractedData(TestCase):
    def test_call(self):
        m = ExtractedData(
            coercer=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping('foo_field_a', probability=1.0),
                fields.WeightedMapping('foo_field_b', probability=0.8)
            ])

        self.assertIsNotNone(m)
