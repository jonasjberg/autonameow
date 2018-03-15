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
    logs,
    master_provider,
    repository,
    types
)
from core.model import genericfields as gf
from core.namebuilder import fields
from core.namebuilder.fields import NameTemplateField
from core.repository import DataBundle
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
    def __init__(self, fileobject, name_template_fields):
        self.fileobject = fileobject
        self._fields = name_template_fields

        self.data_sources = dict()
        self.fields_data = dict()

    def mapped_all_template_fields(self):
        return all(field in self.data_sources for field in self._fields)

    def add_known_source(self, field, uri):
        sanity.check_isinstance_meowuri(
            uri,
            msg='TODO: Fix collecting/verifying data from sources.'
        )
        if field in self._fields:
            if not self.data_sources.get(field):
                log.debug('Added (first) known source for field {!s} :: {!s}'.format(field, uri))
                self.data_sources[field] = [uri]
            else:
                log.debug('Added (additional) known source for field {!s} :: {!s}'.format(field, uri))
                self.data_sources[field] += [uri]
        else:
            log.debug('Attempted to add source for unused name template field '
                      '"{!s}": {!s}'.format(field, uri))

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
        with logs.log_runtime(log, '{!s}.collect()'.format(self)):
            self._gather_data()
            self._verify_types()

    def collected_all(self):
        if not self.fields_data:
            return False

        return self._has_data_for_placeholder_fields()

    def lookup_candidates(self, field):
        # TODO: [TD0024][TD0025] Implement Interactive mode.
        log.debug('Resolver is looking up candidates for field {!s} ..'.format(field))

        candidates = repository.SessionRepository.query_mapped(self.fileobject, field)
        log.debug('Resolver got {} candidates for field {!s}'.format(len(candidates), field))

        out = []
        for uri, candidate in candidates:
            sanity.check_isinstance_meowuri(uri)
            sanity.check_isinstance(candidate, DataBundle)

            candidate_mapped_fields = candidate.mapped_fields
            if not candidate_mapped_fields:
                continue

            # TODO: How does this behave if the same generic field is mapped more than once with different probabilities?
            _candidate_probability = str(0.0)
            for mapping in candidate_mapped_fields:
                if mapping.field == field:
                    _candidate_probability = str(mapping.probability)
                    break

            _candidate_coercer = candidate.coercer
            _candidate_value = candidate.value
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

            _candidate_source = candidate.source
            if not _candidate_source:
                log.warning('Unknown source: {!s}'.format(candidate))
                _candidate_source = '(unknown source)'

            _candidate_generic_field = candidate.generic_field

            # TODO: Translate generic 'choice.meowuri' to not generic..
            if uri.is_generic:
                log.error('Added generic candidate MeowURI {!s}'.format(uri))

            out.append(
                FieldDataCandidate(string_value=_formatted_value,
                                   source=_candidate_source,
                                   probability=_candidate_probability,
                                   meowuri=uri,
                                   coercer=_candidate_coercer,
                                   generic_field=_candidate_generic_field)
            )

        # TODO: [TD0104] Merge candidates and re-normalize probabilities.
        return out

    def _has_data_for_placeholder_fields(self):
        for field in self._fields:
            if field not in self.fields_data.keys():
                log.warning('Missing placeholder field {!s}'.format(field))
                return False
            elif self.fields_data.get(field) is None:
                log.error('None data for placeholder field "{}"'.format(field))
                return False
        return True

    def _gather_data_for_template_field(self, _field, uri):
        log.debug(
            'Gathering data for template field {!s} from {!r}->'
            '[{!s}]'.format(_field, self.fileobject, uri)
        )
        response = self._request_data(self.fileobject, uri)
        if not response:
            return False

        # Response is either a DataBundle or a list of DataBundles
        if not isinstance(response, DataBundle):
            # TODO: [TD0112] FIX THIS HORRIBLE MESS!
            assert isinstance(response, list)
            assert all(isinstance(d, DataBundle) for d in response)

            log.debug('Got list of data. Attempting to deduplicate list of datadicts')
            _deduped_list = dedupe_list_of_databundles(response)
            if len(_deduped_list) < len(response):
                # TODO: [TD0112] FIX THIS HORRIBLE MESS!
                # Use the deduplicated list
                response = _deduped_list

            if len(_deduped_list) == 1:
                log.debug('Deduplicated list of datadicts has a single element')
                log.debug('Using one of {} equivalent '
                          'entries'.format(len(response)))
                log.debug('Using "{!s}" from equivalent: {!s}'.format(response[0].value, ', '.join('"{}"'.format(_d.value) for _d in response)))
                response = response[0]
            else:
                log.debug('Deduplicated list of datadicts still has multiple elements')

                # TODO: [TD0112] Handle this properly!
                if uri.is_generic:
                    maybe_one = get_one_from_many_generic_values(response, uri)
                    if not maybe_one:
                        log.warning('[TD0112] Not sure what data to use for field {!s}..'.format(_field))
                        for i, d in enumerate(response):
                            log.debug('[TD0112] Field {!s} candidate {:03d} :: "{!s}"'.format(_field, i, d.value))
                        return False
                    else:
                        assert isinstance(maybe_one, DataBundle)
                        response = maybe_one

        if isinstance(response.value, list):
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
                    response.value = list(list(seen_data)[0])

        # TODO: [TD0112] FIX THIS HORRIBLE MESS!
        sanity.check_isinstance(response, DataBundle)

        log.debug('Updated data for field {!s} :: {!s}'.format(_field,
                                                               response.value))
        self.fields_data[_field] = response
        return True

    def _gather_data(self):
        for field, uris in self.data_sources.items():
            if (field in self.fields_data
                    and self.fields_data[field] is not None):
                log.debug('Skipping previously gathered data for field '
                          '{!s}"'.format(field))
                continue

            for uri in uris:
                if self._gather_data_for_template_field(field, uri):
                    break

    def _verify_types(self):
        for field, databundle in self.fields_data.items():
            assert isinstance(databundle, DataBundle)
            self._verify_type(field, databundle)

        # Remove data type is incompatible with associated field.
        # TODO: ?????
        _fields_data = self.fields_data.copy()
        for field, databundle in _fields_data.items():
            if databundle is None:
                self.fields_data.pop(field)

    def _verify_type(self, field, databundle):
        log.debug('Verifying type of field {!s} with data :: {!s}'.format(
            field, databundle.value))
        if field.type_compatible(databundle.coercer):
            log.debug('Field-Data type compatible')
        else:
            self.fields_data[field] = None
            log.debug('Field-Data type INCOMPATIBLE')

    def _request_data(self, fileobject, uri):
        log.debug('{!s} requesting {!r}->[{!s}]'.format(self, fileobject, uri))

        # Pass a "tie-breaker" to resolve cases where we only want one item?
        # TODO: [TD0175] Handle requesting exactly one or multiple alternatives.
        response = master_provider.request(fileobject, uri)
        if response:
            return response
        log.debug('Resolver got no data from query {!r}'.format(response))
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
    sanity.check_isinstance(primary_field, NameTemplateField)
    if secondary_field is not None:
        sanity.check_isinstance(secondary_field, NameTemplateField)

    databundles.sort(
        key=lambda b: (b.field_mapping_probability(primary_field),
                       b.field_mapping_probability(secondary_field)),
        reverse=True
    )
    return databundles


def get_one_from_many_generic_values(databundle_list, uri):
    """
    Use weighted mapping probabilities to return a single bundle.

    This is a pretty messy attempt at finding "best suited" candidates based
    on 'WeightedMapping' probabilities assigned by providers.

    Args:
        databundle_list: List of instances of 'DataBundle'.
                         Presumably related to the given MeowURI. (?)
        uri: The MeowURI that should be resolved into a single data bundle.

    Returns:
        The "best suited" bundle, based on weighted mapping probabilities
        for the name template field related to the MeowURI "leaf".
    """
    if uri.leaf == 'author':
        prioritized = sort_by_mapped_weights(databundle_list,
                                             primary_field=fields.Author)
        return prioritized[0]
    elif uri.leaf == 'title':
        prioritized = sort_by_mapped_weights(databundle_list,
                                             primary_field=fields.Title)
        return prioritized[0]
    # TODO: [TD0112] Handle ranking candidates.
    return None
