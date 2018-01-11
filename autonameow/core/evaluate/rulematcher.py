# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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
from collections import namedtuple

from core import (
    provider,
    ui
)
from util import sanity


log = logging.getLogger(__name__)


MatchResult = namedtuple('MatchResult', 'rule score weight')


class RuleMatcher(object):
    def __init__(self, rules, list_rulematch=None):
        self._rules = list(rules)
        self._list_rulematch = bool(list_rulematch)

    def request_data(self, fileobject, meowuri):
        # TODO: [TD0133] Fix inconsistent use of MeowURIs
        #       Stick to using either instances of 'MeowURI' _OR_ strings.
        sanity.check_isinstance_meowuri(
            meowuri, msg='TODO: [TD0133] Fix inconsistent use of MeowURIs'
        )

        response = provider.query(fileobject, meowuri)
        if response:
            sanity.check_isinstance(response, dict,
                                    msg='FileObject [{!s}] MeowURI {!s}'.format(fileobject.hash_partial, meowuri))
            return response.get('value')
        return None

    def match(self, fileobject):
        if not self._rules:
            log.debug('No rules available for matching!')
            return []

        all_rules = list(self._rules)

        # Functions that use this does not have access to 'self.fileobject'.
        # This method, which calls a callback, is itself passed as a callback..
        def _data_request_callback(meowuri):
            return self.request_data(fileobject, meowuri)

        log.debug('Examining {} rules ..'.format(len(all_rules)))
        condition_evaluator = RuleConditionEvaluator(_data_request_callback)
        for rule in all_rules:
            condition_evaluator.evaluate(rule)

        # Remove rules that require an exact match and contains a condition
        # that failed evaluation.
        remaining_rules = []
        for rule in all_rules:
            if rule.exact_match:
                if condition_evaluator.failed(rule):
                    # List of failed conditions for this rule is not empty.
                    continue
            remaining_rules.append(rule)

        num_rules_remain = len(remaining_rules)
        if num_rules_remain == 0:
            log.debug('No rules remain after discarding those that require an '
                      'exact match and failed evaluation of any condition ..')
            return []

        log.debug('{} rules remain after discarding those that require an '
                  'exact match and failed evaluation.'.format(num_rules_remain))

        # Calculate score and weight for each rule, store the results in a
        # new local dict keyed by the 'Rule' class instances.
        max_condition_count = max(rule.number_conditions
                                  for rule in remaining_rules)
        scored_rules = dict()
        for rule in remaining_rules:
            met_conditions = len(condition_evaluator.passed(rule))
            num_conditions = rule.number_conditions

            # Ratio of met conditions to the total number of conditions
            # for a single rule.
            score = met_conditions / max(1, num_conditions)

            # Ratio of number of conditions in this rule to the number of
            # conditions in the rule with the highest number of conditions.
            weight = num_conditions / max(1, max_condition_count)

            scored_rules[rule] = {'score': score, 'weight': weight}

        log.debug(
            'Prioritizing remaining {} candidates ..'.format(num_rules_remain)
        )
        prioritized_rules = prioritize_rules(scored_rules)

        discarded_rules = [r for r in all_rules if r not in remaining_rules]
        self._log_results(prioritized_rules, scored_rules, discarded_rules)

        if self._list_rulematch:
            self._display_details(prioritized_rules, scored_rules,
                                  discarded_rules, condition_evaluator)
        else:
            self._log_results(prioritized_rules, scored_rules, discarded_rules)

        # Return list of (RULE (Rule), SCORE (float), WEIGHT (float) tuples.
        return [
            MatchResult(rule=rule,
                        score=scored_rules[rule]['score'],
                        weight=scored_rules[rule]['weight'])
            for rule in prioritized_rules
        ]

    @staticmethod
    def _log_results(prioritized_rules, scored_rules, discarded_rules):
        if log.getEffectiveLevel() < logging.INFO:
            return

        FMT_DISCARDED = 'Rule #{} (Exact: {}  Score: N/A   Weight: N/A   Bias: {}) {}'
        FMT_PRIORITIZED = 'Rule #{} (Exact: {}  Score: {:.2f}  Weight: {:.2f}  Bias: {:.2f}) {}'

        def _prettyprint_prioritized_rule(n, exact, score, weight, bias, desc):
            _exact = 'Yes' if exact else 'No '
            log.info(
                FMT_PRIORITIZED.format(n, _exact, score, weight, bias, desc)
            )

        def _prettyprint_discarded_rule(n, exact, bias, desc):
            _exact = 'Yes' if exact else 'No '
            log.info(FMT_DISCARDED.format(n, _exact, bias, desc))

        log.info('Remaining, prioritized rules:')
        for i, rule in enumerate(prioritized_rules, start=1):
            _prettyprint_prioritized_rule(
                i, rule.exact_match, scored_rules[rule]['score'],
                scored_rules[rule]['weight'], rule.ranking_bias,
                rule.description
            )

        log.info('Discarded rules:')
        for i, rule in enumerate(discarded_rules, start=1):
            _prettyprint_discarded_rule(
                i, rule.exact_match, rule.ranking_bias, rule.description
            )

    @staticmethod
    def _display_details(prioritized_rules, scored_rules, discarded_rules,
                         condition_evaluator):
        def _prettyprint_rule_details(n, _rule, _bias, _score=None, _weight=None):
            conditions_passed = condition_evaluator.passed(_rule)
            conditions_failed = condition_evaluator.failed(_rule)

            UNAVAILABLE = 'N/A '
            FMT_DECIMAL = '{:.2f}'
            if _score is None:
                _str_score = UNAVAILABLE
            else:
                _str_score = FMT_DECIMAL.format(_score)
            if _weight is None:
                _str_weight = UNAVAILABLE
            else:
                _str_weight = FMT_DECIMAL.format(_weight)

            _str_exact = 'Yes' if rule.exact_match else 'No '
            # s = 'Rule #{:02d} (Exact: {}  Score: {}  Weight: {}  Bias: {})  [{!s}]'
            # ui.msg(s.format(n, _str_exact, _str_score, _str_weight, _bias,
            #                _rule.description))
            sr = 'Rule #{:02d}  {!s}'.format(n, _rule.description)
            ui.msg(ui.colorize(sr, fore='LIGHTWHITE_EX'))

            si = 'Exact: {}  Score: {}  Weight: {}  Bias: {}'.format(_str_exact, _str_score, _str_weight, _bias)
            ui.msg(si + '\n')

            cf = ui.ColumnFormatter()
            cf.setalignment('right', 'left')
            msg_label_pass = ui.colorize('PASSED', fore='GREEN')
            msg_label_fail = ui.colorize('FAILED', fore='RED')
            for c in conditions_passed:
                d = condition_evaluator.evaluated(_rule, c)

                cf.addrow(msg_label_pass, str(c.meowuri))
                cf.addrow('Expression:', str(c.expression))
                cf.addrow('Evaluated Data:', str(d))

            for c in conditions_failed:
                d = condition_evaluator.evaluated(_rule, c)
                cf.addrow(msg_label_fail, str(c.meowuri))
                cf.addrow('Expression:', str(c.expression))
                cf.addrow('Evaluated Data:', str(d))

            ui.msg(str(cf))
            ui.msg('\n')

        ui.msg('\nRemaining, prioritized rules:', style='heading')
        for i, rule in enumerate(prioritized_rules, start=1):
            _bias = rule.ranking_bias
            _score = scored_rules[rule]['score']
            _weight = scored_rules[rule]['weight']
            _prettyprint_rule_details(i, rule, _bias, _score, _weight)

        ui.msg('\nDiscarded rules:', style='heading')
        for i, rule in enumerate(discarded_rules, start=1):
            _bias = rule.ranking_bias
            _prettyprint_rule_details(i, rule, _bias)


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


class RuleConditionEvaluator(object):
    def __init__(self, data_query_function):
        self.data_query_function = data_query_function

        self._failed = dict()
        self._passed = dict()
        self._evaluated = dict()

    def evaluate(self, rule_to_evaluate):
        assert rule_to_evaluate not in (self._failed, self._passed), (
            'Rule has already been evaluated; {!r}'.format(rule_to_evaluate)
        )
        self._failed[rule_to_evaluate] = []
        self._passed[rule_to_evaluate] = []
        self._evaluated[rule_to_evaluate] = dict()

        self.evaluate_rule_conditions(rule_to_evaluate)

    def failed(self, rule):
        return self._failed.get(rule, [])

    def passed(self, rule):
        return self._passed.get(rule, [])

    def evaluated(self, rule, condition):
        if rule not in self._evaluated:
            return None
        return self._evaluated[rule].get(condition)

    def evaluate_rule_conditions(self, rule):
        if rule.description:
            _desc = '{} :: '.format(rule.description)
        else:
            _desc = ''

        for condition in rule.conditions:
            _data_meowuri = condition.meowuri
            data = self.data_query_function(_data_meowuri)
            if self._evaluate_condition(condition, data):
                log.debug('{}Condition PASSED: "{!s}"'.format(_desc, condition))
                self._passed[rule].append(condition)
            else:
                log.debug('{}Condition FAILED: "{!s}"'.format(_desc, condition))
                self._failed[rule].append(condition)

            assert condition not in self._evaluated.get(rule, {})
            self._evaluated[rule][condition] = data

    @staticmethod
    def _evaluate_condition(condition, data):
        if data is None:
            log.warning('Unable to evaluate condition due to missing data:'
                        ' "{!s}"'.format(condition))
            return False

        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        return condition.evaluate(data)
