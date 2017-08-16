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

import analyzers
from core import (
    exceptions,
    util,
    repository
)
from core.fileobject import FileObject


class Analysis(object):
    """
    Performs high-level handling of an analysis.

    A run queue is populated based on which analyzers are suited for the
    current file.  The enqueued analyzers are executed and any results are
    passed back through a callback function.
    """
    def __init__(self, file_object):
        """
        Setup an analysis of a given file. This is done once per file.

        Args:
            file_object: File to analyze as an instance of class 'FileObject'.
        """
        if not isinstance(file_object, FileObject):
            raise TypeError('Argument must be an instance of "FileObject"')
        self.file_object = file_object

        self.add_pool_data = repository.SessionRepository.store
        self.request_data = repository.SessionRepository.resolve

        self.analyzer_queue = AnalysisRunQueue()

    def collect_results(self, label, data):
        """
        Collects analysis results. Passed to analyzers as a callback.

        Analyzers call this to store collected data.

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
        assert label is not None and isinstance(label, str)

        if isinstance(data, dict):
            flat_data = util.flatten_dict(data)
            for k, v in flat_data.items():
                merged_label = label + '.' + str(k)
                self.collect_data(merged_label, v)
        else:
            self.collect_data(label, data)

    def collect_data(self, label, data):
        self.add_pool_data(self.file_object, label, data)

    def start(self):
        """
        Starts the analysis by populating and executing the run queue.
        """
        log.debug('File is of type "{!s}"'.format(self.file_object.mime_type))
        self._populate_run_queue()

        # Run all analyzers in the queue.
        self._execute_run_queue()

        # TODO: Fix or remove result count tally.
        # log.info('Finished executing {} analyzers. Got {} results'.format(
        #     len(self.analyzer_queue), len(self.results)
        # ))

    def _populate_run_queue(self):
        """
        Populate the run queue with analyzers suited for the given file.
        """

        classes = analyzers.suitable_analyzers_for(self.file_object)
        if not classes:
            raise exceptions.AutonameowException(
                'None of the analyzers applies (!)'
            )

        analyzer_instances = self._instantiate_analyzers(classes)
        for a in analyzer_instances:
            self.analyzer_queue.enqueue(a)
        log.debug('Enqueued analyzers: {!s}'.format(self.analyzer_queue))

    def _instantiate_analyzers(self, class_list):
        """
        Get a list of class instances from a given list of classes.

        Args:
            class_list: The classes to instantiate as a list of type 'class'.

        Returns:
            One instance of each of the given classes as a list of objects.
        """
        return [a(self.file_object, self.collect_results, self.request_data)
                for a in class_list]

    def _execute_run_queue(self):
        """
        Executes analyzers in the analyzer run queue.
        """
        for i, a in enumerate(self.analyzer_queue):
            log.debug('Executing queue item {}/{}: '
                      '{!s}'.format(i + 1, len(self.analyzer_queue), a))
            if not a:
                log.critical('Got undefined analyzer from the run queue (!)')
                continue

            log.debug('Running Analyzer "{!s}"'.format(a))
            a.run()
            log.debug('Finished running "{!s}"'.format(a))


def include_analyzer_name(result_list, source):
    out = []
    for result in result_list:
        result['analyzer'] = str(source)
        out.append(result)
    return out


class AnalysisRunQueue(util.GenericQueue):
    """
    Execution queue for analyzers.

    The queue order is determined by the class variable "run_queue_priority".
    """
    def __init__(self):
        super().__init__()

    def enqueue(self, analyzer):
        """
        Adds a analyzer to the queue.

        The queue acts as a set; duplicate analyzers are silently ignored.

        Args:
            analyzer: Analyzer to enqueue as type 'type'.
        """
        if analyzer not in self._items:
            self._items.insert(0, analyzer)

    def __iter__(self):
        for item in sorted(self._items, key=lambda x: x.run_queue_priority):
            yield item

    def __str__(self):
        out = []
        for pos, item in enumerate(self):
            out.append('{:02d}: {!s}'.format(pos, item))
        return ', '.join(out)
