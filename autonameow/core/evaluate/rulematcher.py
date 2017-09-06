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
import operator

import copy

from core import (
    repository
)
from extractors import ExtractedData

log = logging.getLogger(__name__)


class RuleMatcher(object):
    def __init__(self, file_object, active_config):
        self.file_object = file_object

        if not active_config or not active_config.rules:
            log.error('Configuration does not contain any rules to evaluate')
            self._rules = []
        else:
            # NOTE(jonas): Check a copy of all rules.
            # Temporary fix for mutable state in the 'Rule' instances,
            # which are initialized *once* when the configuration is loaded.
            # This same configuration instance is used when iterating over the
            # files. The 'Rule' scores were not reset between files.
            # TODO: Double-check that this isn't needed anymore, then remove.
            self._rules = copy.deepcopy(active_config.rules)

        self._scored_rules = {}
        self._candidates = []

    def request_data(self, file_object, meowuri):
        log.debug('requesting [{!s}][{!s}]'.format(file_object, meowuri))
        response = repository.SessionRepository.resolve(file_object, meowuri)
        log.debug('Got response ({}): {!s}'.format(type(response), response))
        if response is not None and isinstance(response, ExtractedData):
            return response.value
        else:
            return response

    def _request_data(self, meowuri):
        # Functions that use this does not have access to 'self.file_object'.
        # This method, which calls a callback, is itself passed as a callback..
        return self.request_data(self.file_object, meowuri)

    def start(self):
        log.debug('Examining {} rules ..'.format(len(self._rules)))

        remaining_rules = remove_rules_failing_exact_match(self._rules,
                                                           self._request_data)
        if len(remaining_rules) == 0:
            log.info('No rules remain after discarding those who requires an'
                     ' exact match but failed evaluation ..')
            return

        log.debug('{} rules remain after removing rules that require exact'
                  ' matches'.format(len(remaining_rules)))

        # Calculate score and weight for each rule, store the results in a
        # new local dict instead of mutating the 'Rule' instances.
        # The new dict is keyed by the 'Rule' class instances.
        max_condition_count = max(len(rule.conditions)
                                  for rule in remaining_rules)
        for rule in remaining_rules:
            met_conditions = rule.count_conditions_met(self._request_data)

            # Ratio of met conditions to the total number of conditions
            # for a single rule.
            score = met_conditions / max(1, len(rule.conditions))

            # Ratio of number of conditions in this rule to the number of
            # conditions in the rule with the highest number of conditions.
            weight = len(rule.conditions) / max(1, max_condition_count)

            self._scored_rules[rule] = {'score': score,
                                        'weight': weight}

        log.debug('Prioritizing remaining {} candidates ..'.format(
            len(remaining_rules))
        )
        prioritized_rules = prioritize_rules(self._scored_rules)

        _candidates = []
        for i, rule in enumerate(prioritized_rules):
            _candidates.append(rule)

            _exact = 'Yes' if rule.exact_match else 'No '
            log.info('Rule #{} (Exact: {}  Score: {:.2f}  Weight: {:.2f}  Bias: {:.2f}) {} '.format(
                i + 1, _exact,
                self._scored_rules[rule]['score'],
                self._scored_rules[rule]['weight'],
                rule.ranking_bias, rule.description)
            )

        self._candidates = _candidates

    @property
    def best_match(self):
        if not self._candidates:
            return False
        return self._candidates[0]


def prioritize_rules(rules):
    """
    Prioritizes (sorts) a dict with 'Rule' instances and scores/weights.

    Rules are sorted by multiple attributes in the following order;

    1. By "score", a float between 0-1
       Represents the number of satisfied rule conditions.
    2. By Whether the rule requires an exact match or not.
       Rules that require an exact match are ranked higher.
    3. By "weight", a float between 0-1.
       Represents the number of met conditions for the rule, compared to
       the number of conditions in other rules.
    4. By "ranking bias", a float between 0-1.
       Optional user-specified biasing of rule prioritization.

    This means that a rule that met all conditions will be ranked lower than
    another rule that also met all conditions but *did* require an exact match.
    Rules requiring an exact match is filtered are removed at a prior
    stage and should never get here.

    Args:
        rules: Dict keyed by instances of 'Rule' storing score/weight-dicts.

    Returns:
        A sorted/prioritized list of tuples composed of 'Rule' instances
        and score/weight-dicts.
    """
    prioritized_rules = sorted(
        rules.items(),
        reverse=True,
        key=lambda d: (d[1]['score'],
                       d[0].exact_match,
                       d[1]['weight'],
                       d[0].ranking_bias)
    )
    return [rule[0] for rule in prioritized_rules]


def remove_rules_failing_exact_match(rules_to_examine, data_query_function):
    return [rule for rule in rules_to_examine if
            rule.evaluate_exact(data_query_function)]
