import logging
import os
from datetime import datetime


# Analysis relevant to all files, regardless of file mime type.
# Examines:
#   * file names
#   * file system metadata (modified, created, ..)



class AnalyzerBase(object):
    def __init__(self, file_object):
        self.file_object = file_object

    def run(self):
        """
        Run the analysis.
        """

        fs_timestamps = self.get_datetime_from_filesystem()
        if fs_timestamps:
            self.file_object.add_datetime(fs_timestamps)

        fn_timestamps = self.get_datetime_from_name()
        if fn_timestamps:
            self.file_object.add_datetime(fn_timestamps)


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

        logging.debug('Fetching file system timestamps ..')
        try:
            mtime = os.path.getmtime(filename)
            ctime = os.path.getctime(filename)
            atime = os.path.getatime(filename)
        except OSError:
            logging.critical('Exception OSError')

        results['Modified'] = datetime.fromtimestamp(mtime) if mtime else None
        results['Created'] = datetime.fromtimestamp(ctime) if ctime else None
        results['Accessed'] = datetime.fromtimestamp(atime) if atime else None

        return results

    def get_datetime_from_name(self):
        # TODO: Get datetime from file name.
        #       Basically a bunch of regexes matching preset patterns:
        #       * Date-/timestamp
        #       * incrementer (file ends with a number)

        #       * Find information in creation-, modification- and
        #         access-date/time.

        pass
