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

from core import constants as C
from core import (
    exceptions,
    providers,
    types,
    util
)
from core.config import field_parsers
from core.model import MeowURI
from core.namebuilder import fields


log = logging.getLogger(__name__)


class RuleCondition(object):
    """
    Represents a single condition contained in a configuration rule.
    """
    def __init__(self, meowuri, raw_expression):
        """
        Validates the arguments and returns a 'RuleCondition' instance if
        the validation is successful. Else an exception is thrown.

        The "meowURI" is a reference to some data.
        The expression is some expression that will be evaluated on the data
        contained at the location referenced to by the "meowURI".

        Example: If the "meowURI" is 'contents.mime_type', a valid
        expression could be 'image/*'. When this condition is evaluated,
        the data contained at 'contents.mime_type' might be 'image/jpeg'.
        In this case the evaluation would return True.

        Args:
            meowuri: A "meowURI" describing the target of the condition,
                     as an instance of 'MeowURI'.
            raw_expression: A expression to use when evaluating this condition.
        """
        # TODO: Clean up setting the 'parser' attribute.
        # NOTE(jonas): The "meowURI" determines which parser class is used.

        # TODO: [TD0015] Allow conditionals in the configuration rules.
        # Possible a list of functions already "loaded" with the target value.
        # Also "loaded" with corresponding (reference to) a validation function.
        self._parser = None
        self._meowuri = None
        self._expression = None

        self.meowuri = meowuri
        self.expression = raw_expression

    @property
    def meowuri(self):
        return self._meowuri

    @meowuri.setter
    def meowuri(self, meowuri):
        # The "meowURI" is considered valid if a field parser can handle it.
        valid_meowuri = self._validate_meowuri(meowuri)
        if valid_meowuri:
            self._meowuri = meowuri
        else:
            raise TypeError(
                'No field parser can handle MeowURI: "{!s}"'.format(meowuri)
            )

    @property
    def expression(self):
        return self._expression

    @expression.setter
    def expression(self, raw_expression):
        # The "meowURI" is required in order to know how the expression
        # should be evaluated. Consider the expression invalid.
        if not self.meowuri:
            raise ValueError('The condition first needs a valid "meowURI" in '
                             'order to validate an expression')

        # TODO: [TD0089] Validate only "generic" metadata fields ..
        # TODO: Check if the "MeowURI" is "generic", only validate if it is.
        #       Skip validation of source-specific MeowURIs for now.

        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)

        if not self._get_parser(self.meowuri):
            raise ValueError('Found no suitable parsers for meowURI: '
                             '"{!s}"'.format(self.meowuri))

        valid_expression = self._validate_expression(raw_expression)
        if valid_expression:
            log.debug('Validated expression: "{!s}"'.format(raw_expression))
            self._expression = raw_expression
        else:
            raise ValueError(
                'Invalid expression: "{!s}"'.format(raw_expression)
            )

    def _validate_meowuri(self, meowuri):
        # Consider the "meowURI" valid if any parser can handle it.
        if self._get_parser(meowuri):
            return True
        else:
            return False

    def _validate_expression(self, raw_expression):
        if self._parser.validate(raw_expression):
            return True
        else:
            return False

    def _get_parser(self, meowuri):
        if self._parser:
            return self._parser

        parsers = field_parsers.suitable_field_parser_for(meowuri)
        if parsers:
            # NOTE(jonas): Assume only one parser per "meowURI" for now ..
            assert len(parsers) == 1, (
                   'Unexpectedly got {} parsers for meowURI '
                   '"{!s}"'.format(len(parsers), meowuri))

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
            log.critical('Unimplemented condition evaluation -- meowURI: '
                         '"{!s}" expression: "{!s}"'.format(self.meowuri,
                                                            self.expression))
            return False

        result = self._parser.evaluate(self.expression, data)
        if result:
            return result
        else:
            return False

    def __str__(self):
        return '{!s}: {!s}'.format(self.meowuri, self.expression)

    def __repr__(self):
        return 'RuleCondition("{}", "{}")'.format(self.meowuri,
                                                  self.expression)


class Rule(object):
    """
    Represents a single rule entry in a loaded configuration.

    All data validation happens at 'Rule' init or when setting any attribute.
    """
    def __init__(self, description, exact_match, ranking_bias, name_template,
                 conditions, data_sources):
        """
        Creates a new 'Rule' instance.

        Args:
            description: (OPTIONAL) Human-readable description.
            exact_match: True if all conditions must be met at evaluation.
            ranking_bias: (OPTIONAL) Float between 0-1 that influences ranking.
            name_template: Name template to use for files matching the rule.
            conditions: Dict used to create instances of 'RuleCondition'
            data_sources: Dict of template field names and "meowURIs".
        """
        self._description = None
        self._exact_match = None
        self._ranking_bias = None
        self._name_template = None
        self._conditions = None
        self._data_sources = None

        self.description = description
        self.exact_match = exact_match
        self.ranking_bias = ranking_bias
        self.name_template = name_template
        self.conditions = conditions
        self.data_sources = data_sources

        if not self.conditions:
            raise exceptions.InvalidRuleError(
                'Rule does not specify any conditions: "{!s}"'.format(self)
            )

    @property
    def description(self):
        return self._description

    @description.setter
    def description(self, raw_description):
        valid_description = types.force_string(raw_description)
        if valid_description:
            self._description = valid_description
        else:
            self._description = C.DEFAULT_RULE_DESCRIPTION

    @property
    def exact_match(self):
        return self._exact_match

    @exact_match.setter
    def exact_match(self, raw_exact_match):
        try:
            self._exact_match = types.AW_BOOLEAN(raw_exact_match)
        except types.AWTypeError as e:
            raise exceptions.InvalidRuleError(e)

    @property
    def ranking_bias(self):
        if self._ranking_bias:
            return self._ranking_bias
        else:
            return C.DEFAULT_RULE_RANKING_BIAS

    @ranking_bias.setter
    def ranking_bias(self, raw_ranking_bias):
        try:
            self._ranking_bias = parse_ranking_bias(raw_ranking_bias)
        except exceptions.ConfigurationSyntaxError as e:
            log.warning(e)
            self._ranking_bias = C.DEFAULT_RULE_RANKING_BIAS

    @property
    def name_template(self):
        return self._name_template

    @name_template.setter
    def name_template(self, raw_name_template):
        # Name template has already been validated in the 'Configuration' class.
        if not raw_name_template:
            raise exceptions.InvalidRuleError('Got None name template')
        self._name_template = raw_name_template

    @property
    def conditions(self):
        return self._conditions

    @conditions.setter
    def conditions(self, valid_conditions):
        def _raise_exception():
            raise exceptions.InvalidRuleError(
                'Invalid condition: ({!s}) "{!s}"'.format(type(c), c)
            )

        if not valid_conditions:
            _raise_exception()
        if not isinstance(valid_conditions, list):
            _raise_exception()
        for c in valid_conditions:
            if not isinstance(c, RuleCondition):
                _raise_exception()

        self._conditions = valid_conditions

    @property
    def data_sources(self):
        return self._data_sources

    @data_sources.setter
    def data_sources(self, raw_data_sources):
        # Skips and warns about invalid/missing sources. Does not fail or
        # raise any exceptions even if all of the sources fail validation.
        self._data_sources = parse_data_sources(raw_data_sources)

    def referenced_meowuris(self):
        """
        Get all "meowURIs" referenced by this rule.

        The "meowURI" can be part of either a condition or a data source.

        Returns: The set of all "meowURIs" referenced by this rule.
        """
        unique_meowuris = set()

        for condition in self.conditions:
            unique_meowuris.add(condition.meowuri)

        for _, _meowuris in self.data_sources.items():
            for m in _meowuris:
                unique_meowuris.add(m)

        return unique_meowuris

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
        if self.description:
            _desc = '{} :: '.format(self.description)
        else:
            _desc = ''

        # Pass if exact match isn't required.
        if not self.exact_match:
            log.debug('{}Exact match not required'.format(_desc))
            return True

        for condition in self.conditions:
            if not self._evaluate_condition(condition, data_query_function):
                log.debug('{}Condition FAILED: "{!s}"'.format(_desc, condition))
                log.debug('{}Exact match FAILED!'.format(_desc))
                return False
            else:
                log.debug('{}Condition PASSED: "{!s}"'.format(_desc, condition))
        log.debug('{}Exact match PASSED!'.format(_desc))
        return True

    def number_conditions_met(self, data_query_function):
        """
        Evaluates rule conditions using data provided by a callback function.

        Args:
            data_query_function: Callback for retrieving the data to evaluate.

        Returns:
            The number of met conditions as an integer.
        """
        assert self.conditions and len(self.conditions) > 0, (
               'Rule.conditions is missing or empty')

        if self.description:
            _desc = '{} :: '.format(self.description)
        else:
            _desc = ''

        _count_met_conditions = 0
        for condition in self.conditions:
            if self._evaluate_condition(condition, data_query_function):
                log.debug('{}Condition PASSED: "{!s}"'.format(_desc, condition))
                _count_met_conditions += 1
            else:
                log.debug('{}Condition FAILED: "{!s}"'.format(_desc, condition))

        return _count_met_conditions

    def _evaluate_condition(self, condition, data_query_function):
        data = data_query_function(condition.meowuri)
        if data is None:
            log.warning('Unable to evaluate condition due to missing data:'
                        ' "{!s}"'.format(condition))
            return False

        return condition.evaluate(data)

    def __str__(self):
        return util.dump(self.__dict__)

    def __repr__(self):
        out = []
        for key in self.__dict__:
            out.append('{}="{}"'.format(key.title(), self.__dict__[key]))
        return 'Rule({})'.format(', '.join(out))


def get_valid_rule(description, exact_match, ranking_bias, name_template,
                   conditions, data_sources):
    """
    Main retrieval mechanism for 'Rule' class instances.

    Does validation of all data, suited to handle input from untrusted sources.

    Returns:
        An instance of 'Rule' if the given arguments are valid.
    Raises:
        InvalidRuleError: Validation failed or the 'Rule' could not be created.
    """
    try:
        valid_conditions = parse_conditions(conditions)
    except exceptions.ConfigurationSyntaxError as e:
        raise exceptions.InvalidRuleError(e)

    try:
        _rule = Rule(description, exact_match, ranking_bias, name_template,
                     valid_conditions, data_sources)
    except exceptions.InvalidRuleError as e:
        raise e
    else:
        return _rule


def get_valid_rule_condition(meowuri, raw_expression):
    """
    Tries to create and return a 'RuleCondition' instance.

    Validation of the "raw" arguments are performed as part of the
    'RuleCondition' initialization. In case of failure, False is returned.

    Args:
        meowuri: The "meowURI" that provides access to *some data* to be
                 evaluated in the condition, as an instance of 'MeowURI'.
        raw_expression: The expression or value that describes the condition.

    Returns:
        An instance of the 'RuleCondition' class if the given arguments are
        valid, otherwise False.
    Raises:
        InvalidRuleError: The 'RuleCondition' instance could not be created.
    """
    assert isinstance(meowuri, MeowURI), 'Expected instance of "MeowURI"'

    try:
        condition = RuleCondition(meowuri, raw_expression)
    except (TypeError, ValueError) as e:
        # Add information and then pass the exception up the chain so that the
        # error can be displayed with additional contextual information.
        raise exceptions.InvalidRuleError(
            'Invalid rule condition ("{!s}": "{!s}"); {!s}'.format(
                meowuri, raw_expression, e
            )
        )
    else:
        return condition


def parse_ranking_bias(value):
    """
    Validates data to be used as a "ranking_bias".

    The value must be an integer or float between 0 and 1.
    To allow for an unspecified bias, None values are allowed and substituted
    with the default bias defined by "DEFAULT_RULE_RANKING_BIAS".

    Args:
        value: The raw value to parse.
    Returns:
        The specified value if the value is a number type in the range 0-1.
        If the specified value is None, a default bias is returned.
    Raises:
        ConfigurationSyntaxError: The value is of an unexpected type or not
            within the range 0-1.
    """
    if value is None:
        return C.DEFAULT_RULE_RANKING_BIAS

    try:
        _value = types.AW_FLOAT(value)
    except types.AWTypeError:
        raise exceptions.ConfigurationSyntaxError(
            'Expected float but got "{!s}" ({!s})'.format(value, type(value))
        )
    else:
        if float(0) <= _value <= float(1):
            return _value
        else:
            raise exceptions.ConfigurationSyntaxError(
                'Expected float within 0.0-1.0 but got {} -- Using default:'
                ' {}'.format(value, C.DEFAULT_RULE_RANKING_BIAS)
            )


def parse_conditions(raw_conditions):
    log.debug('Parsing {} raw conditions ..'.format(len(raw_conditions)))

    if not raw_conditions:
        raise exceptions.ConfigurationSyntaxError('Got no conditions')
    if not isinstance(raw_conditions, dict):
        raise exceptions.ConfigurationSyntaxError(
            'Expected conditions to be of type dict'
        )

    passed = []
    try:
        for meowuri_string, expression_string in raw_conditions.items():
            try:
                _meowuri = MeowURI(meowuri_string)
            except exceptions.InvalidMeowURIError as e:
                raise exceptions.ConfigurationSyntaxError(e)

            try:
                valid_condition = get_valid_rule_condition(_meowuri,
                                                           expression_string)
            except exceptions.InvalidRuleError as e:
                raise exceptions.ConfigurationSyntaxError(e)
            else:
                passed.append(valid_condition)
                log.debug('Validated condition: "{!s}"'.format(valid_condition))
    except ValueError as e:
        raise exceptions.ConfigurationSyntaxError(
            'contains invalid condition: ' + str(e)
        )

    log.debug(
        'Returning {} (out of {}) valid conditions'.format(len(passed),
                                                           len(raw_conditions))
    )
    return passed


def parse_data_sources(raw_sources):
    passed = {}

    log.debug('Parsing {} raw sources ..'.format(len(raw_sources)))

    if not raw_sources:
        raise exceptions.ConfigurationSyntaxError('Got no sources')
    if not isinstance(raw_sources, dict):
        raise exceptions.ConfigurationSyntaxError(
            'Expected sources to be of type dict'
        )

    for raw_templatefield, raw_meowuri_strings in raw_sources.items():
        if not fields.is_valid_template_field(raw_templatefield):
            log.warning('Skipped source with invalid name template field '
                        '(meowURI: "{!s}")'.format(raw_meowuri_strings))
            continue

        tf = fields.nametemplatefield_class_from_string(raw_templatefield)
        if not tf:
            log.warning('Failed to convert template field string to class '
                        'instance. This should not happen!')
            log.warning('Template Field: ”{!s}"'.format(raw_templatefield))
            continue

        if not raw_meowuri_strings:
            log.debug('Skipped source with empty meowURI(s) '
                      '(template field: "{!s}")'.format(raw_templatefield))
            continue

        if not isinstance(raw_meowuri_strings, list):
            raw_meowuri_strings = [raw_meowuri_strings]

        for meowuri_string in raw_meowuri_strings:
            try:
                _meowuri = MeowURI(meowuri_string)
            except exceptions.InvalidMeowURIError as e:
                log.warning('Skipped source with invalid MeoWURI: '
                            '"{!s}"; {!s}'.format(meowuri_string, e))
                continue

            if is_valid_source(_meowuri):
                log.debug('Validated source: [{!s}]: {!s}'.format(
                    tf.as_placeholder(), _meowuri
                ))
                if not passed.get(tf):
                    passed[tf] = [_meowuri]
                else:
                    passed[tf] += [_meowuri]
            else:
                log.debug('Invalid source: [{!s}]: {!s}'.format(
                    tf.as_placeholder(), _meowuri
                ))

    log.debug(
        'Returning {} (out of {}) valid sources'.format(len(passed),
                                                        len(raw_sources))
    )
    return passed


def is_valid_source(source_value):
    """
    Check if the source is valid.

    Tests if the given source starts with the same text as any of the
    date source "meowURIs" stored in the 'SessionRepository'.

    For example, the source value "extractor.metadata.exiftool.PDF:CreateDate"
    would be considered valid if "extractor.metadata.exiftool" was registered
    by a source.

    Args:
        source_value: The source to test as a text string.

    Returns:
        The given source value if it passes the test, otherwise False.
    """
    if providers.Registry.resolvable(source_value):
        return True
    return False
