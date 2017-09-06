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
from datetime import datetime

from core import (
    exceptions,
    fields,
    repository,
    util,
)
from core.util import diskutils
from extractors import ExtractedData

log = logging.getLogger(__name__)


class NameBuilder(object):
    """
    Constructs a new filename for a 'FileObject' given a name template and
    a data sources dict mapping name template fields to "meowURIs".
    """
    def __init__(self, file_object, active_config, name_template, data_sources):
        self.file = file_object
        self.config = active_config
        self.name_template = name_template
        self.data_sources = data_sources

        self._new_name = None

    @property
    def new_name(self):
        return self._new_name

    def request_data(self, file_object, meowuri):
        log.debug('Requesting [{!s}] "{!s}"'.format(file_object, meowuri))
        response = repository.SessionRepository.resolve(file_object, meowuri)
        log.debug('Got response ({}): {!s}'.format(type(response), response))
        if response is not None and isinstance(response, ExtractedData):
            # TODO: Clean up ..
            log.debug('Formatting response value "{!s}"'.format(response.value))
            formatted = response.wrapper.format(response.value)
            if formatted and not formatted == response.wrapper.null:
                log.debug('Response value formatted: "{!s}"'.format(formatted))
                return formatted
            else:
                log.debug(
                    'ERROR when formatted value "{!s}"'.format(response.value)
                )
        else:
            return response

    def _gather_data(self, field_meowuri_map):
        """
        Populates a dictionary with data fields matching a "meowURI".

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

        # NOTE(jonas): Mapping specified sources to extracted data and
        # analysis results must be redesigned. Sources must be queried
        # individually. Requires re-evaluating the configuration source
        # description format.
        # TODO: [TD0017] Rethink source specifications relation to source data.
        # TODO: [TD0082] Integrate the 'ExtractedData' class.
        for field, meowuri in field_meowuri_map.items():
            #if field == 'extension':
            #    _data = self.request_data(self.file, meowuri,
            #                              mapped_to_field=fields.extension)
            #else:
            #    _data = self.request_data(self.file, meowuri)

            _data = self.request_data(self.file, meowuri)
            if _data:
                out[field] = _data

        return out

    def build(self):
        log.debug('Using name template: "{}"'.format(self.name_template))

        # TODO: [TD0024][TD0017] Should be able to handle fields not in sources.
        # Add automatically resolving missing sources from possible candidates.

        # TODO: [TD0062] Move test for name template fields mapping to sources.
        # NOTE(jonas): Move this to the rule matcher?
        # Or maybe to when reading the configuration, which would give a
        # heads-up on that switching to the "interactive mode" would be
        # required in order to complete the rename. This would be useful to
        # implement the feature to force non-interactive mode, see [TD0023].

        if not all_template_fields_defined(self.name_template,
                                           self.data_sources):
            log.error('All name template placeholder fields must be '
                      'given a data source; Check the configuration!')
            raise exceptions.NameBuilderError(
                'Some template field sources are unknown'
            )

        # Get a dictionary of data to pass to 'assemble_basename'.
        # Should be keyed by the placeholder fields used in the name template.
        data = self._gather_data(self.data_sources)
        if not data:
            log.warning('Unable to get data from specified sources')
            raise exceptions.NameBuilderError('Unable to assemble basename')

        log.debug('NameBuilder results field query returned: {!s}'.format(data))

        # Check that all name template fields can be populated.
        if not has_data_for_placeholder_fields(self.name_template, data):
            log.warning('Unable to populate name. Missing field data.')
            raise exceptions.NameBuilderError('Unable to assemble basename')

        # TODO: [TD0017][TD0041] Format ALL data before assembly!
        # NOTE(jonas): This step is part of a ad-hoc encoding boundary.
        data = pre_assemble_format(data, self.config)
        log.debug('After pre-assembly formatting;')
        log.debug(str(data))

        # Construct the new file name
        try:
            new_name = populate_name_template(self.name_template, **data)
        except exceptions.NameTemplateSyntaxError as e:
            log.debug('Unable to assemble basename with template "{!s}" and '
                      'data: {!s}'.format(self.name_template, data))
            raise exceptions.NameBuilderError(
                'Unable to assemble basename: {!s}'.format(e)
            )

        assert(isinstance(new_name, str))
        log.debug('Assembled basename: "{!s}"'.format(new_name))

        # Do any file name "sanitation".
        if self.config.get(['FILESYSTEM_OPTIONS', 'sanitize_filename']):
            if self.config.get(['FILESYSTEM_OPTIONS', 'sanitize_strict']):
                log.debug('Sanitizing filename (restricted=True)')
                new_name = diskutils.sanitize_filename(new_name,
                                                       restricted=True)
            else:
                log.debug('Sanitizing filename')
                new_name = diskutils.sanitize_filename(new_name)

            log.debug('Sanitized basename (unicode): "{!s}"'.format(
                util.displayable_path(new_name))
            )
        else:
            log.debug('Skipped sanitizing filename')

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

        elif key == 'tags':
            assert(isinstance(value, list))
            out[key] = ' '.join(value)

        # TODO: [TD0044] Rework converting "raw data" to an internal format.
        else:
            # TODO: [TD0004] Take a look at this ad-hoc encoding boundary.
            if isinstance(value, bytes):
                log.error('Unexpectedly got "bytes": "{!s}"'.format(value))
                value = util.decode_(value)
                out[key] = value
            else:
                out[key] = data[key]

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


def probable_extension(file_object):
    # TODO: [TD0017] Get file extension for MIME-type.
    import mimetypes
    candidates = mimetypes.guess_all_extensions(mime_type)
    if file_object.extension in candidates:
        return file_object.extension
    pass
