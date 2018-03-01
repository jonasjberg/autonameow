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

import logging

from core import constants as C
from core import types
from core.model import (
    genericfields,
    WeightedMapping
)
from core.namebuilder.fields import nametemplatefield_class_from_string
from util import sanity


log = logging.getLogger(__name__)


class ProviderMixin(object):
    def __init__(self):
        pass

    def coerce_field_value(self, field, value):
        # TODO: [TD0157] Look into analyzers 'FIELD_LOOKUP' attributes.
        # TODO: [hack] This is very bad.
        _field_lookup_entry = self.metainfo().get(field)
        if not _field_lookup_entry:
            self.log.debug(
                'Field not in "FIELD_LOOKUP" (through "metainfo()" method); '
                '"{!s}" with value: "{!s}" ({!s})'.format(field, value,
                                                          type(value)))
            return None

        try:
            coercer_string = _field_lookup_entry.get('coercer')
        except AttributeError:
            # Might be case of malformed 'FIELD_LOOKUP'.
            coercer_string = None

        if not coercer_string:
            self.log.warning('Coercer unspecified for field; "{!s}" with value:'
                             ' "{!s}" ({!s})'.format(field, value, type(value)))
            return None

        sanity.check_internal_string(coercer_string)
        coercer = get_coercer_from_metainfo_string(coercer_string)
        assert isinstance(coercer, (types.BaseType, types.MultipleTypes)), (
            'Got ({!s}) "{!s}"'.format(type(coercer), coercer)
        )

        if 'multivalued' not in _field_lookup_entry:
            self.log.debug(
                'Multivalued unspecified for field; "{!s}" with value:'
                ' "{!s}" ({!s})'.format(field, value, type(value))
            )

        if isinstance(value, list):
            # Check "FIELD_LOOKUP" assumptions.
            if not _field_lookup_entry.get('multivalued'):
                self.log.warning(
                    'Got list but "FIELD_LOOKUP" specifies a single value.'
                    ' Tag: "{!s}" Value: "{!s}"'.format(field, value)
                )
                return None

            try:
                return types.listof(coercer)(value)
            except types.AWTypeError as e:
                self.log.debug('Coercing "{!s}" with value "{!s}" raised '
                               'AWTypeError: {!s}'.format(field, value, e))
                return None
        else:
            # Check "FIELD_LOOKUP" assumptions.
            if _field_lookup_entry.get('multivalued'):
                self.log.debug(
                    'Got single value but "FIELD_LOOKUP" specifies multiple. '
                    'Coercing to list. Tag: "{!s}" Value: "{!s}"'.format(field,
                                                                         value)
                )
            try:
                return coercer(value)
            except types.AWTypeError as e:
                self.log.debug('Coercing "{!s}" with value "{!s}" raised '
                               'AWTypeError: {!s}'.format(field, value, e))
                return None


def wrap_provider_results(datadict, metainfo, source_klass):
    """
    Translates metainfo to internal format and merges it with source and data.

    Args:
        datadict: Provider results data, keys are provider-specific fields
                  storing coerced data as primitive types.
        metainfo: Additional information keyed by provider-specific fields.
        source_klass: The provider class that produced this data.

    Returns:
        A dict with various information bundled with the actual data.
    """
    sanity.check_isinstance(metainfo, dict,
                            msg='Source provider: {!s}'.format(source_klass))
    log.debug('Wrapping provider {!s} results (datadict len: {}) (metainfo len: {})'.format(source_klass, len(datadict), len(metainfo)))

    wrapped = dict()

    for field, value in datadict.items():
        raw_field_metainfo = metainfo.get(field, {})
        if not raw_field_metainfo:
            log.warning('Missing metainfo for field "{!s}"'.format(field))
            log.debug('Field {} not in {!s}'.format(field, metainfo))
            continue

        field_metainfo = _translate_field_metainfo_to_internal_format(raw_field_metainfo)
        if not field_metainfo:
            log.warning('Translation of metainfo to internal format failed for provider {!s} field "{!s}"'.format(source_klass, field))
            continue

        wrapped[field] = _wrap_provider_result_field(field_metainfo, source_klass, value)

    return wrapped


def _translate_field_metainfo_to_internal_format(field_metainfo):
    # TODO: [TD0146] Rework "generic fields". Possibly bundle in "records".
    _field_metainfo = dict(field_metainfo)
    internal_field_metainfo = dict()

    coercer_klass = get_coercer_from_metainfo_string(_field_metainfo.get('coercer'))
    if coercer_klass is None:
        # TODO: Improve robustness. Raise appropriate exception.
        # TODO: Improve robustness. Log provider with malformed metainfo entries.
        # Fail by returning None if coercer is missing.
        return None

    internal_field_metainfo['coercer'] = coercer_klass

    mapped_fields_strings = _field_metainfo.get('mapped_fields')
    if mapped_fields_strings:
        translated_mapped_fields = translate_metainfo_mappings(mapped_fields_strings)
        if translated_mapped_fields:
            internal_field_metainfo['mapped_fields'] = translated_mapped_fields

    # Map strings to generic field classes.
    generic_field_string = _field_metainfo.get('generic_field')
    if generic_field_string:
        generic_field_klass = genericfields.get_field_for_uri_leaf(generic_field_string)
        if generic_field_klass:
            internal_field_metainfo['generic_field'] = generic_field_klass

    multivalued_string = _field_metainfo.get('multivalued')
    if multivalued_string is not None:
        translated_multivalued = translate_multivalued(multivalued_string)
        if translated_multivalued is not None:
            internal_field_metainfo['multivalued'] = translated_multivalued

    return internal_field_metainfo


def _wrap_provider_result_field(field_metainfo, source_klass, value):
    _field_metainfo = dict(field_metainfo)
    field_info_to_add = {
        # Do not store a reference to the class itself before actually needed..
        'source': str(source_klass),
        'value': value
    }
    _field_metainfo.update(field_info_to_add)
    return _field_metainfo


_METAINFO_STRING_COERCER_KLASS_MAP = {
    'aw_path': types.AW_PATH,
    'aw_pathcomponent': types.AW_PATHCOMPONENT,
    'aw_timedate': types.AW_TIMEDATE,
    'aw_mimetype': types.AW_MIMETYPE,
    'aw_boolean': types.AW_BOOLEAN,
    'aw_integer': types.AW_INTEGER,
    'aw_date': types.AW_DATE,
    'aw_exiftooltimedate': types.AW_EXIFTOOLTIMEDATE,
    'aw_float': types.AW_FLOAT,
    'aw_string': types.AW_STRING,
}


def get_coercer_from_metainfo_string(string):
    return _METAINFO_STRING_COERCER_KLASS_MAP.get(string)


def translate_metainfo_mappings(metainfo_mapped_fields):
    # TODO: Improve robustness. Raise appropriate exception.
    # TODO: Improve robustness. Log provider with malformed metainfo entries.
    translated = list()
    if not metainfo_mapped_fields:
        return translated

    for mapping in metainfo_mapped_fields:
        for mapping_type, mapping_params in mapping.items():
            # TODO: [cleanup] Allow possible alternative future mapping types.
            if mapping_type == 'WeightedMapping':
                param_field_str = mapping_params.get('field')
                param_prob_str = mapping_params.get('probability')
                # TODO: Improve robustness. Raise appropriate exception.
                # TODO: Improve robustness. Log provider with malformed metainfo entries.
                assert param_field_str
                assert param_prob_str

                param_field = get_field_class_from_metainfo_string(param_field_str)
                param_prob = types.AW_FLOAT(param_prob_str)
                # TODO: Improve robustness. Raise appropriate exception.
                # TODO: Improve robustness. Log provider with malformed metainfo entries.
                assert param_field
                assert param_prob

                translated.append(WeightedMapping(
                    field=param_field,
                    probability=param_prob
                ))
    return translated


def translate_multivalued(multivalued_string):
    return types.AW_BOOLEAN(multivalued_string)


def get_field_class_from_metainfo_string(string):
    return nametemplatefield_class_from_string(string)


class ProviderRegistry(object):
    def __init__(self, meowuri_source_map):
        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )

        self.meowuri_sources = dict(meowuri_source_map)
        self._debug_log_mapped_meowuri_sources()

        # Set of all MeowURIs "registered" by extractors or analyzers.
        self.mapped_meowuris = self.unique_map_meowuris(self.meowuri_sources)

        # Providers declaring generic MeowURIs through 'metainfo()'.
        self.generic_meowuri_sources = _map_generic_sources(
            self.meowuri_sources
        )

        # VALID_SOURCE_ROOTS = set(C.MEOWURI_ROOTS_SOURCES)
        # assert all(r in self.generic_meowuri_sources
        #            for r in VALID_SOURCE_ROOTS)

    def _debug_log_mapped_meowuri_sources(self):
        if not __debug__:
            return

        for key in self.meowuri_sources.keys():
            for meowuri, klass in self.meowuri_sources[key].items():
                self.log.debug('Mapped MeowURI "{!s}" to "{!s}" ({!s})'.format(
                    meowuri, klass, key))

    def might_be_resolvable(self, uri):
        if not uri:
            return False

        sanity.check_isinstance_meowuri(uri)
        resolvable = list(self.mapped_meowuris)
        uri_without_leaf = uri.stripleaf()
        return any(m.matches_start(uri_without_leaf) for m in resolvable)

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

        if requested_meowuri.is_generic:
            found = self._providers_for_generic_meowuri(requested_meowuri,
                                                        includes)
        else:
            found = self._source_providers_for_meowuri(requested_meowuri,
                                                       includes)

        log.debug('{} returning {} providers for MeowURI {!s}'.format(
            self.__class__.__name__, len(found), requested_meowuri))
        return found

    def _yield_included_roots(self, includes=None):
        VALID_INCLUDES = set(C.MEOWURI_ROOTS_SOURCES)
        if not includes:
            # No includes specified -- search all ("valid includes") providers.
            includes = VALID_INCLUDES
        else:
            # Search only specified providers.
            if __debug__:
                # Sanity-check 'includes' argument.
                for include in includes:
                    assert include in VALID_INCLUDES, (
                        '"{!s}" is not one of {!s}'.format(include, VALID_INCLUDES)
                    )

        # Sort for more consistent behaviour.
        for root in sorted(list(includes)):
            yield root

    def _providers_for_generic_meowuri(self, requested_meowuri, includes=None):
        found = set()
        for root in self._yield_included_roots(includes):
            for klass, meowuris in self.generic_meowuri_sources[root].items():
                if requested_meowuri in meowuris:
                    found.add(klass)
        return found

    def _source_providers_for_meowuri(self, requested_meowuri, includes=None):
        # 'uri' is shorter "root";
        #     'extractor.metadata.epub'
        # 'requested_meowuri' is full "source-specific";
        #     'extractor.metadata.exiftool.EXIF:CreateDate'
        found = set()
        requested_meowuri_without_leaf = requested_meowuri.stripleaf()
        for root in self._yield_included_roots(includes):
            for uri in self.meowuri_sources[root].keys():
                if uri.matches_start(requested_meowuri_without_leaf):
                    found.add(self.meowuri_sources[root][uri])
        return found

    @staticmethod
    def unique_map_meowuris(meowuri_class_map):
        out = set()
        # for root in ['extractors', 'analyzer'] ..
        for root in meowuri_class_map.keys():
            for uri in meowuri_class_map[root].keys():
                out.add(uri)
        return out


def _get_meowuri_source_map():
    def __get_meowuri_roots_for_providers(module_name):
        """
        Returns a dict mapping "MeowURIs" to provider classes.

        Example return value: {
            'extractor.filesystem.xplat': CrossPlatformFilesystemExtractor,
            'extractor.metadata.exiftool': ExiftoolMetadataExtractor,
            'extractor.text.pdf': PdfTextExtractor
        }

        Returns: Dictionary keyed by instances of the 'MeowURI' class,
                 storing provider classes.
        """
        _klass_list = getattr(module_name, 'ProviderClasses')
        sanity.check_isinstance(_klass_list, list)

        mapping = dict()
        for klass in _klass_list:
            uri = klass.meowuri_prefix()
            if not uri:
                log.critical('Got empty from '
                             '"{!s}.meowuri_prefix()"'.format(klass.__name__))
                continue

            assert uri not in mapping, (
                'Provider MeowURI "{!s}" is already mapped'.format(uri)
            )
            mapping[uri] = klass

        return mapping

    import analyzers
    import extractors
    return {
        'extractor': __get_meowuri_roots_for_providers(extractors),
        'analyzer': __get_meowuri_roots_for_providers(analyzers),
    }


def _map_generic_sources(meowuri_class_map):
    """
    Returns a dict keyed by provider classes storing sets of "generic"
    fields as Unicode strings.
    """
    out = dict()

    # for root in ['extractors', 'analyzer'] ..
    for root in sorted(list(C.MEOWURI_ROOTS_SOURCES)):
        if root not in meowuri_class_map:
            continue

        out[root] = dict()
        for _, klass in meowuri_class_map[root].items():
            out[root][klass] = set()

            # TODO: [TD0151] Fix inconsistent use of classes/instances.
            # TODO: [TD0157] Look into analyzers 'FIELD_LOOKUP' attributes.
            for _, field_metainfo in klass.metainfo().items():
                _generic_field_string = field_metainfo.get('generic_field')
                if not _generic_field_string:
                    continue

                sanity.check_internal_string(_generic_field_string)
                _generic_field_klass = genericfields.get_field_for_uri_leaf(_generic_field_string)
                if not _generic_field_klass:
                    continue

                assert issubclass(_generic_field_klass, genericfields.GenericField)
                _generic_meowuri = _generic_field_klass.uri()
                if not _generic_meowuri:
                    continue

                out[root][klass].add(_generic_meowuri)
    return out


def get_providers_for_meowuri(meowuri, include_roots=None):
    sanity.check_isinstance_meowuri(meowuri)
    return set(Registry.providers_for_meowuri(meowuri, include_roots))


def get_providers_for_meowuris(meowuri_list, include_roots=None):
    providers = set()
    if not meowuri_list:
        return providers

    for uri in meowuri_list:
        sanity.check_isinstance_meowuri(uri)
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
