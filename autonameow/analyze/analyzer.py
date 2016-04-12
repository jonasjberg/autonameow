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

    def run(self):
        # TODO: Run common analysis:
        # * Find information in original file name.

        # TODO: Check file name
        #       Basically a bunch of regexes matching preset patterns:
        #       * Date-/timestamp
        #       * incrementer (file ends with a number)

        #       * Find information in creation-, modification- and
        #         access-date/time.
        pass







