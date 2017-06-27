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

import logging as log

from core import (
    constants,
    util
)
from core.exceptions import InvalidDataSourceError
from core.util.queue import GenericQueue

# TODO: [hack] Fix this! Used for instantiating extractors so that they are
# included in the global namespace and seen by 'get_extractor_classes()'.
from extractors.extractor import Extractor
from extractors.metadata import MetadataExtractor
from extractors.metadata import ExiftoolMetadataExtractor
from extractors.metadata import PyPDFMetadataExtractor
from extractors.textual import TextExtractor
from extractors.textual import PdfTextExtractor
__dummy_a = Extractor(None)
__dummy_b = MetadataExtractor(None)
__dummy_c = ExiftoolMetadataExtractor(None)
__dummy_d = PyPDFMetadataExtractor(None)
__dummy_e = TextExtractor(None)
__dummy_f = PdfTextExtractor(None)


class Extraction(object):
    """
    Performs high-level handling of data extraction.

    A run queue is populated with extractors suited for the current file.
    The enqueued extractors are executed and any results are passed back
    through a callback function.
    """
    def __init__(self, file_object):
        """
        Instantiates extraction for a given file. This is done once per file.

        Args:
            file_object: File to extract data from, as a 'FileObject' instance.
        """
        self.file_object = file_object

        self.data = ExtractedData()
        self.extractor_queue = GenericQueue()

    def collect_results(self, label, data):
        """
        Collects extracted data. Passed to extractors as a callback.

        If argument "data" is a dictionary, it is "flattened" here.
        Example:

          Incoming arguments:
          LABEL: 'metadata.exiftool'     DATA: {'a': 'b', 'c': 'd'}

          Would be "flattened" to:
          LABEL: 'metadata.exiftool.a'   DATA: 'b'
          LABEL: 'metadata.exiftool.c'   DATA: 'd'

        Args:
            label: Label that uniquely identifies the data.
            data: The data to add.
        """
        if not label:
            raise InvalidDataSourceError('Missing required argument "label"')
        if not isinstance(label, str):
            raise InvalidDataSourceError('Argument "label" must be of type str')

        if isinstance(data, dict):
            flat_data = util.flatten_dict(data)
            for k, v in flat_data.items():
                merged_label = label + '.' + str(k)
                self.data.add(merged_label, v)
        else:
            self.data.add(label, data)

    def start(self):
        """
        Starts the data extraction.
        """
        log.debug('Started data extraction')

        # Select extractors based on detected file type.
        extractors = suitable_data_extractors_for(self.file_object)
        extractor_instances = self._instantiate_extractors(extractors)
        log.debug('Got {} suitable extractors'.format(len(extractors)))

        for e in extractor_instances:
            self.extractor_queue.enqueue(e)
        log.debug('Enqueued extractors: {!s}'.format(self.extractor_queue))

        # Add information from 'FileObject' to results.
        # TODO: Move this to a "PlatformIndependentFilesystemExtractor"?
        # NOTE: Move would make little sense aside from maybe being
        #       a bit more consistent with the class hierarchy, etc.

        # NOTE(jonas): Store bytestring versions of original file name
        # components? If the user wants to use parts of the original file
        # name in the new name, conversion can't be lossy. Solve by storing
        # bytestring versions of these fields as well?

        # TODO: [encoding] Enforce encoding boundary for extracted data.
        self.collect_results('filesystem.basename.full',
                             util.decode_(self.file_object.filename))
        self.collect_results('filesystem.basename.extension',
                             util.decode_(self.file_object.suffix))
        self.collect_results('filesystem.basename.suffix',
                             util.decode_(self.file_object.suffix))
        self.collect_results('filesystem.basename.prefix',
                             util.decode_(self.file_object.fnbase))
        self.collect_results('filesystem.pathname.full',
                             util.decode_(self.file_object.pathname))
        self.collect_results('filesystem.pathname.parent',
                             util.decode_(self.file_object.pathparent))

        # Execute all suitable extractors and collect results.
        self._execute_run_queue()

        log.info('Finished executing {} extractors. Got {} results'.format(
            len(self.extractor_queue), len(self.data)
        ))

    def _instantiate_extractors(self, class_list):
        """
        Get a list of class instances from a given list of classes.

        Args:
            class_list: The classes to instantiate as a list of type 'class'.

        Returns:
            One instance of each of the given classes as a list of objects.
        """
        data_source = self.file_object.abspath
        return [e(data_source) for e in class_list]

    def _execute_run_queue(self):
        """
        Executes all enqueued extractors and collects the results.
        """
        for i, e in enumerate(self.extractor_queue):
            log.debug('Executing queue item {}/{}: '
                      '{!s}'.format(i + 1, len(self.extractor_queue), e))

            self.collect_results(e.data_query_string, e.query())


class ExtractedData(object):
    """
    Container for data gathered by extractors.
    """
    def __init__(self):
        self._data = {}

    def add(self, label, data):
        if not data:
            return
        if not label:
            raise InvalidDataSourceError('Invalid source (missing label)')
        else:
            # TODO: Necessary to handle multiple adds to the same label?
            if label in self._data:
                t = self._data[label]
                self._data[label] = [t] + [data]
            else:
                self._data[label] = data

    def get(self, label=None):
        """
        Returns extracted data, optionally matching the specified label.

        Args:
            One of the strings defined in "constants.VALID_DATA_SOURCES".
        Returns:
            Extracted data associated with the given label, or False if the
            data does not exist. If no label is specified, all data is returned.
        Raises:
            InvalidDataSourceError: The label is not a valid data source.
        """
        # TODO: Methods 'get' and 'query' perform essentially the same task?
        if label is not None:
            if label not in constants.VALID_DATA_SOURCES:
                raise InvalidDataSourceError(
                    'Invalid label: "{}"'.format(label)
                )
            else:
                return self._data.get(label, False)
        else:
            return self._data

    def query(self, query_string):
        """
        Returns extracted data for the given "query string".

        If the given query string does not map to any data, False is returned.

        Args:
            query_string: The query string key for the data to return.
                Example:  'metadata.exiftool.DateTimeOriginal'

        Returns:
            Extracted data for matching the specified query string or False.
        """
        # TODO: Methods 'get' and 'query' perform essentially the same task?
        if query_string in self._data:
            return self._data.get(query_string)
        return False

    def __iter__(self):
        for k, v in self._data.items():
            yield (k, v)

    def __len__(self):
        def count_dict_recursive(dictionary, count):
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    count_dict_recursive(value, count)
                elif value:
                    if isinstance(value, list):
                        for v in value:
                            if v:
                                count += 1
                    else:
                        count += 1

            return count

        return count_dict_recursive(self._data, 0)


def suitable_data_extractors_for(file_object):
    """
    Returns extractor classes that can handle the given file object.

    Args:
        file_object: File to get extractors for as an instance of 'FileObject'.

    Returns:
        A list of extractor classes that can extract data from the given file.
    """
    return [e for e in ExtractorClasses if e.can_handle(file_object)]


def get_extractor_classes():
    """
    Get a list of all available extractors as a list of "type".
    All classes inheriting from the "Extractor" class are included.

    Returns:
        All available extractor classes as a list of type.
    """
    # TODO: Include ALL extractors!
    out = ([klass for klass in globals()['MetadataExtractor'].__subclasses__()]
           + [klass for klass in globals()['TextExtractor'].__subclasses__()])
    return out


ExtractorClasses = get_extractor_classes()
