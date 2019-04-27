# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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

from core import exceptions
from util import disk
from util import encoding as enc
from util.text import remove_zerowidth_spaces


log = logging.getLogger(__name__)


def build(config, name_template, field_databundle_dict):
    """
    Constructs a new filename given a name template and a dict mapping
    name template fields to data to be populated in each field.
    """

    # NOTE(jonas): Internal object representations to Unicode string boundary.
    # Learning techniques will need to keep track of a lot of details on
    # successful renames --- when a file is renamed (especially after being
    # explicitly confirmed by the user) whatever future learning systems might
    # be used need to receive this notification in a manner that allows looking
    # up detailed information on individual field values.
    #
    # Defer conversion from objects to strings for as long as possible.
    # TODO: Look into interactions between the renamer, builder and resolver.
    # TODO: [TD0092] Track file names accepted/used, suggested, discarded, etc.

    if not field_databundle_dict:
        raise exceptions.NameBuilderError(
            'Unexpectedly empty or None field/databundle dict'
        )

    # TODO: [cleanup] Remove this check once boundaries are defined.
    _assert_is_expected_types(field_databundle_dict)

    # NOTE(jonas): This step is part of a ad-hoc encoding boundary.
    formatted_fields = pre_assemble_format(field_databundle_dict, config)

    # TODO: Move to use name template field classes as keys.
    str_fields_values = _with_simple_string_keys(formatted_fields)

    log.debug('After pre-assembly formatting;')
    for str_field, str_value in str_fields_values.items():
        log.debug('Pre-assembly formatted field "%s": "%s"', str_field, str_value)

    # TODO: [TD0196] Allow user to define maximum lengths for new names.
    # TODO: [TD0197] Template field-specific length limits and trimming.

    # Construct the new file name
    str_name_template = str(name_template)
    log.debug('Populating name template "%s"', str_name_template)
    try:
        new_name = populate_name_template(str_name_template, **str_fields_values)
    except (exceptions.NameTemplateSyntaxError, TypeError) as e:
        log.debug('Unable to assemble basename with template "%s" and data %s',
                  name_template, str_fields_values)
        raise exceptions.NameBuilderError(
            'Unable to assemble basename: {!s}'.format(e)
        )

    assert isinstance(new_name, str)
    new_name = post_assemble_format(new_name)
    log.debug('Assembled basename: "%s"', new_name)

    # Do any file name "sanitation".
    if config.get(['POST_PROCESSING', 'sanitize_filename']):
        if config.get(['POST_PROCESSING', 'sanitize_strict']):
            log.debug('Sanitizing filename (restricted=True)')
            new_name = disk.sanitize_filename(new_name, restricted=True)
        else:
            log.debug('Sanitizing filename')
            new_name = disk.sanitize_filename(new_name)

        log.debug('Sanitized basename (unicode): "%s"', enc.displayable_path(new_name))
    else:
        log.debug('Skipped sanitizing filename')

    # TODO: [TD0036] Allow per-field replacements and customization.
    return new_name


def _assert_is_expected_types(field_databundle_dict):
    # TODO: [cleanup] Remove these assertions once boundaries are defined.
    from core.datastore.repository import DataBundle
    from core.namebuilder.fields import NameTemplateField

    for field, databundle in field_databundle_dict.items():
        assert field and isinstance(field, NameTemplateField)
        assert databundle and isinstance(databundle, DataBundle)


def pre_assemble_format(field_databundle_dict, config):
    formatted_values = dict()

    for field, databundle in field_databundle_dict.items():
        log.debug('pre_assemble_format(%s, %s)', field, databundle)

        # TODO: [TD0115] Clear up uncertainties about data multiplicities
        if databundle.multivalued:
            if not field.MULTIVALUED:
                raise exceptions.NameBuilderError(
                    'Name template field {!s} expects a single value but got '
                    'databundle with {} values'.format(field, len(databundle))
                )

        # TODO: [TD0036] Allow per-field replacements and customization.
        formatted_value = field.format(databundle, config=config)
        if formatted_value is None:
            raise exceptions.NameBuilderError(
                'Unable to format name template field "{!s}"'.format(field)
            )
        assert isinstance(formatted_value, str)
        formatted_values[field] = formatted_value

    return formatted_values


def _with_simple_string_keys(data_dict):
    return {k.as_placeholder(): v for k, v in data_dict.items()}


def post_assemble_format(new_name):
    # TODO: [TD0043][TD0036] Remove hardcoded behaviour and settings.
    modified_name = remove_zerowidth_spaces(new_name)
    modified_name = modified_name.rstrip('.')
    return modified_name


def _remove_single_and_double_quotes(string):
    # TODO: [TD0043][TD0036] Remove hardcoded behaviour and settings.
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
        # TODO: [TD0043][TD0036] Remove hardcoded behaviour and settings.
        log.debug('Removing single and double quotes from format string "%s"',
                  format_string)
        format_string = _remove_single_and_double_quotes(format_string)

    # NOTE: Used to validate format strings in the configuration file.
    try:
        return format_string.format(**kwargs)
    except (TypeError, KeyError, ValueError) as e:
        raise exceptions.NameTemplateSyntaxError(e)
