import logging
from datetime import datetime
import magic
import os
from PIL.Image import Image
from __builtin__ import str


# Analysis relevant to all files, regardless of file mime type.
# Examines:
#   * file names
#   * file system metadata (modified, created, ..)



class AnalyzerBase(object):
    def __init__(self, fileObject):
        self.fileObject = fileObject

    def run(self):
        """
        Run the analysis.
        """

        fs_timestamps = self.get_datetime_from_filesystem()
        if fs_timestamps:
            self.fileObject.add_datetime(fs_timestamps)

            # TODO: Find information in original file name.

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
        filename = self.fileObject.path
        results = {}

        logging.debug('Fetching file system timestamps ..')
        try:
            mtime = os.path.getmtime(filename)
            ctime = os.path.getctime(filename)
            atime = os.path.getatime(filename)
        except:
            logging.warn('Exception OSError')
            OSError

        if mtime:
            results['Modified'] = datetime.fromtimestamp(mtime)
        if ctime:
            results['Created'] = datetime.fromtimestamp(ctime)
        if atime:
            results['Accessed'] = datetime.fromtimestamp(atime)

        return results

    def get_datetime_from_name(self):
        # TODO: Get datetime from file name.
        #       Basically a bunch of regexes matching preset patterns:
        #       * Date-/timestamp
        #       * incrementer (file ends with a number)

        #       * Find information in creation-, modification- and
        #         access-date/time.
        pass
