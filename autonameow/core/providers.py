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

import logging

from core import types


log = logging.getLogger(__name__)


class ProviderMixin(object):
    def __init__(self):
        pass

    def coerce_field_value(self, field, value):
        _field_lookup_entry = self.FIELD_LOOKUP.get(field)
        if not _field_lookup_entry:
            self.log.debug('Field not in "FIELD_LOOKUP"; "{!s}" with value:'
                           ' "{!s}" ({!s})'.format(field, value, type(value)))
            return None

        try:
            _coercer = _field_lookup_entry.get('coercer')
        except AttributeError:
            # Might be case of malformed 'FIELD_LOOKUP'.
            _coercer = None
        if not _coercer:
            self.log.debug('Coercer unspecified for field; "{!s}" with value:'
                           ' "{!s}" ({!s})'.format(field, value, type(value)))
            return None

        assert _coercer and isinstance(_coercer, types.BaseType), (
               'Got ({!s}) "{!s}"'.format(type(_coercer), _coercer))
        wrapper = _coercer

        if isinstance(value, list):
            # Check "FIELD_LOOKUP" assumptions.
            if not _field_lookup_entry.get('multivalued'):
                self.log.warning(
                    'Got list but "FIELD_LOOKUP" specifies a single value.'
                    ' Tag: "{!s}" Value: "{!s}"'.format(field, value)
                )
                return None

            try:
                return types.listof(wrapper)(value)
            except types.AWTypeError as e:
                self.log.debug('Coercing "{!s}" with value "{!s}" raised '
                               'AWTypeError: {!s}'.format(field, value, e))
                return None
        else:
            # Check "FIELD_LOOKUP" assumptions.
            if _field_lookup_entry.get('multivalued'):
                self.log.warning(
                    'Got single value but "FIELD_LOOKUP" specifies multiple.'
                    ' Tag: "{!s}" Value: "{!s}"'.format(field, value)
                )
                return None

            try:
                return wrapper(value)
            except types.AWTypeError as e:
                self.log.debug('Coercing "{!s}" with value "{!s}" raised '
                               'AWTypeError: {!s}'.format(field, value, e))
                return None


class ProviderRegistry(object):
    def __init__(self, meowuri_source_map):
        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )

        self.meowuri_sources = meowuri_source_map
        assert isinstance(self.meowuri_sources, dict)

        # Debug logging
        for key in self.meowuri_sources.keys():
            for meowuri, klass in self.meowuri_sources[key].items():
                self.log.debug(
                    'Mapped meowURI "{!s}" to "{!s}" ({!s})'.format(meowuri,
                                                                    klass, key)
                )

        # Set of all MeowURIs "registered" by extractors, analyzers or plugins.
        self.mapped_meowuris = self.unique_map_meowuris(self.meowuri_sources)

    def resolvable(self, meowuri):
        if not meowuri:
            return False

        resolvable = list(self.mapped_meowuris)
        # TODO: [TD0113] Fix exceptions not being handled properly (?)
        if any(r in meowuri for r in resolvable):
            return True
        return False

    def provider_for_meowuri(self, requested_meowuri, includes=None):
        """
        Returns a list of classes that could store data using a given "MeowURI".

        Args:
            requested_meowuri: The "MeowURI" of interest.
            includes: Optional list of sources to include. Default: include all

        Returns:
            A list of classes that "could" produce and store data under a
            MeowURI that "matches" (!) the given MeowURI.
        """
        def _search_source_type(root):
            for _meowuri in self.meowuri_sources[root].keys():
                if _meowuri in requested_meowuri:
                    return self.meowuri_sources[root][_meowuri]
            return None

        if not requested_meowuri:
            log.error('"provider_for_meowuri()" got empty MeowURI!')
            return []

        if includes is None:
            return (_search_source_type('extractor')
                    or _search_source_type('analyzer')
                    or _search_source_type('plugin')
                    or [])
        else:
            if not isinstance(includes, list):
                includes = [includes]
            for include in includes:
                if include not in ('analyzer', 'extractor', 'plugin'):
                    continue

                result = _search_source_type(include)
                if result is not None:
                    return result

            return []

    @staticmethod
    def unique_map_meowuris(meowuri_class_map):
        out = set()

        # for key in ['extractors', 'analyzer', 'plugin'] ..
        for key in meowuri_class_map.keys():
            for _meowuri in meowuri_class_map[key].keys():
                assert not isinstance(_meowuri, list), (
                    'Unexpectedly got "meowuri" of type list')
                out.add(_meowuri)

        return out


def _get_meowuri_source_map():
    """
    The 'MeowURIClassMap' attributes in non-core modules keep
    references to the available component classes.
    These are dicts with keys being the "meowURIs" that the respective
    component uses when storing data and the contained values are lists of
    classes mapped to the "meowURI".

    Returns: Dictionary keyed by "MeowURIs", storing lists of "source" classes.
    """
    import analyzers
    import extractors
    import plugins
    return {
        'extractor': extractors.MeowURIClassMap,
        'analyzer': analyzers.MeowURIClassMap,
        'plugin': plugins.MeowURIClassMap
    }


def get_providers_for_meowuris(meowuri_list, include_roots=None):
    if not meowuri_list:
        return []

    out = set()
    for uri in meowuri_list:
        source_classes = Registry.provider_for_meowuri(uri, include_roots)

        # TODO: Improve robustness of linking "MeowURIs" to data source classes.
        if source_classes:
            assert isinstance(source_classes, list)
            for source in source_classes:
                out.add(source)

    return list(out)


Registry = None


def initialize():
    # Keep one global 'ProviderRegistry' singleton per 'Autonameow' instance.
    global Registry
    if not Registry:
        Registry = ProviderRegistry(
            meowuri_source_map=_get_meowuri_source_map()
        )
