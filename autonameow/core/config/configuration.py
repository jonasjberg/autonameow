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

from core.config import load_yaml_file, write_yaml_file
from core.config.rule_parsers import get_instantiated_parsers
from core.exceptions import ConfigurationSyntaxError
from core.util.misc import unique_identifier


class Rule(object):
    def __init__(self):
        # self.help = ''
        pass


class FileRule(Rule):
    """
    Represents a single file rule entry in a configuration.
    """
    # EXAMPLE FILE RULE:
    # ==================
    # {'_description': 'First Entry in the Default Configuration',
    #  '_exact_match': False,
    #  '_weight': None,
    #  'name_template': 'default_template_name',
    #  'conditions': {
    #      'filename': {
    #          'pathname': None,
    #          'basename': None,
    #          'extension': None
    #      },
    #      'contents': {
    #          'mime_type': None
    #      }
    #  },
    #      'data_sources': {
    #          'datetime': None,
    #          'description': None,
    #          'title': None,
    #          'author': None,
    #          'publisher': None,
    #          'extension': 'filename.extension'
    #      }
    # },
    def __init__(self, **kwargs):
        super().__init__()

        self.description = str(kwargs.get('description'))
        self.exact_match = bool(kwargs.get('exact_match'))
        self.weight = kwargs.get('weight')
        self.name_template = kwargs.get('name_template')
        self.conditions = kwargs.get('conditions', {})
        self.data_sources = kwargs.get('data_sources', {})

    def __str__(self):
        desc = []
        for key in self.__dict__:
            desc.append('{}: {}'.format(key.title(), self.__dict__[key]))
        return '\n'.join(desc)


class Configuration(object):
    def __init__(self, data=None):
        self._file_rules = []
        self._name_templates = []

        # Instantiate rule parsers inheriting from the 'Parser' class.
        self.rule_parsers = get_instantiated_parsers()

        if data:
            self._data = data
            self._load_name_templates()
            self._load_file_rules()
        else:
            self._data = {}

    def _load_name_templates(self):
        if not self._data:
            # TODO: Handle properly ..
            return False

        templates = []

        if 'name_templates' in self._data:
            for nt in self._data['name_templates']:
                valid_format = self.validate(nt, 'name_format')
                if not valid_format:
                    msg = 'Invalid format: "{}"'.format(nt.get('name_format'))
                    raise ConfigurationSyntaxError(msg)
                templates.append({'description': nt.get('_description'),
                                  'name': nt.get('_name', unique_identifier()),
                                  'name_format': valid_format})
        self._name_templates += templates

    def _load_file_rules(self):
        if not self._data:
            # TODO: Handle properly ..
            return False

        # Check raw dictionary data.
        # Create and populate "FileRule" objects with *validated* data.
        for fr in self._data['file_rules']:

            # Prioritize 'name_format', the "raw" name format string.
            # If it is not defined in the rule, check that 'name_template'
            # refers to a valid entry in 'name_templates'.
            _valid_template = None
            if 'name_format' in fr and fr.get('name_format'):
                _valid_template = self.validate(fr, 'name_format')
            elif 'name_template' in fr:
                _template_name = fr.get('name_template')

                for nt in self.name_templates:
                    if nt['name'] == _template_name:
                        _valid_template = nt.get('name_format')
                        break

            if not _valid_template:
                log.critical('Bad: ' + str(fr))
                raise ConfigurationSyntaxError('Invalid name format')

            file_rule = FileRule(description=fr.get('_description'),
                                 exact_match=fr.get('_exact_match'),
                                 weight=fr.get('_weight'),
                                 name_template=_valid_template,
                                 conditions=self._parse_conditions(),
                                 data_sources=self._parse_sources())

            self._file_rules.append(file_rule)

    def validate(self, raw_file_rule, field_name):
        for parser in self.rule_parsers:
            if field_name in parser.applies_to_field:
                val_func = parser.get_validation_function()
                if val_func(raw_file_rule.get(field_name)):
                    return raw_file_rule.get(field_name)

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

    # TODO: Implement something like this here?
    #def parse_file_conditional(self, field_name, field_value):
    #   pass

    def _parse_name_template(self, param):
        # TODO: Use "NameBuilder" in try/catch-block to validate name template.
        return None
        pass

    def _parse_conditions(self):
        # TODO: ..
        return None
        pass

    def _parse_sources(self):
        # TODO: ..
        return None
        pass
