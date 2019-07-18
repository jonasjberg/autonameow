# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from core import constants as C
from core import master_provider
from core.config import field_parsers
from core.exceptions import ConfigError
from core.exceptions import ConfigurationSyntaxError
from core.exceptions import InvalidMeowURIError
from core.model import MeowURI
from core.namebuilder import fields
from core.namebuilder.template import NameTemplate


log = logging.getLogger(__name__)


class InvalidRuleError(ConfigError):
    """Error while constructing an instance of 'Rule' or its members."""


class InvalidRuleConditionError(ConfigError):
    """Error while instantiating a new 'RuleCondition'."""


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
            InvalidRuleConditionError: The 'RuleCondition' instantiation failed.
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
            raise InvalidRuleConditionError(
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
            raise InvalidRuleConditionError(
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
            raise InvalidRuleConditionError(
                'No field parser can handle MeowURI: "{!s}"'.format(self.meowuri)
            )

        valid_expression = self._validate_expression(raw_expression)
        if not valid_expression:
            raise InvalidRuleConditionError(
                'Invalid expression: "{!s}"'.format(raw_expression)
            )
        log.debug('Validated expression: "%s"', raw_expression)
        self._expression = raw_expression

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
                         '"%s" expression: "%s"', self.meowuri, self.expression)
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
            name_template: Name template to use for files matching the rule,
                           as an instance of 'NameTemplate'.
            description: (OPTIONAL) Human-readable description.
            exact_match: (OPTIONAL) True if all conditions must be met at
                         evaluation. Defaults to False.
            ranking_bias: (OPTIONAL) Float between 0-1 that influences ranking.
        """
        assert isinstance(conditions, list)
        self._conditions = conditions

        assert isinstance(data_sources, dict)
        self.data_sources = dict(data_sources)

        self.name_template = name_template

        if isinstance(description, str) and description.strip():
            self.description = description
        else:
            self.description = str(C.DEFAULT_RULE_DESCRIPTION)

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

    def __gt__(self, other):
        # Sort by arbitrary attributes to get repeatable results. HOWEVER, note
        # that the 'RuleMatcher' uses 'prioritize_rules()' to sort rules prior
        # to evaluation.
        return (
            len(self.conditions),
            len(self.data_sources),
            self.ranking_bias,
            self.exact_match,
            str(self.name_template),
            self.description,
        ) > (
           len(other.conditions),
           len(other.data_sources),
           other.ranking_bias,
           other.exact_match,
           str(other.name_template),
           other.description,
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
        return '{!s}({!r}, {!r}, {!r}, {!r}, {!r})'.format(
            self.__class__.__name__,
            self.conditions,
            self.data_sources,
            self.exact_match,
            self.name_template,
            self.ranking_bias,
        )

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


def get_valid_rule(description, exact_match, ranking_bias, format_string,
                   conditions, raw_data_sources):
    """
    Main retrieval mechanism for 'Rule' class instances.

    Returns:
        An instance of 'Rule' if the given arguments are valid.

    Raises:
        InvalidRuleError: Validation failed or the 'Rule' instantiation failed.
    """
    # Skips and warns about invalid/missing sources. Does not fail or
    # raise any exceptions even if all of the sources fail validation.
    data_sources = parse_data_sources(raw_data_sources)

    if not isinstance(format_string, str):
        raise InvalidRuleError('Expected "format_string" to be of type "str"')

    # Convert previously validated format string to instance of 'NameTemplate'.
    # Name templates should be passed as class instances from here on out.
    name_template = NameTemplate(format_string)

    if not isinstance(exact_match, bool):
        raise InvalidRuleError('Expected "exact_match" to be of type "bool"')

    if not isinstance(ranking_bias, float):
        raise InvalidRuleError('Expected "ranking_bias" to be of type "float"')

    return Rule(conditions, data_sources, name_template,
                description, exact_match, ranking_bias)


def parse_data_sources(raw_sources):
    if not raw_sources:
        # Allow empty/None data sources.
        raw_sources = dict()

    log.debug('Parsing %d raw sources ..', len(raw_sources))
    if not isinstance(raw_sources, dict):
        raise ConfigurationSyntaxError(
            'Expected sources to be of type dict'
        )

    parsed_data_sources = dict()
    for raw_templatefield, raw_meowuri_strings in raw_sources.items():
        if not raw_meowuri_strings:
            log.debug('Skipped source with empty MeowURI(s) '
                      '(template field: "%s")', raw_templatefield)
            continue

        if not fields.is_valid_template_field(raw_templatefield):
            log.warning('Skipped source with invalid name template field '
                        '(MeowURI: "%s")', raw_meowuri_strings)
            continue

        tf = fields.nametemplatefield_class_from_string(raw_templatefield)
        assert isinstance(tf, fields.NameTemplateField), type(tf)

        if not isinstance(raw_meowuri_strings, list):
            raw_meowuri_strings = [raw_meowuri_strings]

        for meowuri_string in raw_meowuri_strings:
            try:
                uri = MeowURI(meowuri_string)
            except InvalidMeowURIError as e:
                log.warning('Skipped source with invalid MeowURI: '
                            '"%s"; %s', meowuri_string, e)
                continue

            if is_valid_source(uri):
                log.debug('Validated field %s source: %s', tf, uri)
                if not parsed_data_sources.get(tf):
                    parsed_data_sources[tf] = [uri]
                else:
                    parsed_data_sources[tf] += [uri]
            else:
                log.debug('Invalid field %s source: %s', tf, uri)

    log.debug('Returning %d (out of %d) valid sources',
              len(parsed_data_sources), len(raw_sources))
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
    if not isinstance(uri, MeowURI):
        return False

    if uri.is_generic:
        return True
    # TODO: [TD0185] Rework access to 'master_provider' functionality.
    if master_provider.Registry.might_be_resolvable(uri):
        return True
