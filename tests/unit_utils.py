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

import inspect
import io
import os
import sys
import tempfile
import unittest
from contextlib import contextmanager
from datetime import datetime

import analyzers

from core import util
from core.config import rules
from core.fileobject import FileObject

import unit_utils_constants as uuconst


class TestCase(unittest.TestCase):
    # TODO: Use this to get rid of duplicate self.maxDiff settings, etc.
    def setUp(self):
        pass

    def tearDown(self):
        pass


def abspath_testfile(testfile_basename):
    """
    Utility function used by tests to construct a full path to individual test
    files in the 'test_files' directory.
    
    Args:
        testfile_basename: The basename of a file in the 'test_files' directory
            as a Unicode string (internal string format)

    Returns:
        The full absolute path to the given file.
    """
    return os.path.abspath(os.path.join(uuconst.TEST_FILES_DIR,
                                        testfile_basename))


def file_exists(file_path):
    """
    Tests whether a given path is an existing file.

    Args:
        file_path: Path to the file to test.

    Returns:
        True if the file exists, else False.
    """
    return os.path.isfile(file_path)


def dir_exists(dir_path):
    """
    Tests whether a given path is an existing directory.

    Args:
        dir_path: The path to test.

    Returns:
        True if the directory exists and is readable, else False.
    """
    try:
        return os.path.exists(dir_path) and os.path.isdir(dir_path)
    except OSError:
        return False


def make_temp_dir():
    """
    Creates and returns a temporary directory.

    Returns:
        A new temporary directory.
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
        The full absolute path of the created file as a bytestring.
    """
    if basename:
        f = os.path.realpath(tempfile.NamedTemporaryFile(delete=False).name)
        _dest_dir = os.path.realpath(os.path.dirname(f))
        _dest_path = os.path.join(_dest_dir, util.syspath(basename))
        os.rename(f, _dest_path)

        out = os.path.realpath(_dest_path)
    else:
        out = os.path.realpath(tempfile.NamedTemporaryFile(delete=False,
                                                           prefix=prefix,
                                                           suffix=suffix).name)
    return util.bytestring_path(out)


def get_mock_fileobject(mime_type=None):
    """
    Returns 'FileObject' instances for use by unit tests.

    Args:
        mime_type: Optional MIME type of the source file.

    Returns:
        A mock FileObject built from an actual (empty) file.
    """
    # TODO: [hardcoded] Might break if options data structure is modified.

    MIME_TYPE_TEST_FILE_LOOKUP = {
        'application/pdf': 'magic_pdf.pdf',
        'image/gif': 'magic_gif.gif',
        'image/jpeg': 'magic_jpg.jpg',
        'image/png': 'magic_png.png',
        'image/x-ms-bmp': 'magic_bmp.bmp',
        'text/plain': 'magic_txt.txt',
        'video/mp4': 'magic_mp4.mp4',
        'inode/x-empty': 'empty',
    }

    if mime_type and mime_type in MIME_TYPE_TEST_FILE_LOOKUP:
        __test_file_basename = MIME_TYPE_TEST_FILE_LOOKUP[mime_type]
        temp_file = abspath_testfile(__test_file_basename)
    else:
        temp_file = make_temporary_file()

    return FileObject(util.normpath(temp_file))


def get_mock_empty_extractor_data():
    """
    Returns: Mock extracted (empty) data from an 'Extraction' instance.
    """
    return {}


def mock_request_data_callback(file_object, label):
    data = mock_session_data_pool_with_extractor_and_analysis_data(file_object)
    try:
        d = util.nested_dict_get(data, [file_object, label])
    except KeyError:
        return None
    else:
        return d


def mock_add_results_callback(file_object, label, data):
    pass


def mock_session_data_pool(file_object):
    """
    Returns: Mock session data pool with typical extractor data.
    """
    data = {}
    util.nested_dict_set(data,
                         [file_object, 'filesystem.basename.full'],
                         b'gmail.pdf')
    util.nested_dict_set(data,
                         [file_object, 'filesystem.basename.extension'],
                         b'pdf.pdf')
    util.nested_dict_set(data,
                         [file_object, 'filesystem.basename.suffix'],
                         b'pdf.pdf')
    util.nested_dict_set(data,
                         [file_object, 'filesystem.pathname.parent'],
                         b'test_files')
    util.nested_dict_set(data,
                         [file_object, 'filesystem.contents.mime_type'],
                         'application/pdf')
    util.nested_dict_set(data,
                         [file_object, 'metadata.exiftool.PDF:Creator'],
                         'Chromium')
    util.nested_dict_set(data,
                         [file_object, 'metadata.exiftool'],
                         {'File:MIMEType': 'application/bar'})

    return data


def mock_session_data_pool_empty_analysis_data(file_object):
    data = {}
    util.nested_dict_set(data,
                         [file_object, 'analysis.filename_analyzer.datetime'],
                         [])
    util.nested_dict_set(data,
                         [file_object, 'analysis.filename_analyzer.tags'],
                         [])
    util.nested_dict_set(data,
                         [file_object, 'analysis.filename_analyzer.title'],
                         [])
    util.nested_dict_set(data,
                         [file_object, 'analysis.filesystem_analyzer.datetime'],
                         [])
    util.nested_dict_set(data,
                         [file_object, 'analysis.filesystem_analyzer.tags'],
                         [])
    util.nested_dict_set(data,
                         [file_object, 'analysis.filesystem_analyzer.title'],
                         [])
    return data


def mock_session_data_pool_with_analysis_data(file_object):
    data = {}
    util.nested_dict_set(data,
                         [file_object, 'analysis.filename_analyzer.tags'],
                         [{'source': 'filenamepart_tags',
                           'value': ['tagfoo', 'tagbar'],
                           'weight': 1}])
    util.nested_dict_set(data,
                         [file_object, 'analysis.filename_analyzer.title'],
                         [{'source': 'filenamepart_base',
                           'value': 'gmail',
                           'weight': 0.25}])
    util.nested_dict_set(data,
                         [file_object, 'analysis.filesystem_analyzer.datetime'],
                         [{'source': 'modified',
                           'value': datetime(2017, 6, 12, 22, 38, 34),
                           'weight': 1},
                          {'source': 'created',
                           'value': datetime(2017, 6, 12, 22, 38, 34),
                           'weight': 1},
                          {'source': 'accessed',
                           'value': datetime(2017, 6, 12, 22, 38, 34),
                           'weight': 0.25}])
    return data


def mock_session_data_pool_with_extractor_and_analysis_data(file_object):
    data = {}
    util.nested_dict_set(data,
                         [file_object, 'filesystem.basename.full'],
                         b'gmail.pdf')
    util.nested_dict_set(data,
                         [file_object, 'filesystem.basename.extension'],
                         b'pdf.pdf')
    util.nested_dict_set(data,
                         [file_object, 'filesystem.basename.suffix'],
                         b'pdf.pdf')
    util.nested_dict_set(data,
                         [file_object, 'filesystem.pathname.parent'],
                         b'test_files')
    util.nested_dict_set(data,
                         [file_object, 'filesystem.contents.mime_type'],
                         'application/pdf')
    util.nested_dict_set(data,
                         [file_object, 'metadata.exiftool.PDF:Creator'],
                         'Chromium')
    util.nested_dict_set(data,
                         [file_object, 'metadata.exiftool'],
                         {'File:MIMEType': 'application/bar'})
    util.nested_dict_set(data,
                         [file_object, 'analysis.filename_analyzer.tags'],
                         [{'source': 'filenamepart_tags',
                           'value': ['tagfoo', 'tagbar'],
                           'weight': 1}])
    util.nested_dict_set(data,
                         [file_object, 'analysis.filetags.tags'],
                         [])
    util.nested_dict_set(data,
                         [file_object, 'analysis.filetags.description'],
                         'gmail')
    util.nested_dict_set(data,
                         [file_object, 'analysis.filetags.extension'],
                         'pdf')
    util.nested_dict_set(data,
                         [file_object, 'analysis.filetags.timestamp'],
                         None)
    util.nested_dict_set(data,
                         [file_object, 'analysis.filename_analyzer.title'],
                         [{'source': 'filenamepart_base',
                           'value': 'gmail',
                           'weight': 0.25}])
    util.nested_dict_set(data,
                         [file_object, 'analysis.filesystem_analyzer.datetime'],
                         [{'source': 'modified',
                           'value': datetime(2017, 6, 12, 22, 38, 34),
                           'weight': 1},
                          {'source': 'created',
                           'value': datetime(2017, 6, 12, 22, 38, 34),
                           'weight': 1},
                          {'source': 'accessed',
                           'value': datetime(2017, 6, 12, 22, 38, 34),
                           'weight': 0.25}])
    return data


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
    Returns: A FileObject based on a temporary file with the given basename.
    """
    tf = make_temporary_file(basename=basename)
    return FileObject(util.normpath(tf))


@contextmanager
def capture_stdout(finally_print=False):
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
        if finally_print:
            print(capture.getvalue())


def get_instantiated_analyzers():
    """
    Get a list of all available analyzers as instantiated class objects.
    All classes inheriting from the "Analyzer" class are included.

    Returns:
        A list of class instances, one per subclass of "Analyzer".
    """
    # NOTE: These are instantiated with a None FileObject, which might be a
    #       problem and is surely not very pretty.
    return [klass(None, None, None) for klass in
            analyzers.get_analyzer_classes()]


def get_dummy_rules_to_examine():

    _raw_conditions = get_dummy_raw_conditions()
    _raw_sources = get_dummy_raw_data_sources()

    out = []
    out.append(rules.Rule(
        description='test_files Gmail print-to-pdf',
        exact_match=True,
        ranking_bias=0.5,
        name_template='{datetime} {title}.{extension}',
        conditions=_raw_conditions[0],
        data_sources=_raw_sources[0]
    ))
    out.append(rules.Rule(
        description='test_files smulan.jpg',
        exact_match=True,
        ranking_bias=1.0,
        name_template='{datetime} {description}.{extension}',
        conditions=_raw_conditions[1],
        data_sources=_raw_sources[1]
    ))
    out.append(rules.Rule(
        description='Sample Entry for Photos with strict rules',
        exact_match=True,
        ranking_bias=1.0,
        name_template='{datetime} {description} -- {tags}.{extension}',
        conditions=_raw_conditions[1],
        data_sources=_raw_sources[1]
    ))
    out.append(rules.Rule(
        description='Sample Entry for EPUB e-books',
        exact_match=True,
        ranking_bias=1.0,
        name_template='{publisher} {title} {edition} - {author} {date}.{extension}',
        conditions=_raw_conditions[1],
        data_sources=_raw_sources[1]
    ))

    return out


def get_dummy_rulecondition_instances():
    return [rules.RuleCondition(meowuri, expression)
            for meowuri, expression in uuconst.DUMMY_RAW_RULE_CONDITIONS]


def get_dummy_raw_conditions():
    return [{meowuri: expression}
            for meowuri, expression in uuconst.DUMMY_RAW_RULE_CONDITIONS]


def get_dummy_raw_data_sources():
    return uuconst.DUMMY_RAW_RULE_DATA_SOURCES


def get_dummy_rule():
    return rules.Rule(
        description='dummy',
        exact_match=False,
        ranking_bias=0.5,
        name_template='dummy',
        conditions=get_dummy_raw_conditions()[0],
        data_sources=get_dummy_raw_data_sources()[0]
    )


def is_class_instance(thing):
    """
    Tests whether a given object is a instance of a class.

    Args:
        thing: The object to test.

    Returns:
        True if the given object is an instance of a class, otherwise False.
    """
    if not thing:
        return False
    if isinstance(thing,
                  (type, bool, str, bytes, int, float, list, set, tuple)):
        return False

    if hasattr(thing, '__class__'):
        return True

    # Make sure to always return boolean. Catches case where "thing" is a
    # built-in/primitive not included in the messy "isinstance"-check ..
    return False


def is_class(thing):
    """
    Tests whether a given object is an (uninstantiated) class.

    Args:
        thing: The object to test.

    Returns:
        True if the given object is a class, otherwise False.
    """
    return inspect.isclass(thing)


def str_to_datetime(yyyy_mm_ddthhmmss):
    """
    Converts a string on the form "YYYY-MM-DD HHMMSS" to a 'datetime' object.

    Args:
        yyyy_mm_ddthhmmss: String to convert.

    Returns:
        A 'datetime' object if the conversion was successful.
    Raises:
        ValueError: The string could not be converted.
    """
    return datetime.strptime(yyyy_mm_ddthhmmss, '%Y-%m-%d %H%M%S')


def is_importable(module_name):
    """
    Tests if a given module can be imported without raising an exception.

    Returns: True if the module was successfully imported, otherwise False.
    """
    try:
        _ = __import__(module_name, None, None)
    except (TypeError, ValueError, ImportError):
        return False
    else:
        return True
