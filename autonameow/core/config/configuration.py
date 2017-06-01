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
    RegexConfigFieldParser
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

        # Instantiate rule parsers inheriting from the 'Parser' class.
        self.field_parsers = get_instantiated_field_parsers()

        if data:
            self._data = data
            self._load_name_templates()
            self._load_file_rules()
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

            # Prioritize 'name_format', the "raw" name format string.
            # If it is not defined in the rule, check that 'name_template'
            # refers to a valid entry in 'name_templates'.
            #
            # TODO: Consolidate 'name_format' and 'name_template' to one field.
            #       Test if the field data is a valid name template,
            #       if it isn't, use it as a format string.
            _valid_template = None
            if 'NAME_FORMAT' in fr and fr.get('NAME_FORMAT'):
                _valid_template = self.validate_field(fr, 'NAME_FORMAT')
            elif 'NAME_TEMPLATE' in fr:
                _template_name = fr.get('NAME_TEMPLATE')

                if _template_name in self.name_templates:
                    _valid_template = self._name_templates.get(_template_name)

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
                else:
                    valid_condition = validate_condition(key, value)
                    if valid_condition:
                        out[key] = value
        except ValueError as e:
            raise ConfigurationSyntaxError('Bad condition; ' + str(e))

    if 'contents' in raw_conditions:
        raw_contents = raw_conditions['contents']
        traverse_dict(raw_contents)

    return out


def validate_condition(condition_field, condition_value):
    for parser in field_parsers:
        if condition_field in parser.applies_to_field:
            if parser.validate(condition_value):
                return condition_value
            else:
                return False
