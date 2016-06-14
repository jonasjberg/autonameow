# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import datetime
import logging
import os

from datetime import datetime

from analyze.analyze_abstract import AbstractAnalyzer
from util import dateandtime
from util import misc


# Analysis relevant to all files, regardless of file mime type.
# Examines:
#   * file names
#   * file system metadata (modified, created, ..)
class FilesystemAnalyzer(AbstractAnalyzer):

    def get_datetime(self):
        # TODO: Get datetime from information common to all file types;
        #       file name, files in the same directory, name of directory, etc..
        result = []
        fs_timestamps = self._get_datetime_from_filesystem()
        if fs_timestamps:
            result.append(fs_timestamps)
            #self.filter_datetime(fs_timestamps)

        fn_timestamps = self._get_datetime_from_name()
        if fn_timestamps:
            result.append(fn_timestamps)
            # self.filter_datetime(fn_timestamps)

        return result

    def get_title(self):
        # TODO: Implement.
        pass

    def get_author(self):
        # TODO: Implement.
        pass

    def _get_datetime_from_filesystem(self):
        """
        Extracts date and time information "from the file system", I.E.
        access-, modification- and creation-timestamps.
        NOTE: This is all very platform-specific, I think.
        :return: dictionary of datetime objects keyed by source
        """
        filename = self.file_object.path
        results = {}

        mtime = ctime = atime = None
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
            results['Fs_Modified'] = dt_fts(mtime)
            results['Fs_Created'] = dt_fts(ctime)
            results['Fs_Accessed'] = dt_fts(atime)

        logging.info('Got [{:^3}] timestamps from '
                     'filesystem.'.format(len(results)))
        return results

    def _get_datetime_from_name(self):
        fn = self.file_object.basename_no_ext

        # 1. The Very Special Case
        # ========================
        # If this matches, it is very likely to be relevant, so test it first.
        dt_special = dateandtime.match_special_case(fn)
        if dt_special:
            return {'Filename_specialcase': dt_special}

        # 2. Common patterns
        # ==================
        # Try more common patterns, starting with the most common.
        # TODO: This is not the way to do it!
        dt_android = dateandtime.match_android_messenger_filename(fn)
        if dt_android:
            return {'Filename_android': dt_android}

        results = []

        dt_unix = dateandtime.match_unix_timestamp(fn)
        if dt_unix:
            results.append({"Filename_unix": dt_unix})
        else:
            dt_regex = dateandtime.regex_search_str(fn, 'Filename_regex')
            if dt_regex:
                return dt_regex
                # results.append(dt_regex)
            else:
                logging.warning('Unable to extract date/time-information '
                                'from file name using regex search.')

            dt_brute = dateandtime.bruteforce_str(fn, 'Filename_brute')
            if dt_brute:
                return dt_brute
                # results.append(dt_brute)
            else:
                logging.warning('Unable to extract date/time-information '
                                'from file name using brute force search.')

        return results
