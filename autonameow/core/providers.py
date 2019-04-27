# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from core.model import genericfields
from core.model import WeightedMapping
from core.namebuilder.fields import nametemplatefield_class_from_string
from util import coercers


log = logging.getLogger(__name__)


class ProviderMixin(object):
    def coerce_field_value(self, field, value):
        if value is None:
            return None

        # TODO: [TD0157] Look into analyzers 'FIELD_LOOKUP' attributes.
        # TODO: [hack] This is very bad.
        field_metainfo = self.metainfo().get(field)
        if not field_metainfo:
            self.log.debug(
                '"metainfo" does not contain field "%s" with value "%s" (%s)',
                field, value, type(value)
            )
            return None

        try:
            coercer_string = field_metainfo.get('coercer')
        except AttributeError:
            # Might be case of malformed "metainfo" ..
            coercer_string = None

        if not coercer_string:
            self.log.warning(
                '"coercer" unspecified for field "%s" with value "%s" (%s)',
                field, value, type(value)
            )
            return None

        assert isinstance(coercer_string, str)
        coercer = get_coercer_for_metainfo_string(coercer_string)
        if not isinstance(coercer, (coercers.BaseCoercer, coercers.MultipleTypes)):
            msg = 'Expected coercer class. Got {} "{!s}" from coercer_string {!s} "{!s}"'.format(
                type(coercer), coercer, type(coercer_string), coercer_string
            )
            raise AssertionError(msg)

        if 'multivalued' not in field_metainfo:
            # Abort instead of using a default value. Many systems rely on this
            # being correct --- make sure that the provider metainfo is correct.
            self.log.warning(
                '"multivalued" unspecified for field "%s" with value "%s" (%s)',
                field, value, type(value)
            )
            return None

        multivalued = bool(field_metainfo.get('multivalued'))
        return self._coerce_field_value(field, value, coercer, multivalued)

    def _coerce_field_value(self, field, value, coercer, multivalued):
        """
        Check whether types and multiplicities defined in "metainfo"
        matches the actual data and do type coercions.
        """
        # Value is a list ("multivalued") --- coerce to list or abort
        # if expecting a single value, can't do reliable conversion.
        if isinstance(value, list):
            if multivalued:
                return self._coerce_multiple_values(field, value, coercer)

            # TODO: [incomplete] Handle mismatch somehow instead of skipping?
            # Fields like "date created" is expected to be a single value,
            # If an actual value is [1942, 2018] it should probably be handled
            # as two separate possible fields.
            # TODO: How would this fit into the concept of "records"?
            self.log.debug(
                'Got list but "metainfo" specifies a single value for field '
                '"%s" with value "%s" (%s)', field, value, type(value)
            )
            return None

        # Value is not a list --- do single value coercion or coerce into list.
        if multivalued:
            self.log.debug(
                'Got single value but "metainfo" specifies "multivalued"; '
                'coercing to list. Field "%s" with value "%s" (%s)',
                field, value, type(value)
            )
            return self._coerce_multiple_values(field, value, coercer)

        return self._coerce_single_value(field, value, coercer)

    def _coerce_single_value(self, field, value, coercer):
        try:
            return coercer(value)
        except coercers.AWTypeError as e:
            self.log.debug('Error coercing field "%s" with value "%s" :: %s',
                           field, value, e)
            return None

    def _coerce_multiple_values(self, field, values, coercer):
        try:
            return coercers.listof(coercer)(values)
        except coercers.AWTypeError as e:
            self.log.debug('Error coercing field "%s" with values "%s" :: %s',
                           field, values, e)
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
    assert isinstance(metainfo, dict), repr(source_klass)
    log.debug('Wrapping %s results (datadict len: %d) (metainfo len: %d)',
              source_klass.name(), len(datadict), len(metainfo))

    wrapped = dict()

    for field, value in datadict.items():
        raw_field_metainfo = metainfo.get(field)
        if not raw_field_metainfo:
            log.warning('Missing metainfo for field "%s"', field)
            log.debug('Field %s not in %s', field, metainfo)
            continue

        field_metainfo = _translate_field_metainfo_to_internal_format(raw_field_metainfo)
        if not field_metainfo:
            log.warning('Translation of metainfo to internal format failed for '
                        'provider %s field "%s"', source_klass, field)
            continue

        wrapped[field] = _wrap_provider_result_field(field_metainfo, source_klass, value)

    return wrapped


def _translate_field_metainfo_to_internal_format(field_metainfo):
    # TODO: [TD0146] Rework "generic fields". Possibly bundle in "records".
    _field_metainfo = dict(field_metainfo)
    internal_field_metainfo = dict()

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
    if multivalued_string is None:
        raise AssertionError('TODO: Handle missing "multivalued" metainfo entry in {!s}'.format(field_metainfo))

    translated_multivalued = translate_multivalued(multivalued_string)
    assert translated_multivalued is not None
    internal_field_metainfo['multivalued'] = translated_multivalued

    coercer_klass = get_coercer_for_metainfo_string(_field_metainfo.get('coercer'))
    assert coercer_klass is not None
    internal_field_metainfo['coercer'] = coercer_klass

    return internal_field_metainfo


def _wrap_provider_result_field(field_metainfo, source_klass, value):
    _field_metainfo = dict(field_metainfo)
    field_info_to_add = {
        # Do not store a reference to the class itself before actually needed..
        # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
        # TODO: [cleanup][hack] Can't use str(source_klass) on the class ..
        'source': str(source_klass.name()),
        'value': value
    }
    _field_metainfo.update(field_info_to_add)
    return _field_metainfo


_METAINFO_STRING_COERCER_KLASS_MAP = {
    'aw_path': coercers.AW_PATH,
    'aw_pathcomponent': coercers.AW_PATHCOMPONENT,
    'aw_timedate': coercers.AW_TIMEDATE,
    'aw_mimetype': coercers.AW_MIMETYPE,
    'aw_boolean': coercers.AW_BOOLEAN,
    'aw_integer': coercers.AW_INTEGER,
    'aw_date': coercers.AW_DATE,
    'aw_exiftooltimedate': coercers.AW_EXIFTOOLTIMEDATE,
    'aw_float': coercers.AW_FLOAT,
    'aw_string': coercers.AW_STRING,
}


def get_coercer_for_metainfo_string(string):
    return _METAINFO_STRING_COERCER_KLASS_MAP.get(string)


def translate_metainfo_mappings(metainfo_mapped_fields):
    # TODO: [TD0184] Improve robustness. Raise appropriate exception.
    # TODO: [TD0184] Log provider with malformed metainfo entries.
    translated = list()
    if not metainfo_mapped_fields:
        return translated

    for mapping in metainfo_mapped_fields:
        for mapping_type, mapping_params in mapping.items():
            # TODO: [cleanup] Allow possible alternative future mapping types.
            if mapping_type == 'WeightedMapping':
                param_field_str = mapping_params.get('field')
                param_prob_str = mapping_params.get('weight')
                # TODO: [TD0184] Improve robustness. Raise appropriate exception.
                # TODO: [TD0184] Log provider with malformed metainfo entries.
                # TODO: [TD0184] Clean up translation of 'metainfo' to "internal format".
                assert param_field_str
                assert param_prob_str

                param_field = nametemplatefield_class_from_string(param_field_str)
                param_prob = coercers.AW_FLOAT(param_prob_str)
                # TODO: Improve robustness. Raise appropriate exception.
                # TODO: Improve robustness. Log provider with malformed metainfo entries.
                assert param_field
                assert param_prob

                translated.append(WeightedMapping(
                    field=param_field,
                    weight=param_prob
                ))
    return translated


def translate_multivalued(multivalued_string):
    return coercers.AW_BOOLEAN(multivalued_string)
