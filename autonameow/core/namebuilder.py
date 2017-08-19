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

import logging as log
import re
from datetime import datetime

from core import (
    exceptions,
    util,
    repository
)


class NameBuilder(object):
    """
    Constructs a new filename for a FileObject given a set of rules,
    a file object and data gathered by analyzers.

    A rule contains the name template that determines the format of the
    resulting name. The rule also determines what analysis data to use when
    populating the name template fields.
    """
    def __init__(self, file_object, active_config, active_rule):
        self.file = file_object
        self.config = active_config
        self.active_rule = active_rule

        self.request_data = repository.SessionRepository.resolve

        self._new_name = None

    @property
    def new_name(self):
        return self._new_name

    def _gather_data(self, field_querystring_map):
        """
        Populates a dictionary with data fields matching a "query string".

        The dictionary specifies which fields and a corresponding query string.
        The extracted data is queried for the query string first, if the data
        exists, it is used and the analyzer data query is skipped.

        Args:
            field_querystring_map: Dictionary of fields and query string.

                Example: {'datetime'    = 'metadata.exiftool.DateTimeOriginal'
                          'description' = 'plugin.microsoft_vision.caption'
                          'extension'   = 'filesystem.basename.extension'}

        Returns:
            Results data for the specified fields matching the specified query.
        """
        out = {}

        # NOTE(jonas): Mapping specified sources to extracted data and
        # analysis results must be redesigned. Sources must be queried
        # individually. Requires re-evaluating the configuration source
        # description format.
        # TODO: [TD0017] Rethink source specifications relation to source data.
        for field, query_string in field_querystring_map.items():
            _data = self.request_data(self.file, query_string)
            if _data:
                out[field] = _data
            # else:
            #     analysis_data = self.analysis_data.get(query_string)
            #     if analysis_data:
            #         out[field] = analysis_data
            # TODO: Or else what.. ?

        return out

    def build(self):
        template = self.active_rule.name_template
        log.debug('Using name template: "{}"'.format(template))

        # TODO: [TD0024][TD0017] Should be able to handle fields not in sources.
        # Add automatically resolving missing sources from possible candidates.

        # TODO: [TD0062] Move test for name template fields mapping to sources.
        # NOTE(jonas): Move this to the rule matcher?
        # Or maybe to when reading the configuration, which would give a
        # heads-up on that switching to the "interactive mode" would be
        # required in order to complete the rename. This would be useful to
        # implement the feature to force non-interactive mode, see [TD0023].

        # NOTE(jonas): Make sure name builder always gets a valid rule?

        data_sources = self.active_rule.data_sources
        if not all_template_fields_defined(template, data_sources):
            log.error('All name template placeholder fields must be '
                      'given a data source; Check the configuration!')
            raise exceptions.NameBuilderError(
                'Some template field sources are unknown'
            )

        # Get a dictionary of data to pass to 'assemble_basename'.
        # Should be keyed by the placeholder fields used in the name template.
        data = self._gather_data(data_sources)
        if not data:
            log.warning('Unable to get data from specified sources')
            raise exceptions.NameBuilderError('Unable to assemble basename')

        log.debug('Query for results fields returned:')
        log.debug(str(data))

        # Check that all name template fields can be populated.
        if not has_data_for_placeholder_fields(template, data):
            log.warning('Unable to populate name. Missing field data.')
            raise exceptions.NameBuilderError('Unable to assemble basename')

        # TODO: [TD0017][TD0041] Format ALL data before assembly!
        # NOTE(jonas): This step is part of a ad-hoc encoding boundary.
        data = pre_assemble_format(data, self.config)
        log.debug('After pre-assembly formatting;')
        log.debug(str(data))

        # Construct the new file name
        new_name = populate_name_template(template, **data)
        log.debug('Assembled basename: "{!s}"'.format(new_name))
        assert(isinstance(new_name, str))

        if not new_name:
            log.debug('Unable to assemble basename with template "{!s}" and '
                      'data: {!s}'.format(template, data))
            raise exceptions.NameBuilderError('Unable to assemble basename')

        self._new_name = new_name
        return new_name


def populate_name_template(name_template, **kwargs):
    """
    Assembles a basename string from a given "name_template" format string
    that is populated with an arbitrary number of keyword arguments.

    Args:
        name_template: The format string to populate and return.
        **kwargs: An arbitrary number of keyword arguments used to fill out
            the format string.

    Returns:
        A string on the form specified by the given name template, populated
        with values from the given argument keywords.

    Raises:
        NameTemplateSyntaxError: Error due to either an invalid "name_template"
            or insufficient/invalid keyword arguments.
    """
    if not isinstance(name_template, str):
        raise TypeError('"name_template" must be of type "str"')

    if "'" or '"' in name_template:
        log.debug('Removing single and double quotes from template: '
                  '"{!s}"'.format(name_template))
    while "'" in name_template:
        name_template = name_template.replace("'", '')
    while '"' in name_template:
        name_template = name_template.replace('"', '')

    # NOTE: Used to validate name formatting strings in the configuration file.
    try:
        out = name_template.format(**kwargs)
    except (TypeError, KeyError) as e:
        raise exceptions.NameTemplateSyntaxError(e)
    else:
        return out


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


def pre_assemble_format(data, config):
    out = {}

    # TODO: [TD0017][TD0041] This needs refactoring, badly.
    # [TD0049] Think about defining legal "placeholder fields".
    #          .. Instead of passing wrapped types, pass wrapped fields?

    for key, value in data.items():
        if key == 'datetime':
            datetime_format = config.options['DATETIME_FORMAT']['datetime']
            out[key] = formatted_datetime(data[key], datetime_format)
        elif key == 'date':
            datetime_format = config.options['DATETIME_FORMAT']['date']
            out[key] = formatted_datetime(data[key], datetime_format)
        elif key == 'time':
            datetime_format = config.options['DATETIME_FORMAT']['time']
            out[key] = formatted_datetime(data[key], datetime_format)

        # TODO: [TD0044] Rework converting "raw data" to an internal format.
        else:
            # TODO: [TD0004] Take a look at this ad-hoc encoding boundary.
            if isinstance(value, bytes):
                value = util.decode_(value)
                out[key] = value
            else:
                out[key] = data[key]

            # TODO: [TD0017] Get file extension from MIME type strings.
            if key == 'extension':
                _maybe_mime_type = out.get(key)
                if re.match(r'^[a-z]+/[a-z0-9\-+]+$', _maybe_mime_type):
                    out[key] = _maybe_mime_type.split('/')[1]

        # TODO: [TD0041] Other substitutions, etc ..

    return out


def formatted_datetime(datetime_object, format_string):
    """
    Takes a date/time string, converts it to a datetime object and
    returns a formatted version on the form specified with "format_string".

    Note that the parsing of "datetime_string" might fail.
    TODO: Handle the [raw data] -> [formatted datetime] conversion better!

    Args:
        datetime_object: Date/time information as a datetime object.
        format_string: The format string to use for the output. Refer to:
            https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

    Returns:
        A string in the specified format with the data from the given string.
    """
    assert(isinstance(datetime_object, datetime))
    return datetime_object.strftime(format_string)


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


def has_data_for_placeholder_fields(template, data):
    placeholder_fields = format_string_placeholders(template)
    result = True
    for field in placeholder_fields:
        if field not in data.keys():
            log.error('Missing data for placeholder field "{}"'.format(field))
            result = False
    return result
