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

from core import constants as C
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
                    'Mapped MeowURI "{!s}" to "{!s}" ({!s})'.format(meowuri,
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

    def providers_for_meowuri(self, requested_meowuri, includes=None):
        """
        Returns a set of classes that might store data under a given "MeowURI".

        Note that the provider "MeowURI" is matched as a substring of the
        requested "MeowURI".

        Args:
            requested_meowuri: The "MeowURI" of interest.
            includes: Optional list of provider roots to include.
                      Must be one of 'C.MEOWURI_ROOTS_SOURCES'.
                      Default is to include all.

        Returns:
            A set of classes that "could" produce and store data under a
            "MeowURI" that is a substring of the given "MeowURI".
        """
        found = set()
        if not requested_meowuri:
            log.error('"providers_for_meowuri()" got empty MeowURI!')
            return found

        def _search_providers_with_root(root):
            # '_meowuri' is shorter "root";
            #            'extractor.metadata.epub'
            # 'requested_meowuri' is full "source-specific";
            #                     'extractor.metadata.exiftool.EXIF:CreateDate'
            for _meowuri in self.meowuri_sources[root].keys():
                if _meowuri in requested_meowuri:
                    return self.meowuri_sources[root][_meowuri]
            return None

        # TODO: [TD0147] This currently only uses the first found provider!
        if not includes:
            # TODO: Simplify by matching substrings here.
            # NOTE(jonas): Sort for more consistent behaviour.
            for root in sorted(C.MEOWURI_ROOTS_SOURCES):
                _found_provider = _search_providers_with_root(root)
                if _found_provider:
                    found.add(_found_provider)
            return found

        VALID_INCLUDES = C.MEOWURI_ROOTS_SOURCES
        for include in includes:
            assert include in VALID_INCLUDES, (
                '"{!s}" is not one of {!s}'.format(include, VALID_INCLUDES)
            )

            result = _search_providers_with_root(include)
            if result is not None:
                found.add(result)

        return found

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
    def __root_meowuris_for_providers(module_name):
        """
        Returns a dict mapping "MeowURIs" to extractor classes.

        Example return value: {
            'extractor.filesystem.xplat': CrossPlatformFilesystemExtractor,
            'extractor.metadata.exiftool': ExiftoolMetadataExtractor,
            'extractor.text.pdftotext': PdftotextTextExtractor
        }

        Returns: Dictionary keyed by Unicode string "MeowURIs",
                 storing extractor classes.
        """
        _klass_list = getattr(module_name, 'ProviderClasses')
        assert isinstance(_klass_list, list), type(_klass_list)

        mapping = dict()
        for klass in _klass_list:
            _meowuri = klass.meowuri_prefix()
            if not _meowuri:
                log.critical('Got empty from '
                             '"{!s}.meowuri_prefix()"'.format(klass.__name__))
                continue

            assert _meowuri not in mapping, (
                'Provider MeowURI "{!s}" is already mapped'.format(_meowuri)
            )
            mapping[_meowuri] = klass

        return mapping

    import analyzers
    import extractors
    import plugins
    return {
        'extractor': __root_meowuris_for_providers(extractors),
        'analyzer': __root_meowuris_for_providers(analyzers),
        'plugin': __root_meowuris_for_providers(plugins)
    }


def get_providers_for_meowuris(meowuri_list, include_roots=None):
    providers = set()
    if not meowuri_list:
        return providers

    for uri in meowuri_list:
        source_classes = Registry.providers_for_meowuri(uri, include_roots)
        providers.update(source_classes)
    return providers


Registry = None


def initialize():
    # Keep one global 'ProviderRegistry' singleton per 'Autonameow' instance.
    global Registry
    if not Registry:
        Registry = ProviderRegistry(
            meowuri_source_map=_get_meowuri_source_map()
        )
