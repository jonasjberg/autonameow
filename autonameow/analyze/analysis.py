# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging

import config_defaults
from evaluate.matcher import RuleMatcher
from util import misc


class Results(object):
    def __init__(self):
        self.datetime = {}
        self.title = {}
        self.tags = []
        # self.author = []
        # etc ..


class Analysis(object):
    """
    Handles the filename analyzer and analyzers specific to file content.
    A run queue is populated based on which analyzers are suited for the
    current file, based on the file type type magic.
    The analysises in the run queue is then executed and the results are
    stored as dictionary entries, with the source analyzer name being the key.
    """
    def __init__(self, file_object, filters):
        assert file_object is not None
        self.file_object = file_object

        self.filters = filters
        self.results = Results()

        # List of analyzers to run.
        # Start with a basic analyzer that is common to all file types.
        from analyze.analyze_filesystem import FilesystemAnalyzer
        from analyze.analyze_filename import FilenameAnalyzer
        self.analysis_run_queue = [FilesystemAnalyzer, FilenameAnalyzer]

        # Select analyzer based on detected file type.
        logging.debug('File is of type [{}]'.format(self.file_object.type))
        self._populate_run_queue()

        # Run all analyzers in the queue.
        self._execute_run_queue()

        # Create a rule matcher
        rule_matcher = RuleMatcher(self.file_object, config_defaults.rules)
        logging.debug('File matches rule: '
                      '{}'.format(rule_matcher.file_matches_rule))

    def _populate_run_queue(self):
        """
        Populate the list of analyzers to run.
        Imports are done locally for performance reasons.
        """
        # Analyzers to use for file types
        # TODO: Do the actual imports for found matches only!
        from analyze.analyze_pdf import PdfAnalyzer
        from analyze.analyze_image import ImageAnalyzer
        from analyze.analyze_text import TextAnalyzer
        from analyze.analyze_video import VideoAnalyzer
        ANALYZER_TYPE_LOOKUP = {ImageAnalyzer: ['jpg', 'png'],
                                PdfAnalyzer: 'pdf',
                                TextAnalyzer: ['txt', 'md'],
                                VideoAnalyzer: ['mp4'],
                                None: 'none'}

        # Compare file mime type with entries in "ANALYZER_TYPE_LOOKUP".
        found_azr = None
        for azr, tpe in ANALYZER_TYPE_LOOKUP.iteritems():
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
            self.analysis_run_queue.append(found_azr)
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

            a = analysis(self.file_object, self.filters)
            if not a:
                logging.error('Unable to instantiate analysis '
                              '"{}"'.format(str(analysis)))
                continue

            logging.debug('Running Analyzer: {}'.format(a.__class__))
            self.results.datetime[a.__class__.__name__] = a.get_datetime()
            self.results.title[a.__class__.__name__] = a.get_title()
            self.results.tags.append(a.get_tags())
            # collected_title.append(analysis.get_title())
            # collected_author.append(analysis.get_author())
            # etc ..

    def print_all_datetime_info(self):
        """
        Prints all date/time-information for the current file.
        """
        misc.dump(self.results.datetime)

    def print_title_info(self):
        """
        Prints the title for the current file, if found.
        """
        misc.dump(self.results.title)

    def print_all_results_info(self):
        """
        Prints all analysis results for the current file.
        """
        print('TITLE:')
        misc.dump(self.results.title)
        print('DATETIME:')
        misc.dump(self.results.datetime)
        print('TAGS:')
        misc.dump(self.results.tags)
