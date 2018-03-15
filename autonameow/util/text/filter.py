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

import re

from util import sanity


# TODO: [TD0034] All filtering must be (re-)designed.


class RegexFilter(object):
    """
    Filters strings by matching multiple regular expressions.

    Example usage:

        >>> fa = RegexFilter(r'[fF]oo')
        >>> fa('bar')
        'bar'
        >>> fa('Foo')
        >>> fa(['foo', 'bar', 'Foo'])
        ['bar']
        >>> fb = RegexFilter([r'[fF]oo', '.*'])
        >>> fb('bar')
        >>> fb(['Foo', 'bar'])
        []
    """
    def __init__(self, expressions):
        """
        Creates a new re-usable instance.

        Args:
            expressions: Either one or a list of Unicode strings to be
                         compiled into regular expressions.
        """
        # Used to ignore previously added expressions.
        self._seen_expressions = set()
        self._regexes = self._compile_regexes(expressions)

    @property
    def regexes(self):
        return set(self._regexes)

    def __call__(self, values):
        if isinstance(values, (list, set)):
            # Preserve input sequence type
            container_type = type(values)
            return container_type(
                v for v in values if not self._matches_any_regex(v)
            )
        else:
            value = values
            if not self._matches_any_regex(value):
                return value
        return None

    def _compile_regexes(self, expressions):
        if not isinstance(expressions, list):
            expressions = [expressions]

        regexes = set()
        for expression in expressions:
            sanity.check_internal_string(expression)
            if expression in self._seen_expressions:
                # Can't do de-duplication by adding compiled regexes to a set ..
                continue

            regexes.add(re.compile(expression))
            self._seen_expressions.add(expression)

        return regexes

    def _matches_any_regex(self, value):
        return bool(any(regex.match(value) for regex in self.regexes))

    def __len__(self):
        return len(self.regexes)
