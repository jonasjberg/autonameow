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
import os

from core import (
    config,
    constants,
    exceptions,
    util
)
from core.config.field_parsers import (
    NameFormatConfigFieldParser,
    DateTimeConfigFieldParser,
    FieldParsers
)
from core.util import (
    textutils
)


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
        self.weight = kwargs.get('weight', constants.FILERULE_DEFAULT_WEIGHT)
        self.name_template = kwargs.get('name_template')
        self.conditions = kwargs.get('conditions', False)
        self.data_sources = kwargs.get('data_sources', False)

        # Rules are sorted/prioritized by first the score, secondly the weight.
        self.score = 0

        # TODO: Implement "conditions" field ..
        # Possible a list of functions already "loaded" with the target value.
        # Also "loaded" with corresponding (reference to) a validation function.

    def __str__(self):
        return util.dump(self.__dict__)

    def __repr__(self):
        out = []
        for key in self.__dict__:
            out.append('{}="{}"'.format(key.title(), self.__dict__[key]))
        return 'FileRule({})'.format(', '.join(out))

    # TODO: Should 'FileRule' objects be re-created for each file?
    # TODO: Store score in a dictionary keyed by files?
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


class Configuration(object):
    """
    Container for a loaded and active configuration.

    Loads and validates data from a dictionary or YAML file.
    """
    def __init__(self, source):
        """
        Instantiates a new Configuration object.

        Loads a configuration from either a dictionary or file path.
        All parsing and loading happens at instantiation.

        Args:
            source: The configuration to load as either a dictionary or a
                bytestring path.
        """
        self._file_rules = []
        self._name_templates = {}
        self._options = {'DATETIME_FORMAT': {},
                         'FILETAGS_OPTIONS': {}}
        self._version = None

        if isinstance(source, dict):
            self._load_from_dict(source)
        else:
            self._load_from_disk(source)

        # TODO: Handle configuration file compatibility between versions.
        # TODO: Warn the user if 'self.version' != 'version.__version__'

    def _load_from_dict(self, data):
        self._data = data
        self._load_name_templates()
        self._load_file_rules()
        self._load_options()
        self._load_version()

    def _load_from_disk(self, load_path):
        try:
            _yaml_data = config.load_yaml_file(load_path)
        except (OSError, exceptions.ConfigReadError) as e:
            raise exceptions.ConfigError(e)
        else:
            if not _yaml_data:
                raise exceptions.ConfigError(
                    'Bad (empty?) config: {!s}'.format(load_path)
                )

            self._load_from_dict(_yaml_data)

    def write_to_disk(self, dest_path):
        if os.path.exists(dest_path):
            raise FileExistsError
        else:
            config.write_yaml_file(dest_path, self._data)

    def _load_name_templates(self):
        if not self._data:
            raise exceptions.ConfigError(
                'Invalid state; missing "self._data" ..'
            )

        if ('NAME_TEMPLATES' not in self._data or
                self._data['NAME_TEMPLATES'] is None):
            log.debug('Configuration does not contain any name templates')
            return

        loaded_templates = {}
        for k, v in self._data.get('NAME_TEMPLATES').items():
            # Remove any non-breaking spaces in the name template.
            v = textutils.remove_nonbreaking_spaces(v)

            if NameFormatConfigFieldParser.is_valid_format_string(v):
                loaded_templates[k] = v
            else:
                msg = 'invalid name template "{}": "{}"'.format(k, v)
                raise exceptions.ConfigurationSyntaxError(msg)

        self._name_templates.update(loaded_templates)

    def _load_file_rules(self):
        if not self._data:
            raise exceptions.ConfigError(
                'Invalid state; missing "self._data" ..'
            )

        if 'FILE_RULES' not in self._data or self._data['FILE_RULES'] is None:
            raise exceptions.ConfigError(
                'The configuration file does not contain any file rules'
            )

        # Check raw dictionary data.
        for fr in self._data['FILE_RULES']:
            try:
                valid_file_rule = self._validate_rule_data(fr)
            except exceptions.ConfigurationSyntaxError as e:
                fr_desc = fr.get('description', False)
                if not fr_desc:
                    fr_desc = 'UNDESCRIBED'
                log.error('File rule "{!s}" {!s}'.format(fr_desc, e))
            else:
                # Create and populate "FileRule" objects with *validated* data.
                self._file_rules.append(valid_file_rule)

    def _validate_rule_data(self, raw_rule):
        """
        Validates one "raw" file rule from a configuration and returns an
        instance of the 'FileRule' class, representing the "raw" file rule.

        Args:
            raw_rule: A single file rule entry from a confiugration.

        Returns:
            An instance of the 'FileRule' class representing the given rule.

        Raises:
            ConfigurationSyntaxError: The given file rule contains bad data,
                making instantiating a 'FileRule' object impossible.
                Note that the message will be used in the following sentence:
                "ERROR -- File Rule "x" {message}"
        """
        if 'NAME_FORMAT' not in raw_rule:
            log.debug('File rule contains no name format data' + str(raw_rule))
            raise exceptions.ConfigurationSyntaxError(
                'is missing name template format'
            )

        # First test if the field data is a valid name template entry,
        # If it is, use the format string defined in that entry.
        # If not, try to use 'name_template' as a format string.
        name_format = raw_rule.get('NAME_FORMAT')
        if name_format in self.name_templates:
            valid_format = self.name_templates.get(name_format, False)
        else:
            if NameFormatConfigFieldParser.is_valid_format_string(name_format):
                valid_format = name_format
            else:
                valid_format = False

        if not valid_format:
            log.debug('File rule name format is invalid: ' + str(raw_rule))
            raise exceptions.ConfigurationSyntaxError(
                'uses invalid name template format'
            )

        valid_conditions = parse_conditions(raw_rule.get('CONDITIONS'))
        valid_sources = parse_sources(raw_rule.get('DATA_SOURCES'))
        valid_weight = parse_weight(raw_rule.get('weight'))
        valid_exact_match = bool(raw_rule.get('exact_match'))
        valid_description = raw_rule.get('description', False)
        if not valid_description:
            valid_description = 'UNDESCRIBED'

        file_rule = FileRule(description=valid_description,
                             exact_match=valid_exact_match,
                             weight=valid_weight,
                             name_template=valid_format,
                             conditions=valid_conditions,
                             data_sources=valid_sources)
        return file_rule

    def _load_options(self):
        def _try_load_date_format_option(option):
            if 'DATETIME_FORMAT' in self._data:
                _value = self._data['DATETIME_FORMAT'].get(option)
            else:
                _value = False
            if _value and DateTimeConfigFieldParser.is_valid_datetime(_value):
                self._options['DATETIME_FORMAT'][option] = _value

        def _try_load_filetags_option(option, default):
            if 'FILETAGS_OPTIONS' in self._data:
                _value = self._data['FILETAGS_OPTIONS'].get(option)
            else:
                _value = False
            if _value:
                self._options['FILETAGS_OPTIONS'][option] = _value
            else:
                self._options['FILETAGS_OPTIONS'][option] = default

        _try_load_date_format_option('date')
        _try_load_date_format_option('time')
        _try_load_date_format_option('datetime')

        _try_load_filetags_option(
            'filename_tag_separator',
            constants.FILETAGS_DEFAULT_FILENAME_TAG_SEPARATOR
        )
        _try_load_filetags_option(
            'between_tag_separator',
            constants.FILETAGS_DEFAULT_BETWEEN_TAG_SEPARATOR
        )

    def _load_version(self):
        version = self._data.get('autonameow_version', False)
        if not version:
            log.error('Unable to read program version from configuration')
        else:
            self._version = version

    @property
    def version(self):
        """
        Returns: The program version that wrote the configuration.
        """
        return self._version

    @property
    def options(self):
        """
        Public interface for configuration options.
        Returns:
            Current and valid configuration options.
        """
        return self._options

    @property
    def data(self):
        """
        NOTE: Intended for debugging and testing!

        Returns:
            Raw configuration data as a dictionary.
        """
        return self._data

    @property
    def file_rules(self):
        if self._file_rules and len(self._file_rules) > 0:
            return self._file_rules
        else:
            return False

    @property
    def name_templates(self):
        return self._name_templates

    def __str__(self):
        out = ['Written by autonameow version v{}\n\n'.format(self.version)]

        for number, rule in enumerate(self.file_rules):
            out.append('File Rule {}:\n'.format(number + 1))
            out.append(textutils.indent(str(rule), amount=4) + '\n')

        out.append('\nName Templates:\n')
        out.append(textutils.indent(util.dump(self.name_templates), amount=4))

        out.append('\nMiscellaneous Options:\n')
        out.append(textutils.indent(util.dump(self.options), amount=4))

        return ''.join(out)


def parse_weight(value):
    """
    Validates data to be used as a "weight".

    The value must be an integer or float between 0 and 1.
    To allow for unspecified weights, None values are allowed and substituted
    with the default weight defined by "FILERULE_DEFAULT_WEIGHT".
    Args:
        value: The raw value to parse.

    Returns:
        The specified value if the value is a number type in the range 0-1.
        If the specified value is None, a default weight is returned.
    Raises:
        ConfigurationSyntaxError: The value is of an unexpected type or not
            within the range 0-1.
    """
    ERROR_MSG = 'Expected float in range 0-1. Got: "{}"'.format(value)

    if value is None:
        return constants.FILERULE_DEFAULT_WEIGHT
    if not isinstance(value, (int, float)):
        raise exceptions.ConfigurationSyntaxError(ERROR_MSG)

    try:
        w = float(value)
    except TypeError:
        raise exceptions.ConfigurationSyntaxError(ERROR_MSG)
    else:
        if float(0) <= w <= float(1):
            return w
        else:
            raise exceptions.ConfigurationSyntaxError(ERROR_MSG)


def parse_sources(raw_sources):
    passed = {}

    log.debug('Parsing {} raw sources ..'.format(len(raw_sources)))

    for field, value in raw_sources.items():
        if not value:
            log.debug('Skipped empty source specification: {}'.format(field))
            continue

        if not isinstance(value, list):
            value = [value]

        for v in value:
            if is_valid_source(v):
                log.debug('Validated source: [{}]: {}'.format(field, v))
                passed[field] = v
            else:
                log.debug('Invalid source: [{}]: {}'.format(field, v))

    log.debug('First filter passed {} sources'.format(len(passed)))

    return passed


def is_valid_source(source_value):
    """
    Check if the source is valid.

    Tests if the given source starts with the same text as any of the valid
    date sources defined in the 'VALID_DATA_SOURCES' list.

    For example, that the source value "metadata.exiftool.PDF:CreateDate" is
    considered valid because "metadata.exiftool" is listed as a valid source.

    NOTE:
        The field could still be invalid! The result query might fail!

    Args:
        source_value: The source to test as a text string.

    Returns:
        The given source value if it passes the test, otherwise False.
    """
    if not source_value or not source_value.strip():
        return False

    # TODO: Test if the field specified in the source is valid.

    if source_value.startswith(tuple(constants.VALID_DATA_SOURCES)):
        return source_value
    else:
        return False


def parse_conditions(raw_conditions):
    # TODO: This needs a lookover and probably at least a partial rewrite.
    out = {}

    log.debug('Parsing {} raw conditions ..'.format(len(raw_conditions)))

    def traverse_dict(the_dict):
        try:
            for key, value in the_dict.items():
                if isinstance(value, dict):
                    traverse_dict(value)

                valid_condition = validate_condition(key, value)
                if not valid_condition:
                    raise exceptions.ConfigurationSyntaxError(
                        'contains invalid condition [{}]: {}'.format(key, value)
                    )

                # TODO: Check if clobbering is an issue and how to fix.
                if key in out:
                    log.warning('Clobbering condition: {!s}'.format(key))
                out[key] = value
                log.debug('Validated condition: [{}]: {}'.format(key, value))
        except ValueError as e:
            raise exceptions.ConfigurationSyntaxError(
                'contains invalid condition: ' + str(e)
            )

    if 'contents' in raw_conditions:
        raw_contents = raw_conditions['contents']
        traverse_dict(raw_contents)

    if 'filesystem' in raw_conditions:
        raw_contents = raw_conditions['filesystem']
        traverse_dict(raw_contents)

    log.debug('First filter passed {} conditions'.format(len(out)))

    return out


def validate_condition(condition_field, condition_value):
    """
    Validates a file rule condition.

    The "condition_field" must be assigned to a field parser. This parser
    validates the "condition_value". If this validation returns True,
    the condition is valid.

    Args:
        condition_field: Field (key/name) to validate, for example: "mime_type".
        condition_value: Value to validate, for example: "image/jpeg".

    Returns:
        True if the given "condition_field" can be handled by one of the
        field parser classes _AND_ the subsequent validation of the given
        "condition_value" returns True.  Else False.
    """
    if not condition_value:
        return False

    for parser in FieldParsers:
        if condition_field in parser.applies_to_field:
            if parser.validate(condition_value):
                return condition_value
            else:
                return False
