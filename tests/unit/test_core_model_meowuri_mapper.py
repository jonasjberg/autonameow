# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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

import unit.constants as uuconst
import unit.utils as uu
from core.model.meowuri_mapper import GenericMeowUriMapper
from core.model.meowuri_mapper import MeowUriLeafMapper
from core.model.genericfields import GenericPublisher
from core.model.genericfields import GenericTitle


class TestMeowUriLeafMapper(TestCase):
    def test_instantiated_mapper_is_not_none(self):
        mapper = MeowUriLeafMapper(valid_generic_field_uri_leaves=[])
        self.assertIsNotNone(mapper)

    def test_not_yet_mapped_explicit_uri_returns_empty_set(self):
        mapper = MeowUriLeafMapper(valid_generic_field_uri_leaves=['publisher'])

        explicit_uri = uu.as_meowuri('extractor.metadata.exiftool.XMP-dc:Publisher')
        actual = mapper.fetch(explicit_uri)
        self.assertEqual(0, len(actual))
        self.assertEqual(set(), actual)

    def test_explicit_uri_mapped_to_leaf_alias_can_be_retrieved_with_alias(self):
        mapper = MeowUriLeafMapper(valid_generic_field_uri_leaves=['publisher'])

        generic_uri = GenericPublisher.uri()
        explicit_uri = uu.as_meowuri('extractor.metadata.exiftool.XMP-dc:Publisher')
        mapper.map(explicit_uri, generic_uri)

        aliased_leaf_uri = uu.as_meowuri('extractor.metadata.exiftool.publisher')
        actual = mapper.fetch(aliased_leaf_uri)
        self.assertEqual(1, len(actual))
        self.assertIn(explicit_uri, actual)

    def test_all_explicit_uris_mapped_to_leaf_alias_can_be_retrieved_with_alias(self):
        mapper = MeowUriLeafMapper(valid_generic_field_uri_leaves=['title'])

        generic_uri = GenericTitle.uri()
        explicit_uri_A = uu.as_meowuri('extractor.metadata.exiftool.XMP:Title')
        explicit_uri_B = uu.as_meowuri('extractor.metadata.exiftool.PDF:Title')
        mapper.map(explicit_uri_A, generic_uri)
        mapper.map(explicit_uri_B, generic_uri)

        aliased_leaf_uri = uu.as_meowuri('extractor.metadata.exiftool.title')
        actual = mapper.fetch(aliased_leaf_uri)
        self.assertEqual(2, len(actual))
        self.assertIn(explicit_uri_A, actual)
        self.assertIn(explicit_uri_B, actual)


class TestGenericMeowUriMapper(TestCase):
    def test_instantiated_mapper_is_not_none(self):
        mapper = GenericMeowUriMapper()
        self.assertIsNotNone(mapper)

    def test_not_yet_mapped_generic_uri_returns_empty_set(self):
        mapper = GenericMeowUriMapper()

        generic_uri = uu.as_meowuri(uuconst.MEOWURI_GEN_METADATA_TITLE)
        actual = mapper.fetch(generic_uri)
        self.assertEqual(0, len(actual))
        self.assertEqual(set(), actual)

    def test_explicit_uri_mapped_to_generic_uri_can_be_retrieved_with_generic_uri(self):
        mapper = GenericMeowUriMapper()

        generic_uri = uu.as_meowuri(uuconst.MEOWURI_GEN_METADATA_TITLE)
        explicit_uri = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCTITLE)
        mapper.map(explicit_uri, generic_uri)

        actual = mapper.fetch(generic_uri)
        self.assertEqual(1, len(actual))
        self.assertIn(explicit_uri, actual)

    def test_all_explicit_uris_mapped_to_generic_uri_can_be_retrieved_with_generic_uri(self):
        mapper = GenericMeowUriMapper()

        generic_uri = uu.as_meowuri(uuconst.MEOWURI_GEN_METADATA_TITLE)
        explicit_uri_A = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCTITLE)
        explicit_uri_B = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_TITLE)
        mapper.map(explicit_uri_A, generic_uri)
        mapper.map(explicit_uri_B, generic_uri)

        actual = mapper.fetch(generic_uri)
        self.assertEqual(2, len(actual))
        self.assertIn(explicit_uri_A, actual)
        self.assertIn(explicit_uri_B, actual)
