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
import operator

from dateutil import parser

import core.config.configuration
from core.fileobject import FileObject
from core.exceptions import (
    NameTemplateSyntaxError,
    InvalidFileRuleError,
    AutonameowException,
    NameBuilderError
)
from core.util import cli


class NameBuilder(object):
    """
    Constructs a new filename for a FileObject given a set of rules,
    a file object and data gathered by analyzers.

    A rule contains the name template that determines the format of the
    resulting name. The rule also determines what analysis data to use when
    populating the name template fields.
    """
    # TODO: [BL010] Implement NameBuilder.
    def __init__(self, file_object, analysis_results, active_config):
        self.file = file_object
        self.analysis_data = analysis_results
        self.config = active_config

        self._new_name = None

    @property
    def new_name(self):
        return self._new_name

    def build(self):
        # TODO: [BL010] Implement NameBuilder.

        # TODO: Format date/time-information using "datetime_format" in config.

        template = None
        data_sources = None

        # Check a copy of all rules.
        # Conditions are evaluated with the current file object and current
        # analysis results data.
        # If a rule requires an exact match, it is skipped at first failed
        # evaluation. After evaluating all rules, the remaining rules in
        # "ok_rules" are sorted. The first rule in the resulting list is used.
        rules_to_examine = list(self.config.file_rules)

        ok_rules = examine_rules(rules_to_examine, self.file,
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

        active_rule = rules_sorted[0]
        cli.msg('Using file rule: {}'.format(active_rule.description))

        template = active_rule.name_template
        log.debug('Using name template: {}'.format(template))

        data_sources = active_rule.data_sources

        if not all_template_fields_defined(template, data_sources):
            log.error('All name template placeholder fields must be '
                      'given a data source; Check the configuration!')
            raise NameBuilderError('Some template field sources are unknown')

        # Get a dictionary of data to pass to 'assemble_basename'.
        # Should be keyed by the placeholder fields used in the name template.
        data = self.analysis_data.query(data_sources)
        log.debug('Query for results fields returned:')
        log.debug(str(data))

        # Format datetime
        data = pre_assemble_format(data, template, self.config)
        log.debug('After pre-assembly formatting;')
        log.debug(str(data))

        # TODO: Populate "template" with entries from "self.analysis_data"
        # TODO: as specified in "data_sources".

        result = assemble_basename(template, **data)
        log.debug('Assembled basename: "{}"'.format(result))

        if not result:
            log.debug('Unable to assemble basename with template "{!s}" and '
                      'data: {!s}'.format(template, data))
            raise NameBuilderError('Unable to assemble basename')

        return result


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


def examine_rules(rules_to_examine, file_object, analysis_data):
    ok_rules = []

    for count, rule in enumerate(rules_to_examine):
        log.debug('Evaluating rule {}/{}: "{}"'.format(count + 1,
                                                       len(rules_to_examine),
                                                       rule.description))
        result = evaluate_rule(rule, file_object, analysis_data)
        if rule.exact_match and result is False:
            log.debug('Rule evaluated false, removing: '
                      '"{}"'.format(rule.description))
            continue

        log.debug('Rule evaluated true: "{}"'.format(rule.description))
        ok_rules.append(rule)

    return ok_rules


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


def eval_condition(condition_field, condition_value, file_object,
                   analysis_data):
    def eval_regex(expression, match_data):
        if re.match(expression, match_data):
            return True
        return False

    def eval_mime_type(expression, match_data):
        if expression == match_data:
            return True
        return False

    def eval_datetime(expression, match_data):
        # TODO: Implement!
        return True

    # Regex Fields
    if condition_field == 'basename':
        return eval_regex(condition_value, file_object.filename)

    elif condition_field == 'extension':
        return eval_regex(condition_value, file_object.suffix)

    elif condition_field == 'pathname':
        return eval_regex(condition_value, file_object.abspath)

    # TODO: Fix MIME type check
    elif condition_field == 'mime_type':
        return eval_mime_type(condition_value, file_object.mime_type)

    # TODO: Implement datetime check
    elif condition_field == 'date_accessed':
        return eval_datetime(condition_value, None)

    else:
        raise AutonameowException('Unhandled condition check!')


def evaluate_rule(file_rule, file_object, analysis_data):
    """
    Tests if a rule applies to a given file.

    Returns at first unmatched condition if the rule requires an exact match.
    If the rule does not require an exact match, all conditions are
    evaluated and the rule is scored through "upvote()" and "downvote()".

    Args:
        file_object: The file to test as an instance of 'FileObject'.
        file_rule: The rule to test as an instance of 'FileRule'.
        analysis_data: Results data from analysis of the given file.

    Returns:
        If the rule requires an exact match:
            True if all rule conditions evaluates to True.
            False if any rule condition evaluates to False.
        If the rule does not require an exact match:
            True
    """
    if not isinstance(file_object, FileObject):
        raise TypeError('"file_object" must be instance of "FileObject"')
    if not isinstance(file_rule, core.config.configuration.FileRule):
        raise TypeError('"file_rule" must be instance of "FileRule"')
    if not file_rule.conditions:
        raise InvalidFileRuleError('Rule does not specify any conditions')

    if file_rule.exact_match:
        for cond_field, cond_value in file_rule.conditions.items():
            log.debug('Evaluating condition "{} == {}"'.format(cond_field,
                                                               cond_value))
            if not eval_condition(cond_field, cond_value, file_object,
                                  analysis_data):
                log.debug('Condition FAILED -- Exact match impossible ..')
                return False
            else:
                file_rule.upvote()
        return True

    for cond_field, cond_value in file_rule.conditions.items():
        log.debug('Evaluating condition "{} == {}"'.format(cond_field,
                                                           cond_value))
        if eval_condition(cond_field, cond_value, file_object, analysis_data):
            log.debug('Condition Passed rule.votes++')
            file_rule.upvote()
        else:
            # file_rule.downvote()
            # log.debug('Condition FAILED rule.votes--')
            log.debug('Condition FAILED')

    # Rule was not completely discarded but could still have failed all tests.
    return True


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

    # TODO: Handle this properly and more generally

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
        datetime_object = parser.parse(datetime_string)
    except (TypeError, ValueError) as e:
        log.error('Unable to format datetime string: "{!s}"'.format(
            datetime_string))
    else:
        return datetime_object.strftime(format_string)
