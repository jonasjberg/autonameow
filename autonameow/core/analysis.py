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

import logging

import analyzers
from core import (
    exceptions,
    util,
    repository
)
from core.fileobject import FileObject
from extractors import ExtractedData

log = logging.getLogger(__name__)

"""
Performs high-level handling of an analysis.

A run queue is populated based on which analyzers are suited for the
current file.  The enqueued analyzers are executed and any results are
passed back through a callback function.
"""


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


def _execute_run_queue(analyzer_queue):
    """
    Executes analyzers in the analyzer run queue.
    """
    for i, a in enumerate(analyzer_queue):
        log.debug('Executing queue item {}/{}: '
                  '{!s}'.format(i + 1, len(analyzer_queue), a))

        log.debug('Running Analyzer "{!s}"'.format(a))
        a.run()
        log.debug('Finished running "{!s}"'.format(a))


def request_global_data(file_object, meowuri):
    response = repository.SessionRepository.query(file_object, meowuri)
    # TODO: [TD0082] Integrate the 'ExtractedData' class.
    if response is not None and isinstance(response, ExtractedData):
        return response.value
    else:
        return response


def collect_results(file_object, label, data):
    """
    Collects analysis results. Passed to analyzers as a callback.

    Analyzers call this to store results data in the session repository.

    Args:
        file_object: Instance of 'file_object' that produced the data to add.
        label: Label that uniquely identifies the data, as a Unicode str.
        data: The data to add, as any type or container.
    """
    repository.SessionRepository.store(file_object, label, data)


def _instantiate_analyzers(file_object, klass_list):
    """
    Get a list of class instances from a given list of classes.

    Args:
        file_object: The file to analyze.
        klass_list: The classes to instantiate as a list of type 'class'.

    Returns:
        One instance of each of the given classes as a list of objects.
    """
    return [analyzer(file_object,
                     add_results_callback=collect_results,
                     request_data_callback=request_global_data)
            for analyzer in klass_list]


def start(file_object):
    """
    Starts analyzing 'file_object' using all analyzers deemed "suitable".
    """
    if not isinstance(file_object, FileObject):
        raise TypeError('Argument must be an instance of "FileObject"')

    klasses = analyzers.suitable_analyzers_for(file_object)
    if not klasses:
        raise exceptions.AutonameowException(
            'None of the analyzers applies (!)'
        )

    analyzer_queue = AnalysisRunQueue()
    for a in _instantiate_analyzers(file_object, klasses):
        analyzer_queue.enqueue(a)
    log.debug('Enqueued analyzers: {!s}'.format(analyzer_queue))

    # Run all analyzers in the queue.
    _execute_run_queue(analyzer_queue)

