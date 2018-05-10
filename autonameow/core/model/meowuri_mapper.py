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

from collections import defaultdict

from core.model import genericfields
from core.model import MeowURI


# TODO: [TD0125] Add aliases (generics) for MeowURI leafs


class MeowUriLeafMapper(object):
    def __init__(self, all_generic_field_uri_leaves):
        self._all_generic_field_uri_leaves = set(all_generic_field_uri_leaves)

        # Stores references from URIs with "aliased" leaves to "explicit" URIs.
        # I.E. URIs like; 'extractor.metadata.exiftool.publisher'
        #   maps to URIs: 'extractor.metadata.exiftool.XMP-dc:Publisher'
        self._aliased_leaf_to_explicit_uri_map = defaultdict(set)

    def map(self, uri, generic_uri):
        """
        Stores a mapping between a "explicit" URI and a "generic" URI for
        translation from "explicit" URIs with "generic" (aliased) leaves.

        That is, given URI: 'extractor.metadata.exiftool.XMP-dc:Publisher'
           and generic URI: 'generic.metadata.publisher' (GenericPublisher)

        Future calls to 'fetch()' with 'extractor.metadata.exiftool.publisher'
        will return 'extractor.metadata.exiftool.XMP-dc:Publisher'.
        """
        self._map_generic_leaf_alias_if_possible(uri, generic_uri)

    def fetch(self, uri):
        """Translates a URI with an "aliased" leaf to a full "explicit" URI."""
        if uri in self._aliased_leaf_to_explicit_uri_map:
            return self._aliased_leaf_to_explicit_uri_map[uri]

        return uri

    def _map_generic_leaf_alias_if_possible(self, uri, generic_uri):
        generic_uri_leaf = generic_uri.uri().leaf
        if generic_uri_leaf in self._all_generic_field_uri_leaves:
            self._map_generic_leaf_alias(generic_uri_leaf, uri)

    def _map_generic_leaf_alias(self, generic_field_leaf, explicit_uri):
        explicit_uri_without_leaf = explicit_uri.stripleaf()

        leaf_alias_uri = MeowURI(explicit_uri_without_leaf, generic_field_leaf)
        self._aliased_leaf_to_explicit_uri_map[leaf_alias_uri].add(explicit_uri)


leaves = MeowUriLeafMapper(
    all_generic_field_uri_leaves=genericfields.get_all_generic_field_uri_leaves()
)
