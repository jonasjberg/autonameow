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
from collections import defaultdict

from core import repository


log = logging.getLogger(__name__)


class RuleMatcher(object):
    def __init__(self, rules):
        self._rules = list(rules)

    def request_data(self, fileobject, meowuri):
        response = repository.SessionRepository.query(fileobject, meowuri)
        if response:
            return response.get('value')
        else:
            return None

    def match(self, fileobject):
        return self.new_match(fileobject)

        # TODO: [cleanup] Remove duplication ..
        if not self._rules:
            log.debug('No rules available for matching!')
            return []

        all_rules = list(self._rules)

        # Functions that use this does not have access to 'self.fileobject'.
        # This method, which calls a callback, is itself passed as a callback..
        def _request_data(meowuri):
            return self.request_data(fileobject, meowuri)
        scored_rules = {}

        # Out of all possible rules, remove those that require an exact match
        # and contains any condition that fail evaluation.
        log.debug('Examining {} rules ..'.format(len(all_rules)))
        remaining_rules = remove_rules_failing_exact_match(all_rules,
                                                           _request_data)
        if len(remaining_rules) == 0:
            log.debug('No rules remain after discarding those that require an '
                      'exact match and failed evaluation of any condition ..')
            return []

        log.debug('{} rules remain after discarding those that require an '
                  'exact match and failed evaluation.'.format(len(remaining_rules)))

        # Calculate score and weight for each rule, store the results in a
        # new local dict instead of mutating the 'Rule' instances.
        # The new dict is keyed by the 'Rule' class instances.
        max_condition_count = max(rule.number_conditions
                                  for rule in remaining_rules)
        for rule in remaining_rules:
            met_conditions = rule.number_conditions_met(_request_data)
            num_conditions = rule.number_conditions

            # Ratio of met conditions to the total number of conditions
            # for a single rule.
            score = met_conditions / max(1, num_conditions)

            # Ratio of number of conditions in this rule to the number of
            # conditions in the rule with the highest number of conditions.
            weight = num_conditions / max(1, max_condition_count)

            scored_rules[rule] = {'score': score, 'weight': weight}

        log.debug('Prioritizing the remaining {} candidates ..'.format(
            len(remaining_rules))
        )
        prioritized_rules = prioritize_rules(scored_rules)

        # TODO: [TD0135] Add option to display rule matching details.
        log.info('Remaining, prioritized rules:')
        for i, rule in enumerate(prioritized_rules, start=1):
            self._prettyprint_prioritized_rule(
                i, rule.exact_match, scored_rules[rule]['score'],
                scored_rules[rule]['weight'], rule.ranking_bias,
                rule.description
            )

        _discarded_rules = [r for r in all_rules if r not in remaining_rules]
        log.info('Discarded rules:')
        for i, rule in enumerate(_discarded_rules, start=1):
            self._prettyprint_discarded_rule(
                i, rule.exact_match, rule.ranking_bias, rule.description
            )
        # Return list of ( RULE, SCORE(float), WEIGHT(float) ) tuples.
        return [
            (r, scored_rules[r]['score'], scored_rules[r]['weight'])
            for r in prioritized_rules
        ]

    def new_match(self, fileobject):
        if not self._rules:
            log.debug('No rules available for matching!')
            return []

        all_rules = list(self._rules)

        # Functions that use this does not have access to 'self.fileobject'.
        # This method, which calls a callback, is itself passed as a callback..
        def _request_data(meowuri):
            return self.request_data(fileobject, meowuri)
        scored_rules = {}

        log.debug('Examining {} rules ..'.format(len(all_rules)))
        rule_evaluator = RuleEvaluator(_request_data)
        for rule in all_rules:
            rule_evaluator.evaluate(rule)

        remaining_rules = []
        for rule in all_rules:
            if rule.exact_match:
                if rule_evaluator.failed[rule]:
                    continue
            remaining_rules.append(rule)

        if len(remaining_rules) == 0:
            log.debug('No rules remain after discarding those that require an '
                      'exact match and failed evaluation of any condition ..')
            return []

        log.debug('{} rules remain after discarding those that require an '
                  'exact match and failed evaluation.'.format(len(remaining_rules)))

        # Calculate score and weight for each rule, store the results in a
        # new local dict instead of mutating the 'Rule' instances.
        # The new dict is keyed by the 'Rule' class instances.
        max_condition_count = max(rule.number_conditions
                                  for rule in remaining_rules)
        for rule in remaining_rules:
            met_conditions = rule.number_conditions_met(_request_data)
            num_conditions = rule.number_conditions

            # Ratio of met conditions to the total number of conditions
            # for a single rule.
            score = met_conditions / max(1, num_conditions)

            # Ratio of number of conditions in this rule to the number of
            # conditions in the rule with the highest number of conditions.
            weight = num_conditions / max(1, max_condition_count)

            scored_rules[rule] = {'score': score, 'weight': weight}

        log.debug('Prioritizing the remaining {} candidates ..'.format(
            len(remaining_rules))
        )
        prioritized_rules = prioritize_rules(scored_rules)

        # TODO: [TD0135] Add option to display rule matching details.
        log.info('Remaining, prioritized rules:')
        for i, rule in enumerate(prioritized_rules, start=1):
            self._prettyprint_prioritized_rule(
                i, rule.exact_match, scored_rules[rule]['score'],
                scored_rules[rule]['weight'], rule.ranking_bias,
                rule.description
            )

        _discarded_rules = [r for r in all_rules if r not in remaining_rules]
        log.info('Discarded rules:')
        for i, rule in enumerate(_discarded_rules, start=1):
            self._prettyprint_discarded_rule(
                i, rule.exact_match, rule.ranking_bias, rule.description
            )
        # Return list of ( RULE, SCORE(float), WEIGHT(float) ) tuples.
        return [
            (r, scored_rules[r]['score'], scored_rules[r]['weight'])
            for r in prioritized_rules
        ]


    @staticmethod
    def _prettyprint_prioritized_rule(num, exact, score, weight, bias, desc):
        _exact = 'Yes' if exact else 'No '
        log.info(
            'Rule #{} (Exact: {}  Score: {:.2f}  Weight: {:.2f}  Bias: {:.2f}) '
            '{} '.format(num, _exact, score, weight, bias, desc)
        )

    @staticmethod
    def _prettyprint_discarded_rule(number, exact, bias, desc):
        _exact = 'Yes' if exact else 'No '
        log.info(
            'Rule #{} (Exact: {}  Score: N/A   Weight: N/A   Bias: {:.2f}) '
            '{} '.format(number, _exact, bias, desc)
        )


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


class RuleEvaluator(object):
    def __init__(self, data_query_function):
        self.data_query_function = data_query_function

        # Allows setting values two levels down without intermediate keys.
        self.results = defaultdict(dict)

        self.failed = dict()
        self.passed = dict()

    def evaluate(self, rule_to_evaluate):
        assert rule_to_evaluate not in self.results, (
            'Rule has already been evaluated; {!r}'.format(rule_to_evaluate)
        )
        self.results[rule_to_evaluate]['passed'] = []
        self.results[rule_to_evaluate]['failed'] = []

        # TODO: [cleanup] Remove duplication ..
        self.failed[rule_to_evaluate] = []
        self.passed[rule_to_evaluate] = []

        self.evaluate_rule_conditions(rule_to_evaluate)

    def evaluate_rule_conditions(self, rule):
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        for condition in rule.conditions:
            if self._evaluate_condition(condition):
                self.results[rule]['passed'].append(condition)

                # TODO: [cleanup] Remove duplication ..
                self.passed[rule].append(condition)
            else:
                self.results[rule]['failed'].append(condition)

                # TODO: [cleanup] Remove duplication ..
                self.failed[rule].append(condition)

    def _evaluate_condition(self, condition):
        _data_meowuri = condition.meowuri
        data = self.data_query_function(_data_meowuri)
        if data is None:
            log.warning('Unable to evaluate condition due to missing data:'
                        ' "{!s}"'.format(condition))
            return False

        return condition.evaluate(data)
