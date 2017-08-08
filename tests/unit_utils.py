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
import os
import io
import tempfile
import sys
import unittest

from contextlib import contextmanager
from datetime import datetime

import analyzers
from core.config import rules
from core.extraction import ExtractedData
from core.fileobject import FileObject
from core import util

_THIS_DIR = os.path.abspath(os.path.dirname(__file__))
_PARENT_DIR = os.path.join(_THIS_DIR, os.pardir)
TESTS_DIR = os.path.join(_PARENT_DIR + os.sep + util.syspath('test_files'))
AUTONAMEOW_SRCROOT_DIR = os.path.join(
    _PARENT_DIR + os.sep + util.syspath('autonameow')
)


class TestCase(unittest.TestCase):
    # TODO: Use this to get rid of duplicate self.maxDiff settings, etc.
    def setUp(self):
        pass

    def tearDown(self):
        pass


def abspath_testfile(file):
    """
    Utility function used by tests to construct a full path to individual test
    files in the 'test_files' directory.
    
    Args:
        file: The basename of a file in the 'test_files' directory as a
            Unicode string (internal format)

    Returns:
        The full path to the specified file.
    """
    return os.path.normpath(
        os.path.join(TESTS_DIR + os.sep + util.syspath(file))
    )


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
    class MockOptions(object):
        def __init__(self):
            self.options = {'FILETAGS_OPTIONS':
                            {'between_tag_separator': ' -- ',
                             'filename_tag_separator': ' '}}
    opts = MockOptions()

    MIME_TYPE_TEST_FILE_LOOKUP = {
        'application/pdf': 'magic_pdf.pdf',
        'image/gif': 'magic_gif.gif',
        'image/jpeg': 'magic_jpg.jpg',
        'image/png': 'magic_png.png',
        'image/x-ms-bmp': 'magic_bmp.bmp',
        'text/plain': 'magic_txt.txt',
        'video/mp4': 'magic_mp4.mp4',
    }

    if mime_type and mime_type in MIME_TYPE_TEST_FILE_LOOKUP:
        __test_file_basename = MIME_TYPE_TEST_FILE_LOOKUP[mime_type]
        temp_file = abspath_testfile(__test_file_basename)
    else:
        temp_file = make_temporary_file()

    return FileObject(util.normpath(temp_file), opts)


def get_mock_empty_extractor_data():
    """
    Returns: Mock extracted (empty) data from an 'Extraction' instance.
    """
    return {}


def get_mock_extractor_data():
    """
    Returns: Mock extracted data from an 'Extraction' instance.
    """
    data = ExtractedData()
    data.add('filesystem.basename.extension', 'bar')
    data.add('filesystem.basename.full', 'foo.bar')
    data.add('filesystem.basename.prefix', 'foo')
    data.add('filesystem.basename.suffix', 'bar')
    data.add('metadata.exiftool', {'File:MIMEType': 'application/bar'})
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
    Returns: A FileObject with mocked options and the specified basename.
    """
    tf = make_temporary_file(basename=basename)

    class MockOptions(object):
        def __init__(self):
            self.options = {'FILETAGS_OPTIONS':
                                {'between_tag_separator': ' ',
                                 'filename_tag_separator': ' -- '}}
    opts = MockOptions()

    return FileObject(util.normpath(tf), opts)


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
    out = []

    dummy_conditions = [
        [rules.RuleCondition('contents.mime_type', 'application/pdf'),
         rules.RuleCondition('filesystem.basename.extension', 'pdf'),
         rules.RuleCondition('filesystem.basename.full', 'gmail.pdf')],

        [rules.RuleCondition('contents.mime_type', 'image/jpeg'),
         rules.RuleCondition('filesystem.basename.full', 'smulan.jpg')],

        [rules.RuleCondition('contents.mime_type', 'image/jpeg'),
         rules.RuleCondition('filesystem.basename.extension', 'jpg'),
         rules.RuleCondition('filesystem.basename.full', 'DCIM*'),
         rules.RuleCondition('filesystem.pathname.full', '~/Pictures/incoming'),
         rules.RuleCondition('metadata.exiftool.EXIF:DateTimeOriginal',
                             'Defined')],

        [rules.RuleCondition('contents.mime_type', 'application/epub+zip'),
         rules.RuleCondition('filesystem.basename.extension', 'epub'),
         rules.RuleCondition('filesystem.basename.full', '.*'),
         rules.RuleCondition('filesystem.pathname.full', '.*'),
         rules.RuleCondition('metadata.exiftool.XMP-dc:Creator', 'Defined')],
    ]

    dummy_sources = [
        {'datetime': 'metadata.exiftool.PDF:CreateDate',
         'extension': 'filesystem.basename.extension',
         'title': 'filesystem.basename.prefix'},

        {'datetime': 'metadata.exiftool.EXIF:DateTimeOriginal',
         'description': 'plugin.microsoft_vision.caption',
         'extension': 'filesystem.basename.extension'},

        {'datetime': 'metadata.exiftool.EXIF:CreateDate',
         'description': 'plugin.microsoft_vision.caption',
         'extension': 'filesystem.basename.extension'},

        {'author': 'metadata.exiftool.XMP-dc:CreatorFile-as',
         'datetime': 'metadata.exiftool.XMP-dc:Date',
         'extension': 'filesystem.basename.extension',
         'publisher': 'metadata.exiftool.XMP-dc:Publisher',
         'title': 'metadata.exiftool.XMP-dc:Title'},
    ]

    out.append(rules.FileRule(
        description='test_files Gmail print-to-pdf',
        exact_match=True,
        weight=0.5,
        name_template='{datetime} {title}.{extension}',
        conditions=dummy_conditions[0],
        data_sources=dummy_sources[0]
    ))
    out.append(rules.FileRule(
        description='test_files smulan.jpg',
        exact_match=True,
        weight=1.0,
        name_template='{datetime} {description}.{extension}',
        conditions=dummy_conditions[1],
        data_sources=dummy_sources[1]
    ))
    out.append(rules.FileRule(
        description='Sample Entry for Photos with strict rules',
        exact_match=True,
        weight=1.0,
        name_template='{datetime} {description} -- {tags}.{extension}',
        conditions=dummy_conditions[1],
        data_sources=dummy_sources[1]
    ))
    out.append(rules.FileRule(
        description='Sample Entry for EPUB e-books',
        exact_match=True,
        weight=1.0,
        name_template='{publisher} {title} {edition} - {author} {date}.{extension}',
        conditions=dummy_conditions[1],
        data_sources=dummy_sources[1]
    ))

    return out


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
