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
import sys

from core import util
from core.fileobject import (
    FileObject
)

# Extractors are assumed to be located in the same directory as this file.
AUTONAMEOW_EXTRACTOR_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, AUTONAMEOW_EXTRACTOR_PATH)


class BaseExtractor(object):
    """
    Top-level abstract base class for all filetype-specific extractor classes.

    Includes common functionality and interfaces that must be implemented
    by inheriting extractor classes.

    All "extractors" must inherit from the 'BaseExtractor' class. This class
    is never used directly -- it is an abstract class that defines interfaces
    that must be implemented by inheriting classes.

    Currently, there is also an additional layer of abstraction/inheritance/
    (indirection..) between the 'BaseExtractor' and the *actual *REAL**
    extractor classes that are used at runtime.

    Current inheritance hierarchy:

        (abstract)  @ BaseExtractor
                    |
        (abstract)  +--* AbstractTextExtractor
                    |  |
                    |  +--* ImageOCRTextExtractor
                    |  '--* PdfTextExtractor
                    |
        (abstract)  '--* AbstractMetadataExtractor
                       |
                       +--* ExiftoolMetadataExtractor
                       '--* PyPDFMetadataExtractor

    The abstract extractors defines additional interfaces, extending the base.
    It is pretty messy and should be redesigned and simplified at some point ..
    """

    # List of MIME types that this extractor can extract information from.
    # Supports simple "globbing". Examples: ['image/*', 'application/pdf']
    handles_mime_types = None

    # Query string label for the data returned by this extractor.
    # Example:  'metadata.exiftool'
    data_query_string = None

    # Controls whether the extractor is enabled and used by default.
    # Used to exclude slow running extractors from always being executed.
    # If the extractor is not enabled by the default, it must be explicitly
    # specified in order to be enqueued in the extractor run queue.
    is_slow = False

    def __init__(self, source):
        """
        Creates a extractor instance acting on the specified source data.

        Args:
            source: Source of data from which to extract information as a
                byte string path (internal path format)
        """
        # Make sure the 'source' paths are in the "internal bytestring" format.
        # The is-None-check below is for unit tests that pass a None 'source'.
        if source is not None and not isinstance(source, FileObject):
            assert(isinstance(source, bytes))
        self.source = source

    def query(self, field=None):
        """
        Queries the extractor for extracted data.

        Argument "field" is optional. All data is returned by default.
        If the data is text, is should be returned as Unicode strings.

        Implementing classes should make sure to catch all exceptions and
        re-raise an "ExtractorError", passing any valuable information along.
        Only raise the "ExtractorError" exception for any irrecoverable errors.
        Otherwise, implementers should strive to return empty values of the
        same type as that of the expected, valid data.

        Args:
            field: Optional refinement of the query.
                Expect format and type is defined by the extractor class.

        Returns:
            All data gathered by the extractor if no field is specified.
            Else the data matching the specified field.

        Raises:
            ExtractorError: The extraction could not be completed successfully.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    @classmethod
    def can_handle(cls, file_object):
        """
        Tests if this extractor class can handle the given file.

        The extractor is considered to be able to handle the given file if the
        file MIME type is listed in the class attribute 'handles_mime_types'.

        Inheriting extractor classes can override this method if they need
        to perform additional tests in order to determine if they can handle
        the given file object.

        Args:
            file_object: The file to test as an instance of 'FileObject'.

        Returns:
            True if the extractor class can extract data from the given file,
            else False.
        """
        if cls.handles_mime_types is None:
            raise NotImplementedError('Must be defined by inheriting classes.')

        if util.eval_magic_glob(file_object.mime_type, cls.handles_mime_types):
            return True
        else:
            return False

    @classmethod
    def __str__(cls):
        return cls.__name__

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        return '<{}>'.format(self.__class__.__name__)


def find_extractor_files():
    """
    Finds Python source files assumed to be autonameow extractors.

    Returns: List of found extractor source files basenames.
    """
    extractor_files = [x for x in os.listdir(AUTONAMEOW_EXTRACTOR_PATH)
                       if x.endswith('.py')
                       and x != '__init__.py']
    return extractor_files


def _get_all_extractor_classes(extractor_files):
    # Strip extensions.
    _to_import = [f[:-3] for f in extractor_files]

    _extractor_classes = []
    _abstract_extractor_classes = []
    for extractor_file in _to_import:
        __import__(extractor_file, None, None)
        namespace = inspect.getmembers(sys.modules[extractor_file],
                                       inspect.isclass)
        for _obj_name, _obj_type in namespace:
            if not issubclass(_obj_type, BaseExtractor):
                continue
            if _obj_type == BaseExtractor:
                continue
            if _obj_name.startswith('Abstract'):
                _abstract_extractor_classes.append(_obj_type)
            else:
                _extractor_classes.append(_obj_type)

    return _abstract_extractor_classes, _extractor_classes


def get_abstract_extractor_classes(extractor_files):
    _abstract, _implemented = _get_all_extractor_classes(extractor_files)
    return _abstract


def get_extractor_classes(extractor_files):
    _abstract, _implemented = _get_all_extractor_classes(extractor_files)
    return _implemented


def suitable_data_extractors_for(file_object):
    """
    Returns extractor classes that can handle the given file object.

    Args:
        file_object: File to get extractors for as an instance of 'FileObject'.

    Returns:
        A list of extractor classes that can extract data from the given file.
    """
    return [e for e in ExtractorClasses if e.can_handle(file_object)]


def get_query_strings():
    """
    Get the set of "query strings" for all extractor classes.

    Returns:
        Unique extractor query strings as a set.
    """
    out = set()
    for e in ExtractorClasses:
        if e.data_query_string:
            out.add(e.data_query_string)

    # TODO: [TD0053] Fix special case of collecting data from 'FileObject'.
    out.add('filesystem.basename.full')
    out.add('filesystem.basename.extension')
    out.add('filesystem.basename.suffix')
    out.add('filesystem.basename.prefix')
    out.add('filesystem.pathname.full')
    out.add('filesystem.pathname.parent')
    out.add('contents.mime_type')
    return out


def get_metadata_query_strings():
    _abstract_classes = get_abstract_extractor_classes(find_extractor_files())

    klasses = False
    for klass in _abstract_classes:
        if klass == 'AbstractMetadataExtractor':
            klasses = [k for k in klass.__subclasses__()]

    if not klasses:
        return None

    out = set()
    for e in klasses:
        if e.data_query_string:
            out.add(e.data_query_string)
    return out


ExtractorClasses = get_extractor_classes(find_extractor_files())
QueryStrings = get_query_strings()
MetadataExtractorQueryStrings = get_metadata_query_strings()
