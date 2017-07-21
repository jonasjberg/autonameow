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

from extractors import extractor

# TODO: [TD0003][hack] Fix this! Used for instantiating extractors so that they
# are included in the global namespace and seen by 'get_extractor_classes()'.
from extractors.extractor import Extractor
from extractors.metadata import ExiftoolMetadataExtractor
from extractors.metadata import MetadataExtractor
from extractors.metadata import PyPDFMetadataExtractor
from extractors.textual import PdfTextExtractor
from extractors.textual import TextExtractor

__dummy_a = Extractor(None)
__dummy_b = MetadataExtractor(None)
__dummy_c = ExiftoolMetadataExtractor(None)
__dummy_d = PyPDFMetadataExtractor(None)
__dummy_e = TextExtractor(None)
__dummy_f = PdfTextExtractor(None)


# Extractors are assumed to be located in the same directory as this file.
AUTONAMEOW_EXTRACTOR_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, AUTONAMEOW_EXTRACTOR_PATH)


def find_extractor_files():
    """
    Finds and imports Python source files assumed to be autonameow extractors.

    Returns: List of found extractor source files basenames.
    """
    extractor_files = [x for x in os.listdir(AUTONAMEOW_EXTRACTOR_PATH)
                       if x.endswith('.py')
                       and x != 'extractor.py'
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

        print(namespace)

        for _obj_name, _obj_type in namespace:
            if _obj_name == 'Extractor':
                continue
            if not issubclass(_obj_type, Extractor):
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
    klasses = [k for k in globals()['MetadataExtractor'].__subclasses__()]

    out = set()
    for e in klasses:
        if e.data_query_string:
            out.add(e.data_query_string)
    return out


ExtractorClasses = get_extractor_classes(find_extractor_files())
ExtractorQueryStrings = get_query_strings()
MetadataExtractorQueryStrings = get_metadata_query_strings()
