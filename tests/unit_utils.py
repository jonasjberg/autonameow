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
import tempfile

from core.analyze.analyze_abstract import get_instantiated_analyzers
from core.fileobject import FileObject

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


def make_temp_dir():
    """
    Creates and returns a temporary directory.

    Returns: A new temporary directory.

    """
    return tempfile.mkdtemp()


def make_temporary_file(prefix=None, suffix=None, basename=None):
    """
    Creates a temporary file and returns the full path to the file.

    Use "basename" to specify a specific file basename, including any extension.
    Arguments "prefix" and "suffix" have no effect if "basename" is specified.

    If "basename" is not specified, either or both of "prefix" and "suffix"
    can be used to specify a fixed suffix or prefix of the file basename.
    Any file extension should be specified with "suffix".

    Args:
        prefix: Optional prefix for the file basename given as a string.
        suffix: Optional suffix for the file basename given as a string.
        basename: Basename for the file given as a string.
            Overrides "prefix" and "suffix".

    Returns:
        The full absolute path of the created file as a string.
    """
    if basename:
        f = os.path.realpath(tempfile.NamedTemporaryFile(delete=False).name)
        _dest_dir = os.path.realpath(os.path.dirname(f))
        _dest_path = os.path.join(_dest_dir, basename)
        os.rename(f, _dest_path)
        return os.path.realpath(_dest_path)

    return os.path.realpath(tempfile.NamedTemporaryFile(delete=False,
                                                        prefix=prefix,
                                                        suffix=suffix).name)


def get_mock_fileobject():
    """
    Returns: A mock FileObject built from an actual (empty) file.
    """
    return FileObject(make_temporary_file())


def get_mock_analyzer():
    """
    Returns: A mock Analyzer class.
    """
    n = 0
    while n < len(get_instantiated_analyzers()):
        yield get_instantiated_analyzers()[n]
        n += 1
