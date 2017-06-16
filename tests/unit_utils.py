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
import io
import tempfile
import sys

from contextlib import contextmanager

from analyzers.analyzer import get_instantiated_analyzers
from core.fileobject import FileObject

_THIS_DIR = os.path.abspath(os.path.dirname(__file__))
_PARENT_DIR = os.path.normpath(_THIS_DIR + os.sep + os.pardir)
TESTS_DIR = os.path.join(_PARENT_DIR + os.sep + 'test_files')


def abspath_testfile(file):
    """
    Utility function used by tests to construct a full path to individual test
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


def get_mock_fileobject(mime_type=None):
    """
    Returns 'FileObject' instances for use by unit tests.

    Args:
        mime_type: Optional MIME type of the source file.

    Returns:
        A mock FileObject built from an actual (empty) file.
    """
    # TODO: [hardcoded] Might break if options data structure is modified.
    class MockOptions(object):
        def __init__(self):
            self.options = {'FILETAGS_OPTIONS':
                            {'between_tag_separator': ' -- ',
                             'filename_tag_separator': ' '}}
    opts = MockOptions()

    if mime_type:
        if mime_type == 'video/mp4':
            temp_file = abspath_testfile('magic_mp4.mp4')
    else:
        temp_file = make_temporary_file()

    return FileObject(temp_file, opts)


def get_mock_empty_extractor_data():
    """
    Returns: Mock extracted (empty) data from an 'Extraction' instance.
    """
    return {}


def get_mock_analyzer():
    """
    Returns: A mock Analyzer class.
    """
    n = 0
    while n < len(get_instantiated_analyzers()):
        yield get_instantiated_analyzers()[n]
        n += 1


def get_named_file_object(basename):
    """
    Returns: A FileObject with mocked options and the specified basename.
    """
    tf = make_temporary_file(basename=basename)

    class MockOptions(object):
        def __init__(self):
            self.options = {'FILETAGS_OPTIONS':
                                {'between_tag_separator': ' ',
                                 'filename_tag_separator': ' -- '}}
    opts = MockOptions()

    return FileObject(tf, opts)


@contextmanager
def capture_stdout():
    """Save stdout in a StringIO.

    >>> with capture_stdout() as output:
    ...     print('spam')
    ...
    >>> output.getvalue()
    'spam'

    NOTE:  This method was lifted and modified from the "beets" project.

           Source repo: https://github.com/beetbox/beets
           Source file: 'beets/test/helper.py'
           Commit hash: 7a2bdf502f88a278da6be55f93770dad738a14e6
    """
    initial_state = sys.stdout
    sys.stdout = capture = io.StringIO()
    try:
        yield sys.stdout
    finally:
        sys.stdout = initial_state
        print(capture.getvalue())
