# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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
import re
from datetime import datetime

from core import exceptions
from core import namebuilder
from core.model import genericfields as gf
from core.namebuilder.fields import NAMETEMPLATEFIELD_PLACEHOLDER_STRINGS
from util import coercers
from util import encoding as enc
from util import mimemagic
from util import sanity


log = logging.getLogger(__name__)


# TODO: [TD0154] Add "incrementing counter" placeholder field


class ConfigFieldParser(object):
    """
    Top-level superclass for all configuration field parsers.

    Provides common functionality and interfaces that must be implemented
    by inheriting parser classes.

    The field parser classes each handle different types of "keys" in the
    "key-value pairs" that make up configuration entries.
    The "key" is a "MeowURI" that represent a location or provider of some data.
    The "value" is some kind of expression.

    The "MeowURI" (key) determines which parser class is to be used by
    matching the "MeowURI" against class variables 'APPLIES_TO_MEOWURIS'.
    This is handled with the 'eval_meowuri_glob' function, which supports
    "globs"/wildcards. Parser classes whose 'APPLIES_TO_MEOWURIS' attribute
    evaluates True for a given "MeowURI" is used to parse the associated value.

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

    # List of "MeowURIs" (or configuration "keys"/"fields") used to
    # determine if the class is suited to handle the expression or data.
    #
    # The "MeowURI" consist of a lower case words, separated by periods.
    # The "MeowURI" can contain "globs" as wildcards. Globs substitute
    # any of the lower case words with an asterisk, effectively ignoring that
    # part during comparison.
    #
    # Example:  ['filesystem.basename.*', 'filesystem.*.extension]
    APPLIES_TO_MEOWURIS = list()

    # Whether to allow multiple expressions or not.
    ALLOW_MULTIVALUED_EXPRESSION = None

    def __init__(self):
        # TODO: [TD0177] Refactor the 'ConfigFieldParser' classes.
        self.init()

    def init(self):
        # Possibly implemented by inheriting classes.
        pass

    @classmethod
    def get_validation_function(cls):
        """
        Used to check the syntax of a configuration field expression.

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
        # TODO: [cleanup] THIS IS SUCH A MESS! Decouple parsing from evaluation!
        validation_func = self.get_validation_function()
        if not self.ALLOW_MULTIVALUED_EXPRESSION:
            if isinstance(expression, list):
                # Instant fail for unexpectedly "multivalued" expression.
                return False

            return validation_func(expression)

        # Multivalued expressions ARE allowed, turn all expressions into lists.
        expressions = expression
        if not isinstance(expressions, list):
            expressions = [expressions]

        # All expressions must pass validation.
        for expr in expressions:
            if not validation_func(expr):
                return False

        return True

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
        # TODO: [cleanup] THIS IS SUCH A MESS! Decouple parsing from evaluation!
        # TODO: [TD0015] Handle expression in 'condition_value'
        #                ('Defined', '> 2017', etc)
        evaluation_func = self.get_evaluation_function()
        if self.ALLOW_MULTIVALUED_EXPRESSION is True:
            if not isinstance(expression, list):
                expression = [expression]

            # Only one expression need evaluate true.
            for expr in expression:
                if evaluation_func(expr, data):
                    return True
            return False
        else:
            if isinstance(expression, list):
                log.error('Unexpected "multi-valued" expression: "%s"', expression)
                return False
            return evaluation_func(expression, data)

    def __str__(self):
        return self.__class__.__name__


class BooleanConfigFieldParser(ConfigFieldParser):
    # TODO: [TD0177] Refactor the 'ConfigFieldParser' classes.
    APPLIES_TO_MEOWURIS = ['*.filetags.follows_filetags_convention']
    ALLOW_MULTIVALUED_EXPRESSION = False

    @staticmethod
    def is_valid_boolean(expression):
        try:
            coercers.AW_BOOLEAN(expression)
        except coercers.AWTypeError:
            return False
        else:
            return True

    @staticmethod
    def evaluate_boolean_operation(expression, test_data):
        try:
            a = coercers.AW_BOOLEAN(expression)
            b = coercers.AW_BOOLEAN(test_data)
        except coercers.AWTypeError:
            # TODO: [TD0149] Make sure this case is handled properly.
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
    # TODO: [TD0177] Refactor the 'ConfigFieldParser' classes.
    # NOTE: Globs does not include all possible extractor globs.
    APPLIES_TO_MEOWURIS = [
        '*.EXIF:Model', '*.QuickTime:Model',
        '*.ICC_Profile:DeviceManufacturer',
        '*.ICC_Profile:ProfileCreator',
        '*.XMP-dc:Creator', '*.XMP-dc:Producer', '*.XMP-dc:Publisher',
        '*.XMP-dc:Title', '*.PDF:Creator', '*.PDF:Producer', '*.PDF:Publisher',
        '*.XMP:UserComment',
        '*.PDF:Title' '*.pathname.*', '*.basename.*', '*.extension',
        '*.abspath_full',
        '*.basename_full',
        '*.basename_prefix',
        '*.basename_suffix',
        '*.pathname_full',
        '*.pathname_parent',
        '*.text.*', '*.text'
    ]
    # Add MeowURIs from "generic" fields.
    APPLIES_TO_MEOWURIS.extend([
        field.uri() for field in gf.get_string_fields()
    ])
    ALLOW_MULTIVALUED_EXPRESSION = True

    @staticmethod
    def is_valid_regex(expression):
        if not expression:
            return False

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

        test_data = enc.encode_(test_data)
        expression = enc.encode_(expression)

        match = re.match(expression, test_data)
        return match if match else False

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


class MimeTypeConfigFieldParser(ConfigFieldParser):
    # TODO: [TD0177] Refactor the 'ConfigFieldParser' classes.
    APPLIES_TO_MEOWURIS = ['*.mime_type', gf.GenericMimeType.uri()]
    ALLOW_MULTIVALUED_EXPRESSION = True

    @staticmethod
    def is_valid_mime_type(expression):
        if not expression:
            return False

        str_expression = coercers.force_string(expression)
        if not str_expression:
            return False

        try:
            # Match with or without globs; 'inode/x-empty', '*/jpeg', 'image/*'
            if re.match(r'^([a-z]+|\*)/([a-z0-9\-.+]+|\*)$', str_expression):
                return True
        except TypeError:
            pass
        return False

    @staticmethod
    def evaluate_mime_type_globs(expression, mime_to_match):
        if not expression:
            return False

        try:
            evaluates_true = mimemagic.eval_glob(mime_to_match, expression)
        except (TypeError, ValueError) as e:
            log.error('Error evaluating expression "%s"; %s', expression, e)
            return False
        return evaluates_true

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
    # TODO: [TD0177] Refactor the 'ConfigFieldParser' classes.
    # NOTE: Globs does not include all possible extractor globs.
    APPLIES_TO_MEOWURIS = [
        '*.PDF:CreateDate', '*.PDF:ModifyDate', '*.EXIF:DateTimeOriginal',
        '*.EXIF:ModifyDate'
    ]
    # Add MeowURIs from "generic" fields.
    APPLIES_TO_MEOWURIS.extend([
        field.uri() for field in gf.get_datetime_fields()
    ])
    ALLOW_MULTIVALUED_EXPRESSION = True

    @staticmethod
    def is_valid_datetime(expression):
        if not expression:
            return False

        try:
            _ = datetime.today().strftime(expression)
        except (ValueError, TypeError) as e:
            log.debug('Bad datetime expression: "%s"', expression)
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
        return lambda *_: False


# Used for validating name templates. Populated like so;
#   NAMETEMPLATEFIELDS_DUMMYDATA = {
#       'author': 'DUMMY',
#        .. additional placeholders, dynamically generated in 'fields.py' ..
#       'year': 'DUMMY'
#   }
NAMETEMPLATEFIELDS_DUMMYDATA = dict.fromkeys(
    NAMETEMPLATEFIELD_PLACEHOLDER_STRINGS, 'DUMMY'
)


class NameTemplateConfigFieldParser(ConfigFieldParser):
    # TODO: [TD0177] Refactor the 'ConfigFieldParser' classes.
    APPLIES_TO_MEOWURIS = list()
    ALLOW_MULTIVALUED_EXPRESSION = False

    @staticmethod
    def is_valid_nametemplate_string(expression):
        if not expression:
            return False

        try:
            namebuilder.populate_name_template(expression,
                                               **NAMETEMPLATEFIELDS_DUMMYDATA)
        except (exceptions.NameTemplateSyntaxError, TypeError):
            return False
        else:
            return True

    @classmethod
    def get_validation_function(cls):
        return cls.is_valid_nametemplate_string

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


def suitable_field_parser_for(meowuri):
    """
    Returns field parser instances that can handle the given "MeowURI".

    Args:
        meowuri: Resource identifier to match against a RuleParser class,
                 as an instance of 'MeowURI'.

    Returns:
        A list of instantiated field parsers suited for the given "MeowURI".
    """
    log.debug('suitable_field_parser_for("%s")', meowuri)
    sanity.check_isinstance_meowuri(meowuri)

    candidates = [p for p in FieldParserInstances
                  if meowuri.matchglobs(p.APPLIES_TO_MEOWURIS)]
    if not candidates:
        return None

    # NOTE(jonas): Assume only one parser per "MeowURI" for now ..
    assert len(candidates) == 1, (
        'Unexpectedly got {} parsers for MeowURI '
        '"{!s}"'.format(len(candidates), meowuri)
    )
    return candidates[0]


# Instantiate rule parsers inheriting from the 'Parser' class.
FieldParserInstances = get_instantiated_field_parsers()
