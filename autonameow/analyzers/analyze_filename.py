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

from analyzers import BaseAnalyzer

from core.util import dateandtime


class FilenameAnalyzer(BaseAnalyzer):
    run_queue_priority = 1
    handles_mime_types = ['*/*']
    data_query_string = 'analysis.filename_analyzer'

    def __init__(self, file_object, add_results_callback,
                 request_data_callback):
        super(FilenameAnalyzer, self).__init__(
            file_object, add_results_callback, request_data_callback
        )

    def _add_results(self, label, data):
        query_string = 'analysis.filename_analyzer.{}'.format(label)
        logging.debug('{} passed "{}" to "add_results" callback'.format(
            self, query_string)
        )
        if data is not None:
            self.add_results(query_string, data)

    def run(self):
        # Pass results through callback function provided by the 'Analysis'.
        self._add_results('datetime', self.get_datetime())
        self._add_results('title', self.get_title())
        self._add_results('tags', self.get_tags())

    def get_datetime(self):
        results = []

        fn_timestamps = self._get_datetime_from_name()
        if fn_timestamps:
            results += fn_timestamps

        return results if results else None

    def get_title(self):
        results = []

        fn_title = self._get_title_from_filename()
        if fn_title:
            results += fn_title

        return results if results else None

    def get_tags(self):
        return [{'value': self.file_object.filenamepart_tags,
                 'source': 'filenamepart_tags',
                 'weight': 1}]

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
        # TODO: [TD0019][TD0044] This is not the way to do it!
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
            # TODO: [TD0044] Look at how results are stored and named.
            # TODO: [TD0019] Rework The FilenameAnalyzer class.
            self._add_results(
                'datetime',
                {'value': dt_unix,
                 'source': 'filesystem.basename.prefix.unix_timestamp',
                 'weight': 1}
            )

        # Match screencapture-prefixed UNIX timestamp
        dt_screencapture_unix = dateandtime.match_screencapture_unixtime(fn)
        if dt_screencapture_unix:
            # results.append({'value': dt_screencapture_unix,
            #                 'source': 'screencapture_unixtime',
            #                 'weight': 1})
            # TODO: [TD0044] Look at how results are stored and named.
            # TODO: [TD0019] Rework The FilenameAnalyzer class.
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


def _find_datetime_isodate(text_line):
    # TODO: [TD0070] Implement arbitrary basic personal use case.
    pass
