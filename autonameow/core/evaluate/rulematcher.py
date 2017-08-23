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

from core import (
    exceptions,
    repository
)


class RuleMatcher(object):
    def __init__(self, file_object, active_config):
        self.file_object = file_object
        self.request_data = repository.SessionRepository.resolve

        if not active_config or not active_config.rules:
            log.error('Configuration does not contain any rules to evaluate')
            self._rules = []
        else:
            # NOTE(jonas): Check a copy of all rules.
            # Temporary fix for mutable state in the 'Rule' instances,
            # which are initialized *once* when the configuration is loaded.
            # This same configuration instance is used when iterating over the
            # files. The 'Rule' scores were not reset between files.
            self._rules = copy.deepcopy(active_config.rules)

        self._candidates = []

    def query_data(self, meowuri):
        # Functions that use this does not have access to the 'file_object'.
        # This method, which calls a callback, is itself passed as a callback..
        return self.request_data(self.file_object, meowuri)

    def start(self):
        log.debug('Examining {} rules ..'.format(len(self._rules)))

        ok_rules = evaluate_rule_conditions(self._rules, self.query_data)
        if len(ok_rules) == 0:
            log.info('No valid rules remain after evaluation')
            return

        log.debug('Prioritizing remaining {} candidates ..'.format(len(ok_rules)))
        ok_rules = prioritize_rules(ok_rules)
        for i, rule in enumerate(ok_rules):
            _exact = 'Yes' if rule.exact_match else 'No '
            log.info('Rule #{} (Exact: {}  Score: {:.2f}  Weight: {:.2f}  Bias: {:.2f}) {} '.format(
                i + 1, _exact, rule.score, rule.weight, rule.ranking_bias,
                rule.description)
            )

        self._candidates = ok_rules

    @property
    def best_match(self):
        if not self._candidates:
            return False
        return self._candidates[0]


def prioritize_rules(rules):
    """
    Prioritizes (sorts) a list of 'Rule' instances.

    The list is sorted by multiple attributes in the following order;

    1. By "score", a float between 0-1
       Represents the number of satisfied rule conditions.
    2. By Whether the rule requires an exact match or not.
       Rules that require an exact match are ranked higher.
    3. By "weight", a float between 0-1.
       Represents the number of met conditions for the rule, compared to the
       number of conditions in other rules.
    4. By "ranking bias", a float between 0-1.
       Optional user-specified biasing of rule prioritization.

    This means that a rule that met all conditions will be ranked lower than
    another rule that also met all conditions but *did* require an exact match.
    Rules requiring an exact match is filtered are removed at a prior stage and
    will never get here.

    Args:
        rules: The list of 'Rule' instances to prioritize/sort.

    Returns:
        A sorted/prioritized list of 'Rule' instances.
    """
    return sorted(rules, reverse=True,
                  key=operator.attrgetter('score', 'exact_match', 'weight',
                                          'ranking_bias'))


def evaluate_rule_conditions(rules_to_examine, data_query_function):
    # Conditions are evaluated with data accessed through the callback function
    # 'data_query_function' which returns data for 'RuleMatcher.file_object'.
    passed = remove_rules_failing_exact_match(rules_to_examine,
                                              data_query_function)
    log.debug('{} rules remain after removing rules that require exact'
              ' matches'.format(len(passed)))
    evaluate_rules_and_update_scores(passed, data_query_function)
    return passed


def remove_rules_failing_exact_match(rules_to_examine, data_query_function):
    return [rule for rule in rules_to_examine if
            rule.evaluate_exact(data_query_function)]


def evaluate_rules_and_update_scores(rules_to_examine, data_query_function):
    for count, rule in enumerate(rules_to_examine):
        log.debug('Scoring Rule {}/{}: "{}"'.format(
            count + 1, len(rules_to_examine), rule.description)
        )
        rule.evaluate_score(data_query_function)
