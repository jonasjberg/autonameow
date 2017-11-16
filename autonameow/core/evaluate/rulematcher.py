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

from core import repository


log = logging.getLogger(__name__)


class RuleMatcher(object):
    def __init__(self, fileobject, active_config):
        self.fileobject = fileobject

        if not active_config or not active_config.rules:
            log.error('Configuration does not contain any rules to evaluate')
            self._rules = []
        else:
            self._rules = list(active_config.rules)

        self._scored_rules = {}
        self._candidates = []

    def _request_data(self, fileobject, meowuri):
        # log.debug(
        #     'requesting [{:8.8}]->[{!s}]'.format(fileobject.hash_partial,
        #                                          meowuri)
        # )
        response = repository.SessionRepository.query(fileobject, meowuri)
        # log.debug('Got response ({}): {!s}'.format(type(response), response))
        if response:
            return response.get('value')
        else:
            return None

    def request_data(self, meowuri):
        # Functions that use this does not have access to 'self.fileobject'.
        # This method, which calls a callback, is itself passed as a callback..
        return self._request_data(self.fileobject, meowuri)

    def start(self):
        log.debug('Examining {} rules ..'.format(len(self._rules)))

        remaining_rules = remove_rules_failing_exact_match(self._rules,
                                                           self.request_data)
        if len(remaining_rules) == 0:
            log.debug('No rules remain after discarding those who requires an'
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
            met_conditions = rule.number_conditions_met(self.request_data)

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
        log.info('Remaining, prioritized rules:')
        for i, rule in enumerate(prioritized_rules):
            _candidates.append(rule)

            _exact = 'Yes' if rule.exact_match else 'No '
            log.info('Rule #{} (Exact: {}  Score: {:.2f}  Weight: {:.2f}  Bias:'
                     ' {:.2f}) {} '.format(
                i + 1, _exact,
                self._scored_rules[rule]['score'],
                self._scored_rules[rule]['weight'],
                rule.ranking_bias, rule.description)
            )

        _discarded_rules = [r for r in self._rules if r not in remaining_rules]
        log.info('Discarded rules:')
        for i, rule in enumerate(_discarded_rules, start=i+1):
            _exact = 'Yes' if rule.exact_match else 'No '
            log.info('Rule #{} (Exact: {}  Score: N/A   Weight: N/A   Bias:'
                     ' {:.2f}) {} '.format(i + 1, _exact, rule.ranking_bias,
                                          rule.description))

        self._candidates = _candidates

    @property
    def best_match(self):
        if not self._candidates:
            return False
        return self._candidates[0]

    def candidates(self):
        if not self._candidates:
            return []
        return self._candidates

    def best_match_score(self):
        best = self.best_match
        if best:
            rule = self._scored_rules.get(best)
            if rule:
                return rule.get('score')
        return 0


def prioritize_rules(rules):
    """
    Prioritizes/sorts a dict keyed by 'Rule' instances storing scores/weights.

    Rules are sorted by multiple attributes;

      * By "score", a float between 0-1.
        Represents the number of satisfied rule conditions.
      * By Whether the rule requires an exact match or not.
        Rules that require an exact match are ranked higher.
      * By "weight", a float between 0-1.
        Represents the number of met conditions for the rule, compared to
        the number of conditions in other rules.
      * By "ranking bias", a float between 0-1.
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
        # key=lambda d: (d[1]['score'],
        #                d[0].exact_match,
        #                d[1]['weight'],
        #                d[0].ranking_bias)
        key=lambda d: (d[1]['score'] * d[1]['weight'],
                       d[0].exact_match,
                       d[1]['score'],
                       d[1]['weight'],
                       d[0].ranking_bias)
    )
    return [rule[0] for rule in prioritized_rules]


def remove_rules_failing_exact_match(rules_to_examine, data_query_function):
    return [rule for rule in rules_to_examine if
            rule.evaluate_exact(data_query_function)]
