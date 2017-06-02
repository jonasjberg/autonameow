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

import glob
import os
import re
from datetime import datetime

from core.config.constants import (
    DATA_FIELDS,
    MAGIC_TYPE_LOOKUP
)
from core.evaluate import namebuilder


class ConfigFieldParser(object):
    """
    Top-level superclass for all parsers of configuration fields.

    Provides common functionality and interfaces that must be implemented
    by inheriting rule parser classes.
    """
    applies_to_field = []

    def __init__(self):
        self.init()

    def init(self):
        # Possibly implemented by inheriting classes.
        pass

    def get_validation_function(self):
        """
        Used to check that the syntax and content of a subset of fields.

        Returns:
            A function that validates configuration fields, specified
            by "applies_to_field".
            This function returns True if the field is valid, otherwise False.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def validate(self, expression):
        """
        Validates a given field. Should be called through classes inheriting
        from "ConfigFieldParser", which will validate the expression depending
        on which class is used.  Can NOT be called as a class method.

        Args:
            expression: The expression to validate.

        Returns:
            True if expression is valid, else False.

        """
        return self.get_validation_function()(expression)

    # TODO: Add validation and evaluation methods to parser classes?


class RegexConfigFieldParser(ConfigFieldParser):
    applies_to_field = ['pathname', 'basename', 'extension', 'raw_text']

    @staticmethod
    def is_valid_regex(expression):
        try:
            re.compile(expression)
        except (re.error, TypeError):
            return False
        else:
            return True

    @staticmethod
    def evaluate_regex(expression, test_data):
        _match = re.match(expression, test_data)
        if _match:
            return _match
        else:
            return False

    def get_validation_function(self):
        return self.is_valid_regex


class MimeTypeConfigFieldParser(ConfigFieldParser):
    applies_to_field = ['mime_type']

    @staticmethod
    def is_valid_mime_type(expression):
        if not expression:
            return False

        if '/' in expression:
            for magic_value in MAGIC_TYPE_LOOKUP.values():
                if expression in magic_value:
                    return True
        elif expression in MAGIC_TYPE_LOOKUP.keys():
            return True

        return False

    def get_validation_function(self):
        return self.is_valid_mime_type


class DateTimeConfigFieldParser(ConfigFieldParser):
    applies_to_field = ['datetime', 'date_accessed', 'date_created',
                        'date_modified']

    @staticmethod
    def is_valid_datetime(expression):
        try:
            _ = datetime.today().strftime(expression)
        except (ValueError, TypeError):
            return False
        else:
            return True

    def get_validation_function(self):
        return self.is_valid_datetime


class NameFormatConfigFieldParser(ConfigFieldParser):
    applies_to_field = ['NAME_FORMAT']

    @staticmethod
    def is_valid_format_string(expression):
        if not expression:
            return False

        try:
            namebuilder.assemble_basename(expression, **DATA_FIELDS)
        except (ValueError, TypeError, Exception):
            # TODO: Have NameBuilder raise a custom exception?
            return False
        else:
            return True

    def get_validation_function(self):
        return self.is_valid_format_string


def get_instantiated_field_parsers():
    """
    Get a list of all available field parsers as instantiated class objects.
    All classes inheriting from the "ConfigFieldParser" class are included.

    Returns:
        A list of class instances, one per subclass of "ConfigFieldParser".
    """
    return [p() for p in globals()['ConfigFieldParser'].__subclasses__()]


def available_field_parsers():
    """
    Get a list of all available field parsers, I.E. the names of all classes
    that inherit from "ConfigFieldParser".

    Returns:
        The names of available field parsers as strings.
    """
    return [klass.__name__ for klass in
            globals()['ConfigFieldParser'].__subclasses__()]

