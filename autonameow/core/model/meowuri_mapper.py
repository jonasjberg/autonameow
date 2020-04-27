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

import logging
from collections import defaultdict

from core.model import genericfields
from core.model import MeowURI


log = logging.getLogger(__name__)


class MeowUriLeafMapper(object):
    def __init__(self, valid_generic_field_uri_leaves):
        """
        Provides aliases (generics) for MeowURI leafs
        """
        # Used to validate leaves of incoming 'generic_uri'.
        self._valid_generic_field_uri_leaves = set(valid_generic_field_uri_leaves)

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
        generic_uri_leaf = generic_uri.leaf
        if generic_uri_leaf in self._valid_generic_field_uri_leaves:
            self._map_generic_leaf_alias(generic_uri_leaf, uri)

    def fetch(self, uri):
        """Translates a URI with an "aliased" leaf to a full "explicit" URI."""
        result = self._aliased_leaf_to_explicit_uri_map.get(uri)
        return result or set()

    def _map_generic_leaf_alias(self, generic_uri_leaf, explicit_uri):
        explicit_uri_without_leaf = explicit_uri.stripleaf()

        leaf_alias_uri = MeowURI(explicit_uri_without_leaf, generic_uri_leaf)
        log.debug('Mapping aliased leaf MeowURI %s to explicit MeowURI %s',
                  leaf_alias_uri, explicit_uri)
        self._aliased_leaf_to_explicit_uri_map[leaf_alias_uri].add(explicit_uri)


class GenericMeowUriMapper(object):
    def __init__(self):
        """Stores mapping from "generic" to "explicit" URIs."""
        self._generic_to_explicit_uri_map = defaultdict(set)

    def map(self, uri, generic_uri):
        self._map_generic_to_explicit_uri(generic_uri, uri)

    def fetch(self, generic_uri):
        result = self._get_explicit_uris_from_generic_uri(generic_uri)
        return result or set()

    def _map_generic_to_explicit_uri(self, generic_uri, explicit_uri):
        if explicit_uri in self._generic_to_explicit_uri_map[generic_uri]:
            return

        log.debug('Mapping generic MeowURI %s to explicit MeowURI %s',
                  generic_uri, explicit_uri)
        self._generic_to_explicit_uri_map[generic_uri].add(explicit_uri)

    def _get_explicit_uris_from_generic_uri(self, generic_uri):
        return self._generic_to_explicit_uri_map.get(generic_uri)


leaves = MeowUriLeafMapper(
    valid_generic_field_uri_leaves=genericfields.get_all_generic_field_uri_leaves()
)

generic = GenericMeowUriMapper()
