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
import operator
import re

from core.evaluate import rulematcher
from core.exceptions import (
    NameTemplateSyntaxError,
    NameBuilderError
)
from core.util import dateandtime


class NameBuilder(object):
    """
    Constructs a new filename for a FileObject given a set of rules,
    a file object and data gathered by analyzers.

    A rule contains the name template that determines the format of the
    resulting name. The rule also determines what analysis data to use when
    populating the name template fields.
    """
    def __init__(self, file_object, analysis_results, active_config):
        self.file = file_object
        self.analysis_data = analysis_results
        self.config = active_config

        self._new_name = None

    @property
    def new_name(self):
        return self._new_name

    def build(self):
        # Check a copy of all rules.
        # Conditions are evaluated with the current file object and current
        # analysis results data.
        # If a rule requires an exact match, it is skipped at first failed
        # evaluation. After evaluating all rules, the remaining rules in
        # "ok_rules" are sorted. The first rule in the resulting list is used.
        rules_to_examine = list(self.config.file_rules)

        ok_rules = rulematcher.examine_rules(rules_to_examine, self.file,
                                             self.analysis_data)

        if len(ok_rules) == 0:
            log.debug('No valid rules remain after evaluation')
            raise NameBuilderError('None of the rules seem to apply')

        log.debug('Prioritizing (sorting) remaining {} rules'
                  ' ..'.format(len(ok_rules)))
        rules_sorted = sorted(ok_rules, reverse=True,
                              key=operator.attrgetter('score', 'weight'))
        for i, rule in enumerate(rules_sorted):
            log.debug('{}. (score: {}, weight: {}) {} '.format(i + 1,
                      rule.score, rule.weight, rule.description))

        # A rule is chosen
        active_rule = rules_sorted[0]
        log.info('Using file rule: "{!s}"'.format(active_rule.description))

        template = active_rule.name_template
        log.debug('Using name template: "{}"'.format(template))

        data_sources = active_rule.data_sources

        # TODO: Future redesign should be able to handle fields not in sources.
        # Add automatically resolving missing sources from possible candidates.
        if not rulematcher.all_template_fields_defined(template, data_sources):
            log.error('All name template placeholder fields must be '
                      'given a data source; Check the configuration!')
            raise NameBuilderError('Some template field sources are unknown')

        # Get a dictionary of data to pass to 'assemble_basename'.
        # Should be keyed by the placeholder fields used in the name template.
        data = self.analysis_data.query(data_sources)
        if not data:
            log.warning('Analysis data query did not return expected data.')
            raise NameBuilderError('Unable to assemble basename')

        log.debug('Query for results fields returned:')
        log.debug(str(data))

        # Format datetime
        # TODO: Format ALL data before assembly, not only date/time-information.
        data = pre_assemble_format(data, template, self.config)
        log.debug('After pre-assembly formatting;')
        log.debug(str(data))

        # Construct the new file name
        result = assemble_basename(template, **data)
        log.debug('Assembled basename: "{}"'.format(result))

        if not result:
            log.debug('Unable to assemble basename with template "{!s}" and '
                      'data: {!s}'.format(template, data))
            raise NameBuilderError('Unable to assemble basename')

        return result


def assemble_basename(name_template, **kwargs):
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
        log.debug('Removing single and double quotes from template')
    while "'" in name_template:
        name_template = name_template.replace("'", '')
    while '"' in name_template:
        name_template = name_template.replace('"', '')

    # NOTE: Used to validate name formatting strings in the configuration file.
    try:
        out = name_template.format(**kwargs)
    except (TypeError, KeyError) as e:
        raise NameTemplateSyntaxError(e)
    else:
        return out


def format_string_placeholders(format_string):
    """
    Gets the format string placeholder fields from a text string.

    The text "{foo} mjao baz {bar}" would return ['foo', 'bar'].

    Args:
        format_string: Format string to get placeholders from.

    Returns:
        Format string placeholder fields in the text as a list of strings.

    """
    if not format_string:
        return []
    return re.findall(r'{(\w+)}', format_string)


def pre_assemble_format(data, template, config):
    out = {}

    # TODO: This needs refactoring, badly.

    for key, value in data.items():
        if key == 'datetime':
            datetime_format = config.options['DATETIME_FORMAT']['datetime']
            out['datetime'] = formatted_datetime(data['datetime'],
                                                 datetime_format)
        elif key == 'date':
            datetime_format = config.options['DATETIME_FORMAT']['date']
            out['date'] = formatted_datetime(data['date'],
                                             datetime_format)
        elif key == 'time':
            datetime_format = config.options['DATETIME_FORMAT']['time']
            out['time'] = formatted_datetime(data['time'],
                                             datetime_format)
        else:
            # TODO: Other substitutions, etc ..
            out[key] = data[key]

    return out


def formatted_datetime(datetime_string, format_string):
    """
    Takes a date/time string, converts it to a datetime object and
    returns a formatted version on the form specified with "format_string".

    Note that the parsing of "datetime_string" might fail.
    TODO: Handle the [raw data] -> [formatted datetime] conversion better!

    Args:
        datetime_string: Date/time information as a string.
        format_string: The format string to use for the output. Refer to:
            https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

    Returns:
        A string in the specified format with the data from the given string.
    """

    try:
        datetime_object = dateandtime.to_datetime(datetime_string)
    except (TypeError, ValueError) as e:
        log.error('Unable to format datetime string: "{!s}"'.format(
            datetime_string))
    else:
        return datetime_object.strftime(format_string)
