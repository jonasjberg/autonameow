# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging

from core.util import misc
from core.analyze.analyze_pdf import PdfAnalyzer
from core.analyze.analyze_image import ImageAnalyzer
from core.analyze.analyze_text import TextAnalyzer
from core.analyze.analyze_video import VideoAnalyzer
from core.analyze.analyze_filename import FilenameAnalyzer
from core.analyze.analyze_filesystem import FilesystemAnalyzer

# Collect all analyzers from their class name.
_ALL_ANALYZER_CLASSES = [
        klass
        for name, klass in list(globals().items())
        if name.endswith('Analyzer') and name != 'AbstractAnalyzer'
    ]


def get_analyzer_classes():
    """
    Returns all analyzer classes in '_ALL_ANALYZER_CLASSES' as a list of type.
    :return: a list of all analyzers.
    """
    return _ALL_ANALYZER_CLASSES


def get_instantiated_analyzers():
    """
    Returns a list of instantiated analyzers defined in '_ALL_ANALYZER_CLASSES'.
    :return: a list of all analyzers as objects.
    """
    # NOTE: These are instantiated with a None FIleObject, which might be a
    #       problem and is surely not very pretty.
    return [klass(None) for klass in get_analyzer_classes()]


def get_analyzer_mime_mappings():
    """
    Returns a dictionary keyed by the class names of all analyzers, storing
    the class variable 'applies_to_mime' from each analyzer.
    :return: a dictionary of strings or list of strings.
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
        if isinstance(analysis, list):
            self._queue += analysis
        else:
            self._queue.append(analysis)

    def __len__(self):
        return len(self._queue)

    def __getitem__(self, item):
        return self._queue[item]


class Analysis(object):
    """
    Handles the filename analyzer and analyzers specific to file content.
    A run queue is populated based on which analyzers are suited for the
    current file, based on the file type type magic.
    The analyses in the run queue is then executed and the results are
    stored as dictionary entries, with the source analyzer name being the key.
    """
    def __init__(self, file_object):
        assert file_object is not None
        self.file_object = file_object

        self.results = {'datetime': {},
                        'title': {},
                        'tags': {}}

        # List of analyzers to run.
        # Start with a basic analyzer that is common to all file types.
        self.analysis_run_queue = AnalysisRunQueue()
        self.analysis_run_queue.enqueue([FilesystemAnalyzer, FilenameAnalyzer])

        # Select analyzer based on detected file type.
        logging.debug('File is of type [{}]'.format(self.file_object.type))
        self._populate_run_queue()

        # Run all analyzers in the queue.
        self._execute_run_queue()

    def _populate_run_queue(self):
        """
        Populate the list of analyzers to run.
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
            self.results['datetime'][a.__class__.__name__] = a.get_datetime()
            self.results['title'][a.__class__.__name__] = a.get_title()
            self.results['tags'][a.__class__.__name__] = a.get_tags()

    def print_all_datetime_info(self):
        """
        Prints all date/time-information for the current file.
        """
        misc.dump(self.results['datetime'])

    def print_title_info(self):
        """
        Prints the title for the current file, if found.
        """
        misc.dump(self.results['title'])

    def print_all_results_info(self):
        """
        Prints all analysis results for the current file.
        """
        misc.dump(self.results)

    def get_datetime_by_alias(self, alias):
        pass
        # ALIAS_LOOKUP = {
        #     'accessed': f for f in self.results['datetime']['FilesystemAnalyzer'] if f['source'] == 'accessed',
        #     'very_special_case': None
        # }
