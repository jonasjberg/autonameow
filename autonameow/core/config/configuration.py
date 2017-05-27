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

import os
import logging as log

from core.config import load_yaml_file, write_yaml_file, rule_parsers


class ConfigurationSyntaxError(Exception):
    pass


# TODO: [BL004] Implement storing settings in configuration file.
# def load_config():
#     config = yaml.safe_load(open("path/to/config.yml"))


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
        self.description = kwargs.get('description')
        self.exact_match = kwargs.get('exact_match')
        self.weight = kwargs.get('weight')
        self.name_template = kwargs.get('name_template')
        self.conditions = kwargs.get('conditions', {})
        self.data_sources = kwargs.get('data_sources', {})

        #for key, value in file_rule.items():
        #    try:
        #        setattr(self, key, value)
        #    except AttributeError as e:
        #        logging.error('{}  KEY:{} VALUE:{}'.format(str(e), str(key),
        #                                                   str(value)))
        #        raise AttributeError

    def test_file_conditions(self, file, rule):
        # TODO: ..
        for condition in rule['conditions']:
            self.parse_file_conditional()

    def parse_file_conditional(self, field_name, field_value):
        # 'conditions': {
        #     'filename': {
        #         'pathname': '~/Pictures/incoming',
        #         'basename': 'DCIM*',
        #         'extension': 'jpg'
        #     },
        #     'contents': {
        #         'mime_type': 'image/jpeg',
        #         'metadata': 'exif.datetimeoriginal'
        #         ^^^^^^^^^^   ^^^^^^^^^^^^^^^^^^^^^
        #     }   ||||||||||
        # },      field_name

        # Check which of all available parsers should handle this conditional.
        for parser in self.parsers:
            # TODO: ..
            if field_name in parser.applies_to_field:
                pass

            pass


class Configuration(object):
    def __init__(self, data=None):
        self._file_rules = []

        if data:
            self._data = data
            self._load_file_rules()
        else:
            self._data = {}

        # Instantiate rule parsers inheriting from the 'Parser' class.
        self.parsers = [p() for p in rule_parsers.__dict__.values()
                        if isinstance(p, rule_parsers.RuleParser)
                        and issubclass(p, rule_parsers.RuleParser)
                        and p != rule_parsers.RuleParser]

    def _load_file_rules(self):
        for file_rule_entry in self._data['file_rules']:
            file_rule = FileRule(file_rule_entry)

    @property
    def data(self):
        return self._data

    @property
    def file_rules(self):
        return self._file_rules

    def load_from_dict(self, data):
        self._data = data
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

    def _parse_name_template(self, param):
        # TODO: Use "NameBuilder" in try/catch-block to validate name template.
        pass
