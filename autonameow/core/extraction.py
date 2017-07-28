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

import extractors
from core import (
    constants,
    util,
    types
)
from core.exceptions import InvalidDataSourceError
from core.util.queue import GenericQueue


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

        # TODO: [TD0056] Determine which extractors should be used.
        required_extractors = []

        # Select extractors based on detected file type.
        classes = extractors.suitable_data_extractors_for(self.file_object)

        # Exclude "slow" extractors if they are not explicitly required.
        classes = keep_slow_extractors_if_required(classes, required_extractors)

        log.debug('Got {} suitable extractors'.format(len(classes)))
        instances = self._instantiate_extractors(classes)

        # TODO: [TD0013] Add conditional extraction.
        # TODO: [TD0056] Add conditional extraction.

        for e in instances:
            self.extractor_queue.enqueue(e)
        log.debug('Enqueued extractors: {!s}'.format(self.extractor_queue))

        # Add information from 'FileObject' to results.
        # TODO: [TD0053] Fix special case of collecting data from 'FileObject'.

        # TODO: Move this to a "PlatformIndependentFilesystemExtractor"?
        # NOTE: Move would make little sense aside from maybe being
        #       a bit more consistent with the class hierarchy, etc.

        # NOTE(jonas): Store bytestring versions of original file name
        # components? If the user wants to use parts of the original file
        # name in the new name, conversion can't be lossy. Solve by storing
        # bytestring versions of these fields as well?
        self.collect_results('filesystem.basename.full',
                             types.AW_PATH(self.file_object.filename))
        self.collect_results('filesystem.basename.extension',
                             types.AW_PATH(self.file_object.suffix))
        self.collect_results('filesystem.basename.suffix',
                             types.AW_PATH(self.file_object.suffix))
        self.collect_results('filesystem.basename.prefix',
                             types.AW_PATH(self.file_object.fnbase))
        self.collect_results('filesystem.pathname.full',
                             types.AW_PATH(self.file_object.pathname))
        self.collect_results('filesystem.pathname.parent',
                             types.AW_PATH(self.file_object.pathparent))
        self.collect_results('contents.mime_type',
                             self.file_object.mime_type)

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
        if label is not None:
            if label not in constants.VALID_DATA_SOURCES:
                log.critical(
                    'ExtractedData.get() got bad label: "{}"'.format(label)
                )
            return self._data.get(label, False)
        else:
            return self._data

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


def keep_slow_extractors_if_required(extractor_klasses, required_extractors):
    """
    Filters out "slow" extractor classes if they are not explicitly required.

    If the extractor class variable 'is_slow' is True, the extractor is
    excluded if the same class is not specified in 'required_extractors'.

    Args:
        extractor_klasses: List of extractor classes to filter.
        required_extractors: List of required extractor classes.

    Returns:
        A list of extractor classes, including "slow" classes only if required.
    """
    out = []

    for klass in extractor_klasses:
        if klass.is_slow is True:
            if klass in required_extractors:
                out.append(klass)
                log.debug(
                    'Included required slow extractor "{!s}"'.format(klass)
                )
            else:
                log.debug(
                    'Excluded slow extractor "{!s}"'.format(klass)
                )
        else:
            out.append(klass)

    return out
