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

from core import constants as C
from core import (
    providers,
    types,
)
from core.config import field_parsers
from core.exceptions import (
    ConfigError,
    ConfigurationSyntaxError,
    InvalidMeowURIError
)
from core.model import MeowURI
from core.namebuilder import fields
import util


log = logging.getLogger(__name__)


class InvalidRuleError(ConfigError):
    """The Rule is in a bad state. The Rule state should only be set
    with known good data. This error implies data validation has failed."""


class RuleCondition(object):
    """
    Represents a single condition contained in a configuration rule.
    """
    def __init__(self, meowuri, raw_expression):
        """
        Validates the arguments and returns a 'RuleCondition' instance if
        the validation is successful. Else an exception is thrown.

        The "MeowURI" is a reference to some data.
        The expression is some expression that will be evaluated on the data
        contained at the location referenced to by the "MeowURI".

        Example: If the "MeowURI" is 'contents.mime_type', a valid
        expression could be 'image/*'. When this condition is evaluated,
        the data contained at 'contents.mime_type' might be 'image/jpeg'.
        In this case the evaluation would return True.

        Args:
            meowuri: A "MeowURI" describing the target of the condition,
                     as a previously validated instance of 'MeowURI'.
            raw_expression: A expression to use when evaluating this condition.
        """
        # TODO: Clean up setting the 'parser' attribute.
        # NOTE(jonas): The "MeowURI" determines which parser class is used.

        # TODO: [TD0015] Allow conditionals in the configuration rules.
        # Possible a list of functions already "loaded" with the target value.
        # Also "loaded" with corresponding (reference to) a validation function.
        self._parser = None
        self._meowuri = None
        self._expression = None
        # TODO: [TD0138] Fix inconsistent type of 'expression'. Enforce list?

        self.meowuri = meowuri
        self.expression = raw_expression

    @property
    def meowuri(self):
        return self._meowuri

    @meowuri.setter
    def meowuri(self, meowuri):
        if not isinstance(meowuri, MeowURI):
            raise TypeError(
                'Expected instance of MeowURI. Got {!s}'.format(type(meowuri))
            )

        # Consider the "MeowURI" valid if any parser can handle it.
        if not self._get_parser_for(meowuri):
            raise ValueError(
                'No field parser can handle MeowURI: "{!s}"'.format(meowuri)
            )
        else:
            self._meowuri = meowuri

    @property
    def expression(self):
        return self._expression

    @expression.setter
    def expression(self, raw_expression):
        # The "MeowURI" is required in order to know how the expression
        # should be evaluated. Consider the expression invalid.
        if not self.meowuri:
            raise ValueError('The condition first needs a valid "MeowURI" in '
                             'order to validate an expression')

        # TODO: [TD0089] Validate only "generic" metadata fields ..
        # TODO: Check if the "MeowURI" is "generic", only validate if it is.
        #       Skip validation of source-specific MeowURIs for now.

        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)

        # TODO: [TD0138] Fix inconsistent type of 'expression'. Enforce list?

        if not self._get_parser_for(self.meowuri):
            raise ValueError('Found no suitable parsers for MeowURI: '
                             '"{!s}"'.format(self.meowuri))

        valid_expression = self._validate_expression(raw_expression)
        if valid_expression:
            log.debug('Validated expression: "{!s}"'.format(raw_expression))
            self._expression = raw_expression
        else:
            raise ValueError(
                'Invalid expression: "{!s}"'.format(raw_expression)
            )

    def _validate_expression(self, raw_expression):
        return bool(self._parser.validate(raw_expression))

    def _get_parser_for(self, meowuri):
        if self._parser:
            return self._parser

        parser = field_parsers.suitable_field_parser_for(meowuri)
        if parser:
            self._parser = parser

        return self._parser

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
            log.critical('Unimplemented condition evaluation -- MeowURI: '
                         '"{!s}" expression: "{!s}"'.format(self.meowuri,
                                                            self.expression))
            return False

        result = self._parser.evaluate(self.expression, data)
        return result if result else False

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return (
            self.expression == other.expression and
            self.meowuri == other.meowuri
        )

    def __hash__(self):
        # TODO: [TD0138] Fix inconsistent type of 'expression'. Enforce list?
        if isinstance(self.expression, list):
            expressions = self.expression
        else:
            expressions = [self.expression]

        hashed_expressions = sum(hash(x) for x in expressions)
        return hash(
            (hashed_expressions, self.meowuri)
        )

    def __str__(self):
        return '{!s}: {!s}'.format(self.meowuri, self.expression)

    def __repr__(self):
        return 'RuleCondition({_meowuri}, {_expression})'.format(**self.__dict__)


class Rule(object):
    """
    Represents a single rule entry in a loaded configuration.

    All data validation happens at 'Rule' init or when setting any attribute.
    """
    def __init__(self, conditions, data_sources, name_template,
                 description=None, exact_match=None, ranking_bias=None):
        """
        Creates a new 'Rule' instance.

        Args:
            conditions: Dict used to create instances of 'RuleCondition'.
                        NOTE: Rules without conditions always evaluates True.
            data_sources: Dict of template field names and "MeowURIs".
                          NOTE: Rules without data sources are allowed.
            name_template: Name template to use for files matching the rule.
            description: (OPTIONAL) Human-readable description.
            exact_match: (OPTIONAL) True if all conditions must be met at
                         evaluation. Defaults to False.
            ranking_bias: (OPTIONAL) Float between 0-1 that influences ranking.
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

        # NOTE(jonas): This assumes instances of 'RuleCondition' are immutable!
        self.__cached_hash = None

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
            raise InvalidRuleError(e)

    @property
    def ranking_bias(self):
        if self._ranking_bias:
            return self._ranking_bias
        return C.DEFAULT_RULE_RANKING_BIAS

    @ranking_bias.setter
    def ranking_bias(self, raw_ranking_bias):
        try:
            self._ranking_bias = parse_ranking_bias(raw_ranking_bias)
        except InvalidRuleError as e:
            log.warning(e)
            self._ranking_bias = C.DEFAULT_RULE_RANKING_BIAS

    @property
    def name_template(self):
        return self._name_template

    @name_template.setter
    def name_template(self, raw_name_template):
        # Name template has already been validated in the 'Configuration' class.
        if not raw_name_template:
            raise InvalidRuleError('Got None name template')
        self._name_template = raw_name_template

    @property
    def conditions(self):
        return self._conditions

    @conditions.setter
    def conditions(self, valid_conditions):
        if not isinstance(valid_conditions, list):
            _msg = 'Expected list. Got {!s}'.format(type(valid_conditions))
            raise InvalidRuleError(_msg)

        for c in valid_conditions:
            if not isinstance(c, RuleCondition):
                _msg = 'Invalid condition: ({!s}) "{!s}"'.format(type(c), c)
                raise InvalidRuleError(_msg)

        self._conditions = valid_conditions

    @property
    def number_conditions(self):
        return len(self._conditions)

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
        Get all "MeowURIs" referenced by this rule.

        The "MeowURI" can be part of either a condition or a data source.

        Returns: The set of all "MeowURIs" referenced by this rule.
        """
        unique_meowuris = set()

        for condition in self.conditions:
            unique_meowuris.add(condition.meowuri)

        for _, _meowuris in self.data_sources.items():
            for m in _meowuris:
                unique_meowuris.add(m)

        return unique_meowuris

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return (
            self.conditions == other.conditions and
            self.data_sources == other.data_sources and
            self.description == other.description and
            self.exact_match == other.exact_match and
            self.name_template == other.name_template and
            self.ranking_bias == other.ranking_bias
        )

    def __hash__(self):
        # NOTE(jonas): This assumes instances of 'RuleCondition' are immutable!
        if not self.__cached_hash:
            hashed_conditions = sum(hash(c) for c in self.conditions)
            hashed_data_sources = 0
            for template_field, meowuri_list in self.data_sources.items():
                data_source_hash = hash(template_field) + sum(
                    hash(meowuri) for meowuri in meowuri_list
                )
                hashed_data_sources += data_source_hash

            self.__cached_hash = hash(
                (hashed_conditions, hashed_data_sources, self.description,
                 self.exact_match, self.name_template, self.ranking_bias)
            )

        return self.__cached_hash

    def __str__(self):
        return self.description

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
        InvalidRuleError: Validation failed or the 'Rule' instantiation failed.
    """
    if not conditions:
        conditions = dict()

    try:
        valid_conditions = parse_conditions(conditions)
    except ConfigurationSyntaxError as e:
        raise InvalidRuleError(e)

    try:
        _rule = Rule(valid_conditions, data_sources, name_template,
                     description, exact_match, ranking_bias)
    except InvalidRuleError as e:
        raise e
    else:
        return _rule


def get_valid_rule_condition(meowuri, raw_expression):
    """
    Tries to create and return a 'RuleCondition' instance.

    Validation of the "raw" arguments are performed as part of the
    'RuleCondition' initialization. In case of failure, False is returned.

    Args:
        meowuri: The "MeowURI" that provides access to *some data* to be
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
        raise InvalidRuleError(
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
        raise ConfigurationSyntaxError(
            'Expected float but got "{!s}" ({!s})'.format(value, type(value))
        )
    else:
        if not 0.0 <= _value <= 1.0:
            raise ConfigurationSyntaxError(
                'Expected float between 0.0 and 1.0. Got {} -- Using default: '
                '{}'.format(value, C.DEFAULT_RULE_RANKING_BIAS)
            )
        return _value


def parse_conditions(raw_conditions):
    if not isinstance(raw_conditions, dict):
        raise ConfigurationSyntaxError('Expected conditions of type "dict". '
                                       'Got {!s}'.format(type(raw_conditions)))

    log.debug('Parsing {} raw conditions ..'.format(len(raw_conditions)))
    passed = []
    try:
        for meowuri_string, expression_string in raw_conditions.items():
            try:
                uri = MeowURI(meowuri_string)
            except InvalidMeowURIError as e:
                raise ConfigurationSyntaxError(e)

            try:
                valid_condition = get_valid_rule_condition(uri,
                                                           expression_string)
            except InvalidRuleError as e:
                raise ConfigurationSyntaxError(e)
            else:
                passed.append(valid_condition)
                log.debug('Validated condition: "{!s}"'.format(valid_condition))
    except ValueError as e:
        raise ConfigurationSyntaxError(
            'contains invalid condition: ' + str(e)
        )

    log.debug(
        'Returning {} (out of {}) valid conditions'.format(len(passed),
                                                           len(raw_conditions))
    )
    return passed


def parse_data_sources(raw_sources):
    passed = dict()

    if not raw_sources:
        # Allow empty/None data sources.
        raw_sources = dict()

    log.debug('Parsing {} raw sources ..'.format(len(raw_sources)))
    if not isinstance(raw_sources, dict):
        raise ConfigurationSyntaxError(
            'Expected sources to be of type dict'
        )

    for raw_templatefield, raw_meowuri_strings in raw_sources.items():
        if not fields.is_valid_template_field(raw_templatefield):
            log.warning('Skipped source with invalid name template field '
                        '(MeowURI: "{!s}")'.format(raw_meowuri_strings))
            continue

        tf = fields.nametemplatefield_class_from_string(raw_templatefield)
        if not tf:
            log.warning('Failed to convert template field string to class '
                        'instance. This should not happen!')
            log.warning('Template Field: ”{!s}"'.format(raw_templatefield))
            continue

        assert issubclass(tf, fields.NameTemplateField), type(tf)

        if not raw_meowuri_strings:
            log.debug('Skipped source with empty MeowURI(s) '
                      '(template field: "{!s}")'.format(raw_templatefield))
            continue

        if not isinstance(raw_meowuri_strings, list):
            raw_meowuri_strings = [raw_meowuri_strings]

        for meowuri_string in raw_meowuri_strings:
            try:
                uri = MeowURI(meowuri_string)
            except InvalidMeowURIError as e:
                log.warning('Skipped source with invalid MeoWURI: '
                            '"{!s}"; {!s}'.format(meowuri_string, e))
                continue

            if is_valid_source(uri):
                log.debug('Validated source: [{!s}]: {!s}'.format(
                    tf.as_placeholder(), uri
                ))
                if not passed.get(tf):
                    passed[tf] = [uri]
                else:
                    passed[tf] += [uri]
            else:
                log.debug('Invalid source: [{!s}]: {!s}'.format(
                    tf.as_placeholder(), uri
                ))

    log.debug(
        'Returning {} (out of {}) valid sources'.format(len(passed),
                                                        len(raw_sources))
    )
    return passed


def is_valid_source(meowuri):
    """
    Check if the source is valid.

    For example, the source value "extractor.metadata.exiftool.PDF:CreateDate"
    would be considered valid if "extractor.metadata.exiftool" was registered
    by a source.

    Args:
        meowuri: The source to test as an instance of 'MeowURI'.

    Returns:
        The given source value if it passes the test, otherwise False.
    """
    if not meowuri or not isinstance(meowuri, MeowURI):
        log.warning('Got None or not an instance of "MeowURI"')
        log.debug('"is_valid_source()" got ({!s}) {!s}'.format(type(meowuri),
                                                               meowuri))
        return False

    if meowuri.is_generic:
        return True
    if providers.Registry.resolvable(meowuri):
        return True

    return False
