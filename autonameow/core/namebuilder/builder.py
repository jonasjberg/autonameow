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
    util,
)
from core.util import (
    diskutils,
    sanity
)
from core.model import ExtractedData

log = logging.getLogger(__name__)


def build(config, name_template, field_data_map):
    """
    Constructs a new filename given a name template and a dict mapping
    name template fields to data to be populated in each field.
    """
    log.debug('Using name template: "{}"'.format(name_template))

    # TODO: Move to use name template field classes as keys.
    data = _with_simple_string_keys(field_data_map)

    if not field_data_map:
        log.error('Name builder got empty data map! This should not happen ..')
        raise exceptions.NameBuilderError('Unable to assemble basename')

    # TODO: [TD0017][TD0041] Format ALL data before assembly!
    # NOTE(jonas): This step is part of a ad-hoc encoding boundary.
    data = pre_assemble_format(data, config)
    log.debug('After pre-assembly formatting;')
    log.debug(str(data))

    # Construct the new file name
    try:
        new_name = populate_name_template(name_template, **data)
    except (exceptions.NameTemplateSyntaxError, TypeError) as e:
        log.debug('Unable to assemble basename with template "{!s}" and '
                  'data: {!s}'.format(name_template, data))
        raise exceptions.NameBuilderError(
            'Unable to assemble basename: {!s}'.format(e)
        )

    sanity.check_internal_string(new_name)
    new_name = post_assemble_format(new_name)
    log.debug('Assembled basename: "{!s}"'.format(new_name))

    # Do any file name "sanitation".
    if config.get(['FILESYSTEM_OPTIONS', 'sanitize_filename']):
        if config.get(['FILESYSTEM_OPTIONS', 'sanitize_strict']):
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

    # Do any case-transformations.
    if config.get(['FILESYSTEM_OPTIONS', 'lowercase_filename']):
        new_name = new_name.lower()
    elif config.get(['FILESYSTEM_OPTIONS', 'uppercase_filename']):
        new_name = new_name.upper()

    # Do any user-defined "custom post-processing".
    replacements = config.get(['CUSTOM_POST_PROCESSING', 'replacements'])
    if replacements:
        for regex, replacement in replacements:
            if re.search(regex, new_name):
                log.info('Applying custom replacement. Regex: "{!s}" '
                         'Replacement: "{!s}"'.format(regex, replacement))
                new_name = re.sub(regex, replacement, new_name)

    # TODO: [TD0036] Allow per-field replacements and customization.

    return new_name


def _with_simple_string_keys(data_dict):
    return {k.as_placeholder(): v for k, v in data_dict.items()}


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
    formatted = {}

    # TODO: [TD0017][TD0041] This needs refactoring, badly.
    # [TD0049] Think about defining legal "placeholder fields".
    #          .. Instead of passing wrapped types, pass wrapped fields?

    for field, value in data.items():
        log.debug('Pre-assembly formatting field "{!s}"'.format(field))

        # TODO: [TD0082] Integrate the 'ExtractedData' class.
        if isinstance(data[field], ExtractedData):
            d = value.value
        else:
            d = value

        if field == 'datetime':
            datetime_format = config.options['DATETIME_FORMAT']['datetime']
            formatted[field] = formatted_datetime(d, datetime_format)
        elif field == 'date':
            datetime_format = config.options['DATETIME_FORMAT']['date']
            formatted[field] = formatted_datetime(d, datetime_format)
        elif field == 'time':
            datetime_format = config.options['DATETIME_FORMAT']['time']
            formatted[field] = formatted_datetime(d, datetime_format)

        elif field == 'tags':
            sanity.check_isinstance(value, list)

            _tags = []
            for _tag in value:
                if isinstance(_tag, ExtractedData):
                    _tag = _tag.value
                else:
                    log.critical('TODO: Fix lists of "ExtractedData"')

                _tags.append(_tag)

            sep = config.options['FILETAGS_OPTIONS']['between_tag_separator']
            formatted[field] = sep.join(_tags)

        # TODO: [TD0044] Rework converting "raw data" to an internal format.
        else:
            _formatted = format_field(field, value)
            if _formatted is not None:
                formatted[field] = _formatted

        # TODO: [TD0041] Other substitutions, etc ..

    return formatted


def format_field(field, data):
    # TODO: [TD0082] Integrate the 'ExtractedData' class.
    if isinstance(data, ExtractedData):
        log.debug('Formatting data.value "{!s}"'.format(data.value))

        if data.coercer:
            formatted = data.coercer.format(data.value, formatter=None)
            if formatted is not None and formatted != data.coercer.null:
                log.debug('Formatted value: "{!s}"'.format(formatted))
                return formatted
            else:
                log.debug('Unable to format field "{!s}" with value '
                          '"{!s}"'.format(field, data.value))
    elif data is not None:
        log.warning('Missing formatting information, not coerced in '
                    'ExtractedData: "{!s}": "{!s}"'.format(field, data))

        # TODO: [TD0088] Handle case where 'ExtractedData' isn't provided
        # with a 'coercer' and then also fails to autodetect a proper
        # 'coercer' class from the raw file type ..

        return data
    else:
        log.warning('"format_field" got None data (!)')

    return None


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
    sanity.check_isinstance(datetime_object, datetime)
    return datetime_object.strftime(format_string)


