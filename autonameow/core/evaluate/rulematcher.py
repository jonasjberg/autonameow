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

    def query_data(self, query_string):
        # Functions that use this does not have access to the 'file_object'.
        # This method, which calls a callback, is itself passed as a callback..
        return self.request_data(self.file_object, query_string)

    def start(self):
        log.debug('Examining {} rules ..'.format(len(self._rules)))
        ok_rules = evaluate_rule_conditions(self._rules, self.query_data)
        if len(ok_rules) == 0:
            log.info('No valid rules remain after evaluation')
            return

        log.debug('Prioritizing remaining {} candidates ..'.format(len(ok_rules)))
        ok_rules = prioritize_rules(ok_rules)
        for i, rule in enumerate(ok_rules):
            log.info('Rule #{} (Score: {:.2f} Weight: {:.2f}) {} '.format(
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


def evaluate_rule_conditions(rules_to_examine, data_query_function):
    # Conditions are evaluated with data accessed through the callback function
    # 'data_query_function' which returns data for 'RuleMatcher.file_object'.
    ok_rules = []

    for count, rule in enumerate(rules_to_examine):
        log.debug('Evaluating rule {}/{}: "{}"'.format(
            count + 1, len(rules_to_examine), rule.description)
        )

        result = rule.evaluate(data_query_function)
        if rule.exact_match and result is False:
            log.debug(
                'Rule evaluated FALSE, removing: "{}"'.format(rule.description)
            )
            continue

        log.debug('Rule evaluated TRUE: "{}"'.format(rule.description))
        ok_rules.append(rule)

    return ok_rules


