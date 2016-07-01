# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import datetime
import logging
import os

from datetime import datetime

from guessit import guessit

from analyze.analyze_abstract import AbstractAnalyzer
from util import dateandtime
from util import misc


# Analysis relevant to all files, regardless of file mime type.
# Examines:
#   * file names
class FilenameAnalyzer(AbstractAnalyzer):

    def __init__(self, file_object, filters):
        super(FilenameAnalyzer, self).__init__(file_object, filters)

    def get_datetime(self):
        result = []

        fn_timestamps = self._get_datetime_from_name()
        if fn_timestamps:
            result += fn_timestamps
            # self.filter_datetime(fn_timestamps)

        # Arbitrary length check limits (very slow) calls to guessit.
        if len(self.file_object.basename_no_ext) > 20:
            # FIXME: Temporarily disable guessit while debugging.
            return
            guessit_timestamps = self._get_datetime_from_guessit_metadata()
            if guessit_timestamps:
                result += guessit_timestamps

        return result

    def get_title(self):
        titles = []

        guessit_title = self._get_title_from_guessit_metadata()
        if guessit_title:
            titles += guessit_title

        return titles

    def get_author(self):
        # TODO: Implement.
        pass

    def _get_title_from_guessit_metadata(self):
        """
        Calls the external program "guessit" and collects any results.
        :return: a list of dictionaries (actually just one) on the form:
                 [ { 'title': "The Cats Meouw,
                     'source' : "guessit",
                     'weight'  : 0.75
                   }, .. ]
        """
        guessit_metadata = self._get_metadata_from_guessit()
        if guessit_metadata:
            if 'title' in guessit_metadata:
                return [{'title': guessit_metadata['title'],
                         'source': 'guessit',
                         'weight': 0.75}]

    def _get_datetime_from_guessit_metadata(self):
        """
        Calls the external program "guessit" and collects any results.
        :return: a list of dictionaries (actually just one) on the form:
                 [ { 'datetime': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : "Create date",
                     'weight'  : 1
                   }, .. ]
        """
        guessit_metadata = self._get_metadata_from_guessit()
        if guessit_metadata:
            if 'date' in guessit_metadata:
                return [{'datetime': guessit_metadata['date'],
                         'source': 'guessit',
                         'weight': 0.75}]

    def _get_metadata_from_guessit(self):
        """
        Call external program "guessit".
        :return: dictionary of results if successful, otherwise false
        """
        guessit_matches = guessit(self.file_object.basename_no_ext)
        return guessit_matches if guessit_matches is not None else False

    def _get_datetime_from_name(self):
        """
        Extracts date and time information from the file name.
        :return: a list of dictionaries on the form:
                 [ { 'datetime': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : "Create date",
                     'weight'  : 1
                   }, .. ]
        """
        fn = self.file_object.basename_no_ext
        results = []

        # 1. The Very Special Case
        # ========================
        # If this matches, it is very likely to be relevant, so test it first.
        dt_special = dateandtime.match_special_case(fn)
        if dt_special:
            results.append({'datetime': dt_special,
                            'source': 'very_special_case',
                            'weight': 1})

        # 2. Common patterns
        # ==================
        # Try more common patterns, starting with the most common.
        # TODO: This is not the way to do it!
        dt_android = dateandtime.match_android_messenger_filename(fn)
        if dt_android:
            results.append({'datetime': dt_android,
                            'source': 'android_messenger',
                            'weight': 1})

        dt_unix = dateandtime.match_unix_timestamp(fn)
        if dt_unix:
            results.append({'datetime': dt_unix,
                            'source': 'unix_timestamp',
                            'weight': 1})
        else:
            dt_regex = dateandtime.regex_search_str(fn)
            if dt_regex:
                for dt in dt_regex:
                    results.append({'datetime': dt,
                                    'source': 'regex_search',
                                    'weight': 0.25})
            else:
                logging.warning('Unable to extract date/time-information '
                                'from file name using regex search.')

            dt_brute = dateandtime.bruteforce_str(fn)
            if dt_brute:
                for dt in dt_brute:
                    results.append({'datetime': dt,
                                    'source': 'bruteforce_search',
                                    'weight': 0.1})
            else:
                logging.warning('Unable to extract date/time-information '
                                'from file name using brute force search.')

        return results