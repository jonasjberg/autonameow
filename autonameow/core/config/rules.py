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

from core import (
    constants,
    util,
    exceptions,
    types
)
from core.config import field_parsers


class RuleCondition(object):
    """
    Represents a single condition contained in a configuration file rule.
    """
    def __init__(self, raw_query_string, raw_expression):
        """
        Validates the arguments and returns a 'RuleCondition' instance if
        the validation is successful. Else an exception is thrown.

        The "query string" is a reference to some data.
        The expression is some expression that will be evaluated on the data
        contained at the location referenced to by the "query string".

        Example: If the "query string" is 'contents.mime_type', a valid
        expression could be 'image/*'. When this condition is evaluated,
        the data contained at 'contents.mime_type' might be 'image/jpeg'.
        In this case the evaluation would return True.

        Args:
            raw_query_string: A "query string" describing the target of the
                condition. For example; "contents.mime_type".
            raw_expression: A expression to use when evaluating this condition.
        """
        # TODO: Clean up setting the 'parser' attribute.
        # NOTE(jonas): The query string determines which parser class is used.

        # TODO: [TD0015] Allow conditionals in the configuration file rules.
        # Possible a list of functions already "loaded" with the target value.
        # Also "loaded" with corresponding (reference to) a validation function.
        self._parser = None
        self._query_string = None
        self._expression = None

        self.query_string = raw_query_string
        self.expression = raw_expression

    @property
    def query_string(self):
        return self._query_string

    @query_string.setter
    def query_string(self, raw_query_string):
        # The query string is considered valid if a field parser can handle it.
        valid_query_string = self._validate_query_string(raw_query_string)
        if valid_query_string:
            self._query_string = raw_query_string
        else:
            raise TypeError(
                'Invalid query string: "{!s}"'.format(raw_query_string)
            )

    @property
    def expression(self):
        return self._expression

    @expression.setter
    def expression(self, raw_expression):
        # The "query string" is required in order to know how the expression
        # should be evaluated. Consider the expression invalid.
        if not self.query_string:
            raise ValueError(
                'A valid "query string" is required for validation.'
            )

        # NOTE(jonas): No parser can currently handle these query strings ..
        if self.query_string.startswith('metadata.exiftool'):
            # TODO: [TD0015] Handle expression in 'condition_value'
            #                ('Defined', '> 2017', etc)
            log.warning('Validation of this condition is not yet implemented!'
                        ' (starts with "metadata.exiftool")')

        if not self._get_parser(self.query_string):
            raise ValueError('Found no suitable parsers for query string: '
                             '"{!s}"'.format(self.query_string))

        valid_expression = self._validate_expression(raw_expression)
        if valid_expression:
            self._expression = raw_expression
        else:
            raise ValueError(
                'Invalid expression: "{!s}"'.format(raw_expression)
            )

    def _validate_query_string(self, raw_query_string):
        if not raw_query_string:
            return False

        # Consider the query string valid if any parser can handle it.
        if self._get_parser(raw_query_string):
            return True
        else:
            return False

    def _validate_expression(self, raw_expression):
        if self._parser.validate(raw_expression):
            return raw_expression
        else:
            return False

    def _get_parser(self, query_string):
        if self._parser:
            return self._parser

        parsers = field_parsers.suitable_field_parser_for(query_string)
        if parsers:
            # Assume only one parser can handle a query string for now.
            assert(len(parsers) == 1)
            self._parser = parsers[0]
            return self._parser
        else:
            return False

    def evaluate(self, data):
        """
        Evaluates this condition using the given data.

        Args:
            data: The data to used during the evaluation.

        Returns: The result of the evaluation if the evaluation is successful
            with the given data, otherwise False.
        """
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        if not self._parser:
            log.critical('Unimplemented condition evaluation -- query_string: '
                         '"{!s}" expression: "{!s}"'.format(self.query_string,
                                                            self.expression))
            return False

        result = self._parser.evaluate(self.expression, data)
        if result:
            return result
        else:
            return False

    def __str__(self):
        return '{!s}: {!s}'.format(self.query_string, self.expression)

    def __repr__(self):
        return 'RuleCondition("{}", "{}")'.format(self.query_string,
                                                  self.expression)


class FileRule(object):
    """
    Represents a single file rule entry in a loaded configuration.

    This class is a container; assumes all data in "kwargs" is valid.
    All data validation should be performed outside of this class.

    File rules are prioritized and sorted by both "score" and "weight".

    - score         Represents how well suited a rule is for a given file.
                    This value is changed at run-time.
    - ranking_bias  If multiple rules end up with an equal score, weights are
                    used to further prioritize as to get a single "winning"
                    rule. This value is specified in the active configuration.

    Calculate scores as;  SCORE = conditions_met / number_of_conditions
    Which gives a "normalized" decimal number between 0 and 1 that indicates
    the ratio of satisfied to unsatisfied conditions.
    """
    def __init__(self, description, exact_match, ranking_bias, name_template,
                 **kwargs):
        self.description = description
        self.exact_match = exact_match
        self.ranking_bias = ranking_bias
        self.name_template = name_template
        self.conditions = kwargs.get('conditions', [])
        self.data_sources = kwargs.get('data_sources', [])

        self._count_met_conditions = 0

        if not self.conditions:
            raise exceptions.InvalidFileRuleError(
                'FileRule does not specify any conditions: "{!s}"'.format(self)
            )

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, raw_description):
        if raw_description is None:
            self._description = 'UNDESCRIBED'
        else:
            self._description = raw_description

    @property
    def exact_match(self):
        return self._exact_match

    @exact_match.setter
    def exact_match(self, raw_exact_match):
        self._exact_match = types.AW_BOOLEAN(raw_exact_match)

    @property
    def ranking_bias(self):
        if self._ranking_bias:
            return self._ranking_bias
        else:
            return constants.DEFAULT_FILERULE_RANKING_BIAS

    @ranking_bias.setter
    def ranking_bias(self, raw_ranking_bias):
        try:
            self._ranking_bias = parse_ranking_bias(raw_ranking_bias)
        except exceptions.ConfigurationSyntaxError as e:
            log.warning(e)
            self._ranking_bias = constants.DEFAULT_FILERULE_RANKING_BIAS

    @property
    def name_template(self):
        return self._name_template

    @name_template.setter
    def name_template(self, raw_name_template):
        if not raw_name_template:
            raise exceptions.InvalidFileRuleError('Got None name template')
        self._name_template = raw_name_template

    @property
    def score(self):
        # Calculate scores as;  SCORE = conditions_met / number_of_conditions
        # Number of conditions is clamped at 1 to prevent division by 0.
        score = self._count_met_conditions / max(1, len(self.conditions))
        assert(0 <= score <= 1)
        return score

    @property
    def weight(self):
        # TODO: Calculate weight, or revert "normalized" scores.
        return 0

    def upvote(self):
        """
        Increases the matching score of this rule.
        """
        self._count_met_conditions += 1

    def downvote(self):
        """
        Decreases the matching score of this rule.
        """
        self._count_met_conditions -= 1
        self._count_met_conditions = max(0, self._count_met_conditions)

    def referenced_query_strings(self):
        """
        Get all query strings referenced by this file rule.

        The query string can be part of either a condition or a data source.

        Returns: The set of all query strings referenced by this file rule.
        """
        unique_query_strings = set()

        for condition in self.conditions:
            unique_query_strings.add(condition.query_string)

        for _, query_string in self.data_sources.items():
            unique_query_strings.add(query_string)

        return unique_query_strings

    def evaluate_exact(self, data_query_function):
        """
        Evaluates this rule using data provided by a callback function.

        This tests rules that require exact matches.
        Returns False at first unmatched condition if the rule requires an
        exact match. If the rule does not required an exact match, True is
        returned at once.

        Args:
            data_query_function: Callback for retrieving the data to evaluate.

        Returns:
            If the rule requires an exact match:
                True if all rule conditions evaluates to True.
                False if any rule condition evaluates to False.
            If the rule does not require an exact match:
                True
        """
        # Pass if exact match isn't required.
        if not self.exact_match:
            log.debug('Exact match not required')
            return True

        for condition in self.conditions:
            if not self._evaluate_condition(condition, data_query_function):
                log.debug('Condition FAILED: "{!s}"'.format(condition))
                log.debug('Exact match FAILED!')
                return False
            else:
                log.debug('Condition PASSED: "{!s}"'.format(condition))
        log.debug('Exact match PASSED!')
        return True

    def evaluate_score(self, data_query_function):
        """
        Evaluates this rule using data provided by a callback function.

        Conditions are evaluated and the rule is scored through the 'upvote'
        (and 'downvote' methods)

        Args:
            data_query_function: Callback for retrieving the data to evaluate.
        """
        for condition in self.conditions:
            if self._evaluate_condition(condition, data_query_function):
                log.debug('Condition PASSED: "{!s}"'.format(condition))
                self.upvote()
            else:
                # TODO: file_rule.downvote()?
                log.debug('Condition FAILED: "{!s}"'.format(condition))

    def _evaluate_condition(self, condition, data_query_function):
        # Fetch data at "query_string" using the provided "data_query_function".
        data = data_query_function(condition.query_string)
        if data is None:
            log.warning('Unable to evaluate condition due to missing data:'
                        ' "{!s}"'.format(condition))
            return False

        # Evaluate the condition using actual data.
        return condition.evaluate(data)

    def __str__(self):
        # TODO: [TD0039] Do not include the file rule attribute `score` when
        #       listing the configuration with `--dump-config`.
        return util.dump(self.__dict__)

    def __repr__(self):
        out = []
        for key in self.__dict__:
            out.append('{}="{}"'.format(key.title(), self.__dict__[key]))
        return 'FileRule({})'.format(', '.join(out))


def get_valid_rule_condition(raw_query, raw_value):
    """
    Tries to create and return a 'RuleCondition' instance.

    Validation of the "raw" arguments are performed as part of the
    'RuleCondition' initialization. In case of failure, False is returned.

    Args:
        raw_query: The "query string" specifying *some data* for the condition.
        raw_value: The expression or value that describes the condition.

    Returns:
        An instance of the 'RuleCondition' class if the given arguments are
        valid, otherwise False.
    Raises:
        InvalidFileRuleError: The 'RuleCondition' instance could not be created.
    """
    try:
        condition = RuleCondition(raw_query, raw_value)
    except (TypeError, ValueError) as e:
        # Add information and then pass the exception up the chain so that the
        # error can be displayed with additional contextual information.
        raise exceptions.InvalidFileRuleError(
            'Invalid rule condition ("{!s}": "{!s}"); {!s}'.format(
                raw_query, raw_value, e
            )
        )
    else:
        return condition


def parse_ranking_bias(value):
    """
    Validates data to be used as a "ranking_bias".

    The value must be an integer or float between 0 and 1.
    To allow for an unspecified bias, None values are allowed and substituted
    with the default bias defined by "FILERULE_DEFAULT_RANKING_BIAS".

    Args:
        value: The raw value to parse.
    Returns:
        The specified value if the value is a number type in the range 0-1.
        If the specified value is None, a default bias is returned.
    Raises:
        ConfigurationSyntaxError: The value is of an unexpected type or not
            within the range 0-1.
    """
    ERROR_MSG = 'Expected float in range 0-1. Got: "{}"'.format(value)

    if value is None:
        return constants.DEFAULT_FILERULE_RANKING_BIAS
    if not isinstance(value, (int, float)):
        raise exceptions.ConfigurationSyntaxError(ERROR_MSG)

    try:
        w = float(value)
    except TypeError:
        raise exceptions.ConfigurationSyntaxError(ERROR_MSG)
    else:
        if float(0) <= w <= float(1):
            return w
        else:
            raise exceptions.ConfigurationSyntaxError(ERROR_MSG)
