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
import os
import re
import operator

from core import (
    exceptions,
    fileobject,
    util
)


class RuleMatcher(object):
    def __init__(self, file_object, analysis_results, active_config):
        self.file = file_object
        self.analysis_data = analysis_results
        self.config = active_config

        self._matched_rules = []

    def start(self):
        self._evaluate_rules()

    @property
    def best_match(self):
        if not self._matched_rules:
            return False
        return self._matched_rules[0]

    def _evaluate_rules(self):
        if not self.config.file_rules:
            log.error('Configuration did not provide any rules to evaluate')
            return

        # Check a copy of all rules.
        rules_to_examine = self.config.file_rules
        log.debug('Examining {} rules ..'.format(len(rules_to_examine)))
        ok_rules = examine_rules(rules_to_examine, self.file,
                                 self.analysis_data)
        if len(ok_rules) == 0:
            log.debug('No valid rules remain after evaluation')
            return

        log.debug('Prioritizing remaining {} rules ..'.format(len(ok_rules)))
        ok_rules = prioritize_rules(ok_rules)
        for i, rule in enumerate(ok_rules):
            log.debug('{}. (score: {}, weight: {}) {} '.format(
                i + 1, rule.score, rule.weight, rule.description)
            )

        self._matched_rules = ok_rules


def prioritize_rules(rules):
    """
    Prioritizes (sorts) a list of 'FileRule' instances.

    The list is sorted first by "score" and then by "weight".

    Args:
        rules: The list of 'FileRule' instances to prioritize/sort.

    Returns:
        A sorted/prioritized list of 'FileRule' instances.
    """
    return sorted(rules, reverse=True,
                  key=operator.attrgetter('score', 'weight'))


def examine_rules(rules_to_examine, file_object, analysis_data):
    # Conditions are evaluated with the current file object and current
    # analysis results data.
    # If a rule requires an exact match, it is skipped at first failed
    # evaluation.
    ok_rules = []

    for count, rule in enumerate(rules_to_examine):
        log.debug('Evaluating rule {}/{}: "{}"'.format(count + 1,
                                                       len(rules_to_examine),
                                                       rule.description))
        result = evaluate_rule(rule, file_object, analysis_data)
        if rule.exact_match and result is False:
            log.debug('Rule evaluated FALSE, removing: '
                      '"{}"'.format(rule.description))
            continue

        log.debug('Rule evaluated TRUE: "{}"'.format(rule.description))
        ok_rules.append(rule)

    return ok_rules


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
    if not file_rule.conditions:
        raise exceptions.InvalidFileRuleError(
            'Rule does not specify any conditions'
        )

    if file_rule.exact_match:
        for cond_field, cond_value in file_rule.conditions.items():
            log.debug('Evaluating condition "{} == {}"'.format(cond_field,
                                                               cond_value))
            if not eval_condition(cond_field, cond_value, file_object,
                                  analysis_data):
                log.debug('Condition FAILED -- Exact match impossible ..')
                return False
            else:
                file_rule.upvote()
        return True

    for cond_field, cond_value in file_rule.conditions.items():
        log.debug('Evaluating condition "{} == {}"'.format(cond_field,
                                                           cond_value))
        if eval_condition(cond_field, cond_value, file_object, analysis_data):
            log.debug('Condition Passed rule.votes++')
            file_rule.upvote()
        else:
            # NOTE: file_rule.downvote()?
            # log.debug('Condition FAILED rule.votes--')
            log.debug('Condition FAILED')

    # Rule was not completely discarded but could still have failed all tests.
    return True


def eval_condition(condition_field, condition_value, file_object,
                   analysis_data):
    """
    Evaluates a condition.

    Evaluates a CONDITION, given as a condition field (like "basename") and a
    associated condition value (like "test.jpg").
    The evaluation process depends on the condition field.
    The condition value ("expected") is compared with data in the file
    object and analysis data ("actual").

    Args:
        condition_field:
        condition_value:
        file_object:
        analysis_data:

    Returns:
    """
    # TODO: Needs a COMPLETE rewrite using some general (GOOD) method!

    def eval_regex(expression, match_data):
        if re.match(expression, match_data):
            return True
        return False

    def eval_path(expression, match_data):
        # TODO: [hack] Total rewrite of condition evaluation?
        if expression.startswith(b'~/'):
            try:
                expression = os.path.expanduser(expression)
                expression = os.path.normpath(os.path.abspath(expression))
            except OSError as e:
                log.error('Error while evaluating path: {!s}'.format(e))
                log.debug('eval_path expression: "{!s}" match_data: '
                          '"{!s}"'.format(expression, match_data))
                return False

        # NOTE: Use simple UNIX-style globbing instead of regular expressions?
        try:
            if re.match(expression, match_data):
                return True
        except ValueError:
            pass
        return False

    def eval_mime_type(expression, match_data):
        if fileobject.eval_magic_glob(match_data, expression):
            return True
        return False

    def eval_datetime(expression, match_data):
        # TODO: Implement!
        return True

    # Regex Fields
    if condition_field == 'basename':
        # TODO: [encoding] Handle configuration encoding elsewhere.
        condition_value = util.encode_(condition_value)
        return eval_regex(condition_value, file_object.filename)

    elif condition_field == 'extension':
        # TODO: [encoding] Handle configuration encoding elsewhere.
        condition_value = util.encode_(condition_value)
        return eval_regex(condition_value, file_object.suffix)

    elif condition_field == 'pathname':
        # TODO: [encoding] Handle configuration encoding elsewhere.
        condition_value = util.encode_(condition_value)
        return eval_path(condition_value, file_object.pathname)

    # TODO: Fix MIME type check
    elif condition_field == 'mime_type':
        return eval_mime_type(condition_value, file_object.mime_type)

    # TODO: Implement datetime check
    elif condition_field == 'date_accessed':
        return eval_datetime(condition_value, None)

    else:
        raise exceptions.AutonameowException('Unhandled condition check!')
