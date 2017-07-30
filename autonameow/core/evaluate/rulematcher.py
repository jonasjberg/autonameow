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

import copy

from core import exceptions


class RuleMatcher(object):
    def __init__(self, analysis_results, extracted_data, active_config):
        self.analysis_data = analysis_results
        self.extraction_data = extracted_data

        if not active_config or not active_config.file_rules:
            log.error('Configuration does not contain any rules to evaluate')
            self._rules = []
        else:
            # NOTE(jonas): Check a copy of all rules.
            # Temporary fix for mutable state in the 'FileRule' instances,
            # which are initialized *once* when the configuration is loaded.
            # This same configuration instance is used when iterating over the
            # files. The 'FileRule' scores were not reset between files.
            self._rules = copy.deepcopy(active_config.file_rules)

        self._candidates = []
        self._data_sources = [self.extraction_data, self.analysis_data]

    def query_data(self, query_string):
        for source in self._data_sources:
            data = source.get(query_string)
            if data:
                return data

    def start(self):
        log.debug('Examining {} rules ..'.format(len(self._rules)))
        ok_rules = examine_rules(self._rules, self.query_data)
        if len(ok_rules) == 0:
            log.debug('No valid rules remain after evaluation')
            return

        log.debug('Prioritizing remaining {} candidates ..'.format(len(ok_rules)))
        ok_rules = prioritize_rules(ok_rules)
        for i, rule in enumerate(ok_rules):
            log.debug('{}. (score: {}, weight: {}) {} '.format(
                i + 1, rule.score, rule.weight, rule.description)
            )

        self._candidates = ok_rules

    @property
    def best_match(self):
        if not self._candidates:
            return False
        return self._candidates[0]


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


def examine_rules(rules_to_examine, query_data):
    # Conditions are evaluated with the current file object and current
    # analysis results data.
    # If a rule requires an exact match, it is skipped at first failed
    # evaluation.
    ok_rules = []

    for count, rule in enumerate(rules_to_examine):
        log.debug('Evaluating rule {}/{}: "{}"'.format(
            count + 1, len(rules_to_examine), rule.description))
        result = evaluate_rule(rule, query_data)
        if rule.exact_match and result is False:
            log.debug('Rule evaluated FALSE, removing: '
                      '"{}"'.format(rule.description))
            continue

        log.debug('Rule evaluated TRUE: "{}"'.format(rule.description))
        ok_rules.append(rule)

    return ok_rules


def evaluate_rule(file_rule, query_data):
    """
    Tests if a rule applies to a given file.

    Returns at first unmatched condition if the rule requires an exact match.
    If the rule does not require an exact match, all conditions are
    evaluated and the rule is scored through "upvote()" and "downvote()".

    Args:
        file_rule: The rule to test as an instance of 'FileRule'.
        query_data: Callback function used to query available data.

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
        for condition in file_rule.conditions:
            log.debug('Evaluating condition "{!s}"'.format(condition))
            if not eval_condition(condition, query_data):
                log.debug('Condition FAILED -- Exact match impossible ..')
                return False
            else:
                file_rule.upvote()
        return True

    for condition in file_rule.conditions:
        log.debug('Evaluating condition "{!s}"'.format(condition))
        if eval_condition(condition, query_data):
            log.debug('Condition Passed rule.votes++')
            file_rule.upvote()
        else:
            # NOTE: file_rule.downvote()?
            # log.debug('Condition FAILED rule.votes--')
            log.debug('Condition FAILED')

    # Rule was not completely discarded but could still have failed all tests.
    return True


def eval_condition(condition, query_data):
    query_string = condition.query_string
    data = query_data(query_string)
    return condition.evaluate(data)
