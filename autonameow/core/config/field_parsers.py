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

import logging
import re
import unicodedata
from datetime import datetime

from core import (
    constants,
    exceptions,
    namebuilder,
    types,
    util,
)


log = logging.getLogger(__name__)


class ConfigFieldParser(object):
    """
    Top-level superclass for all configuration field parsers.

    Provides common functionality and interfaces that must be implemented
    by inheriting parser classes.

    The field parser classes each handle different types of "keys" in the
    "key-value pairs" that make up configuration entries.
    The "key" is a "meowURI" that represent a location or provider of some data.
    The "value" is some kind of expression.

    The "meowURI" (key) determines which parser class is to be used by
    matching the "meowURI" against class variables 'applies_to_field'.
    This is handled with the 'eval_meowuri_glob' function, which supports
    "globs"/wildcards. Parser classes whose 'applies_to_field' attribute
    evaluates True for a given "meowURI" is used to parse the associated value.

    * The 'validate' methods
      The 'Configuration' class uses the field parser classes primarily for
      validating the configuration file. This uses the 'validate' methods,
      which accepts an expression and returns either True or False.

    * The 'evaluate' methods
      The 'evaluate' method is very similar, but accepts both an expression
      and some data and returns False if the evaluation of "expression" on
      "data" was unsuccessful. Otherwise, some "truthy" value is returned.
      For example, the 'RegexConfigFieldParser' would return the matched part.
    """

    # List of "meowURIs" (or configuration "keys"/"fields") used to
    # determine if the class is suited to handle the expression or data.
    #
    # The "meowURI" consist of a lower case words, separated by periods.
    # For instance; "contents.mime_type" or "filesystem.basename.extension".
    # The "meowURI" can contain "globs" as wildcards. Globs substitute
    # any of the lower case words with an asterisk, effectively ignoring that
    # part during comparison.
    #
    # Example:  ['filesystem.basename.*', 'filesystem.*.extension]
    applies_to_field = []

    def __init__(self):
        self.init()

    def init(self):
        # Possibly implemented by inheriting classes.
        pass

    @classmethod
    def get_validation_function(cls):
        """
        Used to check that the syntax of a configuration field expression.

        Returns:
            A class-specific function for validating a configuration field.
            The returned function accepts a single 'expression' argument.
            The function returns True if the field is valid, otherwise False.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def get_evaluation_function(cls):
        """
        Returns a function that evaluates a given expression using some
        given data. The function takes two arguments; 'expression' and 'data'.

        Returns:
            A function that evaluates an "expression" using some "data".
            The function returns False if the evaluation is unsuccessful.
            If the evaluation is successful, some "truthy" value is returned.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def validate(self, expression):
        """
        Validates a given expression. To be called through classes inheriting
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
        Evaluates a given 'expression' using the given 'data' by passing the
        arguments to the function returned by 'get_evaluation_function'.

        Args:
            expression: The expression to evaluate.
            data: The data to use during the evaluation.

        Returns:
            False if the evaluation was unsuccessful. Otherwise, the return
            type is some "truthy" value whose type depends on the field parser.
        """
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        return self.get_evaluation_function()(expression, data)

    def __str__(self):
        return self.__class__.__name__


class BooleanConfigFieldParser(ConfigFieldParser):
    applies_to_field = ['*.filetags.follows_filetags_convention']

    @staticmethod
    def is_valid_boolean(expression):
        try:
            types.AW_BOOLEAN(expression)
        except types.AWTypeError:
            return False
        else:
            return True

    @staticmethod
    def evaluate_boolean_operation(expression, test_data):
        try:
            a = types.AW_BOOLEAN(expression)
            b = types.AW_BOOLEAN(test_data)
        except types.AWTypeError:
            # TODO: Handle this case
            raise
        else:
            return a == b

    @classmethod
    def get_validation_function(cls):
        return cls.is_valid_boolean

    @classmethod
    def get_evaluation_function(cls):
        return cls.evaluate_boolean_operation


class RegexConfigFieldParser(ConfigFieldParser):
    applies_to_field = ['*.pathname.*', '*.basename.*', '*.text.*',
                        '*.:Title', '*.:Creator', '*.:Publisher',
                        '*.:Producer']

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

        # test_data = _normalize(test_data)
        test_data = util.encode_(test_data)
        expression = util.encode_(expression)

        # log.debug('test_data: "{!s}" ({})"'.format(test_data,
        #                                            type(test_data)))
        # log.debug('expression: "{!s}" ({})"'.format(expression,
        #                                            type(expression)))
        _match = re.match(expression, test_data)
        if _match:
            return _match
        else:
            return False

    @classmethod
    def get_validation_function(cls):
        return cls.is_valid_regex

    @classmethod
    def get_evaluation_function(cls):
        """
        Returns: A function that in turn returns False or the matched data.
        """
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        return cls.evaluate_regex

    @staticmethod
    def _normalize(unicode_string):
        """
        Normalizes unwieldy text, (hopefully) making matching more intuitive.

            Return the normal form form for the Unicode string unistr.

            For each character, there are two normal forms: normal form C and
            normal form D. Normal form D (NFD) is also known as canonical
            decomposition, and translates each character into its decomposed
            form. Normal form C (NFC) first applies a canonical decomposition,
            then composes pre-combined characters again.

            Source:  https://docs.python.org/3.5/library/unicodedata.html

        Args:
            unicode_string: The unicode string to normalize.

        Returns:
            A normalized version of the given string.
        """
        return unicodedata.normalize('NFC', unicode_string)


class MimeTypeConfigFieldParser(ConfigFieldParser):
    applies_to_field = ['*.mime_type']

    @staticmethod
    def is_valid_mime_type(expression):
        if not expression:
            return False

        if not isinstance(expression, list):
            expression = [expression]

        for expr in expression:
            if not expr or not isinstance(expr, (str, bytes)):
                return False

            # Match with or without globs; 'inode/x-empty', '*/jpeg', 'image/*'
            if not re.match(r'^([a-z]+|\*)/([a-z0-9\-+]+|\*)$', expr):
                return False

        return True

    @staticmethod
    def evaluate_mime_type_globs(expression, mime_to_match):
        if not isinstance(expression, list):
            expression = [expression]

        # True is returned if any of the given expressions evaluates true.
        for expr in expression:
            try:
                evaluates_true = util.eval_magic_glob(mime_to_match, expr)
            except (TypeError, ValueError) as e:
                log.error(
                    'Error evaluating expression "{!s}"; {!s}'.format(expr, e)
                )
                continue
            if evaluates_true:
                return True
        return False

    @classmethod
    def get_validation_function(cls):
        return cls.is_valid_mime_type

    @classmethod
    def get_evaluation_function(cls):
        """
        Returns: A function that in turn returns either True or False.
        """
        return cls.evaluate_mime_type_globs


class DateTimeConfigFieldParser(ConfigFieldParser):
    applies_to_field = ['datetime', 'date_accessed', 'date_created',
                        'date_modified', '*.PDF:CreateDate', '*.PDF:ModifyDate',
                        '*.EXIF:DateTimeOriginal', '*.EXIF:ModifyDate']

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

    @classmethod
    def get_validation_function(cls):
        return cls.is_valid_datetime

    @classmethod
    def get_evaluation_function(cls):
        # TODO: Implement this!
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        return lambda *_: True


class NameFormatConfigFieldParser(ConfigFieldParser):
    applies_to_field = ['NAME_FORMAT']

    @staticmethod
    def is_valid_format_string(expression):
        if not expression:
            return False

        try:
            namebuilder.populate_name_template(expression, **DATA_FIELDS)
        except exceptions.NameTemplateSyntaxError:
            return False
        else:
            return True

    @classmethod
    def get_validation_function(cls):
        return cls.is_valid_format_string

    @classmethod
    def get_evaluation_function(cls):
        # TODO: Implement this!
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        return lambda *_: True


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
    Get a list of all available field parser classes, I.E. all classes
    that inherit from the 'ConfigFieldParser' class.

    Returns:
        A list of all field parser classes.
    """
    return [klass for klass in
            globals()['ConfigFieldParser'].__subclasses__()]


def suitable_field_parser_for(meowuri):
    """
    Returns field parser instances that can handle the given "meowURI".

    The "meowURI" can be a "glob", I.E. contain wildcards.

    Args:
        meowuri: Resource identifier to match against a RuleParser class.

    Returns:
        A list of instantiated field parsers suited for the given "meowURI".
    """
    return [p for p in FieldParserInstances
            if eval_meowuri_glob(meowuri, p.applies_to_field)]


def eval_meowuri_glob(meowuri, glob_list):
    """
    Evaluates a given "meowURI" against a list of "globs".

    The "meowURI" matching any of the given globs evaluates true.

    The "meowURI" consist of a lower case words, separated by periods.
    For instance; "contents.mime_type" or "filesystem.basename.extension".

    Globs substitute any of the lower case words with an asterisk,
    which means that part is ignored during the comparison. Examples:

        meowuri                     glob_list                   evaluates
        'contents.mime_type'        ['contents.mime_type']      True
        'contents.foo'              ['foo.*', 'contents.*']     True
        'foo.bar'                   ['*.*']                     True
        'filesystem.basename.full'  ['contents.*', '*.parent']  False

    Args:
        meowuri: The "meowURI" to match as a Unicode string.
        glob_list: A list of globs as strings.

    Returns:
        True if the given "meowURI" matches any of the specified globs.
    """
    if not meowuri or not glob_list:
        return False

    if not isinstance(glob_list, list):
        glob_list = [glob_list]

    if meowuri in glob_list:
        return True

    # Split the "meowURI" by periods to a list of strings.
    meowuri_parts = util.meowuri_list(meowuri)

    for glob in glob_list:
        glob_parts = glob.split('.')

        # All wildcards match anything.
        if len([gp for gp in glob_parts if gp == '*']) == len(glob_parts):
            return True

        # No wildcards, do direct comparison.
        if '*' not in glob_parts:
            if glob_parts == meowuri_parts:
                return True
            else:
                continue

        if glob.startswith('*.') and glob.endswith('.*'):
            # Check if the center piece is a match.
            literal_glob_parts = [g for g in glob_parts if g != '*']
            for literal_glob_part in literal_glob_parts:
                # Put back periods to match whole parts and not substrings.
                glob_center_part = '.{}.'.format(literal_glob_part)
                if glob_center_part in meowuri:
                    return True

        # First part doesn't matter, check if trailing pieces match.
        if glob.startswith('*.'):
            stripped_glob = re.sub(r'^\*', '', glob)
            if meowuri.endswith(stripped_glob):
                return True

        # Last part doesn't matter, check if leading pieces match.
        if glob.endswith('.*'):
            stripped_glob = re.sub(r'\*$', '', glob)
            if meowuri.startswith(stripped_glob):
                return True

    return False


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
FieldParserInstances = get_instantiated_field_parsers()

# This is used for validating name templates. Dict is populated like this;
#   DATA_FIELDS = {'author': 'DUMMY', ... , 'year': 'DUMMY'}
DATA_FIELDS = dict.fromkeys(constants.NAME_TEMPLATE_FIELDS, 'DUMMY')
RE_VERSION_NUMBER = re.compile(r'v?(\d+)\.(\d+)\.(\d+)')


def parse_versioning(semver_string):
    """
    Validates a "raw" version number string.

    The version number is expected to be a Unicode string on the form 'v1.2.3',
    where the initial 'v' is optional;  I.E. '111.222.333' is also valid.

    Args:
        semver_string: The version number to validate as a Unicode string.

    Returns:
        A tuple of three integers representing the "major", "minor" and
        "patch" version numbers.  Or None if the validation fails.
    """
    if not semver_string or not isinstance(semver_string, str):
        return None
    if not semver_string.strip():
        return None

    match = RE_VERSION_NUMBER.search(semver_string)
    if match:
        try:
            major = int(match.group(1))
            minor = int(match.group(2))
            patch = int(match.group(3))
        except TypeError:
            pass
        else:
            return major, minor, patch

    return None
