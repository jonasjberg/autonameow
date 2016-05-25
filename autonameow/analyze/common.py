# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import datetime
import logging
import os

from datetime import datetime

from util import dateandtime
from util import misc


# Analysis relevant to all files, regardless of file mime type.
# Examines:
#   * file names
#   * file system metadata (modified, created, ..)
class AnalyzerBase(object):
    def __init__(self, file_object, filters):
        self.file_object = file_object
        self.filters = filters

    def run(self):
        """
        Run the analysis.
        """
        fs_timestamps = self.get_datetime_from_filesystem()
        if fs_timestamps:
            self.add_datetime(fs_timestamps)

        fn_timestamps = self.get_datetime_from_name()
        if fn_timestamps:
            self.add_datetime(fn_timestamps)

    def add_datetime(self, dt):
        """
        Adds a datetime-entry by first checking any filters for matches.
        Matches are ignored, "passed out" ..
        :param dt: datetime to add
        """
        if type(dt) is not dict:
            logging.warning('Got unexpected type \"{}\" '
                            '(expected dict)'.format(type(dt)))

        passed = {}
        removed = {}
        ignore_years = [yr.year for yr in self.filters["ignore_years"]]
        if ignore_years is not None and len(ignore_years) > 0:
            for key, value in dt.iteritems():
                if value.year not in ignore_years:
                    # logging.debug('Filter passed date/time {} .. '.format(dt))
                    passed[key] = value
                else:
                    logging.debug('Filter removed date/time {} .. '.format(dt))
                    removed[key] = value

            self.file_object.add_datetime(passed)
        else:
            # Just pass the datetime through, unaffected by the filter.
            self.file_object.add_datetime(dt)

    def get_datetime(self):
        # TODO: Get datetime from information common to all file types;
        #       file name, files in the same directory, name of directory, etc..
        pass

    def get_datetime_from_filesystem(self):
        """
        Extracts date and time information "from the file system", I.E.
        access-, modification- and creation-timestamps.
        NOTE: This is all very platform-specific.
        :return: Touple of datetime objects representing date and time.
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
            results['Fs_Modified'] = datetime.fromtimestamp(mtime).replace(
                microsecond=0)
            results['Fs_Created'] = datetime.fromtimestamp(ctime).replace(
                microsecond=0)
            results['Fs_Accessed'] = datetime.fromtimestamp(atime).replace(
                microsecond=0)

        logging.info(
            'Got [{:^3}] timestamps from filesystem.'.format(len(results)))
        return results

    def get_datetime_from_name(self):
        fn = self.file_object.basename_no_ext
        result_list = []

        dt_special = dateandtime.match_special_case(fn)
        if dt_special:
            result_list.append({"Filename_specialcase": dt_special})
        else:
            # TODO: Check if image file name is Android messenger specific.
            # Example: received_10151287690965808.jpeg

            dt_unix = dateandtime.match_unix_timestamp(fn)
            if dt_unix:
                result_list.append({"Filename_unix": dt_unix})
            else:
                dt_regex = dateandtime.regex_search_str(fn, 'Filename_regex')
                if dt_regex is None:
                    logging.warning('Unable to extract date/time-information '
                                    'from file name using regex search.')
                else:
                    result_list.append(dt_regex)

                dt_brute = dateandtime.bruteforce_str(fn, 'Filename_brute')
                if dt_brute is None:
                    logging.warning('Unable to extract date/time-information '
                                    'from file name using brute force search.')
                else:
                    result_list.append(dt_brute)

        # results = {}
        # for entry in result_list:
        #     for r_key, r_value in entry.iteritems():
        #         # print('results[{}] = {}'.format(r_key, r_value))
        #         results[r_key] = r_value
        return result_list
