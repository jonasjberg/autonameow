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
from core.namebuilder.fields import nametemplatefield_classes_in_formatstring
from core.util import sanity

log = logging.getLogger(__name__)


# TODO: [TD0036] Allow per-field replacements and customization.

# NOTE(jonas): This class might be a good candidate for handling fields.
# If the 'Repository' class is tasked with storing and resolving queries
# for "data".
# Then this class could be tasked with the equivalent handling of "fields",
# as the next level of refinement of data "transformation" in the overall
# "pipeline" --- from "raw" data to the final new file name.


class Resolver(object):
    def __init__(self, file_object, name_template):
        self.file = file_object
        self.name_template = name_template

        self._fields = nametemplatefield_classes_in_formatstring(name_template)

        self.data_sources = {}
        self.fields_data = {}

    def mapped_all_template_fields(self):
        return all(field in self.data_sources for field in self._fields)

    def add_known_source(self, field, meowuri):
        if field in self._fields:
            self.data_sources[field] = meowuri
        else:
            log.debug('Attempted to add source for unused name template field '
                      '"{!s}": {!s}'.format(field, meowuri))

    def add_known_sources(self, source_dict):
        for _field, _meowuri in source_dict.items():
            self.add_known_source(_field, _meowuri)

    def collect(self):
        self._gather_data()
        self._verify_types()

    def collected_all(self):
        if not self.fields_data:
            return False

        return self._has_data_for_placeholder_fields()

    def _has_data_for_placeholder_fields(self):
        for field in self._fields:
            if field not in self.fields_data.keys():
                log.error('Missing placeholder field "{}"'.format(field))
                return False
            elif self.fields_data.get(field) is None:
                log.error('None data for placeholder field "{}"'.format(field))
                return False
        return True

    def _gather_data(self):
        # TODO: [TD0017] Rethink source specifications relation to source data.
        # TODO: [TD0082] Integrate the 'ExtractedData' class.
        for field, meowuri in self.data_sources.items():
            if (field in self.fields_data
                    and self.fields_data.get(field) is not None):
                log.debug('Skipping previously gathered data for field '
                          '"{!s}"'.format(field))
                continue

            log.debug('Gathering data for field "{!s}" from source [{!s}]->'
                      '[{!s}]'.format(field, self.file, meowuri))
            _data = self._request_data(self.file, meowuri)
            if _data is not None:
                log.debug('Got data "{!s}" ({})'.format(_data, type(_data)))
                log.debug('Updated data for field "{!s}"'.format(field))
                self.fields_data[field] = _data
            else:
                log.debug('Got NONE data for [{!s}]->"{!s}"'.format(self.file,
                                                                    meowuri))

                # Remove the source that returned None data.
                log.debug(
                    'Removing source "{!s}"'.format(self.data_sources[field])
                )
                self.data_sources[field] = None

    def _verify_types(self):
        for field, data in self.fields_data.items():
            if isinstance(data, list):
                for d in data:
                    self._verify_type(field, d)
            else:
                self._verify_type(field, data)

    def _verify_type(self, field, data):
        sanity.check(not isinstance(data, list),
                     'Expected "data" not to be a list')

        log.debug('Verifying Field: {!s}  Data:  {!s}'.format(field, data))
        _compatible = field.type_compatible(data.coercer)
        if _compatible:
            log.debug('Verified Field-Data Compatibility  OK!')
        else:
            self.fields_data[field] = None
            log.debug('Verified Field-Data Compatibility  INCOMPATIBLE')

    def _request_data(self, file, meowuri):
        log.debug('{} requesting [{!s}]->[{!s}]'.format(self, file, meowuri))
        return repository.SessionRepository.query(file, meowuri)

    def __str__(self):
        return self.__class__.__name__
