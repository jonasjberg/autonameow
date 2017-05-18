#!/usr/bin/env python3
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
from unittest import TestCase

from core.config import yaml_reader
from unit_utils import make_temp_dir

TEST_CONFIG_DATA = {'key1': 'value1',
                    'key2': ['value2', 'value3'],
                    'key3': {'key4': 'value4',
                             'key5': ['value5', 'value6']}}

class TestWriteConfig(TestCase):
    def setUp(self):
        self.dest_path = os.path.join(make_temp_dir(), 'test_config.yaml')

    def test_setup(self):
        self.assertFalse(os.path.exists(self.dest_path))

    def test_write_config(self):
        yaml_reader.write_config(TEST_CONFIG_DATA, self.dest_path)
        self.assertTrue(os.path.exists(self.dest_path))

