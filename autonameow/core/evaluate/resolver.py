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

from core import (
    provider,
    repository
)
from core.model import genericfields as gf
from core.namebuilder.fields import (
    NameTemplateField,
    nametemplatefield_classes_in_formatstring
)
from core.repository import (
    DataBundle,
    maps_field
)
from util import sanity
from util.text import format_name


log = logging.getLogger(__name__)


# TODO: [TD0036] Allow per-field replacements and customization.

# NOTE(jonas): This class might be a good candidate for handling fields.
# If the 'Repository' class is tasked with storing and resolving queries
# for "data".
# Then this class could be tasked with the equivalent handling of "fields",
# as the next level of refinement of data "transformation" in the overall
# "pipeline" --- from "raw" data to the final new file name.


class FieldDataCandidate(object):
    """
    Simple "struct"-like container used by 'lookup_candidates()'.
    """
    def __init__(self, string_value, source, probability, meowuri, coercer,
                 generic_field):
        self.value = string_value
        self.source = source
        self.probability = probability
        self.meowuri = meowuri
        self.coercer = coercer
        self.generic_field = generic_field

    def __repr__(self):
        a = ', '.join('{}={}'.format(k, v) for k, v in self.__dict__.items())
        return '<FieldDataCandidate({})>'.format(a)


class TemplateFieldDataResolver(object):
    def __init__(self, fileobject, name_template):
        self.file = fileobject
        self.name_template = name_template

        self._fields = nametemplatefield_classes_in_formatstring(name_template)

        self.data_sources = dict()
        self.fields_data = dict()

    def mapped_all_template_fields(self):
        return all(field in self.data_sources for field in self._fields)

    def add_known_source(self, field, meowuri):
        sanity.check_isinstance_meowuri(
            meowuri,
            msg='TODO: Fix collecting/verifying data from sources.'
        )
        if field in self._fields:
            if not self.data_sources.get(field):
                log.debug('Added (first) known source for field {!s} :: {!s}'.format(field.as_placeholder(), meowuri))
                self.data_sources[field] = [meowuri]
            else:
                log.debug('Added (additional) known source for field {!s} :: {!s}'.format(field.as_placeholder(), meowuri))
                self.data_sources[field] += [meowuri]
        else:
            log.debug('Attempted to add source for unused name template field '
                      '"{!s}": {!s}'.format(field, meowuri))

    def add_known_sources(self, source_dict):
        for _field, uri in source_dict.items():
            if isinstance(uri, list):
                for m in uri:
                    self.add_known_source(_field, m)
            else:
                self.add_known_source(_field, uri)

    @property
    def unresolved(self):
        return [f for f in self._fields if f not in self.fields_data.keys()]

    def collect(self):
        self._gather_data()
        self._verify_types()

    def collected_all(self):
        if not self.fields_data:
            return False

        return self._has_data_for_placeholder_fields()

    def lookup_candidates(self, field):
        # TODO: [TD0024][TD0025] Implement Interactive mode.
        log.debug('Resolver is looking up candidates for field {!s} ..'.format(field.as_placeholder()))

        # TODO: [TD0165] Expect the 'DataBundle' class to be returned here.
        candidates = repository.SessionRepository.query_mapped(self.file, field)
        log.debug('Resolver got {} candidates for field {!s}'.format(len(candidates), field.as_placeholder()))

        out = []
        for candidate in candidates:
            sanity.check_isinstance(candidate, dict)

            candidate_mapped_fields = candidate.get('mapped_fields')
            if not candidate_mapped_fields:
                continue

            # TODO: How does this behave if the same generic field is mapped more than once with different probabilities?
            _candidate_probability = str(0.0)
            for mapping in candidate_mapped_fields:
                if mapping.field == field:
                    _candidate_probability = str(mapping.probability)
                    break

            _candidate_coercer = candidate.get('coercer')
            _candidate_value = candidate.get('value')
            _formatted_value = ''
            if _candidate_value and _candidate_coercer:
                try:
                    _formatted_value = _candidate_coercer.format(_candidate_value)
                except types.AWTypeError as e:
                    # TODO: FIX THIS! Should use "list of string"-coercer for authors and other "multi-valued" template fields.
                    log.critical(
                        'Error while formatting (coercing) candidate value in '
                        '"TemplateFieldDataResolver.lookup_candidates()"'
                    )
                    log.critical(str(e))
                    continue

            if 'source' not in candidate:
                log.warning('Unknown source: {!s}'.format(candidate))
            _candidate_source = candidate.get('source', '(unknown source)')
            _candidate_meowuri = candidate.get('meowuri', '')
            _candidate_generic_field = candidate.get('generic_field')

            # TODO: Translate generic 'choice.meowuri' to not generic..
            if _candidate_meowuri.is_generic:
                log.error('Added generic candidate MeowURI {!s}'.format(_candidate_meowuri))

            out.append(
                FieldDataCandidate(string_value=_formatted_value,
                                   source=_candidate_source,
                                   probability=_candidate_probability,
                                   meowuri=_candidate_meowuri,
                                   coercer=_candidate_coercer,
                                   generic_field=_candidate_generic_field)
            )

        # TODO: [TD0104] Merge candidates and re-normalize probabilities.
        return out

    def _has_data_for_placeholder_fields(self):
        for field in self._fields:
            if field not in self.fields_data.keys():
                log.warning('Missing placeholder field "{}"'.format(field))
                return False
            elif self.fields_data.get(field) is None:
                log.error('None data for placeholder field "{}"'.format(field))
                return False
        return True

    def _gather_data(self):
        for _field, _meowuris in self.data_sources.items():
            _str_field = str(_field.as_placeholder())

            if (_field in self.fields_data
                    and self.fields_data.get(_field) is not None):
                log.debug('Skipping previously gathered data for field '
                          '{{{}}}"'.format(_str_field))
                continue

            assert _meowuris, (
                'Resolver attempted to gather data with empty MeowURI!'
            )
            for uri in _meowuris:
                log.debug(
                    'Gathering data for template field {{{}}} from [{:8.8}]->'
                    '[{!s}]'.format(_str_field, self.file.hash_partial, uri)
                )

                response = self._request_data(self.file, uri)
                if not response:
                    continue

                # Response is either a DataBundle or a list of DataBundles
                if not isinstance(response, DataBundle):
                    assert isinstance(response, list)
                    assert all(isinstance(d, DataBundle) for d in response)

                # TODO: [TD0112] FIX THIS HORRIBLE MESS!
                if isinstance(response, list):
                    log.debug('Got list of data. Attempting to deduplicate list of datadicts')
                    _deduped_list = dedupe_list_of_databundles(response)
                    if len(_deduped_list) == 1:
                        log.debug('Deduplicated list of datadicts has a single element')
                        log.debug('Using one of {} equivalent '
                                  'entries'.format(len(response)))
                        log.debug('Using "{!s}" from equivalent: {!s}'.format(response[0].value, ', '.join('"{}"'.format(_d.value) for _d in response)))
                        response = response[0]
                    else:
                        log.debug('Deduplicated list of datadicts still has multiple elements')
                        log.warning('[TD0112] Not sure what data to use for field {{{}}}..'.format(_str_field))
                        for i, d in enumerate(response):
                            log.debug('[TD0112] Field {{{}}} candidate {:03d} :: "{!s}"'.format(_str_field, i, d.value))
                        continue

                # # TODO: [TD0112] Clean up merging data.
                elif isinstance(response.value, list):
                    # TODO: [TD0112] Clean up merging data.
                    list_value = response.value
                    if len(list_value) > 1:
                        seen_data = set()
                        for d in list_value:
                            seen_data.add(d)

                        if len(seen_data) == 1:
                            # TODO: [TD0112] FIX THIS!
                            log.debug('Merged {} equivalent entries ({!s} is now {!s})'.format(
                                len(list_value), list_value, list(list(seen_data)[0])))
                            # TODO: [TD0112] FIX THIS!
                            response.value = list(list(seen_data)[0])

                # TODO: [TD0112] FIX THIS HORRIBLE MESS!
                log.debug('Updated data for field {{{}}} :: "{!s}"'.format(
                    _str_field, response.value))
                self.fields_data[_field] = response
                break

    def _verify_types(self):
        # TODO: [TD0115] Clear up uncertainties about data multiplicities.
        for field, data in self.fields_data.items():
            log.debug('Verifying data for field {{{!s}}}'.format(field.as_placeholder()))
            log.debug('field = {!s}'.format(field))
            log.debug('data = {!s}'.format(data))

            if isinstance(data, list):
                if not field.MULTIVALUED:
                    self.fields_data[field] = None
                    log.debug('Verified Field-Data Compatibility  INCOMPATIBLE')
                    log.debug('Template field {{{!s}}} expects a single value. '
                              'Got ({!s}) "{!s}"'.format(field.as_placeholder(),
                                                         type(data), data))
                for d in data:
                    self._verify_type(field, d)
            else:
                # if field.MULTIVALUED:
                #     self.fields_data[field] = None
                #     log.debug('Verified Field-Data Compatibility  INCOMPATIBLE')
                #     log.debug('Template field {{{!s}}} expects multiple values. '
                #               'Got ({!s}) "{!s}"'.format(field.as_placeholder(),
                #                                          type(data), data))
                self._verify_type(field, data)

        # Remove data type is incompatible with associated field.
        _fields_data = self.fields_data.copy()
        for field, data in _fields_data.items():
            if data is None:
                self.fields_data.pop(field)

    def _verify_type(self, field, data):
        _data_info = 'Type "{!s}" Contents: "{!s}"'.format(type(data), data)
        assert not isinstance(data, list), (
            'Expected "data" not to be a list. Got {}'.format(_data_info)
        )

        log.debug('Verifying Field: {!s}  Data:  {!s}'.format(field, data))
        _coercer = data.coercer
        _compatible = field.type_compatible(_coercer)
        if _compatible:
            log.debug('Verified Field-Data Compatibility  OK!')
        else:
            self.fields_data[field] = None
            log.debug('Verified Field-Data Compatibility  INCOMPATIBLE')

    def _request_data(self, fileobject, meowuri):
        log.debug('{} requesting [{:8.8}]->[{!s}]'.format(
            self, fileobject.hash_partial, meowuri))

        response = provider.query(fileobject, meowuri)
        if response:
            return response
        else:
            log.debug('Resolver got no data.. {!s}'.format(response))
            return None

    def __str__(self):
        return self.__class__.__name__


def dedupe_list_of_databundles(databundle_list):
    """
    Given a list of provider result data dicts, deduplicate identical data.

    If two dicts contain equivalent values, one of the dicts is arbitrarily
    chosen for removal.
    Note that this means that some possibly useful meta-information is lost.

    Args:
        databundle_list: List of instances of 'DataBundle' with "provider" data.

    Returns:
        A list of instances of 'DataBundle' where bundles containing equivalent
        values have been removed, leaving only one arbitrarily chosen bundle
        per group of bundles.
    """
    list_of_databundles = list(databundle_list)
    if len(list_of_databundles) == 1:
        return list_of_databundles

    deduped = []
    seen_values = set()
    seen_lists = []
    for databundle in list_of_databundles:
        value = databundle.value
        # Assume that the data is free from None values at this point.
        assert value is not None, 'None value in databundle: ' + str(databundle)

        if isinstance(value, list):
            sorted_list_value = sorted(list(value))
            if sorted_list_value in seen_lists:
                continue
            seen_lists.append(sorted_list_value)
            deduped.append(databundle)
        else:
            # TODO: [TD0112] Hack! Do this in a separate system.
            if databundle.generic_field is gf.GenericAuthor:
                _normalized_author = format_name(value)
                if _normalized_author in seen_values:
                    continue
                seen_values.add(_normalized_author)
            else:
                if value in seen_values:
                    continue
                seen_values.add(value)

            deduped.append(databundle)

    return deduped


def sort_by_mapped_weights(databundles, primary_field, secondary_field=None):
    """
    Sorts bundles by their "weighted mapping" probabilities for given fields.
    """
    assert issubclass(primary_field, NameTemplateField)
    if secondary_field is not None:
        assert issubclass(secondary_field, NameTemplateField)

    databundles.sort(
        key=lambda b: (b.field_mapping_probability(primary_field),
                       b.field_mapping_probability(secondary_field)),
        reverse=True
    )
    return databundles
