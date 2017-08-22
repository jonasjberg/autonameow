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
    util,
    repository
)


class Extraction(object):
    """
    Performs high-level handling of data extraction.

    A run queue is populated with extractors suited for the current file.
    """
    def __init__(self, file_object,
                 require_extractors=None,
                 require_all_extractors=False):
        """
        Instantiates extraction for a given file. This is done once per file.

        Args:
            file_object: File to extract data from, as a 'FileObject' instance.
        """
        self.file_object = file_object
        self.require_extractors = require_extractors
        self.require_all_extractors = require_all_extractors

        self.add_to_global_data = repository.SessionRepository.store

        self.extractor_queue = util.GenericQueue()

    def collect_results(self, label, data):
        """
        Collects extractor data, passes it the the session repository.

        Args:
            label: Label that uniquely identifies the data.
            data: The data to add.
        """
        self.add_to_global_data(self.file_object, label, data)

    def start(self):
        """
        Starts the data extraction.
        """
        log.debug('Started data extraction')

        if self.require_extractors:
            required_extractors = self.require_extractors
            log.debug('Required extractors: {!s}'.format(required_extractors))
        else:
            required_extractors = []

        # Get all extractors that can handle the current file.
        classes = extractors.suitable_data_extractors_for(self.file_object)
        log.debug('Extractors able to handle the file: {}'.format(len(classes)))

        if not self.require_all_extractors:
            # Exclude "slow" extractors if they are not explicitly required.
            classes = keep_slow_extractors_if_required(classes,
                                                       required_extractors)

        log.debug('Got {} suitable extractors'.format(len(classes)))

        for instance in self._instantiate_extractors(classes):
            self.extractor_queue.enqueue(instance)
        log.debug('Enqueued extractors: {!s}'.format(self.extractor_queue))

        # Execute all suitable extractors and collect results.
        self._execute_run_queue()

        # TODO: Fix or remove result count tally.
        # log.info('Finished executing {} extractors. Got {} results'.format(
        #     len(self.extractor_queue), len(self.data)
        # ))

    def _instantiate_extractors(self, class_list):
        """
        Get a list of class instances from a given list of classes.

        Args:
            class_list: The classes to instantiate as a list of type 'class'.

        Returns:
            One instance of each of the given classes as a list of objects.
        """
        instances = []

        for klass in class_list:
            if klass.__name__ == 'CommonFileSystemExtractor':
                # Special case where the source should be a 'FileObject'.
                instances.append(klass(self.file_object))
            else:
                instances.append(klass(self.file_object.abspath))

        return instances

    def _execute_run_queue(self):
        """
        Executes all enqueued extractors and collects the results.
        """
        for i, e in enumerate(self.extractor_queue):
            log.debug('Executing queue item {}/{}: '
                      '{!s}'.format(i + 1, len(self.extractor_queue), e))

            self.collect_results(e.data_query_string, e.query())


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
