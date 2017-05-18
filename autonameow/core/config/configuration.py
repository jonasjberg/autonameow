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
import yaml

# TODO: [BL004] Implement storing settings in configuration file.
# def load_config():
#     config = yaml.safe_load(open("path/to/config.yml"))


class Configuration(object):
    def __init__(self):
        self.data = {}

    def load_from_disk(self, load_path=None):
        with open(load_path, 'r') as file_handle:
            self.data = yaml.load(file_handle)

    def write_to_disk(self, dest_path=None):
        if os.path.exists(dest_path):
            return False

        with open(dest_path, 'w') as file_handle:
            yaml.dump(self.data, file_handle, default_flow_style=False)
