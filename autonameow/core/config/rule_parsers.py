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

import re
from datetime import datetime

from core.util.diskutils import MAGIC_TYPE_LOOKUP


class RuleParser(object):
    """
    Top-level superclass for all parsers of rule "conditions".
    Provides common functionality and interfaces that must be implemented
    by inheriting rule parser classes.
    """

    applies_to_field = []
    applies_to_conditions = None
    applies_to_data_sources = None

    def __init__(self):

        self.init()

    def __init__(self):
        # Possibly implemented by inheriting classes.
        pass

    def get_validation_function(self):
        """
        Used to check that the syntax and content of a subset of rules.

        Returns:
            A function that validates rules in fields defined in
            "applies_to_field".
            This function returns True if the rule is valid, otherwise False.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')


class RegexRuleParser(RuleParser):
    applies_to_field = ['pathname', 'basename', 'extension']
    applies_to_conditions = True
    applies_to_data_sources = False

    def get_validation_function(self):
        def is_valid_regex(expression):
            try:
                re.compile(expression)
                valid = True
            except re.error:
                return False
            else:
                return True

        return is_valid_regex


class MimeTypeRuleParser(RuleParser):
    applies_to_field = ['mime_type']
    applies_to_conditions = True
    applies_to_data_sources = False

    def get_validation_function(self):
        def is_valid_mime_type(expression):
            if expression in MAGIC_TYPE_LOOKUP.values() or \
               expression in MAGIC_TYPE_LOOKUP.keys():
                return True

            return False

        return is_valid_mime_type


class DateTimeRuleParser(RuleParser):
    applies_to_field = ['datetime']
    applies_to_conditions = True
    applies_to_data_sources = True

    def get_validation_function(self):
        def is_valid_datetime(expression):
            try:
                _ = datetime.strptime(expression, '%Y-%m-%d')
            except ValueError:
                return False
            else:
                return True

        return is_valid_datetime



