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

from core.fileobject import eval_magic_glob


# Extractors are assumed to be located in the same directory as this file.
AUTONAMEOW_EXTRACTOR_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, AUTONAMEOW_EXTRACTOR_PATH)


class BaseExtractor(object):
    """
    Top-level abstract base class for all filetype-specific extractor classes.

    Includes common functionality and interfaces that must be implemented
    by inheriting extractor classes.
    """

    # List of MIME types that this extractor can extract information from.
    # Supports simple "globbing". Examples: ['image/*', 'application/pdf']
    handles_mime_types = None

    # TODO: [TD0003] Implement gathering data on non-core modules at run-time

    # Query string label for the data returned by this extractor.
    #    NOTE:  Must be defined in 'constants.VALID_DATA_SOURCES'!
    # Example:  'metadata.exiftool'
    data_query_string = None

    def __init__(self, source):
        """
        Creates a extractor instance acting on the specified source data.

        Args:
            source: Source of data from which to extract information as a
                byte string path (internal path format)
        """
        # Make sure the 'source' paths are in the "internal bytestring" format.
        # The is-None-check below is for unit tests that pass a None 'source'.
        if source is not None:
            assert(isinstance(source, bytes))
        self.source = source

    def query(self, field=None):
        """
        Queries the extractor for extracted data.

        Argument "field" is optional. All data is returned by default.
        If the data is text, is should be returned as Unicode strings.

        Args:
            field: Optional refinement of the query.
                Expect format and type is defined by the extractor class.

        Returns:
            All data gathered by the extractor if no field is specified.
            Else the data matching the specified field.
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

        if eval_magic_glob(file_object.mime_type, cls.handles_mime_types):
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


# TODO: [TD0003][hack] Fix this! Used for instantiating extractors so that they
# are included in the global namespace and seen by 'get_extractor_classes()'.
from extractors.metadata import ExiftoolMetadataExtractor
from extractors.metadata import AbstractMetadataExtractor
from extractors.metadata import PyPDFMetadataExtractor
from extractors.textual import PdfTextExtractor
from extractors.textual import AbstractTextExtractor

__dummy_a = BaseExtractor(None)
__dummy_b = AbstractMetadataExtractor(None)
__dummy_c = ExiftoolMetadataExtractor(None)
__dummy_d = PyPDFMetadataExtractor(None)
__dummy_e = AbstractTextExtractor(None)
__dummy_f = PdfTextExtractor(None)


def find_extractor_files():
    """
    Finds and imports Python source files assumed to be autonameow extractors.

    Returns: List of found extractor source files basenames.
    """
    extractor_files = [x for x in os.listdir(AUTONAMEOW_EXTRACTOR_PATH)
                       if x.endswith('.py')
                       and x != '__init__.py']
    return extractor_files


def get_extractor_classes(extractor_files):
    # Strip extensions.
    _to_import = [f[:-3] for f in extractor_files]

    _classes = []
    for extractor_file in _to_import:
        # namespace = __import__(extractor_file, None, None)
        __import__(extractor_file, None, None)

        namespace = inspect.getmembers(sys.modules[extractor_file],
                                       inspect.isclass)
        for _obj_name, _obj_type in namespace:
            if _obj_name == 'BaseExtractor' or _obj_name.startswith('Abstract'):
                continue
            if not issubclass(_obj_type, BaseExtractor):
                continue

            _classes.append(_obj_type)

    return _classes


def suitable_data_extractors_for(file_object):
    """
    Returns extractor classes that can handle the given file object.

    Args:
        file_object: File to get extractors for as an instance of 'FileObject'.

    Returns:
        A list of extractor classes that can extract data from the given file.
    """
    return [e for e in ExtractorClasses if e.can_handle(file_object)]


def get_extractor_classes_():
    """
    Get a list of all available extractors as a list of "type".
    All classes inheriting from the "Extractor" class are included.

    Returns:
        All available extractor classes as a list of type.
    """
    # TODO: [TD0003] Include ALL extractors!
    # out = find_extractors()
    # find_extractors()
    out = ([klass for klass in globals()['MetadataExtractor'].__subclasses__()]
           + [klass for klass in globals()['TextExtractor'].__subclasses__()])
    return out


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
    return out


def get_metadata_query_strings():
    klasses = [k for k in globals()['AbstractMetadataExtractor'].__subclasses__()]

    out = set()
    for e in klasses:
        if e.data_query_string:
            out.add(e.data_query_string)
    return out


ExtractorClasses = get_extractor_classes(find_extractor_files())
ExtractorQueryStrings = get_query_strings()
MetadataExtractorQueryStrings = get_metadata_query_strings()
