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

from extractors.metadata import (
    AbstractMetadataExtractor,
)


class TestAbstractMetadataExtractor(TestCase):
    def setUp(self):
        self.e = AbstractMetadataExtractor(uu.make_temporary_file())

    def test_abstract_metadata_extractor_class_is_available(self):
        self.assertIsNotNone(AbstractMetadataExtractor)

    def test_abstract_metadata_extractor_class_can_be_instantiated(self):
        self.assertIsNotNone(self.e)

    def test_method__get_raw_metadata_raises_not_implemented_error(self):
        with self.assertRaises(NotImplementedError):
            self.e._get_raw_metadata()

    def test_query_returns_none_without__get_raw_metadata_implemented(self):
        self.assertIsNone(self.e.query())
        self.assertIsNone(self.e.query(field='some_field'))

    def test_abstract_class_does_not_specify_which_mime_types_are_handled(self):
        self.assertIsNone(self.e.handles_mime_types)

    def test_abstract_class_does_not_specify_data_query_string(self):
        self.assertIsNone(self.e.data_query_string)

    def test__perform_initial_extraction_returns_none(self):
        actual = self.e._perform_initial_extraction()
        self.assertIsNone(actual)
