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
from extractors import (
    ExtractedData,
    ExtractorError
)
from extractors.metadata.common import AbstractMetadataExtractor
import unit_utils as uu


class TestAbstractMetadataExtractor(TestCase):
    def setUp(self):
        self.test_file = uu.make_temporary_file()
        self.e = AbstractMetadataExtractor()

    def test_class_is_available(self):
        self.assertIsNotNone(AbstractMetadataExtractor)

    def test_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_method__get_raw_metadata_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e._get_raw_metadata(self.test_file)

    def test_query_raises_exception_with__get_raw_metadata_unimplemented(self):
        with self.assertRaises(ExtractorError):
            self.assertIsNone(self.e(self.test_file))

        with self.assertRaises(ExtractorError):
            self.assertIsNone(self.e(self.test_file, field='some_field'))

    def test_abstract_class_does_not_specify_which_mime_types_are_handled(self):
        self.assertIsNone(self.e.handles_mime_types)

    def test_abstract_class_does_not_specify_meowuri_root(self):
        self.assertIsNone(self.e.meowuri_root)

    def test__perform_initial_extraction_raises_extractor_error(self):
        with self.assertRaises(ExtractorError):
            _ = self.e.execute(self.test_file)

    def test_check_dependencies_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e.check_dependencies()


class TestExtractedData(TestCase):
    def test_call(self):
        m = ExtractedData(
            wrapper=types.AW_STRING,
            mapped_fields=[
                fields.WeightedMapping('foo_field_a', probability=1.0),
                fields.WeightedMapping('foo_field_b', probability=0.8)
            ])

        self.assertIsNotNone(m)
