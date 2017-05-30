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

from core.analyze.analyze_abstract import (
    get_analyzer_classes_basename,
    get_analyzer_mime_mappings
)
from core.analyze.analyze_filename import FilenameAnalyzer
from core.analyze.analyze_filesystem import FilesystemAnalyzer
from core.config.constants import ANALYSIS_RESULTS_FIELDS


class AnalysisRunQueue(object):
    """
    Execution queue for analyzers.

    The queue order is determined by the class variable "run_queue_priority".
    """
    def __init__(self):
        self._queue = []

    def enqueue(self, analyzer):
        """
        Adds one or more analyzers to the queue.

        Args:
            analyzer: Analyzer(s) to enqueue as either type 'type' or
                list of type 'type'.
        """
        if isinstance(analyzer, list):
            self._queue += analyzer
        else:
            self._queue.append(analyzer)

    def __len__(self):
        return len(self._queue)

    def __getitem__(self, item):
        return self._queue[item]

    def __iter__(self):
        for a in sorted(self._queue, key=lambda x: x.run_queue_priority):
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
            file_object (FileObject): File to analyze.
        """
        assert file_object is not None
        self.file_object = file_object

        self.results = Results()

        # List of analyzers to run.
        # Start with a basic analyzer that is common to all file types.
        self.analysis_run_queue = AnalysisRunQueue()
        self.analysis_run_queue.enqueue([FilesystemAnalyzer, FilenameAnalyzer])

        self.start()

    def start(self):
        # Select analyzer based on detected file type.
        log.debug('File is of type [{!s}]'.format(self.file_object.type))
        self._populate_run_queue()
        log.debug('Queued analyzers: {!s}'.format(self.analysis_run_queue))

        # Run all analyzers in the queue.
        self._execute_run_queue()

    def _populate_run_queue(self):
        """
        Populate the analysis run queue with analyzers that will be executed.

        Note:
            Includes only analyzers whose MIME type ('applies_to_mime')
            matches the MIME type of the current file object.
        """
        # Compare file mime type with entries from get_analyzer_mime_mappings().
        found_azr = None
        for azr, tpe in get_analyzer_mime_mappings().items():
            if found_azr is not None:
                break
            if isinstance(tpe, list):
                for t in tpe:
                    if t == self.file_object.type:
                        found_azr = azr
            else:
                if tpe == self.file_object.type:
                    found_azr = azr

        # Append any matches to the analyzer run queue.
        if found_azr:
            log.debug('Appending "{!s}" to analysis run queue'.format(found_azr))
            self.analysis_run_queue.enqueue(found_azr)
        else:
            log.debug('File type ({!s}) is not yet mapped to a type-specific '
                      'Analyzer.'.format(self.file_object.type))

    def _execute_run_queue(self):
        """
        Executes analyzers in the analyzer run queue.

        Analyzers are called sequentially, results are stored in 'self.results'.
        """
        for i, analysis in enumerate(self.analysis_run_queue):
            log.debug('Executing enqueued analyzer {}/{}: '
                      '{}'.format(i + 1,
                                  len(self.analysis_run_queue),
                                  analysis.__name__))
            if not analysis:
                log.error('Got null analysis from analysis run queue.')
                continue

            a = analysis(self.file_object)
            if not a:
                log.error('Unable to start Analyzer "{!s}"'.format(analysis))
                continue

            # Run the analysis and collect the results.
            a.run()
            for field in ANALYSIS_RESULTS_FIELDS:
                try:
                    result = a.get(field)
                except NotImplementedError as e:
                    log.warning('Called unimplemented code: {!s}'.format(e))
                    result = None

                self.results.add(field, result, str(a.__class__.__name__))

    def get_datetime_by_alias(self, alias):
        pass
        # ALIAS_LOOKUP = {
        #     'accessed': f for f in self.results['datetime']['FilesystemAnalyzer'] if f['source'] == 'accessed',
        #     'very_special_case': None
        # }
