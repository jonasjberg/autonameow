import datetime
import magic
from __builtin__ import str


# Analysis relevant to all files, regardless of file mime type.
# Examines:
#   * file names
#   * file system metadata (modified, created, ..)


# TODO: Check file name
#       Basically a bunch of regexes matching preset patterns:
#       * date-/timestamp
#       * incrementer (file ends with a number)

class AnalyzerBase(object):

    def __init__(self, path):
        self.path = path

    def run(self):
        self.type = self.determine_file_type()
        if type == "JPEG":
            print "will run image routine"
            # run_image_routine()
        elif type == "PDF":
            print "will run pdf routine"
        else:
            print "not sure what to do with file type"







