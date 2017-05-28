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

from core.config.constants import DATA_FIELDS, MAGIC_TYPE_LOOKUP
from core.evaluate import namebuilder


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

    def init(self):
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
            except (re.error, TypeError):
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
            if not expression:
                return False

            if '/' in expression:
                for v in MAGIC_TYPE_LOOKUP.values():
                    if expression in v:
                        return True
            elif expression in MAGIC_TYPE_LOOKUP.keys():
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
                _ = datetime.today().strftime(expression)
            except (ValueError, TypeError):
                return False
            else:
                return True

        return is_valid_datetime


class NameFormatRuleParser(RuleParser):
    applies_to_field = ['name_format']
    applies_to_conditions = False
    applies_to_data_sources = False

    def get_validation_function(self):
        def is_valid_format_string(expression):
            try:
                namebuilder.assemble_basename(expression, **DATA_FIELDS)
            except (ValueError, TypeError, Exception):
                # TODO: Have NameBuilder raise a custom exception?
                return False
            else:
                return True

        return is_valid_format_string


def get_instantiated_parsers():
    """
    Get a list of all available rule parsers as instantiated class objects.
    All classes inheriting from the "RuleParser" class are included.

    Returns:
        A list of class instances, one object per subclass of  "RuleParser".
    """
    return [p() for p in globals()['RuleParser'].__subclasses__()]


def available_parsers():
    """
    Get a list of all available parsers, I.E. the names of all classes that
    inherit from "RuleParser".

    Returns:
        The names of available rule parsers as strings.
    """
    return [klass.__name__ for klass in
            globals()['RuleParser'].__subclasses__()]

