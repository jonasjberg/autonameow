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
from core.config.constants import FILERULE_DEFAULT_WEIGHT
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
    FileRulePriorityError
)
from core.util import misc

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
        self.weight = kwargs.get('weight', FILERULE_DEFAULT_WEIGHT)
        self.name_template = kwargs.get('name_template')
        self.conditions = kwargs.get('conditions', False)
        self.data_sources = kwargs.get('data_sources', False)

        # Rules are sorted/prioritized by first the score, secondly the weight.
        self.score = 0

        # TODO: Implement "conditions" field ..
        # Possible a list of functions already "loaded" with the target value.
        # Also "loaded" with correspondin (reference to) a validation function.

    def __str__(self):
        return misc.dump(self.__dict__)

    def __repr__(self):
        out = []
        for key in self.__dict__:
            out.append('{}: {}'.format(key.title(), self.__dict__[key]))
        return ', '.join(out)

    def upvote(self):
        self.score += 1

    def downvote(self):
        if self.score > 0:
            self.score -= 1

    #def __gt__(self, other):
    #    if self.score == other.score and self.weight == other.weight:
    #        raise FileRulePriorityError('Rules score and weight are both equal')
    #    if self.score == other.score:
    #        return self.weight > other.weight
    #    else:
    #        return self.score > other.score

    #def __lt__(self, other):
    #    if self.score == other.score and self.weight == other.weight:
    #        raise FileRulePriorityError('Rules score and weight are both equal')
    #    if self.score == other.score:
    #        return self.weight < other.weight
    #    else:
    #        return self.score < other.score

    #def __eq__(self, other):
    #    return self.description == other.description and \
    #           self.exact_match == other.exact_match and \
    #           self.weight == other.weight and \
    #           self.name_template == other.name_template and \
    #           self.conditions == other.conditions and \
    #           self.data_sources == other.data_sources


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
                log.debug('Bad rule: ' + str(fr))
                raise ConfigurationSyntaxError('Invalid name template format')

            _valid_conditions = parse_conditions(fr.get('CONDITIONS'))
            _valid_sources = parse_sources(fr.get('DATA_SOURCES'))
            _valid_weight = self.parse_weight(fr.get('weight'))

            file_rule = FileRule(description=fr.get('description'),
                                 exact_match=fr.get('exact_match'),
                                 weight=_valid_weight,
                                 name_template=_valid_template,
                                 conditions=_valid_conditions,
                                 data_sources=_valid_sources)
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

    def parse_weight(self, param):
        try:
            w = float(param)
        except TypeError:
            return FILERULE_DEFAULT_WEIGHT
        else:
            if 0 <= w <= 1:
                return w
            else:
                raise ConfigurationSyntaxError('Expected integer in range 0-1')

    def __str__(self):
        out = []
        for number, rule in enumerate(self.file_rules):
            out.append('File Rule {}:\n'.format(number + 1))
            out.append(misc.indent(str(rule), amount=4) + '\n')

        out.append('\nName Templates:\n')
        out.append(misc.indent(misc.dump(self.name_templates), amount=4))

        out.append('\nMiscellaneous Options:\n')
        out.append(misc.indent(misc.dump(self.options), amount=4))

        return ''.join(out)


def parse_sources(raw_sources):
    # TODO: [hardcoded] Fix this! Solves a very limited number of cases!
    out = {}

    if 'datetime' in raw_sources:
        source = raw_sources['datetime']
        if source:
            if isinstance(source, list):
                source = source[0]
            if source.startswith('metadata.exiftool.'):
                # Slice returns two last items in split() list.
                out['datetime'] = source.split('.')[-2:]

    if 'description' in raw_sources:
        source = raw_sources['description']
        if isinstance(source, list):
            source = source[0]
        if source and source == 'plugin.microsoftvision.caption':
            out['description'] = source.split('.')[-2:]

    if 'extension' in raw_sources:
        source = raw_sources['description']
        if isinstance(source, list):
            source = source[0]
        if source and source == 'filename.extension':
            out['extension'] = 'filesystem.extension'

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
                    if key in out:
                        log.warning('Clobbering condition: {!s}'.format(key))
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
