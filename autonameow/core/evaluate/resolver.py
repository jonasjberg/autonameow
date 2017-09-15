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
        self.fields_data = {}

    def mapped_all_template_fields(self):
        return all_template_fields_defined(self.name_template,
                                           self.data_sources)

    def add_known_source(self, field, meowuri):
        self.data_sources[field] = meowuri

    def collect(self):
        self._gather_data()

    def collected_data_for_all_fields(self):
        if not self.fields_data:
            return False

        return has_data_for_placeholder_fields(self.name_template,
                                               self.fields_data)

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

    def _request_data(self, file, meowuri):
        log.debug('{} requesting [{!s}]->[{!s}]'.format(self, file, meowuri))
        return repository.SessionRepository.query(file, meowuri)

    def __str__(self):
        return self.__class__.__name__


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
    if not isinstance(format_string, str):
        raise TypeError('Expected "format_string" to be of type str')
    if not format_string.strip():
        return []

    return re.findall(r'{(\w+)}', format_string)


def has_data_for_placeholder_fields(template, data):
    """
    Tests if all placeholder fields in the given 'template' has data in 'data'.

    Data should be a dict keyed by placeholder fields in 'template'.
    If any of the fields are missing or None, the test fails.

    Args:
        template: Name template to test, as a Unicode string.
        data: Dict keyed by Unicode strings, storing arbitrary data.

    Returns:
        True if all placeholder fields in 'template' is present in 'data' and
        the values stored in 'data' is not None. Else False.
    """
    placeholder_fields = format_string_placeholders(template)
    for field in placeholder_fields:
        if field not in data.keys():
            log.error('Missing placeholder field "{}"'.format(field))
            return False
        elif data.get(field) is None:
            log.error('None data for placeholder field "{}"'.format(field))
            return False
    return True
