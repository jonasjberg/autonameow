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
import re
from datetime import datetime

from core import (
    constants,
    extraction,
    util,
    fileobject
)
from core.constants import NAME_TEMPLATE_FIELDS
from core.evaluate import namebuilder
from core.exceptions import NameTemplateSyntaxError


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

    def get_evaluation_function(self):
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

    def evaluate(self, expression, data):
        """
        Evaluates a given expression using the specified data.

        Args:
            expression:
            data:

        Returns:
        """
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        return self.get_evaluation_function()(expression, data)

    def __str__(self):
        return self.__class__.__name__


class RegexConfigFieldParser(ConfigFieldParser):
    applies_to_field = ['*.pathname.*', '*.basename.*', '*.raw_text']

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
        if not test_data:
            return False

        test_data = util.encode_(test_data)
        _match = re.match(expression, test_data)
        if _match:
            return _match
        else:
            return False

    def get_validation_function(self):
        return self.is_valid_regex

    def get_evaluation_function(self):
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        return self.evaluate_regex


class MimeTypeConfigFieldParser(ConfigFieldParser):
    applies_to_field = ['contents.mime_type']

    @staticmethod
    def is_valid_mime_type(expression):
        if not expression:
            return False

        # Match with or without globs; 'inode/x-empty', '*/jpeg', 'image/*'
        if re.match(r'^([a-z]+|\*)/([a-z0-9\-+]+|\*)$', expression):
            return True

        return False

    def get_validation_function(self):
        return self.is_valid_mime_type

    def get_evaluation_function(self):
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        return fileobject.eval_magic_glob


class DateTimeConfigFieldParser(ConfigFieldParser):
    applies_to_field = ['datetime', 'date_accessed', 'date_created',
                        'date_modified', '*.DateTimeOriginal']

    @staticmethod
    def is_valid_datetime(expression):
        try:
            _ = datetime.today().strftime(expression)
        except (ValueError, TypeError) as e:
            log.debug('Bad datetime expression: "{!s}"'.format(expression))
            log.debug(str(e))
            return False
        else:
            return True

    def get_validation_function(self):
        return self.is_valid_datetime

    def get_evaluation_function(self):
        # TODO: Implement this!
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        pass


class NameFormatConfigFieldParser(ConfigFieldParser):
    applies_to_field = ['NAME_FORMAT']

    @staticmethod
    def is_valid_format_string(expression):
        if not expression:
            return False

        try:
            namebuilder.assemble_basename(expression, **DATA_FIELDS)
        except NameTemplateSyntaxError:
            return False
        else:
            return True

    def get_validation_function(self):
        return self.is_valid_format_string

    def get_evaluation_function(self):
        # TODO: Implement this!
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        pass


class MetadataSourceConfigFieldParser(ConfigFieldParser):
    applies_to_field = ['metadata.*']

    @staticmethod
    def is_valid_metadata_source(expression):
        if not expression or not isinstance(expression, str):
            return False

        # TODO: [TD0001] Implement proper (?) validation of metadata source!
        query_strings = list(extraction.MetadataExtractorQueryStrings)
        query_strings = [qs.replace('metadata.', '') for qs in query_strings]

        if expression.startswith(tuple(query_strings)):
            return True

        return False

    def get_validation_function(self):
        return self.is_valid_metadata_source

    def get_evaluation_function(self):
        # TODO: Implement this!
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        pass


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


def suitable_field_parser_for(query_string):
    """
    Returns instances of field parser classes that can handle the given query.

    The "query string" can be a "glob", I.E. contain wildcards.

    Args:
        query_string: Query string to match against a RuleParser class.

    Returns:
        A list of instantiated field parsers suited for the given query string.
    """
    # TODO: [TD0046] Improve determining FieldParser suitability.
    return [p for p in FieldParsers
            if eval_query_string_glob(query_string, p.applies_to_field)]


def eval_query_string_glob(query_string, glob_list):
    """
    Evaluates a given "query string" against a list of "globs".

    The "query string" matching any of the given globs evaluates true.

    The "query string" consist of a lower case words, separated by periods.
    For instance; "contents.mime_type" or "filesystem.basename.extension".

    Globs substitute any of the lower case words with an asterisk,
    which means that part is ignored during the comparison. Examples:

        match_query_string          glob_list                   evaluates
        'contents.mime_type'        ['contents.mime_type']      True
        'contents.foo'              ['contents.*']              True
        'foo.bar'                   ['*.*']                     True
        'filesystem.basename.full'  ['filesystem.*', '*.full']  False

    Args:
        query_string: The "query string" to match as a string.
        glob_list: A list of globs as strings.

    Returns:
        True if the given "query string" matches any of the specified globs.
    """
    if not query_string or not glob_list:
        return False

    if query_string in glob_list:
        return True

    for glob in glob_list:
        glob_parts = glob.split('.')
        # All wildcards match anything.
        if all(gp == '*' for gp in glob_parts):
            return True

        # No wildcards, do direct comparison.
        if '*' not in glob_parts:
            query_string_parts = util.query_string_list(query_string)
            if glob_parts == query_string_parts:
                return True
            else:
                continue

        # Convert to regular expression to match wildcards. Simplest solution.
        re_glob = re.compile(glob.replace('*', '.*'))
        if re_glob.match(query_string):
            return True

    return False


def suitable_parser_for_querystr(query_string):
    """
    Returns instances of field parser classes that can handle the given
    query string.

    Args:
        query_string: The field to validate. Examples;
            'metadata.exiftool.EXIF:DateTimeOriginal', 'contents.mime_type'

    Returns:
        A list of instantiated parsers that can handle the given query string.
    """
    # TODO: [TD0015] Allow conditionals in the configuration file rules.

    # TODO: [TD0001] Handle complex cases properly!
    # Handle case where the last component is a field defined by an external
    # source (extractor/analyzer). A typical example is 'exiftool'; the
    # incoming query string 'metadata.exiftool.EXIF:DateTimeOriginal' will
    # result in the 'last_component' being 'EXIF:DateTimeOriginal'.
    # Considering the many possible fields returned by extractors such as
    # exiftool, it does not seem practical to validate by comparing against
    # hard coded values.. Need a better method that is tolerant to changes.

    # Get the last part of the field; 'mime_type' for 'contents.mime_type'.
    field_components = util.query_string_list(query_string)
    # last_component = field_components[-1:][0]

    return suitable_field_parser_for(field_components)


def is_valid_template_field(template_field):
    """
    Checks whether the given string is a legal name template placeholder field.

    Args:
        template_field: The field to test as type str.

    Returns:
        True if the given string is a legal name template field, else False.
    """
    if not template_field:
        return False
    if template_field in constants.NAME_TEMPLATE_FIELDS:
        return True
    return False


# Instantiate rule parsers inheriting from the 'Parser' class.
FieldParsers = get_instantiated_field_parsers()

# This is used for validating name templates. Dict is populated like this;
#   DATA_FIELDS = {'author': 'DUMMY', ... , 'year': 'DUMMY'}
DATA_FIELDS = dict.fromkeys(NAME_TEMPLATE_FIELDS, 'DUMMY')
