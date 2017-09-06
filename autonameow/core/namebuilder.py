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
from datetime import datetime

from core import (
    exceptions,
    util,
)
from core.util import diskutils

log = logging.getLogger(__name__)


class NameBuilder(object):
    """
    Constructs a new filename for a 'FileObject' given a name template and
    a dict mapping name template fields to data to be populated in each field.
    """
    def __init__(self, file_object, active_config, name_template, field_data_map):
        self.file = file_object
        self.config = active_config
        self.name_template = name_template
        self.field_data_map = field_data_map

        self._new_name = None

    @property
    def new_name(self):
        return self._new_name

    def build(self):
        log.debug('Using name template: "{}"'.format(self.name_template))

        data = self.field_data_map
        if not data:
            log.error('Name builder got empty data! This should not happen ..')
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
        new_name = post_assemble_format(new_name)
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


def post_assemble_format(new_name):
    return new_name.rstrip('.')


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


