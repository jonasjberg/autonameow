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
import os

from core import (
    config,
    constants,
    exceptions,
    util
)
from core.config import (
    rules
)
from core.config.field_parsers import (
    DateTimeConfigFieldParser,
    NameFormatConfigFieldParser,
    parse_versioning
)


log = logging.getLogger(__name__)


class Configuration(object):
    """
    Container for a loaded and active configuration.

    Loads and validates data from a dictionary or YAML file.
    """
    def __init__(self, source):
        """
        Instantiates a new Configuration object.

        Loads configuration from a dictionary.
        All parsing and loading happens at instantiation.

        Args:
            source: Configuration data to load as a dict.
        """
        self._rules = []
        self._name_templates = {}
        self._options = {'DATETIME_FORMAT': {},
                         'FILETAGS_OPTIONS': {}}
        self._version = None
        self.referenced_meowuris = set()

        if not isinstance(source, dict):
            raise TypeError('Expected Configuration source to be type dict')

        self._load_from_dict(source)

        if self.version:
            if self.version != constants.PROGRAM_VERSION:
                log.warning('Possible configuration compatibility mismatch!')
                log.warning('Loaded configuration created by {} (currently '
                            'running {})'.format(self.version,
                                                 constants.PROGRAM_VERSION))
                log.info(
                    'The current recommended procedure is to move the '
                    'current config to a temporary location, re-run '
                    'the program so that a new template config file is '
                    'generated and then manually transfer rules to this file.'
                )

    @classmethod
    def from_file(cls, path):
        """
        Returns a new Configuration instantiated from data at a given path.

        Args:
            path: Path of the (YAML) file to read, as an "internal" bytestring.

        Returns:
            An instance of 'Configuration', created from the data at "path".

        Raises:
            EncodingBoundaryViolation: Argument "path" is not a bytestring.
            ConfigReadError: The configuration file could not be read.
            ConfigError: The configuration file is empty.
        """
        util.assert_internal_bytestring(path)

        _loaded_data = config.load_yaml_file(path)
        if not _loaded_data:
            raise exceptions.ConfigError(
                'Read empty config: "{!s}"'.format(util.displayable_path(path))
            )

        return cls(_loaded_data)

    def _load_from_dict(self, data):
        if not data:
            raise exceptions.ConfigError('Attempted to load empty data')

        self._data = data
        self._load_name_templates()
        self._load_rules()
        self._load_options()
        self._load_version()

        # For Debugging/development only.
        _referenced_meowuris = sorted(self.referenced_meowuris)
        for _meowuri in _referenced_meowuris:
            log.debug('Configuration Rule referenced meowURI'
                      ' "{!s}"'.format(_meowuri))

    def write_to_disk(self, dest_path):
        # TODO: This method is currently unused. Remove?
        if os.path.exists(dest_path):
            raise FileExistsError
        else:
            config.write_yaml_file(dest_path, self._data)

    def _load_name_templates(self):
        raw_templates = self._data.get('NAME_TEMPLATES')
        if not raw_templates:
            log.debug('Configuration does not contain any name templates')
            return
        if not isinstance(raw_templates, dict):
            log.debug('Configuration templates is not of type dict')
            return

        loaded_templates = {}
        for k, v in raw_templates.items():
            # Remove any non-breaking spaces in the name template.
            v = util.remove_nonbreaking_spaces(v)

            if NameFormatConfigFieldParser.is_valid_format_string(v):
                loaded_templates[k] = v
            else:
                msg = 'invalid name template "{}": "{}"'.format(k, v)
                raise exceptions.ConfigurationSyntaxError(msg)

        self._name_templates.update(loaded_templates)

    def _load_rules(self):
        raw_rules = self._data.get('RULES')
        if not raw_rules:
            raise exceptions.ConfigError(
                'The configuration file does not contain any rules'
            )

        for rule in raw_rules:
            try:
                valid_rule = self._validate_rule_data(rule)
            except exceptions.ConfigurationSyntaxError as e:
                rule_description = rule.get('description', 'UNDESCRIBED')
                log.error('Bad rule "{!s}"; {!s}'.format(rule_description, e))
            else:
                # Create and populate "Rule" objects with *validated* data.
                self._rules.append(valid_rule)

                # Keep track of all "meowURIs" referenced by rules.
                self.referenced_meowuris.update(
                    valid_rule.referenced_meowuris()
                )

    def _validate_rule_data(self, raw_rule):
        """
        Validates one "raw" rule from a configuration and returns an
        instance of the 'Rule' class, representing the "raw" rule.

        Args:
            raw_rule: A single rule entry from a configuration.

        Returns:
            An instance of the 'Rule' class representing the given rule.

        Raises:
            ConfigurationSyntaxError: The given rule contains bad data,
                making instantiating a 'Rule' object impossible.
                Note that the message will be used in the following sentence:
                "Bad rule "x"; {message}"
        """
        # Get a description for referring to the rule in any log messages.
        description = raw_rule.get('description')
        if description is None:
            description = 'UNDESCRIBED'

        log.debug('Validating rule "{!s}" ..'.format(description))

        if 'NAME_FORMAT' not in raw_rule:
            log.debug('Rule contains no name format data' + str(raw_rule))
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
                valid_format = util.remove_nonbreaking_spaces(name_format)
            else:
                valid_format = False

        if not valid_format:
            log.debug('Rule name format is invalid: ' + str(raw_rule))
            raise exceptions.ConfigurationSyntaxError(
                'uses invalid name template format'
            )

        try:
            _rule = rules.Rule(description=description,
                               exact_match=raw_rule.get('exact_match'),
                               ranking_bias=raw_rule.get('ranking_bias'),
                               name_template=valid_format,
                               conditions=raw_rule.get('CONDITIONS'),
                               data_sources=raw_rule.get('DATA_SOURCES'))
        except exceptions.InvalidRuleError as e:
            raise exceptions.ConfigurationSyntaxError(e)

        log.debug('Validated rule "{!s}" .. OK!'.format(description))
        return _rule

    def _load_options(self):
        def _try_load_datetime_format_option(option, default):
            if 'DATETIME_FORMAT' in self._data:
                _value = self._data['DATETIME_FORMAT'].get(option, None)
                if (_value is not None and
                        DateTimeConfigFieldParser.is_valid_datetime(_value)):
                    self._options['DATETIME_FORMAT'][option] = _value
                    return  # OK!

            # Use verified default value.
            if DateTimeConfigFieldParser.is_valid_datetime(default):
                self._options['DATETIME_FORMAT'][option] = default
            else:
                log.critical('Invalid internal default value "{!s}": '
                             '"{!s}'.format(option, default))
                log.critical('This should not happen!')

        def _try_load_filetags_option(option, default):
            if 'FILETAGS_OPTIONS' in self._data:
                _value = self._data['FILETAGS_OPTIONS'].get(option)
            else:
                _value = None
            if _value is not None:
                self._options['FILETAGS_OPTIONS'][option] = _value
            else:
                self._options['FILETAGS_OPTIONS'][option] = default

        def _try_load_filesystem_option(option, default):
            if 'FILESYSTEM_OPTIONS' in self._data:
                _value = self._data['FILESYSTEM_OPTIONS'].get(option)
            else:
                _value = None
            if _value is not None:
                util.nested_dict_set(
                    self._options, ['FILESYSTEM_OPTIONS', option], _value
                )
            else:
                util.nested_dict_set(
                    self._options, ['FILESYSTEM_OPTIONS', option], default
                )

        _try_load_datetime_format_option(
            'date', constants.DEFAULT_DATETIME_FORMAT_DATE
        )
        _try_load_datetime_format_option(
            'time', constants.DEFAULT_DATETIME_FORMAT_TIME
        )
        _try_load_datetime_format_option(
            'datetime', constants.DEFAULT_DATETIME_FORMAT_DATETIME
        )

        _try_load_filetags_option(
            'filename_tag_separator',
            constants.DEFAULT_FILETAGS_FILENAME_TAG_SEPARATOR
        )
        _try_load_filetags_option(
            'between_tag_separator',
            constants.DEFAULT_FILETAGS_BETWEEN_TAG_SEPARATOR
        )
        _try_load_filesystem_option(
            'sanitize_filename',
            constants.DEFAULT_FILESYSTEM_SANITIZE_FILENAME
        )
        _try_load_filesystem_option(
            'sanitize_strict',
            constants.DEFAULT_FILESYSTEM_SANITIZE_STRICT
        )

        # Unlike the previous options; first load the default ignore patterns,
        # then combine these defaults with any user-specified patterns.
        util.nested_dict_set(
            self._options, ['FILESYSTEM_OPTIONS', 'ignore'],
            constants.DEFAULT_FILESYSTEM_IGNORE
        )
        if 'FILESYSTEM_OPTIONS' in self._data:
            _user_ignores = self._data['FILESYSTEM_OPTIONS'].get('ignore')
            if isinstance(_user_ignores, list):
                _user_ignores = util.filter_none(_user_ignores)
                if _user_ignores:
                    _defaults = util.nested_dict_get(
                        self._options, ['FILESYSTEM_OPTIONS', 'ignore']
                    )

                    _combined = _defaults.union(frozenset(_user_ignores))
                    util.nested_dict_set(
                        self._options, ['FILESYSTEM_OPTIONS', 'ignore'],
                        _combined
                    )

    def _load_version(self):
        _raw_version = self._data.get('autonameow_version')
        valid_version = parse_versioning(_raw_version)
        if valid_version:
            self._version = valid_version
        else:
            log.error('Unable to read program version from configuration.')
            log.debug('Read invalid version: "{!s}"'.format(_raw_version))

    def get(self, key_list):
        return util.nested_dict_get(self._options, key_list)

    @property
    def version(self):
        """
        Returns:
            The version number of the program that wrote the configuration as
            a Unicode string, if it is available.  Otherwise None.
        """
        if self._version:
            return 'v' + '.'.join(map(str, self._version))
        else:
            return None

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
    def rules(self):
        if self._rules and len(self._rules) > 0:
            return self._rules
        else:
            return False

    @property
    def name_templates(self):
        return self._name_templates

    def __str__(self):
        out = ['Written by autonameow version v{}\n\n'.format(self.version)]

        for number, rule in enumerate(self.rules):
            out.append('Rule {}:\n'.format(number + 1))
            out.append(util.indent(str(rule), amount=4) + '\n')

        out.append('\nName Templates:\n')
        out.append(util.indent(util.dump(self.name_templates), amount=4))

        out.append('\nMiscellaneous Options:\n')
        out.append(util.indent(util.dump(self.options), amount=4))

        return ''.join(out)
