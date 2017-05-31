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
    get_analyzer_classes_basename,
    get_analyzer_mime_mappings
)
from core.config.constants import ANALYSIS_RESULTS_FIELDS
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
        for field in ANALYSIS_RESULTS_FIELDS:
            self._data[field] = {}

        # TODO: Redesign data storage structure.
        # self._fixed_data = {'filename'}

    def add(self, field, data, source):
        """
        Adds results from an analyzer.

        Args:
            field: Analysis results field to add.
            data: The results data to add, as a list of dicts.
            source: Class name of the source analyzer.
        """
        if field not in ANALYSIS_RESULTS_FIELDS:
            raise KeyError('Invalid results field: {}'.format(field))

        if source not in get_analyzer_classes_basename():
            raise TypeError('Invalid source analyzer: {}'.format(source))

        self._data[field][source] = data

    def get(self, field):
        """
        Returns all analysis results data for the given field.

        Args:
            field: Analysis results field data to return.
            The field must be one of those defined in "ANALYSIS_RESULTS_FIELD".

        Returns:
            All analysis results data for the given field.
        """
        if field not in ANALYSIS_RESULTS_FIELDS:
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

        self.results = Results()
        self.analysis_run_queue = AnalysisRunQueue()

    def start(self):
        """
        Starts the analysis.
        """
        # Select analyzer based on detected file type.
        log.debug('File is of type [{!s}]'.format(self.file_object.type))
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
                    if t == self.file_object.type or t == 'MIME_ALL':
                        found.append(azr)
                        log.debug('Enqueueing "{!s}"'.format(azr))
            else:
                if tpe == self.file_object.type or tpe == 'MIME_ALL':
                    found.append(azr)
                    log.debug('Enqueueing "{!s}"'.format(azr))

        # Append any matches to the analyzer run queue.
        if found:
            self.analysis_run_queue.enqueue(found)
        else:
            raise AutonameowException('This should not happen!')

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

            a = analysis(self.file_object)
            if not a:
                log.critical('Unable to start Analyzer "{!s}"'.format(analysis))
                continue

            # Run the analysis and collect the results.
            a.run()
            for field in ANALYSIS_RESULTS_FIELDS:
                try:
                    result = a.get(field)
                except NotImplementedError as e:
                    log.error('Called unimplemented code: {!s}'.format(e))
                    result = None

                self.results.add(field, result, str(a.__class__.__name__))

    def get_datetime_by_alias(self, alias):
        pass
        # ALIAS_LOOKUP = {
        #     'accessed': f for f in self.results['datetime']['FilesystemAnalyzer'] if f['source'] == 'accessed',
        #     'very_special_case': None
        # }
