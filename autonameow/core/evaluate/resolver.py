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
import re

from core import repository
from extractors import ExtractedData

log = logging.getLogger(__name__)


class Resolver(object):
    def __init__(self, file_object, name_template):
        self.file = file_object
        self.name_template = name_template
        self.data_sources = {}

    def mapped_all_template_fields(self):
        return all_template_fields_defined(self.name_template,
                                           self.data_sources)

    def add_known_source(self, field, meowuri):
        self.data_sources[field] = meowuri

    def collect(self):
        # TODO: [TD0024][TD0017] Should be able to handle fields not in sources.
        # Add automatically resolving missing sources from possible candidates.

        fields_data = self._gather_data(self.data_sources)

        # Check that all name template fields can be populated.
        if not has_data_for_placeholder_fields(self.name_template, fields_data):
            log.warning('Unable to populate name. Missing field data.')

        return fields_data

    def _gather_data(self, field_meowuri_map):
        """
        Populates a dict of name template fields from data at "meowURIs".

        The dictionary maps name template fields to "meowURIs".
        The extracted data is queried for the "meowURI" first, if the data
        exists, it is used and the analyzer data query is skipped.

        Args:
            field_meowuri_map: Dictionary of fields and "meowURI".

                Example: {'datetime'    = 'metadata.exiftool.DateTimeOriginal'
                          'description' = 'plugin.microsoft_vision.caption'
                          'extension'   = 'filesystem.basename.extension'}

        Returns:
            Results data for the specified fields matching the specified query.
        """
        out = {}

        # TODO: [TD0017] Rethink source specifications relation to source data.
        # TODO: [TD0082] Integrate the 'ExtractedData' class.
        for field, meowuri in field_meowuri_map.items():
            _data = self._request_data(self.file, meowuri)
            if _data is not None:
                out[field] = _data

        return out

    def _request_data(self, file, meowuri):
        log.debug('Requesting [{!s}] "{!s}"'.format(file, meowuri))
        data = repository.SessionRepository.query(file, meowuri)
        log.debug('Got data ({}): {!s}'.format(type(data), data))

        # TODO: [TD0082] Integrate the 'ExtractedData' class.
        if data is not None and isinstance(data, ExtractedData):
            log.debug('Formatting data value "{!s}"'.format(data.value))

            formatted = data.wrapper.format(data.value, formatter=None)
            if formatted is not None and formatted != data.wrapper.null:
                log.debug('Formatted value: "{!s}"'.format(formatted))
                return formatted
            else:
                log.debug(
                    'ERROR when formatted value "{!s}"'.format(data.value)
                )
        else:
            return data


def all_template_fields_defined(template, data_sources):
    """
    Tests if all name template placeholder fields is included in the sources.

    This tests only the keys of the sources, for instance "datetime".
    But the value stored for the key could still be invalid.

    Args:
        template: The name template to compare against.
        data_sources: The sources to check.

    Returns:
        True if all placeholder fields in the template is accounted for in
        the sources. else False.
    """
    format_fields = format_string_placeholders(template)
    for field in format_fields:
        if field not in data_sources.keys():
            log.error('Field "{}" has not been assigned a source'.format(field))
            return False
    return True


def format_string_placeholders(format_string):
    """
    Gets the format string placeholder fields from a text string.

    The text "{foo} mjao baz {bar}" would return ['foo', 'bar'].

    Args:
        format_string: Format string to get placeholders from.

    Returns:
        Any format string placeholder fields as a list of unicode strings.
    """
    if not format_string:
        return []
    return re.findall(r'{(\w+)}', format_string)


def has_data_for_placeholder_fields(template, data):
    placeholder_fields = format_string_placeholders(template)
    result = True
    for field in placeholder_fields:
        if field not in data.keys():
            log.error('Missing data for placeholder field "{}"'.format(field))
            result = False
    return result
