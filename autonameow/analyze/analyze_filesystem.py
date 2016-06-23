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
#   * file system metadata (modified, created, ..)
class FilesystemAnalyzer(AbstractAnalyzer):

    def __init__(self, file_object, filters):
        super(FilesystemAnalyzer, self).__init__(file_object, filters)

    def get_datetime(self):
        # TODO: Get datetime from information common to all file types;
        #       file name, files in the same directory, name of directory, etc..
        result = []
        fs_timestamps = self._get_datetime_from_filesystem()
        if fs_timestamps:
            result += fs_timestamps
            # self.filter_datetime(fs_timestamps)

        fn_timestamps = self._get_datetime_from_name()
        if fn_timestamps:
            result += fn_timestamps
            # self.filter_datetime(fn_timestamps)

        guessit_timestamps = self._get_datetime_from_guessit_metadata()
        if guessit_timestamps:
            result += guessit_timestamps

        return result

    def get_title(self):
        # TODO: Implement.
        pass

    def get_author(self):
        # TODO: Implement.
        pass

    def _get_datetime_from_guessit_metadata(self):
        """
        Calls the external program "guessit" and collects any results.
        :return: a list of dictionaries (actually just one) on the form:
                 [ { 'datetime': datetime.datetime(2016, 6, 5, 16, ..),
                     'source'  : pdf_metadata,
                     'comment' : "Create date",
                     'weight'  : 1
                   }, .. ]
        """
        guessit_metadata = self._get_metadata_from_guessit()
        if guessit_metadata:
            if 'date' in guessit_metadata:
                return [{'datetime': guessit_metadata['date'],
                            'source': 'guessit',
                            'comment': 'guessit',
                        'weight': 0.75}]

    def _get_metadata_from_guessit(self):
        """
        Call external program "guessit".
        :return: dictionary of results if successful, otherwise false
        """
        guessit_matches = guessit(self.file_object.basename_no_ext)
        return guessit_matches if guessit_matches is not None else False

    def _get_datetime_from_filesystem(self):
        """
        Extracts date and time information "from the file system", I.E.
        access-, modification- and creation-timestamps.
        NOTE: This is all very platform-specific, I think.
        :return: list of dictionaries on the form:
                 [ { 'datetime': datetime.datetime(2016, 6, 5, 16, ..),
                     'source'  : pdf_metadata,
                     'comment' : "Create date",
                     'weight'  : 1
                   }, .. ]
        """
        filename = self.file_object.path
        results = []

        logging.debug('Fetching file system timestamps ..')
        try:
            mtime = os.path.getmtime(filename)
            ctime = os.path.getctime(filename)
            atime = os.path.getatime(filename)
        except OSError as e:
            logging.critical('Failed extracting date/time-information '
                             'from file system, which shouldnt happen.')
            logging.critical('OSError: {}'.format(e))
        else:
            def dt_fts(t):
                return datetime.fromtimestamp(t).replace(microsecond=0)

            results.append({'datetime': dt_fts(mtime),
                            'source': 'filesystem',
                            'comment': 'modified',
                            'weight': 1})
            results.append({'datetime': dt_fts(ctime),
                            'source': 'filesystem',
                            'comment': 'created',
                            'weight': 1})
            results.append({'datetime': dt_fts(atime),
                            'source': 'filesystem',
                            'comment': 'accessed',
                            'weight': 1})

        logging.info('Got [{:^3}] timestamps from '
                     'filesystem.'.format(len(results)))
        return results

    def _get_datetime_from_name(self):
        """
        Extracts date and time information from the file name.
        :return: a list of dictionaries on the form:
                 [ { 'datetime': datetime.datetime(2016, 6, 5, 16, ..),
                     'source'  : pdf_metadata,
                     'comment' : "Create date",
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
                            'source': 'filename',
                            'comment': 'very_special_case',
                            'weight': 1})

        # 2. Common patterns
        # ==================
        # Try more common patterns, starting with the most common.
        # TODO: This is not the way to do it!
        dt_android = dateandtime.match_android_messenger_filename(fn)
        if dt_android:
            results.append({'datetime': dt_android,
                            'source': 'filename',
                            'comment': 'android_messenger',
                            'weight': 1})

        dt_unix = dateandtime.match_unix_timestamp(fn)
        if dt_unix:
            results.append({'datetime': dt_unix,
                            'source': 'filename',
                            'comment': 'unix_timestamp',
                            'weight': 1})
        else:
            dt_regex = dateandtime.regex_search_str(fn)
            if dt_regex:
                for dt in dt_regex:
                    results.append({'datetime': dt,
                                    'source': 'filename',
                                    'comment': 'regex_search',
                                    'weight': 0.25})
            else:
                logging.warning('Unable to extract date/time-information '
                                'from file name using regex search.')

            dt_brute = dateandtime.bruteforce_str(fn)
            if dt_brute:
                for dt in dt_brute:
                    results.append({'datetime': dt,
                                    'source': 'filename',
                                    'comment': 'bruteforce_search',
                                    'weight': 0.1})
            else:
                logging.warning('Unable to extract date/time-information '
                                'from file name using brute force search.')

        return results
