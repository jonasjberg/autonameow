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
import unit_utils as uu

from extractors.textual import (
    AbstractTextExtractor
)


class TestTextExtractor(TestCase):
    def setUp(self):
        self.e = AbstractTextExtractor(uu.make_temporary_file())

    def test_text_extractor_class_is_available(self):
        self.assertIsNotNone(AbstractTextExtractor)

    def test_text_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_method__get_raw_text_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e._get_raw_text()

    def test_query_returns_false_without__get_raw_text_implemented(self):
        self.assertFalse(self.e.query())
        self.assertFalse(self.e.query(field='some_field'))


