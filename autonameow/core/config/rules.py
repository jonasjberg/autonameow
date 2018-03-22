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
from core.model import (
    MeowURI,
    NameTemplate
)
from core.namebuilder import fields


log = logging.getLogger(__name__)


class InvalidRuleError(ConfigError):
    """Error while constructing an instance of 'Rule' or its members."""


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

        Example: If the "MeowURI" is 'mime_type', a valid
        expression could be 'image/*'. When this condition is evaluated,
        the data contained at 'mime_type' might be 'image/jpeg'.
        In this case the evaluation would return True.

        Args:
            meowuri: A "MeowURI" describing the target of the condition,
                     as a previously validated instance of 'MeowURI'.
            raw_expression: A expression to use when evaluating this condition.

        Raises:
            InvalidRuleError: The 'RuleCondition' instantiation failed.
        """
        # TODO: Clean up setting the 'parser' attribute.
        # NOTE(jonas): The "MeowURI" determines which parser class is used.

        # TODO: [TD0015] Allow conditionals in the configuration rules.
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
    def meowuri(self, uri):
        if not self._get_parser_for(uri):
            raise InvalidRuleError(
                'No field parser can handle MeowURI: "{!s}"'.format(uri)
            )
        self._meowuri = uri

    @property
    def expression(self):
        return self._expression

    @expression.setter
    def expression(self, raw_expression):
        # The "MeowURI" is required in order to know how the expression
        # should be evaluated. Consider the expression invalid.
        if not self.meowuri:
            raise InvalidRuleError(
                'Rule condition does not (yet) have a valid "MeowURI", '
                'which is required in order to validate an expression'
            )

        # TODO: [TD0089] Validate only "generic" metadata fields ..
        # TODO: Check if the "MeowURI" is "generic", only validate if it is.
        #       Skip validation of source-specific MeowURIs for now.

        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)

        # TODO: [TD0138] Fix inconsistent type of 'expression'. Enforce list?

        if not self._get_parser_for(self.meowuri):
            raise InvalidRuleError('Found no suitable parsers for MeowURI: '
                                   '"{!s}"'.format(self.meowuri))

        valid_expression = self._validate_expression(raw_expression)
        if valid_expression:
            log.debug('Validated expression: "{!s}"'.format(raw_expression))
            self._expression = raw_expression
        else:
            raise InvalidRuleError(
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

        Returns: False if evaluation returned False or failed, or the
                 ("truthy") evaluation result if the evaluation passed.
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

        return bool(
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
    """
    def __init__(self, conditions, data_sources, name_template,
                 description=None, exact_match=None, ranking_bias=None):
        """
        Creates a new 'Rule' instance from previously validated data.

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
        assert isinstance(conditions, list)
        self._conditions = conditions

        assert isinstance(data_sources, dict)
        self.data_sources = data_sources

        self.name_template = name_template
        self.description = description or C.DEFAULT_RULE_DESCRIPTION
        self.exact_match = bool(exact_match)

        if ranking_bias is not None:
            self.ranking_bias = float(ranking_bias)
        else:
            self.ranking_bias = C.DEFAULT_RULE_RANKING_BIAS

        # NOTE(jonas): This assumes instances of 'RuleCondition' are immutable!
        self.__cached_hash = None

    @property
    def conditions(self):
        return list(self._conditions)

    @property
    def number_conditions(self):
        return len(self.conditions)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return bool(
            self.conditions == other.conditions and
            self.data_sources == other.data_sources and
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
                (hashed_conditions, hashed_data_sources,
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

    def stringify(self):
        # TODO: [TD0171] Separate logic from user interface.
        # TODO: [cleanup][hack] This is pretty bad ..
        from core.view.cli import ColumnFormatter
        cf = ColumnFormatter()
        for field, sources in self.data_sources.items():
            cf.addrow(str(field), str(sources[0]))
            for source in sources[1:]:
                cf.addrow('', str(source))
        str_sources = str(cf)

        str_conditions = '\n'.join([str(c) for c in self.conditions])

        return '''"{description}"

Exact Match:  {exact}
Conditions:
{conditions}

Name Template:
{template}

Data Sources:
{sources}
'''.format(description=self.description, exact=self.exact_match,
           conditions=str_conditions, template=self.name_template,
           sources=str_sources)


def get_valid_rule(raw_description, raw_exact_match, raw_ranking_bias, format_string,
                   conditions, raw_data_sources):
    """
    Main retrieval mechanism for 'Rule' class instances.

    Does validation of all data, suited to handle input from untrusted sources.

    Returns:
        An instance of 'Rule' if the given arguments are valid.

    Raises:
        InvalidRuleError: Validation failed or the 'Rule' instantiation failed.
    """
    # Conditions
    if not conditions:
        conditions = dict()
    try:
        valid_conditions = parse_conditions(conditions)
    except ConfigurationSyntaxError as e:
        raise InvalidRuleError(e)

    # Skips and warns about invalid/missing sources. Does not fail or
    # raise any exceptions even if all of the sources fail validation.
    data_sources = parse_data_sources(raw_data_sources)

    # Convert previously validated format string to instance of 'NameTemplate'.
    # Name templates should be passed as class instances from here on out.
    name_template = NameTemplate(format_string)

    # Description
    str_description = types.force_string(raw_description)
    if str_description.strip():
        description = str_description
    else:
        description = C.DEFAULT_RULE_DESCRIPTION

    # Exact match
    try:
        exact_match = types.AW_BOOLEAN(raw_exact_match)
    except types.AWTypeError as e:
        raise InvalidRuleError(e)

    # Ranking bias
    try:
        ranking_bias = parse_ranking_bias(raw_ranking_bias)
    except ConfigurationSyntaxError as e:
        log.warning(e)
        ranking_bias = C.DEFAULT_RULE_RANKING_BIAS

    return Rule(valid_conditions, data_sources, name_template,
                description, exact_match, ranking_bias)


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
        return RuleCondition(meowuri, raw_expression)
    except InvalidRuleError as e:
        log.debug('Invalid rule condition ("{!s}": "{!s}"); {!s}'.format(
            meowuri, raw_expression, e
        ))
        raise


def parse_ranking_bias(value):
    """
    Validates data to be used as a "ranking_bias".

    The value must be an integer or float between 0 and 1.
    To allow for an unspecified bias, None values are allowed and substituted
    with the default bias defined by "DEFAULT_RULE_RANKING_BIAS".

    Args:
        value: The "raw" value to parse.
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
        float_value = types.AW_FLOAT(value)
    except types.AWTypeError:
        raise ConfigurationSyntaxError(
            'Expected float but got "{!s}" ({!s})'.format(value, type(value))
        )
    else:
        if not 0.0 <= float_value <= 1.0:
            raise ConfigurationSyntaxError(
                'Expected float between 0.0 and 1.0. Got {} -- Using default: '
                '{}'.format(value, C.DEFAULT_RULE_RANKING_BIAS)
            )
        return float_value


def parse_conditions(raw_conditions):
    if not isinstance(raw_conditions, dict):
        raise ConfigurationSyntaxError('Expected conditions of type "dict". '
                                       'Got {!s}'.format(type(raw_conditions)))

    log.debug('Parsing {} raw conditions ..'.format(len(raw_conditions)))
    passed = []
    try:
        for str_meowuri, raw_expression in raw_conditions.items():
            try:
                uri = MeowURI(str_meowuri)
            except InvalidMeowURIError as e:
                raise ConfigurationSyntaxError(e)

            try:
                valid_condition = get_valid_rule_condition(uri, raw_expression)
            except InvalidRuleError as e:
                raise ConfigurationSyntaxError(e)
            else:
                passed.append(valid_condition)
                log.debug('Validated condition: "{!s}"'.format(valid_condition))
    except ValueError as e:
        raise ConfigurationSyntaxError(
            'contains invalid condition: {!s}'.format(e)
        )

    log.debug(
        'Returning {} (out of {}) valid conditions'.format(len(passed),
                                                           len(raw_conditions))
    )
    return passed


def parse_data_sources(raw_sources):
    if not raw_sources:
        # Allow empty/None data sources.
        raw_sources = dict()

    log.debug('Parsing {} raw sources ..'.format(len(raw_sources)))
    if not isinstance(raw_sources, dict):
        raise ConfigurationSyntaxError(
            'Expected sources to be of type dict'
        )

    parsed_data_sources = dict()
    for raw_templatefield, raw_meowuri_strings in raw_sources.items():
        if not fields.is_valid_template_field(raw_templatefield):
            log.warning('Skipped source with invalid name template field '
                        '(MeowURI: "{!s}")'.format(raw_meowuri_strings))
            continue

        tf = fields.nametemplatefield_class_from_string(raw_templatefield)
        if not tf:
            log.critical(
                'Failed to convert template field string to class instance. '
                'This should not happen as the prior validation passed!'
            )
            continue

        assert isinstance(tf, fields.NameTemplateField), type(tf)

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
                log.debug('Validated field {!s} source: {!s}'.format(tf, uri))
                if not parsed_data_sources.get(tf):
                    parsed_data_sources[tf] = [uri]
                else:
                    parsed_data_sources[tf] += [uri]
            else:
                log.debug('Invalid field {!s} source: {!s}'.format(tf, uri))

    log.debug(
        'Returning {} (out of {}) valid sources'.format(len(parsed_data_sources),
                                                        len(raw_sources))
    )
    return parsed_data_sources


def is_valid_source(uri):
    """
    Validates a data source represented by an instance of 'MeowURI'.

    All generic sources are valid.
    Sources like "extractor.metadata.exiftool.PDF:CreateDate" are considered
    valid only if "extractor.metadata.exiftool" was registered by a source.

    Args:
        uri: The data source to test as an instance of 'MeowURI'.

    Returns:
        True if the source is valid, otherwise False.
    """
    if isinstance(uri, MeowURI):
        if uri.is_generic:
            return True
        if providers.Registry.might_be_resolvable(uri):
            return True
    return False
