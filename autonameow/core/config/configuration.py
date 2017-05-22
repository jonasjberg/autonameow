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

from core.config import load_yaml_file, write_yaml_file


# TODO: [BL004] Implement storing settings in configuration file.
# def load_config():
#     config = yaml.safe_load(open("path/to/config.yml"))





class Configuration(object):
    def __init__(self, data=None):
        if data:
            self.data = data
        else:
            self.data = {}

    @property
    def rules(self):
        return list(self.data)

    def load_from_dict(self, data):
        self.data = data

    def load_from_disk(self, load_path):
        self.data = load_yaml_file(load_path)

    def write_to_disk(self, dest_path):
        if os.path.exists(dest_path):
            return False
        else:
            write_yaml_file(dest_path, self.data)
