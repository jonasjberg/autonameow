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

from core import constants
from core.exceptions import InvalidDataSourceError
from core.fileobject import FileObject


class Extraction(object):
    """
    Handles "extractors"; subclasses of the 'Extractor' class.
    """
    def __init__(self, file_object):
        """
        Instantiates extraction for a given file. This is done once per file.

        Args:
            file_object: File to extract data from, as a 'FileObject' instance.
        """
        if not isinstance(file_object, FileObject):
            raise TypeError('Argument must be an instance of "FileObject"')
        self.file_object = file_object

        self.data = ExtractedData()

    def collect_results(self, label, data):
        """
        Collects extracted data. Passed to extractors as a callback.

        Args:
            label: Label that identifies the data. Should be one of the string
                defined in "constants.VALID_DATA_SOURCES".
            data: The data to add.
        """
        self.data.add(label, data)

    def start(self):
        """
        Starts the data extraction.
        """
        log.debug('Started data extraction')
        # Select extractors based on detected file type.
        log.debug('File is of type "{!s}"'.format(self.file_object.mime_type))

        # TODO: Get extractors suited for the given file.
        e = suitable_data_extractors_for(self.file_object)

        # TODO: Use a "run queue" is in the 'Analysis' class?
        # log.debug('Enqueued extractors: {!s}'.format(self.run_queue))

        # Add information from 'FileObject' to results.
        self.collect_results('filesystem.basename.full',
                             self.file_object.filename)
        self.collect_results('filesystem.basename.extension',
                             self.file_object.suffix)
        self.collect_results('filesystem.basename.suffix',
                             self.file_object.suffix)
        self.collect_results('filesystem.basename.prefix',
                             self.file_object.fnbase)
        self.collect_results('filesystem.pathname.full',
                             self.file_object.pathname)
        self.collect_results('filesystem.pathname.parent',
                             self.file_object.pathparent)

        # TODO: Execute all suitable extractors and collect results.
        # Run all extractors in the queue.
        # self._execute_run_queue()


class ExtractedData(object):
    """
    Container for data gathered by extractors.
    """
    def __init__(self):
        self._data = {}

    def add(self, label, data):
        if not data:
            return
        if not label or label not in constants.VALID_DATA_SOURCES:
            raise InvalidDataSourceError('Invalid source: "{}"'.format(label))
        else:
            # TODO: Necessary to handle multiple adds to the same label?
            if label in self._data:
                t = self._data[label]
                self._data[label] = [t] + [data]
            else:
                self._data[label] = data

    def get(self, label):
        """
        Returns extracted data matching the specified label.

        Args:
            One of the strings defined in "constants.VALID_DATA_SOURCES".
        Returns:
            Extracted data associated with the given label, or False if the
            data does not exist.
        Raises:
            InvalidDataSourceError: The label is not a valid data source.
        """
        if not label or label not in constants.VALID_DATA_SOURCES:
            raise InvalidDataSourceError('Invalid label: "{}"'.format(label))

        return self._data.get(label, False)

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
    # TODO: Implment ..
    pass
