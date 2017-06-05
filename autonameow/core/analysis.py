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

from analyzers.analyze_abstract import (
    get_analyzer_mime_mappings
)
from core import constants
from core.exceptions import AutonameowException
from core.fileobject import FileObject


class AnalysisRunQueue(object):
    """
    Execution queue for analyzers.

    The queue order is determined by the class variable "run_queue_priority".
    """
    def __init__(self):
        self.__queue = []

    def enqueue(self, analyzers):
        """
        Adds one or more analyzers to the queue.

        The queue acts as a set; duplicate analyzers are silently ignored.

        Args:
            analyzers: Analyzer(s) to enqueue as either type 'type' or
                list of type 'type'.
        """
        def _dupe_check_append(_analyzer):
            if _analyzer not in self.__queue:
                self.__queue.append(_analyzer)

        if isinstance(analyzers, list):
            for a in analyzers:
                _dupe_check_append(a)
        else:
            _dupe_check_append(analyzers)

    def __len__(self):
        return len(self.__queue)

    def __getitem__(self, item):
        return self.__queue[item]

    def __iter__(self):
        for a in sorted(self.__queue, key=lambda x: x.run_queue_priority):
            yield a

    def __str__(self):
        out = []
        for i, a in enumerate(self):
            out.append('{:02d}: {}'.format(i, a.__name__))
        return ', '.join(out)


class Results(object):
    """
    Container for results gathered during an analysis of a file.
    """

    def __init__(self):
        self._data = {}
        for field in constants.ANALYSIS_RESULTS_FIELDS:
            self._data[field] = []

        # TODO: Redesign data storage structure.
        self._fixed_data = dict(constants.RESULTS_DATA_STRUCTURE)
        self.new_data = {}

    def query(self, field):
        # TODO: Return result data from a query of type dict.
        #
        # Example query: {'datetime'    = 'metadata.exiftool.DateTimeOriginal'
        #                 'description' = 'plugin.microsoft_vision.caption'
        #                 'extension'   = 'filesystem.extension'}
        #
        # Should return a dictionary with the same keys, data should be strings
        # that will be used to populate the name template.
        pass

    # def __getitem__(self, key):
    # TODO: Implement proper getter method.

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
    The analyses in the run queue is then executed and the results are
    stored as dictionary entries, with the source analyzer name being the key.
    """
    def __init__(self, file_object):
        """
        Starts an analysis of a file. This is done once per file.

        Note:
            Run queue is populated and executed straight away at instantiation.

        Args:
            file_object: File to analyze as an instance of class 'FileObject'.
        """
        if not isinstance(file_object, FileObject):
            raise TypeError('Argument must be an instance of "FileObject"')
        self.file_object = file_object

        self.test_callbacked_results = dict()

        self.results = Results()
        self.analysis_run_queue = AnalysisRunQueue()

    def collect_results(self, label, data):
        """
        Collects analysis results. Passed to analyzers as a callback.

        Analyzers call this to store collected data.

        Args:
            label: Arbitrary label that uniquely identifies the data.
            data: The data to add.
        """
        self.test_callbacked_results.update({label: data})

    def start(self):
        """
        Starts the analysis.
        """
        # Select analyzer based on detected file type.
        log.debug('File is of type "{!s}"'.format(self.file_object.mime_type))
        self._populate_run_queue()
        log.debug('Enqueued analyzers: {!s}'.format(self.analysis_run_queue))

        # Run all analyzers in the queue.
        self._execute_run_queue()

    def _populate_run_queue(self):
        """
        Populate the analysis run queue with analyzers that will be executed.

        Note:
            Includes only analyzers whose MIME type ('applies_to_mime')
            matches the MIME type of the current file object.
        """
        found = []

        # Compare file mime type with entries from get_analyzer_mime_mappings().
        for azr, tpe in get_analyzer_mime_mappings().items():
            if isinstance(tpe, list):
                for t in tpe:
                    if t == self.file_object.mime_type or t == 'MIME_ALL':
                        found.append(azr)
                        log.debug('Enqueueing "{!s}"'.format(azr))
            else:
                if tpe == self.file_object.mime_type or tpe == 'MIME_ALL':
                    found.append(azr)
                    log.debug('Enqueueing "{!s}"'.format(azr))

        # Append any matches to the analyzer run queue.
        if found:
            self.analysis_run_queue.enqueue(found)
        else:
            raise AutonameowException('None of the analyzers applies (!)')

    # def _execute_common_analyzers(self):
    #     filesystem_analyzer = FilesystemAnalyzer()

    def _execute_run_queue(self):
        """
        Executes analyzers in the analyzer run queue.

        Analyzers are called sequentially, results are stored in 'self.results'.
        """
        for i, analysis in enumerate(self.analysis_run_queue):
            log.debug('Executing queue item {}/{}: '
                      '{}'.format(i + 1,
                                  len(self.analysis_run_queue),
                                  analysis.__name__))
            if not analysis:
                log.critical('Got null analysis from analysis run queue.')
                continue

            a = analysis(self.file_object, self.collect_results)
            if not a:
                log.critical('Unable to start Analyzer "{!s}"'.format(analysis))
                continue

            a_name = str(a.__class__.__name__)
            log.debug('Starting Analyzer "{!s}"'.format(a_name))

            # Run the analysis and collect the results.
            a.run()
            for field in constants.ANALYSIS_RESULTS_FIELDS:
                try:
                    result = a.get(field)
                except NotImplementedError as e:
                    log.error('Called unimplemented code in {!s}: '
                              '{!s}'.format(a_name, e))
                    continue

                if not result:
                    continue

                # Add the analyzer name to the results dictionary.
                results = include_analyzer_name(result, a_name)
                self.results.add(field, results)


def include_analyzer_name(result_list, source):
    out = []
    for result in result_list:
        result['analyzer'] = source
        out.append(result)

    return out
