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

from core.util import misc
from core.analyze.analyze_filename import FilenameAnalyzer
from core.analyze.analyze_filesystem import FilesystemAnalyzer

# NOTE: Below imports needed by unit tests, do not "optimize".
from core.analyze.analyze_pdf import PdfAnalyzer
from core.analyze.analyze_image import ImageAnalyzer
from core.analyze.analyze_text import TextAnalyzer
from core.analyze.analyze_video import VideoAnalyzer


# Collect all analyzers from their class name.
_ALL_ANALYZER_CLASSES = [
        klass
        for name, klass in list(globals().items())
        if name.endswith('Analyzer') and name != 'AbstractAnalyzer'
    ]


def get_analyzer_classes():
    """
    Returns:
        All analyzer classes in '_ALL_ANALYZER_CLASSES' as a list of type.
    """
    return _ALL_ANALYZER_CLASSES


def get_instantiated_analyzers():
    """
    Returns:
        A list of instantiated analyzers (all analyzers as objects)
        defined in '_ALL_ANALYZER_CLASSES'.
    """
    # NOTE: These are instantiated with a None FIleObject, which might be a
    #       problem and is surely not very pretty.
    return [klass(None) for klass in get_analyzer_classes()]


def get_analyzer_mime_mappings():
    """
    Provides a mapping of which analyzers should apply to which mime types.

    Returns:
        Dictionary of strings or list of strings.
        The dictionary is keyed by the class names of all analyzers,
        storing the class variable 'applies_to_mime' from each analyzer.
    """
    analyzer_mime_mappings = {}
    for azr in get_instantiated_analyzers():
        analyzer_mime_mappings[azr.__class__] = azr.applies_to_mime
    return analyzer_mime_mappings


class AnalysisRunQueue(object):
    """
    Stores references to all analyzers to be executed.

    Essentially a glorified list, motivated by future expansion.
    """
    def __init__(self):
        self._queue = []

    def enqueue(self, analysis):
        """
        Adds a analysis to the queue.

        Args:
            analysis: Analysis to enqueue, either single instance or list.
        """
        if isinstance(analysis, list):
            self._queue += analysis
        else:
            self._queue.append(analysis)

    def __len__(self):
        return len(self._queue)

    def __getitem__(self, item):
        return self._queue[item]

    def __iter__(self):
        for a in sorted(self._queue, key=lambda x: x.run_queue_priority):
            yield a


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

        # TODO: [BL006] Reevaluate/redesign internal metadata storage format.
        self.results = {'datetime': {},
                        'publisher': {},
                        'title': {},
                        'tags': {},
                        'author': {}}

        # List of analyzers to run.
        # Start with a basic analyzer that is common to all file types.
        self.analysis_run_queue = AnalysisRunQueue()
        self.analysis_run_queue.enqueue([FilesystemAnalyzer, FilenameAnalyzer])

        self.start()

    def start(self):
        # Select analyzer based on detected file type.
        logging.debug('File is of type [{}]'.format(self.file_object.type))
        self._populate_run_queue()

        # Run all analyzers in the queue.
        self._execute_run_queue()

    def _populate_run_queue(self):
        """
        Populate the list of analyzers to run.

        Note:
            Imports are done locally for performance reasons.
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
            logging.debug('Appending "{}" to analysis run queue'.format(found_azr))
            self.analysis_run_queue.enqueue(found_azr)
        else:
            logging.debug('File type ({}) is not yet mapped to a type-specific '
                          'Analyzer.'.format(self.file_object.type))

    def _execute_run_queue(self):
        """
        Executes analyzers in the analyzer run queue.

        This does all the real work. Analyzers are called in turn and their
        results are stored to `self.results`.

        Note:
            Still a work in progress.
        """
        for i, analysis in enumerate(self.analysis_run_queue):
            logging.debug('Executing analysis run queue item '
                          '[{}/{}]'.format(i + 1, len(self.analysis_run_queue)))
            if not analysis:
                logging.error('Got null analysis from analysis run queue.')
                continue

            a = analysis(self.file_object)
            if not a:
                logging.error('Unable to start Analyzer '
                              '"{}"'.format(str(analysis)))
                continue

            # Run the analysis
            a.run()

            # Collect the results, ordered first by fields, then by the
            # analyzer which produced the results.
            # TODO: Rework how this is done. Fetching the results from the
            #       RuleMatcher is cumbersome with this storage-scheme.
            # TODO: [BL006] Reevaluate/redesign internal metadata storage format.

    def print_all_datetime_info(self):
        """
        Prints all date/time-information for the current file.
        """

        # TODO: [BL007] Move results printing to separate module/class.
        misc.dump(self.results['datetime'])

    def print_title_info(self):
        """
        Prints the title for the current file, if found.
        """

        # TODO: [BL007] Move results printing to separate module/class.
        misc.dump(self.results['title'])

    def print_all_results_info(self):
        """
        Prints all analysis results for the current file.
        """

        misc.dump(self.results)
            for key in self.results.keys():
                self.results[key][a.__class__.__name__] = a.get(key)

    def get_datetime_by_alias(self, alias):
        pass
        # ALIAS_LOOKUP = {
        #     'accessed': f for f in self.results['datetime']['FilesystemAnalyzer'] if f['source'] == 'accessed',
        #     'very_special_case': None
        # }
