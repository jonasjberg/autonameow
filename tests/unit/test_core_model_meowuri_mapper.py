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

import unit.utils as uu
from core.model.meowuri_mapper import MeowURIMapper
from core.model.genericfields import GenericPublisher
from core.model.genericfields import GenericTitle


class TestMeowURIMapper(TestCase):
    def test_instantiated_mapper_is_not_none(self):
        mapper = MeowURIMapper(all_generic_field_uri_leaves=[])
        self.assertIsNotNone(mapper)

    def test_not_yet_mapped_explicit_uri_is_returned_as_is(self):
        mapper = MeowURIMapper(all_generic_field_uri_leaves=['publisher'])

        explicit_uri = uu.as_meowuri('extractor.metadata.exiftool.XMP-dc:Publisher')
        actual = mapper.fetch(explicit_uri)
        self.assertEqual(explicit_uri, actual)

    def test_explicit_uri_mapped_to_leaf_alias_can_be_retrieved_with_alias(self):
        mapper = MeowURIMapper(all_generic_field_uri_leaves=['publisher'])

        explicit_uri = uu.as_meowuri('extractor.metadata.exiftool.XMP-dc:Publisher')
        mapper.map(explicit_uri, GenericPublisher)

        aliased_leaf_uri = uu.as_meowuri('extractor.metadata.exiftool.publisher')
        actual = mapper.fetch(aliased_leaf_uri)
        self.assertIn(explicit_uri, actual)

    def test_all_explicit_uris_mapped_to_leaf_alias_can_be_retrieved_with_alias(self):
        mapper = MeowURIMapper(all_generic_field_uri_leaves=['title'])

        explicit_uri_A = uu.as_meowuri('extractor.metadata.exiftool.XMP:Title')
        mapper.map(explicit_uri_A, GenericTitle)
        explicit_uri_B = uu.as_meowuri('extractor.metadata.exiftool.PDF:Title')
        mapper.map(explicit_uri_B, GenericTitle)

        aliased_leaf_uri = uu.as_meowuri('extractor.metadata.exiftool.title')
        actual = mapper.fetch(aliased_leaf_uri)
        self.assertIn(explicit_uri_A, actual)
        self.assertIn(explicit_uri_B, actual)
