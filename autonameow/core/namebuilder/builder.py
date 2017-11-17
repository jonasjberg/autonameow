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

from core import (
    disk,
    exceptions,
    ui,
    util
)
from core import constants as C
from core.namebuilder.fields import NameTemplateField
from core.util import sanity


log = logging.getLogger(__name__)


def build(config, name_template, field_data_map):
    """
    Constructs a new filename given a name template and a dict mapping
    name template fields to data to be populated in each field.
    """
    log.debug('Using name template: "{}"'.format(name_template))

    if not field_data_map:
        log.error('Name builder got empty data map! This should not happen ..')
        raise exceptions.NameBuilderError('Unable to assemble basename')

    # NOTE(jonas): This step is part of a ad-hoc encoding boundary.
    formatted_fields = pre_assemble_format(field_data_map, config)

    # TODO: Move to use name template field classes as keys.
    data = _with_simple_string_keys(formatted_fields)

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
    if config.get(['CUSTOM_POST_PROCESSING', 'sanitize_filename']):
        if config.get(['CUSTOM_POST_PROCESSING', 'sanitize_strict']):
            log.debug('Sanitizing filename (restricted=True)')
            new_name = disk.sanitize_filename(new_name, restricted=True)
        else:
            log.debug('Sanitizing filename')
            new_name = disk.sanitize_filename(new_name)

        log.debug('Sanitized basename (unicode): "{!s}"'.format(
            util.enc.displayable_path(new_name))
        )
    else:
        log.debug('Skipped sanitizing filename')

    # Do any case-transformations.
    if config.get(['CUSTOM_POST_PROCESSING', 'lowercase_filename']):
        new_name = new_name.lower()
    elif config.get(['CUSTOM_POST_PROCESSING', 'uppercase_filename']):
        new_name = new_name.upper()

    # Do any user-defined "custom post-processing".
    replacements = config.get(['CUSTOM_POST_PROCESSING', 'replacements'])
    if replacements:
        for regex, replacement in replacements:
            _match = re.search(regex, new_name)
            if _match:
                log.debug('Applying custom replacement. Regex: "{!s}" '
                          'Replacement: "{!s}"'.format(regex, replacement))
                msg_replacement(new_name, replacement, regex,
                                color=C.REPLACEMENT_HIGHLIGHT_COLOR)

                new_name = re.sub(regex, replacement, new_name)

    # TODO: [TD0036] Allow per-field replacements and customization.

    return new_name


def pre_assemble_format(field_data_dict, config):
    out = {}

    for field, data in field_data_dict.items():
        log.debug('pre_assemble_format("{!s}", "{!s}")'.format(field, data))
        assert field and issubclass(field, NameTemplateField)

        # TODO: [TD0115] Clear up uncertainties about data multiplicities
        if data.get('multivalued'):
            if not field.MULTIVALUED:
                log.critical(
                    'Template field "{!s}" expects a single value. Got '
                    'multivalued data'.format(field.as_placeholder())
                )
                raise exceptions.NameBuilderError(
                    'Template field "{!s}" expects a single value. '
                    'Got {} values'.format(field.as_placeholder(), len(data))
                )

        _formatted = field.format(data, config=config)
        if _formatted is not None:
            out[field] = _formatted
        else:
            raise exceptions.NameBuilderError(
                'Unable to format name template field "{!s}"'.format(field)
            )

    return out


def msg_replacement(original, replacement, regex, color):
    _name_old = ui.colorize_re_match(original, regex=regex, color=color)
    _name_new = _colorize_replacement(original, replacement, regex, color)
    log.info('Applying custom replacement: "{!s}" -> "{!s}"'.format(_name_old,
                                                                    _name_new))
    # TODO: [TD0096] Fix invalid colouring if the replacement is the last character.
    #
    # Applying custom replacement. Regex: "re.compile('\\.$')" Replacement: ""
    # Applying custom replacement: "2007-04-23_12-comments.png." -> "2007-04-23_12-comments.png"
    #                                                     ^   ^
    #                 Should not be colored red, but is --'   '-- Should be red, but isn't ..


def _colorize_replacement(original, replacement, regex, color):
    _colored_replacement = ui.colorize(replacement, fore=color)
    return re.sub(regex, _colored_replacement, original)


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
    except (TypeError, KeyError, ValueError) as e:
        raise exceptions.NameTemplateSyntaxError(e)
    else:
        return out

