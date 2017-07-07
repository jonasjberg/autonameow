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
        # TODO: [TD0001] Implement this properly!
        # Workaround for 'metadata.exiftool.EXIF:DateTimeOriginal' ..
        # Above test would return 'EXIF:DateTimeOriginal' but this solution
        # would require testing the second to last part; 'exiftool', instead.
        if self.query_string.startswith('metadata.exiftool'):
            # TODO: [TD0015] Handle expression in 'condition_value'
            #                ('Defined', '> 2017', etc)
            if raw_expression:
                self._expression = raw_expression
                return

        # The "query string" is required in order to know how the expression
        # should be evaluated. Consider the expression invalid.
        if not self.query_string:
            raise ValueError(
                'A valid "query string" is required for validation.'
            )

        parsers = field_parsers.suitable_parser_for_querystr(self.query_string)
        if not parsers:
            raise ValueError('Found no suitable parsers for query string: '
                             '"{!s}"'.format(self.query_string))
        else:
            parser = parsers[0]
        if parser.validate(raw_expression):
            self._expression = raw_expression
        else:
            raise ValueError(
                'Invalid expression: "{!s}"'.format(raw_expression)
            )

    @staticmethod
    def _validate_query_string(raw_query_string):
        if not raw_query_string:
            return False

        # TODO: [TD0001] Implement this properly!
        # Workaround for 'metadata.exiftool.EXIF:DateTimeOriginal' ..
        # Above test would return 'EXIF:DateTimeOriginal' but this solution
        # would require testing the second to last part; 'exiftool', instead.
        if raw_query_string.startswith('metadata.exiftool'):
            # TODO: [TD0015] Handle expression in 'condition_value'
            #                ('Defined', '> 2017', etc)
            return True

        if field_parsers.suitable_parser_for_querystr(raw_query_string):
            return True
        return False
