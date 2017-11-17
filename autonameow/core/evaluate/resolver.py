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

from core import repository
from core.model import MeowURI
from core.namebuilder.fields import nametemplatefield_classes_in_formatstring


log = logging.getLogger(__name__)


# TODO: [TD0036] Allow per-field replacements and customization.

# NOTE(jonas): This class might be a good candidate for handling fields.
# If the 'Repository' class is tasked with storing and resolving queries
# for "data".
# Then this class could be tasked with the equivalent handling of "fields",
# as the next level of refinement of data "transformation" in the overall
# "pipeline" --- from "raw" data to the final new file name.


class TemplateFieldDataResolver(object):
    def __init__(self, fileobject, name_template):
        self.file = fileobject
        self.name_template = name_template

        self._fields = nametemplatefield_classes_in_formatstring(name_template)

        self.data_sources = {}
        self.fields_data = {}

    def mapped_all_template_fields(self):
        return all(field in self.data_sources for field in self._fields)

    def add_known_source(self, field, meowuri):
        assert meowuri and isinstance(meowuri, MeowURI), (
               'TODO: Fix collecting/verifying data from sources.')

        if field in self._fields:
            if not self.data_sources.get(field):
                self.data_sources[field] = [meowuri]
            else:
                self.data_sources[field] += [meowuri]
        else:
            log.debug('Attempted to add source for unused name template field '
                      '"{!s}": {!s}'.format(field, meowuri))

    def add_known_sources(self, source_dict):
        for _field, _meowuri in source_dict.items():
            if isinstance(_meowuri, list):
                for m in _meowuri:
                    self.add_known_source(_field, m)
            else:
                self.add_known_source(_field, _meowuri)

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
        # TODO: [TD0023][TD0024][TD0025] Implement Interactive mode.
        candidates = repository.SessionRepository.query_mapped(self.file, field)

        # TODO: [TD0104] Merge candidates and re-normalize probabilities.
        return candidates if candidates else []

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
            if (_field in self.fields_data
                    and self.fields_data.get(_field) is not None):
                log.debug('Skipping previously gathered data for field '
                          '"{!s}"'.format(_field))
                continue

            if not _meowuris:
                log.debug(
                    'Resolver attempted to gather data with empty MeowURI!'
                )
                continue

            for _meowuri in _meowuris:
                log.debug(
                    'Gathering data for field "{!s}" from source [{:8.8}]->'
                    '[{!s}]'.format(_field, self.file.hash_partial, _meowuri)
                )

                _data = self._request_data(self.file, _meowuri)
                if _data is None:
                    log.debug('Got NONE data for [{:8.8}]->"{!s}"'.format(
                        self.file.hash_partial, _meowuri)
                    )
                    continue

                if isinstance(_data, list):
                    if len(_data) == 1:
                        _data = _data[0]
                    else:
                        seen_data = set()
                        for d in _data:
                            seen_data.add(d.get('value'))

                        if len(seen_data) == 1:
                            log.debug('Using first of {} equivalent '
                                      'entries'.format(len(_data)))
                            _data = _data[0]
                            # TODO: [TD0112] FIX THIS!

                _data_info = 'Type "{!s}" Contents: "{!s}"'.format(
                    type(_data.get('value')), _data
                )
                log.debug('Got {}'.format(_data_info))
                # # TODO: [TD0112] Clean up merging data.
                if isinstance(_data.get('value'), list):

                    seen_data = set()
                    for d in _data.get('value'):
                        seen_data.add(d)

                    if len(seen_data) == 1:
                        # TODO: [TD0112] FIX THIS!
                        log.debug('Merged {} equivalent entries'.format(
                            len(_data.get('value')))
                        )

                log.debug('Updated data for field "{!s}"'.format(_field))
                self.fields_data[_field] = _data
                break

    def _verify_types(self):
        # TODO: [TD0115] Clear up uncertainties about data multiplicities.
        for field, data in self.fields_data.items():
            if isinstance(data, list):
                if not field.MULTIVALUED:
                    self.fields_data[field] = None
                    log.debug('Verified Field-Data Compatibility  INCOMPATIBLE')
                    log.debug(
                        'Template field "{!s}" expects a single value. '
                        'Got ({!s}) "{!s}"'.format(field.as_placeholder(),
                                                   type(data), data)
                    )

                for d in data:
                    self._verify_type(field, d)
            else:
                self._verify_type(field, data)

        # Remove data type is incompatible with associated field.
        _fields_data = self.fields_data.copy()
        for field, data in _fields_data.items():
            if data is None:
                self.fields_data.pop(field)

    def _verify_type(self, field, data):
        _data_info = 'Type "{!s}" Contents: "{!s}"'.format(type(data), data)
        assert not isinstance(data, list), (
               'Expected "data" not to be a list. Got {}'.format(_data_info))

        log.debug('Verifying Field: {!s}  Data:  {!s}'.format(field, data))
        _coercer = data.get('coercer')
        _compatible = field.type_compatible(_coercer)
        if _compatible:
            log.debug('Verified Field-Data Compatibility  OK!')
        else:
            self.fields_data[field] = None
            log.debug('Verified Field-Data Compatibility  INCOMPATIBLE')

    def _request_data(self, file, meowuri):
        log.debug('{} requesting [{:8.8}]->[{!s}]'.format(
            self, file.hash_partial, meowuri)
        )
        return repository.SessionRepository.query(file, meowuri)

    def __str__(self):
        return self.__class__.__name__
