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
    util
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
            assert(len(parsers) == 0)
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

        # NOTE(jonas): For unhandled cases like
        # 'metadata.exiftool.EXIF:DateTimeOriginal, 'self._parser' is None
        # and below method call will fail.
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


class Rule(object):
    def __init__(self):
        pass


class FileRule(Rule):
    """
    Represents a single file rule entry in a loaded configuration.

    This class is a container; assumes all data in "kwargs" is valid.
    All data validation should be performed outside of this class.

    File rules are prioritized and sorted by both "score" and "weight".

      - score  Represents how well suited a rule is for a given file.
               This value is changed at run-time.
      - weight If multiple rules end up with an equal score, weights are
               used to further prioritize as to get a single "winning" rule.
               This value is specified in the active configuration.
    """
    def __init__(self, **kwargs):
        super().__init__()

        self.description = str(kwargs.get('description'))
        self.exact_match = bool(kwargs.get('exact_match'))
        self.weight = kwargs.get('weight', constants.DEFAULT_FILERULE_WEIGHT)
        self.name_template = kwargs.get('name_template')
        self.conditions = kwargs.get('conditions', False)
        self.data_sources = kwargs.get('data_sources', False)

        # Rules are sorted/prioritized by first the score, secondly the weight.
        self.score = 0

    def __str__(self):
        # TODO: [TD0039] Do not include the file rule attribute `score` when
        #       listing the configuration with `--dump-config`.
        return util.dump(self.__dict__)

    def __repr__(self):
        out = []
        for key in self.__dict__:
            out.append('{}="{}"'.format(key.title(), self.__dict__[key]))
        return 'FileRule({})'.format(', '.join(out))

    def upvote(self):
        """
        Increases the matching score of this rule.
        """
        self.score += 1

    def downvote(self):
        """
        Decreases the matching score of this rule.
        """
        if self.score > 0:
            self.score -= 1


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
    """
    try:
        condition = RuleCondition(raw_query, raw_value)
    except (TypeError, ValueError) as e:
        log.critical('Invalid rule condition: {!s}'.format(e))
        return False
    else:
        return condition
