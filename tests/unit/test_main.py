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

import unit.utils as uu
import unit.constants as uuconst


class TestMainFileExistsAndIsExecutable(TestCase):
    def setUp(self):
        self.main_file = os.path.normpath(os.path.join(
            uuconst.AUTONAMEOW_SRCROOT_DIR, '__main__.py'
        ))

    def test_assumed_main_source_file_exists(self):
        self.assertTrue(uu.file_exists(self.main_file))

    def test_assumed_main_source_file_is_a_file(self):
        self.assertTrue(uu.file_exists(self.main_file))

    def test_assumed_main_source_file_is_readable(self):
        self.assertTrue(os.access(self.main_file, os.R_OK))

    def test_assumed_main_source_file_is_executable(self):
        self.assertTrue(os.access(self.main_file, os.X_OK))
