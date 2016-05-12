import datetime
import logging
import os
import string
from datetime import datetime

# Analysis relevant to all files, regardless of file mime type.
# Examines:
#   * file names
#   * file system metadata (modified, created, ..)
from util import dateandtime


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
        if dt not in self.filters:
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

        dt_regex = dateandtime.regex_search_str(fn, 'Filename_regex')
        if dt_regex is None:
            logging.warning('Unable to extract date/time-information '
                            'from file name using regex search.')
            pass
        else:
            result_list.append(dt_regex)

        dt_brute = dateandtime.bruteforce_str(fn, 'Filename_brute')
        if dt_brute is None:
            logging.warning('Unable to extract date/time-information '
                            'from file name using brute force search.')
            pass
        else:
            result_list.append(dt_brute)

        results = {}
        for entry in result_list:
            for r_key, r_value in entry.iteritems():
                # print('results[{}] = {}'.format(r_key, r_value))
                results[r_key] = r_value

        return results
