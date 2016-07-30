# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging

from analyze.analyze_abstract import AbstractAnalyzer
from util import dateandtime


class FilenameAnalyzer(AbstractAnalyzer):

    def __init__(self, file_object, filters):
        super(FilenameAnalyzer, self).__init__(file_object, filters)

        self.guessit_metadata = None
        # Arbitrary length check limits (very slow) calls to guessit.
        if len(self.file_object.filenamepart_base) > 20:
            self.guessit_metadata = self._get_metadata_from_guessit()

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

    def get_title(self):
        titles = []

        if self.guessit_metadata:
            guessit_title = self._get_title_from_guessit_metadata()
            if guessit_title:
                titles += guessit_title

        return titles

    def get_author(self):
        # TODO: Implement.
        pass

    def get_tags(self):
        return self.file_object.filenamepart_tags

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
                return [{'title': self.guessit_metadata['title'],
                         'source': 'guessit',
                         'weight': 0.75}]

    def _get_datetime_from_guessit_metadata(self):
        """
        Get date/time-information from the results returned by "guessit".
        :return: a list of dictionaries (actually just one) on the form:
                 [ { 'datetime': datetime.datetime(2016, 6, 5, 16, ..),
                     'source' : "Create date",
                     'weight'  : 1
                   }, .. ]
        """
        if self.guessit_metadata:
            if 'date' in self.guessit_metadata:
                return [{'datetime': self.guessit_metadata['date'],
                         'source': 'guessit',
                         'weight': 0.75}]

    def _get_metadata_from_guessit(self):
        """
        Call external program "guessit".
        :return: dictionary of results if successful, otherwise false
        """
        from guessit import guessit
        guessit_matches = guessit(self.file_object.filenamepart_base, )
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
        fn = self.file_object.filenamepart_base
        results = []

        # 1. The Very Special Case
        # ========================
        # If this matches, it is very likely to be relevant, so test it first.
        dt_special = dateandtime.match_special_case(fn)
        if dt_special:
            results.append({'datetime': dt_special,
                            'source': 'very_special_case',
                            'weight': 1})
        else:
            dt_special_no_date = dateandtime.match_special_case_no_date(fn)
            if dt_special_no_date:
                results.append({'datetime': dt_special_no_date,
                                'source': 'very_special_case_no_date',
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

        # Match UNIX timestamp
        dt_unix = dateandtime.match_any_unix_timestamp(fn)
        if dt_unix:
            results.append({'datetime': dt_unix,
                            'source': 'unix_timestamp',
                            'weight': 1})

        # Match screencapture-prefixed UNIX timestamp
        dt_screencapture_unix = dateandtime.match_screencapture_unixtime(fn)
        if dt_screencapture_unix:
            results.append({'datetime': dt_screencapture_unix,
                            'source': 'screencapture_unixtime',
                            'weight': 1})

        # 3. Generalized patternmatching and bruteforcing
        # ===============================================
        # General "regex search" with various patterns.
        dt_regex = dateandtime.regex_search_str(fn)
        if dt_regex:
            for dt in dt_regex:
                results.append({'datetime': dt,
                                'source': 'regex_search',
                                'weight': 0.25})
        else:
            logging.debug('Unable to extract date/time-information '
                          'from file name using regex search.')

        # Lastly, an iterative brute force search.
        dt_brute = dateandtime.bruteforce_str(fn)
        if dt_brute:
            for dt in dt_brute:
                results.append({'datetime': dt,
                                'source': 'bruteforce_search',
                                'weight': 0.1})
        else:
            logging.debug('Unable to extract date/time-information '
                          'from file name using brute force search.')

        return results
