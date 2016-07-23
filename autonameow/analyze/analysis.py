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
    Main interface to all file analyzers.
    """
    def __init__(self, file_object, filters):
        self.file_object = file_object
        if self.file_object is None:
            logging.critical('Got NULL file!')
            pass

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
        # Analyzers to use for file types
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

    def filter_datetime(self, dt):
        """
        Adds a datetime-entry by first checking any filters for matches.
        Matches are ignored, "passed out" ..
        :param dt: datetime to add
        """
        # TODO: This is currently completely unused!
        if type(dt) is not dict:
            logging.warning('Got unexpected type "{}" '
                            '(expected dict)'.format(type(dt)))

        if type(dt) is list:
            if not dt:
                logging.warning('Got empty list')
                return

            # TODO: Handle whether dicts or lists should be passed, and passed
            #       only that type, OR make sure both types can be handled.
            # for item in dt:
            #     if not item:
            #         continue
            #     if type(item) is dict:
            #         for k, v in item.iteritems():
            #             if v in
            #             dt_dict[k] = v
            return

        passed = {}
        removed = {}
        ignore_years = [yr.year for yr in self.filters['ignore_years']]
        ignore_before = self.filters['ignore_before_year']
        ignore_after = self.filters['ignore_after_year']
        ok = True
        for key, value in dt.iteritems():
            if ignore_years is not None and len(ignore_years) > 0:
                if value.year in ignore_years:
                    ok = False

            if value.year < ignore_before.year:
                ok = False
            if value.year > ignore_after.year:
                ok = False

            if ok:
                # logging.debug('Filter passed date/time {} .. '.format(dt))
                passed[key] = value
            else:
                # logging.debug('Filter removed date/time {} .. '.format(dt))
                removed[key] = value

        logging.debug('Datetime filter removed {} entries, passed {} '
                      'entries.'.format(len(removed), len(passed)))

        self.file_object.add_datetime(passed)

    def print_all_datetime_info(self):
        """
        Prints all date/time-information for the current file.
        :return:
        """
        # Expected format:
        # [ { 'datetime': datetime.datetime(2016, 6, 5, 16, ..),
        # 'source'  : pdf_metadata,
        #             'comment' : "Create date",
        #                         'weight'  : 1
        # }, .. ]
        misc.dump(self.results.datetime)

    def print_oldest_datetime(self):
        oldest_dt = self.file_object.get_oldest_datetime()
        print('Oldest date/time information for file:')
        print('\"%s\"' % str(self.file_object.path))
        print('{:<20} : {:<}'.format('Datetime', 'Value'))
        print('{:<20} : {:<}'.format('oldest', oldest_dt))
