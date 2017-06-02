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

from core.config import (
    load_yaml_file,
    write_yaml_file
)
from core.config.field_parsers import (
    MimeTypeConfigFieldParser,
    NameFormatConfigFieldParser,
    get_instantiated_field_parsers,
    RegexConfigFieldParser,
    DateTimeConfigFieldParser
)
from core.exceptions import (
    ConfigurationSyntaxError,
    ConfigError,
)


field_parsers = get_instantiated_field_parsers()


class Rule(object):
    def __init__(self):
        pass


class FileRule(Rule):
    """
    Represents a single file rule entry in a loaded configuration.
    """
    def __init__(self, **kwargs):
        super().__init__()

        self.description = str(kwargs.get('description'))
        self.exact_match = bool(kwargs.get('exact_match'))
        self.weight = kwargs.get('weight')
        self.name_template = kwargs.get('name_template')
        self.conditions = kwargs.get('conditions', False)
        self.data_sources = kwargs.get('data_sources', False)

        self.score = 0

        # TODO: Implement "conditions" field ..
        # Possible a list of functions already "loaded" with the target value.

    def __str__(self):
        desc = []
        for key in self.__dict__:
            desc.append('{}: {}'.format(key.title(), self.__dict__[key]))
        return '\n'.join(desc)

    def upvote(self):
        self.score += 1

    def downvote(self):
        if self.score > 0:
            self.score -= 1


class Configuration(object):
    def __init__(self, data=None):
        self._file_rules = []
        self._name_templates = {}
        self._options = {'DATETIME_FORMAT': {},
                         'FILETAGS_OPTIONS': {}}

        # Instantiate rule parsers inheriting from the 'Parser' class.
        self.field_parsers = get_instantiated_field_parsers()

        if data:
            self._data = data
            self._load_name_templates()
            self._load_file_rules()
            self._load_options()
        else:
            self._data = {}

    def _load_name_templates(self):
        if not self._data:
            raise ConfigError('Invalid state; missing "self._data" ..')

        if 'NAME_TEMPLATES' not in self._data:
            log.debug('Configuration does not contain name templates')
            return

        loaded_templates = {}
        for k, v in self._data.get('NAME_TEMPLATES').items():
            if NameFormatConfigFieldParser.is_valid_format_string(v):
                loaded_templates[k] = v
            else:
                msg = f'Invalid name template "{k}": "{v}"'
                raise ConfigurationSyntaxError(msg)

        self._name_templates.update(loaded_templates)

    def _load_file_rules(self):
        if not self._data:
            raise ConfigError('Invalid state; missing "self._data" ..')

        # Check raw dictionary data.
        # Create and populate "FileRule" objects with *validated* data.
        for fr in self._data['FILE_RULES']:

            # First test if the field data is a valid name template entry,
            # If it is, use the format string defined in that entry.
            # If not, try to use 'name_template' as a format string.
            _valid_template = None
            if 'NAME_FORMAT' in fr:
                name_format = fr.get('NAME_FORMAT')
                if name_format in self.name_templates:
                    _valid_template = self._name_templates.get(name_format)
                else:
                    _valid_template = self.validate_field(fr, 'NAME_FORMAT')

            if not _valid_template:
                log.debug('Bad: ' + str(fr))
                raise ConfigurationSyntaxError('Invalid name template format')

            _valid_conditions = parse_conditions(fr.get('CONDITIONS'))
            _valid_sources = parse_sources(fr.get('DATA_SOURCES'))

            file_rule = FileRule(description=fr.get('_description'),
                                 exact_match=fr.get('_exact_match'),
                                 weight=fr.get('_weight'),
                                 name_template=_valid_template,
                                 conditions=_valid_conditions,
                                 data_sources=_valid_sources)
            # TODO: Make parse_conditions and parse_sources functions.

            self._file_rules.append(file_rule)

    def validate_field(self, raw_file_rule, field_name):
        for parser in self.field_parsers:
            if field_name in parser.applies_to_field:
                field_value = raw_file_rule.get(field_name)
                if parser.validate(field_value):
                    return field_value

        log.critical('Config file entry not validated correctly!')
        return False

    def _load_options(self):
        def _try_load_date_format_option(option):
            _value = self._data['DATETIME_FORMAT'].get(option)
            if _value and DateTimeConfigFieldParser.is_valid_datetime(_value):
                self._options['DATETIME_FORMAT'][option] = _value

        def _try_load_filetags_option(option):
            _value = self._data['filetags_options'].get(option)
            if _value:
                self._options['filetags'][option] = _value

        if 'DATETIME_FORMAT' in self._data:
            _try_load_date_format_option('date')
            _try_load_date_format_option('time')
            _try_load_date_format_option('datetime')

        if 'FILETAGS_OPTIONS' in self._data:
            _try_load_filetags_option('filename_tag_separator')
            _try_load_filetags_option('between_tag_separator')

    @property
    def options(self):
        return self._options

    @property
    def data(self):
        return self._data

    @property
    def file_rules(self):
        return self._file_rules

    @property
    def name_templates(self):
        return self._name_templates

    def load_from_dict(self, data):
        self._data = data
        self._load_name_templates()
        self._load_file_rules()
        self._load_options()

    def load_from_disk(self, load_path):
        _yaml_data = load_yaml_file(load_path)
        self.load_from_dict(_yaml_data)

    def write_to_disk(self, dest_path):
        if os.path.exists(dest_path):
            raise FileExistsError
        else:
            write_yaml_file(dest_path, self._data)

    def _parse_weight(self, param):
        try:
            w = float(param)
        except TypeError:
            pass
        else:
            if 0 <= w <= 1:
                return w
            else:
                raise ConfigurationSyntaxError('Expected integer in range 0-1')


def parse_sources(raw_sources):
    # TODO: ..
    out = {}

    return out


def parse_conditions(raw_conditions):
    # TODO: ..
    out = {}

    def traverse_dict(the_dict):
        try:
            for key, value in the_dict.items():
                if isinstance(value, dict):
                    traverse_dict(value)

                valid_condition = validate_condition(key, value)
                if valid_condition:
                    out[key] = value
        except ValueError as e:
            raise ConfigurationSyntaxError('Bad condition; ' + str(e))

    if 'contents' in raw_conditions:
        raw_contents = raw_conditions['contents']
        traverse_dict(raw_contents)

    if 'filesystem' in raw_conditions:
        raw_contents = raw_conditions['filesystem']
        traverse_dict(raw_contents)

    return out


def validate_condition(condition_field, condition_value):
    for parser in field_parsers:
        if condition_field in parser.applies_to_field:
            if parser.validate(condition_value):
                return condition_value
            else:
                return False
