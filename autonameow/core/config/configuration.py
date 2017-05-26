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

import logging

from core.config import load_yaml_file, write_yaml_file, rule_parsers


# TODO: [BL004] Implement storing settings in configuration file.
# def load_config():
#     config = yaml.safe_load(open("path/to/config.yml"))


class Rule(object):
    def __init__(self):
        pass


class FileRule(Rule):
    def __init__(self, file_rule):
        for key, value in file_rule.items():
            try:
                setattr(self, key, value)
            except AttributeError as e:
                logging.error('{}  KEY:{} VALUE:{}'.format(str(e), str(key),
                                                           str(value)))
                raise AttributeError

    def get_conditions(self):
        return self.conditions

    def get_data_sources(self):
        return self.data_sources

    def get_name_template(self):
        return self.name_template



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
                        if isinstance(p, rule_parsers.Parser)
                        and issubclass(p, rule_parsers.Parser)
                        and p != rule_parsers.Parser]

    @property
    def data(self):
        return self._data

    @property
    def file_rules(self):
        # return [rule for rule in self._data['file_rules']]
        return self._file_rules

    def load_from_dict(self, data):
        self._data = data
        self._load_file_rules()

    def load_from_disk(self, load_path):
        _yaml_data = load_yaml_file(load_path)
        self.load_from_dict(_yaml_data)

    def write_to_disk(self, dest_path):
        if os.path.exists(dest_path):
            return False
        else:
            write_yaml_file(dest_path, self._data)

    def _load_file_rules(self):
        for rule in self._data['file_rules']:
            file_rule = FileRule(rule)
            if file_rule not in self._file_rules:
                self._file_rules.append(file_rule)
