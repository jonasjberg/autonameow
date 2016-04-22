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

        # TODO: Implement this in some way that makes sense. Do research first.
        self.fields = {"title": None,
                       "Author": None,
                       "datetime": None}

    def run(self):
        # TODO: Run common analysis:
        # * Find information in original file name.
        pass

    def get_datetime(self):
        # TODO: Get datetime from information common to all file types;
        #       file name, files in the same directory, name of directory, etc..
        pass

    def get_datetime_from_filesystem(self):
        filename = self.fileObject.get_path()
        results = {}

        try:
            mtime = os.path.getmtime(filename)
            ctime = os.path.getctime(filename)
            atime = os.path.getatime(filename)
        except:
            logging.warn('Exception OSError')
            OSError

        if mtime:
            results['mtime'] = datetime.fromtimestamp(mtime)
        if ctime:
            results['ctime'] = datetime.fromtimestamp(ctime)
        if atime:
            results['atime'] = datetime.fromtimestamp(atime)

        return results


    def get_datetime_from_name(self):
        # TODO: Get datetime from file name.
        #       Basically a bunch of regexes matching preset patterns:
        #       * Date-/timestamp
        #       * incrementer (file ends with a number)

        #       * Find information in creation-, modification- and
        #         access-date/time.
        pass

