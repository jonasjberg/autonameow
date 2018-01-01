# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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

import glob
import importlib
import os
import unittest


UNIT_TEST_BASENAME_GLOB = "test_*.py"


def build_testsuite(filename_filter=None):
    test_directory = os.path.dirname(__file__)
    current_dir = os.getcwd()
    os.chdir(test_directory)

    test_files = glob.glob(UNIT_TEST_BASENAME_GLOB)
    if filename_filter:
        assert callable(filename_filter)
        test_files = [f for f in test_files if filename_filter(f)]

    test_modules = [name for name, _ in map(os.path.splitext, test_files)]

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for module_name in test_modules:
        module_path = '{}.{}'.format(__name__, module_name)
        module = importlib.import_module(module_path, __name__)
        suite.addTest(loader.loadTestsFromModule(module))

    os.chdir(current_dir)
    return suite
