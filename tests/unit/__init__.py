# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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
import re
import unittest

import unit.constants as uuconst


GLOB_UNIT_TEST_BASENAME = "test_*.py"


def build_testsuite(filename_filter=None):
    unit_test_directory = uuconst.PATH_TESTS_UNIT
    current_dir = os.getcwd()
    os.chdir(unit_test_directory)

    test_files = glob.glob(GLOB_UNIT_TEST_BASENAME)
    if filename_filter:
        assert callable(filename_filter)
        test_files = [f for f in test_files if filename_filter(f)]

    test_modules = [
        name for name, _ in [os.path.splitext(f) for f in test_files]
    ]

    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    for module_name in test_modules:
        module_path = '{}.{}'.format(__name__, module_name)
        module = importlib.import_module(module_path, __name__)
        suite.addTest(loader.loadTestsFromModule(module))

    os.chdir(current_dir)
    return suite


def unit_test_glob(expression, filename):
    """
    Evaluates if a string (test basename) matches a given "glob" expression.

    Matching is case-sensitive. The asterisk matches anything.
    If the glob starts with '!', the matching is negated.
    Examples:
                    string          glob            Returns
                    ---------------------------------------
                    'foo bar'       'foo bar'       True
                    'foo bar'       'foo*'          True
                    'foo x bar'     '*x*'           True
                    'bar'           'foo*'          False
                    'bar'           '!foo'          True
                    'foo x bar'     '!foo*'         False
    """
    assert isinstance(filename, str)
    assert isinstance(expression, str)

    regexp = expression.replace('*', '.*')
    if regexp.startswith('!'):
        regexp = regexp[1:]
        return not bool(re.match(regexp, filename))

    return bool(re.match(regexp, filename))
