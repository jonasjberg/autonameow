import datetime
import magic
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

    def get_datetime_from_name(self):
        # TODO: Get datetime from file name.
        #       Basically a bunch of regexes matching preset patterns:
        #       * Date-/timestamp
        #       * incrementer (file ends with a number)

        #       * Find information in creation-, modification- and
        #         access-date/time.
        pass

