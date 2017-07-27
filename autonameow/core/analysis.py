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
import plugins
from core import (
    constants,
    exceptions,
    util
)
from core.util.queue import GenericQueue


class Analysis(object):
    """
    Performs high-level handling of an analysis.

    A run queue is populated based on which analyzers are suited for the
    current file.  The enqueued analyzers are executed and any results are
    passed back through a callback function.
    """
    def __init__(self, file_object, extracted_data):
        """
        Setup an analysis of a given file. This is done once per file.

        Args:
            file_object: File to analyze as an instance of class 'FileObject'.
            extracted_data: Data from the 'Extraction' instance as an instance
                of the 'ExtractedData' class.
        """
        self.results = AnalysisResults()
        self.analyzer_queue = AnalysisRunQueue()

        self.file_object = file_object

        if extracted_data:
            self.extracted_data = extracted_data

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
        assert data is not None

        if isinstance(data, dict):
            flat_data = util.flatten_dict(data)
            for k, v in flat_data.items():
                merged_label = label + '.' + str(k)
                self.results.add(merged_label, v)
        else:
            self.results.add(label, data)

    def start(self):
        """
        Starts the analysis by populating and executing the run queue.
        """
        log.debug('File is of type "{!s}"'.format(self.file_object.mime_type))
        self._populate_run_queue()

        # Run all analyzers in the queue.
        self._execute_run_queue()

        log.info('Finished executing {} analyzers. Got {} results'.format(
            len(self.analyzer_queue), len(self.results)
        ))

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
        return [a(self.file_object, self.collect_results, self.extracted_data)
                for a in class_list]

    def _execute_run_queue(self):
        """
        Executes analyzers in the analyzer run queue.

        Analyzers are called sequentially, results are stored in 'self.results'.
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


class AnalysisRunQueue(GenericQueue):
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


class AnalysisResults(object):
    """
    Container for results gathered during an analysis of a file.
    """

    def __init__(self):
        self._data = {}

    def query(self, query_string=None):
        """
        Returns analysis data matching the given "query string".

        If the given query string does not map to any data, False is returned.

        Args:
            query_string: The query string key for the data to return.
                Example:  'metadata.exiftool.DateTimeOriginal'

        Returns:
            Results data for the specified fields matching the specified query.
        """
        if not query_string:
            return self._data

        if query_string.startswith('plugin.'):
            # TODO: [TD0009] Results should NOT be querying plugins from here!
            # TODO: [TD0009] Rework processing pipeline to integrate plugins
            plugin_name, plugin_query = query_string.lstrip('plugin.').split('.')
            result = plugins.plugin_query(plugin_name, plugin_query, None)
            return result
        else:
            if query_string in self._data:
                return self._data.get(query_string)
        return False

    def add(self, field, data):
        """
        Adds results data for a specific field to the aggregate data.

        Args:
            field: The field type of the data to add.
                   Must be included in "ANALYSIS_RESULTS_FIELDS".
            data: Data to add as a list of dicts.

        Raises:
            KeyError: The specified field is not in "ANALYSIS_RESULTS_FIELDS".
        """
        if not field:
            raise KeyError('Missing results field')

        self._data.update({field: data})

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
