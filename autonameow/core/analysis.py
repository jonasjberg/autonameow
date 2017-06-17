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

import plugins
from analyzers.analyzer import (
    get_analyzer_classes
)
from core import constants
from core.exceptions import (
    AutonameowException
)
from core.util.queue import GenericQueue


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
        for field in constants.ANALYSIS_RESULTS_FIELDS:
            self._data[field] = []

        # TODO: Replace all "old style" storage with redesigned storage.
        self.new_data = {}

    def query(self, field_data_source_map):
        """
        Returns result data fields matching a "query string".

        Args:
            field_data_source_map: Dictionary of fields and query string.

                Example: {'datetime'    = 'metadata.exiftool.DateTimeOriginal'
                          'description' = 'plugin.microsoft_vision.caption'
                          'extension'   = 'filesystem.extension'}

        Returns:
            Results data for the specified fields matching the specified query.
        """
        out = {}

        for field, source in field_data_source_map.items():

            # TODO: Fix hacky word splitting to keys for dictionary access.
            # NOTE: The stored data should already have been pre-processed
            #       to allow direct queries without having to modify
            #       "field_data_source_map" here.
            if source.startswith('metadata.exiftool'):
                key = source.lstrip('metadata.exiftool')

                # TODO: Handle querying missing data.
                if 'metadata.exiftool' in self.new_data:
                    out[field] = self.new_data['metadata.exiftool'].get(key)
                else:
                    return False

            elif source.startswith('plugin.'):
                # TODO: Results should NOT be querying plugins from here!
                # TODO: Rework processing pipeline to integrate plugins
                plugin_name, plugin_query = source.lstrip('plugin.').split('.')
                result = plugins.plugin_query(plugin_name, plugin_query, None)
                out[field] = result
            else:
                out[field] = self.new_data.get(source)

        return out

    def new_add(self, label, data):
        # TODO: FIX ME! Should replace "old add".
        self.new_data.update({label: data})

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
        if field not in constants.ANALYSIS_RESULTS_FIELDS:
            raise KeyError('Invalid results field: {}'.format(field))

        self._data[field] += data

    def get(self, field):
        """
        Returns all analysis results data for the given field.

        Args:
            field: Analysis results field data to return.
            The field must be one of those defined in "ANALYSIS_RESULTS_FIELD".

        Returns:
            All analysis results data for the given field.
        """
        if field not in constants.ANALYSIS_RESULTS_FIELDS:
            raise KeyError('Invalid results field: {}'.format(field))

        return self._data[field]

    def get_all(self):
        """
        Returns all analysis results data.

        Returns:
            All analysis results data.
        """
        return self._data


class Analysis(object):
    """
    Handles the filename analyzer and analyzers specific to file content.

    A run queue is populated based on which analyzers are suited for the
    current file.
    The analyses in the run queue are executed and any results are
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

            # TODO: Improve handling of incoming data from 'Extraction'.
            for key, value in extracted_data:
                self.collect_results(key, value)

    def collect_results(self, label, data):
        """
        Collects analysis results. Passed to analyzers as a callback.

        Analyzers call this to store collected data.

        Args:
            label: Label that uniquely identifies the data.
            data: The data to add.
        """
        # NOTE: Flatten dictionary in results here? That is, for example;
        #
        #       Incoming arguments:
        #       LABEL: 'metadata.exiftool'     DATA: {'a': 'b', 'c': 'd'}
        #
        #       Would be "flattened" to:
        #       LABEL: 'metadata.exiftool.a'   DATA: 'b'
        #       LABEL: 'metadata.exiftool.c'   DATA: 'd'
        #
        self.results.new_add(label, data)

    def start(self):
        """
        Starts the analysis.
        """
        # Select analyzer based on detected file type.
        log.debug('File is of type "{!s}"'.format(self.file_object.mime_type))
        self._populate_run_queue()
        log.debug('Enqueued analyzers: {!s}'.format(self.analyzer_queue))

        # Run all analyzers in the queue.
        self._execute_run_queue()

    def _populate_run_queue(self):
        """
        Populate the run queue with analyzers suited for the given file.
        """

        analyzers = suitable_analyzers_for(self.file_object)
        if not analyzers:
            raise AutonameowException('None of the analyzers applies (!)')

        analyzer_instances = self.instantiate_analyzers(analyzers)
        for a in analyzer_instances:
            self.analyzer_queue.enqueue(a)
        log.debug('Enqueued analyzers: {!s}'.format(self.analyzer_queue))

    def instantiate_analyzers(self, class_list):
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
                log.critical('Got null a from a run queue.')
                continue

            log.debug('Starting Analyzer "{!s}"'.format(a))
            a.run()

            # TODO: Remove, use callbacks instead.
            for field in constants.ANALYSIS_RESULTS_FIELDS:
                try:
                    result = a.get(field)
                except NotImplementedError as e:
                    log.debug('[WARNING] Called unimplemented code in {!s}: '
                              '{!s}'.format(a, e))
                    continue

                if not result:
                    continue

                # Add the analyzer name to the results dictionary.
                results = include_analyzer_name(result, a)
                self.results.add(field, results)


def include_analyzer_name(result_list, source):
    out = []
    for result in result_list:
        result['analyzer'] = str(source)
        out.append(result)

    return out


def suitable_analyzers_for(file_object):
    """
    Returns analyzer classes that can handle the given file object.

    Args:
        file_object: File to get analyzers for as an instance of 'FileObject'.

    Returns:
        A list of analyzer classes that can analyze the given file.
    """
    out = []

    # NOTE: Below "or get_analyzer_classes()" is a fix for the unit tests.
    for analyzer in AnalyzerClasses or get_analyzer_classes():
        if (file_object.mime_type in analyzer.handles_mime_types or
                'MIME_ALL' in analyzer.handles_mime_types):
            out.append(analyzer)

    return out


AnalyzerClasses = get_analyzer_classes()
