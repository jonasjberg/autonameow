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

from core import util
from extractors.textual import (
    TextExtractor,
    PdfTextExtractor
)
from unit_utils import (
    make_temporary_file,
    abspath_testfile
)


class TestTextExtractor(TestCase):
    def setUp(self):
        self.e = TextExtractor(make_temporary_file())

    def test_text_extractor_class_is_available(self):
        self.assertIsNotNone(TextExtractor)

    def test_text_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_method__get_raw_text_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e._get_raw_text()

    def test_query_returns_false_without__get_raw_text_implemented(self):
        self.assertFalse(self.e.query())
        self.assertFalse(self.e.query(field='some_field'))


class TestPdfTextExtractor(TestCase):
    def setUp(self):
        test_file = util.normpath(abspath_testfile('gmail.pdf'))
        self.e = PdfTextExtractor(test_file)

    def test_pdf_text_extractor_class_is_available(self):
        self.assertIsNotNone(PdfTextExtractor)

    def test_pdf_text_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test__get_raw_text_returns_something(self):
        self.assertIsNotNone(self.e._get_raw_text())

    def test__get_raw_text_returns_expected_type(self):
        self.assertEqual(type(self.e._get_raw_text()), str)
