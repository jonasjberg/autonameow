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

_THIS_DIR = os.path.abspath(os.path.dirname(__file__))
_PARENT_DIR = os.path.normpath(_THIS_DIR + os.sep + os.pardir)
TESTS_DIR = os.path.join(_PARENT_DIR + os.sep + 'test_files')


def abspath_testfile(file):
    """
    Utility method used by tests to construct a full path to individual test
    files in the 'test_files' directory.
    
    Args:
        file: The basename of a file in the 'test_files' directory.

    Returns: The full path to the specified file.

    """
    return os.path.join(TESTS_DIR + os.sep + file)

