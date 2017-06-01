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

import core.config.configuration
from core.fileobject import FileObject
from core.exceptions import (
    NameTemplateSyntaxError,
    InvalidFileRuleError
)


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
        self.data = analysis_results
        self.config = active_config

        self._new_name = None

    @property
    def new_name(self):
        return self._new_name

    def build(self):
        # TODO: [BL010] Implement NameBuilder.

        #   Assemble basename requires;
        #   1. Name template string
        #     * Get rule that knows which string
        #         * Get rule matching current file
        #   2. Data to populate name template
        #     * Get rule that knows what data
        #         * Get rule matching current file
        #
        #   Assemble file sub-tasks;
        #   1. Get rule matching current file
        #   2. Get template string from rule
        #   3. Get data from analysis results, using sources given by the rule

        #   Test if rule matches current file tasks;
        #   1. For each rule;
        #     * Evaluate each condition, upvote for each passing condition
        #   2. For each rule requiring exact match;
        #     *


        template = None
        data_sources = None

        rules_to_examine = list(self.config.file_rules)

        for rule in rules_to_examine:
            if not evaluate_rule(rule, self.file):
                rules_to_examine.remove(rule)

        if len(rules_to_examine) == 0:
            # None of the rules apply to the file
            # TODO: ..
            return False

        # TODO: ..
        raise NotImplementedError('TODO: Implement NameBuilder')


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


def eval_condition(condition, file_object):
    # TODO: ..
    pass


def evaluate_rule(file_rule, file_object):
    """
    Tests if a rule applies to a given file.

    Args:
        file_object: The file to test as an instance of 'FileObject'.
        file_rule: The rule to test as an instance of 'FileRule'.

    Returns: True if the rule applies to the given file, else False.

    """
    if not isinstance(file_object, FileObject):
        raise TypeError('"file_object" must be instance of "FileObject"')
    if not isinstance(file_rule, core.config.configuration.FileRule):
        raise TypeError('"file_rule" must be instance of "FileRule"')

    if not file_rule.conditions:
        raise InvalidFileRuleError('Rule does not specify any conditions')

    # TODO: ..
    if file_rule.exact_match:
        for condition in file_rule.conditions:
            if not eval_condition(condition, file_object):
                return False
        return True

    for condition in file_rule.conditions:
        if eval_condition(condition, file_object):
            file_rule.upvote()
