# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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

from util import sanity


log = logging.getLogger(__name__)


MatchedRule = namedtuple('MatchedRule', 'rule score relative_score')


class RuleMatcher(object):
    def __init__(self, rules, masterprovider, fileobject, ui, list_rulematch=None):
        """
        Creates a new instance that evaluates rules against a given file.
        """
        self._rules = list(rules)
        self._masterprovider = masterprovider
        self._fileobject = fileobject
        self.ui = ui
        self._list_rulematch = bool(list_rulematch)

        self._evaluator_klass = RuleConditionEvaluator

        # Functions that use this does not have access to 'self.fileobject'.
        # This method, which calls a callback, is itself passed as a callback..
        def _data_request_callback(meowuri):
            return self.request_data(self._fileobject, meowuri)

        self.condition_evaluator = self._evaluator_klass(_data_request_callback)

    def request_data(self, fileobject, meowuri):
        sanity.check_isinstance_meowuri(meowuri)

        response = self._masterprovider.request_one(fileobject, meowuri)
        if response:
            return response.value
        return None

    def get_matched_rules(self):
        if not self._rules:
            log.info('No rules available for matching!')
            return []

        all_rules = sorted(self._rules)

        total_rule_count = len(all_rules)
        log.debug('Examining %d rules ..', total_rule_count)
        for n, rule in enumerate(all_rules, start=1):
            log.debug('Evaluating rule %d/%d: %s', n, total_rule_count, rule)
            self.condition_evaluator.evaluate(rule)

        # Remove rules that require an exact match and contains a condition
        # that failed evaluation.
        remaining_rules = [
            rule for rule in all_rules
            if not rule.exact_match
            or rule.exact_match and not self.condition_evaluator.failed(rule)
        ]

        num_rules_remain = len(remaining_rules)
        if num_rules_remain == 0:
            log.debug('No rules remain after discarding those that require an '
                      'exact match and failed evaluation of any condition ..')
            return []

        log.debug('%d rules remain after discarding those that require an '
                  'exact match and failed evaluation.', num_rules_remain)

        # Calculate score and "relative score" for each rule, store the
        # results in a new local dict keyed by the 'Rule' class instances.
        max_condition_count = max(len(rule.conditions)
                                  for rule in remaining_rules)
        scored_rules = dict()
        for rule in remaining_rules:
            scored_rules[rule] = self._score_rule(max_condition_count, rule)

        log.debug('Prioritizing remaining %d candidates ..', num_rules_remain)
        prioritized_rules = prioritize_rules(scored_rules)

        discarded_rules = [r for r in all_rules if r not in remaining_rules]
        if self._list_rulematch:
            self._display_details(prioritized_rules, scored_rules, discarded_rules)
        else:
            self._log_results(prioritized_rules, scored_rules, discarded_rules)

        return [
            MatchedRule(rule=rule,
                        score=scored_rules[rule]['score'],
                        relative_score=scored_rules[rule]['relative_score'])
            for rule in prioritized_rules
        ]

    def _score_rule(self, max_condition_count, rule):
        met_conditions = len(self.condition_evaluator.passed(rule))
        num_conditions = len(rule.conditions)

        # Ratio of met conditions to the total number of conditions
        # for a single rule.
        score = met_conditions / max(1, num_conditions)

        # Ratio of number of conditions in this rule to the number of
        # conditions in the rule with the highest number of conditions.
        relative_score = num_conditions / max(1, max_condition_count)

        return {'score': score, 'relative_score': relative_score}

    @staticmethod
    def _log_results(prioritized_rules, scored_rules, discarded_rules):
        if log.getEffectiveLevel() < logging.INFO:
            return

        FMT_PRIORITIZED = 'Rule #{} (Exact: {}  Score: {:.2f}  Relative Score: {:.2f}  Bias: {:.2f}) {}'
        log.info('Remaining, prioritized rules:')
        for n, rule in enumerate(prioritized_rules, start=1):
            log.info(FMT_PRIORITIZED.format(
                n,
                'Yes' if rule.exact_match else 'No ',
                scored_rules[rule]['score'],
                scored_rules[rule]['relative_score'],
                rule.ranking_bias,
                rule.description,
            ))

        FMT_DISCARDED = 'Rule #{} (Exact: {}  Score: N/A   Relative Score: N/A   Bias: {}) {}'
        log.info('Discarded rules:')
        for n, rule in enumerate(discarded_rules, start=1):
            log.info(FMT_DISCARDED.format(
                n,
                'Yes' if rule.exact_match else 'No ',
                rule.ranking_bias,
                rule.description,
            ))

    def _display_details(self, prioritized_rules, scored_rules, discarded_rules):
        def _prettyprint_rule_details(n, _rule, _bias, _score=None, _relative_score=None):
            # TODO: [TD0171] Separate logic from user interface.
            UNAVAILABLE = 'N/A '
            FMT_DECIMAL = '{:.2f}'

            _str_score = UNAVAILABLE
            if _score is not None:
                _str_score = FMT_DECIMAL.format(_score)

            _str_relative_score = UNAVAILABLE
            if _relative_score is not None:
                _str_relative_score = FMT_DECIMAL.format(_relative_score)

            _str_exact = 'Yes' if rule.exact_match else 'No '
            self.ui.msg('Rule #{:02d}  {!s}'.format(n, _rule.description),
                        style='highlight')

            self.ui.msg('Exact: {}  Score: {}  Relative Score: {}  Bias: {}\n'.format(
                _str_exact, _str_score, _str_relative_score, _bias
            ))

            rows = list()

            def _addrow(*data):
                rows.append(tuple(data))

            msg_label_pass = self.ui.colorize('PASSED', fore='GREEN')
            msg_label_fail = self.ui.colorize('FAILED', fore='RED')
            msg_label_padding = self.ui.colorize('      ', fore='BLACK')

            conditions_passed = self.condition_evaluator.passed(_rule)
            for c in conditions_passed:
                d = self.condition_evaluator.evaluated(_rule, c)

                _addrow(msg_label_pass, str(c.meowuri))
                _addrow(msg_label_padding, 'Expression:', str(c.expression))
                _addrow(msg_label_padding, 'Evaluated Data:', str(d))

            conditions_failed = self.condition_evaluator.failed(_rule)
            for c in conditions_failed:
                d = self.condition_evaluator.evaluated(_rule, c)
                _addrow(msg_label_fail, str(c.meowuri))
                _addrow(msg_label_padding, 'Expression:', str(c.expression))
                _addrow(msg_label_padding, 'Evaluated Data:', str(d))

            self.ui.msg_columnate(
                column_names=[],
                row_data=rows,
                alignment=('right', 'left')
            )

        self.ui.msg('Remaining, prioritized rules:', style='heading')
        i = 1
        for i, rule in enumerate(prioritized_rules, start=1):
            _bias = rule.ranking_bias
            _score = scored_rules[rule]['score']
            _relative_score = scored_rules[rule]['relative_score']
            _prettyprint_rule_details(i, rule, _bias, _score, _relative_score)

        self.ui.msg('Discarded rules:', style='heading')
        for j, rule in enumerate(discarded_rules, start=i+1):
            _bias = rule.ranking_bias
            _prettyprint_rule_details(j, rule, _bias)


def prioritize_rules(rules):
    """
    Prioritizes/sorts a dict keyed by 'Rule' instances storing scores.

    Rules are sorted by multiple attributes;

      * By "score", a float between 0-1.
        Represents the number of satisfied rule conditions.
      * By Whether the rule requires an exact match or not.
        Rules that require an exact match are ranked higher.
      * By "relative score", a float between 0-1.
        Represents the number of satisfied conditions as compared to the
        highest condition count among the evaluated rules.
      * By "ranking bias", a float between 0-1.
        Optional user-specified biasing of rule prioritization.
      * Finally, sort by number of data sources, prioritizing rules with
        higher number of data sources. Rules without data sources are
        assumedly less interesting and more "general".
        This assumption might not hold, but makes the results deterministic
        when values used by the preceding sorting criteria are equal.

    This means that a rule that met all conditions will be ranked lower than
    another rule that also met all conditions but *did* require an exact match.
    Rules requiring an exact match is filtered are removed at a prior
    stage and should never get here.

    Args:
        rules: Dict keyed by instances of 'Rule' storing score-dicts.

    Returns:
        A sorted/prioritized list of tuples composed of 'Rule' instances
        and score-dicts.
    """
    prioritized_rules = sorted(
        rules.items(),
        reverse=True,
        key=lambda d: (d[0].exact_match,
                       d[1]['score'] * d[1]['relative_score'],
                       d[1]['score'],
                       d[1]['relative_score'],
                       d[0].ranking_bias,
                       len(d[0].data_sources))
    )
    return [rule[0] for rule in prioritized_rules]


class RuleConditionEvaluator(object):
    def __init__(self, data_query_function):
        self.data_query_function = data_query_function

        self._failed = dict()
        self._passed = dict()
        self._evaluated = dict()

    def evaluate(self, rule_to_evaluate):
        """
        Evaluates a rule and stores results in instance attributes.

        Args:
            rule_to_evaluate: Rule to evaluate as instance of the 'Rule' class.
        """
        assert rule_to_evaluate not in (self._failed, self._passed), (
            'Rule has already been evaluated; {!r}'.format(rule_to_evaluate)
        )
        self._failed[rule_to_evaluate] = list()
        self._passed[rule_to_evaluate] = list()
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
        log_strprefix = '{!s} :: '.format(rule.description)

        for condition in rule.conditions:
            condition_data_uri = condition.meowuri
            data = self.data_query_function(condition_data_uri)
            if self._evaluate_condition(condition, data):
                log.debug('%sPASS: "%s"', log_strprefix, condition)
                self._passed[rule].append(condition)
            else:
                log.debug('%sFAIL: "%s"', log_strprefix, condition)
                self._failed[rule].append(condition)

            assert condition not in self._evaluated.get(rule, {})
            self._evaluated[rule][condition] = data

    @staticmethod
    def _evaluate_condition(condition, data):
        if data is None:
            log.debug('Missing data to evaluate condition "%s"', condition)
            return False

        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        return condition.evaluate(data)
