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

import re

from analyzers import BaseAnalyzer
from core import types
from core.util import dateandtime


RE_EDITION = re.compile(r'([0-9])+((st|nd|rd|th)\w?(E|ed)?|(E|Ed))')
EDITION_RE_LOOKUP = {
    1: r'1st('
}


class FilenameAnalyzer(BaseAnalyzer):
    run_queue_priority = 1
    handles_mime_types = ['*/*']
    meowuri_root = 'analysis.filename'

    def __init__(self, file_object, add_results_callback,
                 request_data_callback):
        super(FilenameAnalyzer, self).__init__(
            file_object, add_results_callback, request_data_callback
        )

    def run(self):
        # Pass results through callback function provided by the 'Analysis'.
        self._add_results('datetime', self.get_datetime())
        self._add_results('title', self.get_title())
        self._add_results('tags', self.get_tags())
        self._add_results('edition', self.get_edition())

    def get_datetime(self):
        results = []

        fn_timestamps = self._get_datetime_from_name()
        if fn_timestamps:
            results += fn_timestamps

        return results if results else None

    def get_title(self):
        return None

    def get_tags(self):
        # TODO: Remove! Duplicated 'FiletagsAnalyzer' functionality.
        fnp_tags = self.request_data(self.file_object,
                                     'analysis.filetags.tags')
        fnp_base = self.request_data(self.file_object,
                                     'analysis.filetags.description')
        fnp_ts = self.request_data(self.file_object,
                                   'analysis.filetags.datetime')

        # Weight cases with all "filetags" filename parts present higher.
        weight = 0.1
        if fnp_tags and len(fnp_tags) > 0:
            weight = 0.25
            if fnp_base and len(fnp_base) > 0:
                weight = 0.75
                if fnp_ts:
                    weight = 1

        if not fnp_tags:
            fnp_tags = []
        return [{'value': fnp_tags,
                 'source': 'filenamepart_tags',
                 'weight': weight}]

    def get_edition(self):
        basename = self.request_data(self.file_object,
                                     'filesystem.basename.prefix')
        if not basename:
            return

    def _get_datetime_from_name(self):
        """
        Extracts date and time information from the file name.
        :return: a list of dictionaries on the form:
                 [ { 'value': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : "Create date",
                     'weight'  : 1
                   }, .. ]
        """
        fn = self.file_object.basename_prefix
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
            # TODO: [TD0044] Look at how results are stored and named.
            # TODO: [TD0019] Rework The FilenameAnalyzer class.
            results.append(
                {'value': dt_unix,
                 'source': 'unix_timestamp',
                 'weight': 1}
            )

        # Match screencapture-prefixed UNIX timestamp
        dt_screencapture_unix = dateandtime.match_screencapture_unixtime(fn)
        if dt_screencapture_unix:
            # TODO: [TD0044] Look at how results are stored and named.
            # TODO: [TD0019] Rework The FilenameAnalyzer class.
            results.append({'value': dt_screencapture_unix,
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
            self.log.debug('Unable to extract date/time-information '
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
            self.log.debug('Unable to extract date/time-information '
                           'from file name using brute force search.')

        return results

    @classmethod
    def check_dependencies(cls):
        return True


class FileNamePart(object):
    def __init__(self, value):
        self.value = value


def _find_datetime_isodate(text_line):
    # TODO: [TD0070] Implement arbitrary basic personal use case.
    pass


def _find_edition(text):
    match = RE_EDITION.search(text)
    if match:
        e = match.group(1)
        try:
            edition = types.AW_INTEGER(e)
            return edition
        except types.AWTypeError:
            pass

    return None
