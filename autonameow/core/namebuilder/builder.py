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

import re
import logging

from core import exceptions
from core.namebuilder.fields import NameTemplateField
from util import encoding as enc
from util import (
    disk,
    sanity,
)


log = logging.getLogger(__name__)


def build(config, name_template, field_databundle_dict):
    """
    Constructs a new filename given a name template and a dict mapping
    name template fields to data to be populated in each field.
    """
    log.debug('Using name template "{!s}"'.format(name_template))

    if not field_databundle_dict:
        log.error('Name builder got empty data map! This should not happen ..')
        raise exceptions.NameBuilderError('Unable to assemble basename')

    # NOTE(jonas): This step is part of a ad-hoc encoding boundary.
    formatted_fields = pre_assemble_format(field_databundle_dict, config)

    # TODO: Move to use name template field classes as keys.
    data = _with_simple_string_keys(formatted_fields)

    log.debug('After pre-assembly formatting;')
    log.debug(str(data))

    # Construct the new file name
    str_name_template = str(name_template)
    try:
        new_name = populate_name_template(str_name_template, **data)
    except (exceptions.NameTemplateSyntaxError, TypeError) as e:
        log.debug('Unable to assemble basename with name template "{!s}" '
                  'and data: {!s}'.format(name_template, data))
        raise exceptions.NameBuilderError(
            'Unable to assemble basename: {!s}'.format(e)
        )

    sanity.check_internal_string(new_name)
    new_name = post_assemble_format(new_name)
    log.debug('Assembled basename: "{!s}"'.format(new_name))

    # Do any file name "sanitation".
    if config.get(['POST_PROCESSING', 'sanitize_filename']):
        if config.get(['POST_PROCESSING', 'sanitize_strict']):
            log.debug('Sanitizing filename (restricted=True)')
            new_name = disk.sanitize_filename(new_name, restricted=True)
        else:
            log.debug('Sanitizing filename')
            new_name = disk.sanitize_filename(new_name)

        log.debug('Sanitized basename (unicode): '
                  '"{!s}"'.format(enc.displayable_path(new_name)))
    else:
        log.debug('Skipped sanitizing filename')

    # TODO: [TD0036] Allow per-field replacements and customization.
    return new_name


def pre_assemble_format(field_databundle_dict, config):
    out = dict()

    for field, data in field_databundle_dict.items():
        log.debug('pre_assemble_format("{!s}", "{!s}")'.format(field, data))
        assert field and isinstance(field, NameTemplateField)
        from core.repository import DataBundle
        assert data and isinstance(data, DataBundle)

        # TODO: [TD0115] Clear up uncertainties about data multiplicities
        if data.multivalued:
            if not field.MULTIVALUED:
                log.critical(
                    'Template field {!s} expects a single value. Got '
                    'multivalued data'.format(field)
                )
                raise exceptions.NameBuilderError(
                    'Template field {!s} expects a single value. '
                    'Got {} values'.format(field, len(data))
                )

        _formatted = field.format(data, config=config)
        if _formatted is not None:
            out[field] = _formatted
        else:
            raise exceptions.NameBuilderError(
                'Unable to format name template field "{!s}"'.format(field)
            )

    return out


def _with_simple_string_keys(data_dict):
    return {k.as_placeholder(): v for k, v in data_dict.items()}


def post_assemble_format(new_name):
    return new_name.rstrip('.')


def _remove_single_and_double_quotes(string):
    return re.sub(r'[\'"]+', '', string)


def populate_name_template(format_string, **kwargs):
    """
    Assembles a basename string from a given "format_string" filename format
    string that is populated with an arbitrary number of keyword arguments.

    Args:
        format_string: The filename format string to populate and return,
                       as a Unicode string.
        **kwargs: An arbitrary number of keyword arguments used to fill out
                  the filename format string.

    Returns:
        A string on the form specified by the given name template, populated
        with values from the given argument keywords.

    Raises:
        NameTemplateSyntaxError: Error due to either an invalid "format_string"
                                 or insufficient/invalid keyword arguments.
    """
    if not isinstance(format_string, str):
        raise TypeError('Argument "format_string" must be of type "str"')

    if "'" or '"' in format_string:
        log.debug('Removing single and double quotes from format string '
                  '"{!s}"'.format(format_string))
        format_string = _remove_single_and_double_quotes(format_string)

    # NOTE: Used to validate format strings in the configuration file.
    try:
        return format_string.format(**kwargs)
    except (TypeError, KeyError, ValueError) as e:
        raise exceptions.NameTemplateSyntaxError(e)
