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

from .analyze_abstract import AbstractAnalyzer

try:
    import guessit as guessit
except ImportError:
    guessit = False

from core.util import dateandtime


class FilenameAnalyzer(AbstractAnalyzer):
    # @Overrides attribute in AbstractAnalyzer
    run_queue_priority = 1

    def __init__(self, file_object, add_results_callback):
        super(FilenameAnalyzer, self).__init__(file_object,
                                               add_results_callback)
        self.applies_to_mime = 'MIME_ALL'
        self.add_results = add_results_callback

        self.guessit_metadata = None

    # @Overrides method in AbstractAnalyzer
    def run(self):
        # TODO: This test does not belong here! Handle guessit properly.
        if guessit and self.file_object.mime_type == 'mp4':
            self.guessit_metadata = self._get_metadata_from_guessit()

            if self.guessit_metadata:
                self.add_results('plugins.guessit', self.guessit_metadata)

    # @Overrides method in AbstractAnalyzer
    def get_datetime(self):
        result = []

        fn_timestamps = self._get_datetime_from_name()
        if fn_timestamps:
            result += fn_timestamps

        if self.guessit_metadata:
            guessit_timestamps = self._get_datetime_from_guessit_metadata()
            if guessit_timestamps:
                result += guessit_timestamps

        return result

    # @Overrides method in AbstractAnalyzer
    def get_title(self):
        titles = []

        if self.guessit_metadata:
            guessit_title = self._get_title_from_guessit_metadata()
            if guessit_title:
                titles += guessit_title

        fn_title = self._get_title_from_filename()
        if fn_title:
            titles += fn_title

        return titles

    # @Overrides method in AbstractAnalyzer
    def get_author(self):
        # TODO: Implement.
        pass

    # @Overrides method in AbstractAnalyzer
    def get_tags(self):
        return self.file_object.filenamepart_tags

    # @Overrides method in AbstractAnalyzer
    def get_publisher(self):
        return None

    def _get_title_from_filename(self):
        fnp_tags = self.file_object.filenamepart_tags or None
        fnp_base = self.file_object.filenamepart_base or None
        fnp_ts = self.file_object.filenamepart_ts or None

        # Weight cases with all "filetags" filename parts present higher.
        if fnp_base and len(fnp_base) > 0:
            weight = 0.25
            if fnp_ts and len(fnp_ts) > 0:
                weight = 0.75
                if fnp_tags and len(fnp_tags) > 0:
                    weight = 1

            return [{'value': fnp_base,
                     'source': 'filenamepart_base',
                     'weight': weight}]
        else:
            return None

    def _get_title_from_guessit_metadata(self):
        """
        Get the title from the results returned by "guessit".
        :return: a list of dictionaries (actually just one) on the form:
                 [ { 'title': "The Cats Meouw,
                     'source' : "guessit",
                     'weight'  : 0.75
                   }, .. ]
        """
        if self.guessit_metadata:
            if 'title' in self.guessit_metadata:
                return [{'value': self.guessit_metadata['title'],
                         'source': 'guessit',
                         'weight': 0.75}]

    def _get_datetime_from_guessit_metadata(self):
        """
        Get date/time-information from the results returned by "guessit".
        :return: a list of dictionaries (actually just one) on the form:
                 [ { 'value': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : "Create date",
                     'weight'  : 1
                   }, .. ]
        """
        if self.guessit_metadata:
            if 'date' in self.guessit_metadata:
                return [{'value': self.guessit_metadata['date'],
                         'source': 'guessit',
                         'weight': 0.75}]

    def _get_metadata_from_guessit(self):
        """
        Call external program "guessit".
        :return: dictionary of results if successful, otherwise false
        """
        guessit_matches = guessit.guessit(self.file_object.filenamepart_base, )
        return guessit_matches if guessit_matches is not None else False

    def _get_datetime_from_name(self):
        """
        Extracts date and time information from the file name.
        :return: a list of dictionaries on the form:
                 [ { 'value': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : "Create date",
                     'weight'  : 1
                   }, .. ]
        """
        fn = self.file_object.fnbase
        results = []

        # 1. The Very Special Case
        # ========================
        # If this matches, it is very likely to be relevant, so test it first.
        dt_special = dateandtime.match_special_case(fn)
        if dt_special:
            results.append({'value': dt_special,
                            'source': 'very_special_case',
                            'weight': 1})
        else:
            dt_special_no_date = dateandtime.match_special_case_no_date(fn)
            if dt_special_no_date:
                results.append({'value': dt_special_no_date,
                                'source': 'very_special_case_no_date',
                                'weight': 1})

        # 2. Common patterns
        # ==================
        # Try more common patterns, starting with the most common.
        # TODO: This is not the way to do it!
        dt_android = dateandtime.match_android_messenger_filename(fn)
        if dt_android:
            results.append({'value': dt_android,
                            'source': 'android_messenger',
                            'weight': 1})

        # Match UNIX timestamp
        dt_unix = dateandtime.match_any_unix_timestamp(fn)
        if dt_unix:
            # results.append({'value': dt_unix,
            #                 'source': 'unix_timestamp',
            #                 'weight': 1})
            # TODO: Properly integrate new callback-based results gathering.
            self.add_results('filesystem.basename.derived_data.datetime',
                             {'value': dt_unix,
                              'source': 'unix_timestamp',
                              'weight': 1})

        # Match screencapture-prefixed UNIX timestamp
        dt_screencapture_unix = dateandtime.match_screencapture_unixtime(fn)
        if dt_screencapture_unix:
            # results.append({'value': dt_screencapture_unix,
            #                 'source': 'screencapture_unixtime',
            #                 'weight': 1})
            # TODO: Properly integrate new callback-based results gathering.
            self.add_results('filesystem.basename.derived_data.datetime',
                             {'value': dt_screencapture_unix,
                              'source': 'screencapture_unixtime',
                              'weight': 1})

        # 3. Generalized patternmatching and bruteforcing
        # ===============================================
        # General "regex search" with various patterns.
        dt_regex = dateandtime.regex_search_str(fn)
        if dt_regex:
            for dt in dt_regex:
                results.append({'value': dt,
                                'source': 'regex_search',
                                'weight': 0.25})
        else:
            logging.debug('Unable to extract date/time-information '
                          'from file name using regex search.')

        # Lastly, an iterative brute force search.
        # TODO: Collapse duplicate results with 'util.misc.multiset_count'..?
        dt_brute = dateandtime.bruteforce_str(fn)
        if dt_brute:
            for dt in dt_brute:
                results.append({'value': dt,
                                'source': 'bruteforce_search',
                                'weight': 0.1})
        else:
            logging.debug('Unable to extract date/time-information '
                          'from file name using brute force search.')

        return results
