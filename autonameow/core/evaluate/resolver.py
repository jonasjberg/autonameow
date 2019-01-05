# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from core import logs
from core.datastore import repository
from core.datastore.repository import DataBundle
from core.metadata.normalize import normalize_full_human_name
from core.metadata.normalize import normalize_full_title
from core.model import genericfields as gf
from core.namebuilder import fields
from core.truths import known_metadata
from util import sanity


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
    def __init__(self, string_value, source, probability, meowuri,
                 generic_field):
        self.value = string_value
        self.source = source
        self.probability = probability
        self.meowuri = meowuri
        self.generic_field = generic_field

    def __repr__(self):
        a = ', '.join('{}={}'.format(k, v) for k, v in self.__dict__.items())
        return '<FieldDataCandidate({})>'.format(a)


class TemplateFieldDataResolver(object):
    def __init__(self, fileobject, name_template_fields, masterprovider, config):
        self.fileobject = fileobject
        self._fields = name_template_fields
        self._masterprovider = masterprovider
        self.config = config

        self.data_sources = defaultdict(list)
        self.fields_data = dict()

    def mapped_all_template_fields(self):
        return all(field in self.data_sources for field in self._fields)

    def add_known_sources(self, source_dict):
        for field, one_or_many_uris in source_dict.items():
            if isinstance(one_or_many_uris, list):
                for m in one_or_many_uris:
                    self.add_known_source(field, m)
            else:
                self.add_known_source(field, one_or_many_uris)

    def add_known_source(self, field, uri):
        sanity.check_isinstance_meowuri(
            uri,
            msg='TODO: Fix collecting/verifying data from sources.'
        )
        if field not in self._fields:
            log.debug('Attempted to add source for unused name template field "%s": %s',
                      field, uri)
            return

        self._add_known_source(field, uri)

    def _add_known_source(self, field, uri):
        self.data_sources[field].append(uri)
        n = len(self.data_sources[field])
        log.debug('Added known source (#%d) for field %s :: %s', n, field, uri)

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
        log.debug('Resolver is looking up candidates for field %s ..', field)

        candidates = repository.SessionRepository.query_mapped(self.fileobject, field)
        log.debug('Resolver got %d candidates for field %s', len(candidates), field)
        if not candidates:
            return list()

        field_data_candidate_list = list()
        for mapping_weight, uri, databundle in candidates:
            sanity.check_isinstance_meowuri(uri)
            assert isinstance(databundle, DataBundle)

            field_candidate_types_compatible = field.type_compatible(databundle.coercer, databundle.multivalued)
            if not field_candidate_types_compatible:
                log.debug('Type of field %s is NOT compatible with candidate %s', field, databundle)
                continue
            else:
                log.debug('Type of field %s is compatible with candidate %s', field, databundle)

            if isinstance(databundle.value, str):
                if is_known_bad_string_value(field, databundle.value):
                    log.critical('Skipped known bad value for field %s: "%s"',
                                 field, databundle.value)
                    continue

            _formatted_value = field.format(databundle, config=self.config)
            assert _formatted_value is not None

            _candidate_source = databundle.source
            if not _candidate_source:
                log.warning('Unknown source: %s', databundle)
                _candidate_source = '(unknown source)'

            # TODO: Translate generic 'choice.meowuri' to not generic..
            if uri.is_generic:
                log.error('Added generic candidate MeowURI %s', uri)

            field_data_candidate_list.append(FieldDataCandidate(
                string_value=_formatted_value,
                source=_candidate_source,
                probability=str(mapping_weight),
                meowuri=uri,
                generic_field=databundle.generic_field
            ))

        # TODO: [TD0104] Merge candidates and re-normalize probabilities.
        return field_data_candidate_list

    def _has_data_for_placeholder_fields(self):
        log.debug('Checking gathered data for fields..')

        missing_fields = [f for f in self._fields if f not in self.fields_data.keys()]
        if missing_fields:
            str_missing_fields = ' '.join([str(f) for f in missing_fields])
            log.debug('Gathered data does not contain field(s) %s', str_missing_fields)

        none_data_fields = [f for f in self._fields if self.fields_data.get(f, '_') is None]
        if none_data_fields:
            str_none_data_fields = ' '.join([str(f) for f in none_data_fields])
            log.debug('Gathered data is None for field(s) %s', str_none_data_fields)

        if missing_fields or none_data_fields:
            return False

        log.debug('Checking gathered data for fields.. OK!')
        return True

    def _gather_data_for_template_field(self, field, uri):
        log.debug('Gathering data for template field %s from %r->[%s]',
                  field, self.fileobject, uri)
        response = self._request_data(self.fileobject, uri)
        if not response:
            return None

        # Response is either a DataBundle or a list of DataBundles
        databundle = response
        if not isinstance(response, DataBundle):
            # TODO: [TD0112] FIX THIS HORRIBLE MESS!
            assert isinstance(response, list)
            assert all(isinstance(d, DataBundle) for d in response)

            databundles = response
            num_databundles = len(databundles)
            log.debug('Got list of data. Attempting de-duplication of %d databundles',
                      num_databundles)
            deduped_databundles = dedupe_list_of_databundles(databundles)
            num_deduped_databundles = len(deduped_databundles)
            log.debug('De-duplication returned %d of %d databundles',
                      num_deduped_databundles, num_databundles)
            if num_deduped_databundles < num_databundles:
                # TODO: [TD0112] FIX THIS HORRIBLE MESS!
                # Use the deduplicated list
                databundles = deduped_databundles

            if len(databundles) == 1:
                databundle = databundles[0]
                log.debug('Using value "%s" from %d value(s); %s',
                          databundle.value,
                          len(databundles),
                          ', '.join('"{!s}"'.format(d.value) for d in databundles))
            else:
                log.debug('Deduplicated list of databundles still has multiple elements')

                # TODO: [TD0112] Handle this properly!
                # Might be "generic" URI or URI with an "aliased leaf".
                maybe_one = get_one_from_many_generic_values(databundles, uri)
                if maybe_one:
                    assert isinstance(maybe_one, DataBundle)
                    databundle = maybe_one
                    log.debug('Using value "%s" from %d value(s); %s',
                              databundle.value,
                              len(databundles),
                              ', '.join('"{!s}"'.format(d.value) for d in databundles))
                else:
                    log.warning('[TD0112] Not sure what data to use for field %s..', field)
                    for i, d in enumerate(databundles):
                        log.debug('[TD0112] Field %s candidate %03d :: "%s"', field, i, d.value)

                    return None

        # TODO: [TD0112] FIX THIS HORRIBLE MESS!
        assert isinstance(databundle, DataBundle)

        if isinstance(databundle.value, str):
            if is_known_bad_string_value(field, databundle.value):
                log.critical('Skipped known bad value for field %s: "%s"',
                             field, databundle.value)
                return None

        log.debug('Updated data for field %s :: %s', field, databundle.value)
        return databundle

    def _gather_data(self):
        for field, field_data_source_uris in self.data_sources.items():
            if self.fields_data.get(field) is not None:
                log.debug('Skipping previously gathered field %s', field)
                continue

            field_data_source_uris_copy = field_data_source_uris.copy()
            for uri in field_data_source_uris:
                gathered_databundle = self._gather_data_for_template_field(field, uri)
                if gathered_databundle:
                    self.fields_data[field] = gathered_databundle

                    # Remove used known source.
                    field_data_source_uris_copy.remove(uri)
                    break

            # Update known sources. If data was successfully gathered, do not
            # attempt to gather it again if 'collect()' is called a second time
            # after adding additional known sources.
            self.data_sources[field] = field_data_source_uris_copy

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
        log.debug('Verifying type of field %s with data :: %s',
                  field, databundle.value)
        if field.type_compatible(databundle.coercer, databundle.multivalued):
            log.debug('Field-Data type compatible')
        else:
            self.fields_data[field] = None
            log.debug('Field-Data type INCOMPATIBLE')

    def _request_data(self, fileobject, uri):
        log.debug('%s requesting %r->[%s]', self, fileobject, uri)

        # Pass a "tie-breaker" to resolve cases where we only want one item?
        # TODO: [TD0175] Handle requesting exactly one or multiple alternatives.
        # TODO: [TD0185] Rework the highest level data request handler interface.
        response = self._masterprovider.request(fileobject, uri)
        if response:
            return response
        log.debug('Resolver got no data from query %r', response)
        return None

    def __str__(self):
        return self.__class__.__name__


def is_known_bad_string_value(field, value):
    assert isinstance(field, fields.NameTemplateField)
    sanity.check_internal_string(value)

    if value == 'UNKNOWN':
        return True

    fieldname = field.as_placeholder()
    known_bad_values = known_metadata.incorrect_values(fieldname)
    return value in known_bad_values


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

    deduped = list()
    seen_values = set()
    seen_lists = list()
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
            continue

        # TODO: [TD0112] Hack! Do this in a separate system.
        if databundle.generic_field is gf.GenericAuthor:
            normalized_author = normalize_full_human_name(value)
            if normalized_author in seen_values:
                continue

            seen_values.add(normalized_author)

        elif databundle.generic_field is gf.GenericTitle:
            normalized_title = normalize_full_title(value)
            if normalized_title in seen_values:
                continue

            seen_values.add(normalized_title)

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
    assert isinstance(primary_field, fields.NameTemplateField)
    if secondary_field is not None:
        assert isinstance(secondary_field, fields.NameTemplateField)

    databundles.sort(
        key=lambda b: (b.field_mapping_weight(primary_field),
                       b.field_mapping_weight(secondary_field)),
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
    uri_leaf = uri.leaf
    if uri_leaf == 'author':
        prioritized = sort_by_mapped_weights(databundle_list,
                                             primary_field=fields.Author)
        return prioritized[0]
    elif uri_leaf == 'title':
        prioritized = sort_by_mapped_weights(databundle_list,
                                             primary_field=fields.Title)
        return prioritized[0]
    elif uri_leaf == 'date_created':
        prioritized = sort_by_mapped_weights(databundle_list,
                                             primary_field=fields.DateTime)
        return prioritized[0]
    elif uri_leaf == 'publisher':
        prioritized = sort_by_mapped_weights(databundle_list,
                                             primary_field=fields.Publisher)
        return prioritized[0]

    else:
        log.debug('[TD0112] Unhandled uri.leaf: "%s"', uri_leaf)

    # TODO: [TD0112] Handle ranking candidates.
    return None
