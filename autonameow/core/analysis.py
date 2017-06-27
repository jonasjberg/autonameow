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
from core import (
    constants,
    exceptions,
    util
)
from core.util.queue import GenericQueue

# TODO: Fix this! Used for instantiating analyzers so that they are
# included in the global namespace and seen by 'get_analyzer_classes()'.
from analyzers.analyzer import Analyzer
from analyzers.analyze_filename import FilenameAnalyzer
from analyzers.analyze_filesystem import FilesystemAnalyzer
from analyzers.analyze_image import ImageAnalyzer
from analyzers.analyze_pdf import PdfAnalyzer
from analyzers.analyze_video import VideoAnalyzer
__dummy_a = Analyzer(None, None, None)
__dummy_b = FilenameAnalyzer(None, None, None)
__dummy_c = FilesystemAnalyzer(None, None, None)
__dummy_d = ImageAnalyzer(None, None, None)
__dummy_e = PdfAnalyzer(None, None, None)
__dummy_f = VideoAnalyzer(None, None, None)


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

        analyzers = suitable_analyzers_for(self.file_object)
        if not analyzers:
            raise exceptions.AutonameowException(
                'None of the analyzers applies (!)'
            )

        analyzer_instances = self._instantiate_analyzers(analyzers)
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

            log.debug('Finished Analyzer "{!s}"'.format(a))


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

    def query(self, query_string):
        """
        Returns analysis data matching the given "query string".

        If the given query string does not map to any data, False is returned.

        Args:
            query_string: The query string key for the data to return.
                Example:  'metadata.exiftool.DateTimeOriginal'

        Returns:
            Results data for the specified fields matching the specified query.
        """
        if query_string.startswith('plugin.'):
            # TODO: Results should NOT be querying plugins from here!
            # TODO: Rework processing pipeline to integrate plugins
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

    def get(self, field=None):
        """
        Returns analysis results data, optionally for the given field.

        Args:
            field: Optional field of analysis results field data to return.
            The field must be one of those defined in "ANALYSIS_RESULTS_FIELD".

        Returns:
            Analysis results data for the given field or all data.
        """
        if field:
            if field not in constants.ANALYSIS_RESULTS_FIELDS:
                raise KeyError('Invalid results field: {}'.format(field))
            else:
                return self._data[field]
        else:
            return self._data

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


def suitable_analyzers_for(file_object):
    """
    Returns analyzer classes that can handle the given file object.

    Args:
        file_object: File to get analyzers for as an instance of 'FileObject'.

    Returns:
        A list of analyzer classes that can analyze the given file.
    """
    return [a for a in AnalyzerClasses if a.can_handle(file_object)]


def get_analyzer_classes():
    """
    Get a list of all available analyzers as a list of "type".
    All classes inheriting from the "Analyzer" class are included.

    Returns:
        All available analyzer classes as a list of type.
    """
    return [klass for klass in globals()['Analyzer'].__subclasses__()]


def get_analyzer_classes_basename():
    """
    Get a list of class base names for all available analyzers.
    All classes inheriting from the "Analyzer" class are included.

    Returns:
        The base names of available analyzer classes as a list of strings.
    """
    return [c.__name__ for c in get_analyzer_classes()]


AnalyzerClasses = get_analyzer_classes()
