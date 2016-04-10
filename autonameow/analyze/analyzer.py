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

    def __init__(self, fileObject):
        self.fileObject = fileObject

    def run(self):
        if self.fileObject.type == "JPEG":
            print "File is a JPEG image"
            # run_image_routine()
        elif type == "PDF":
            print "File is a PDF document"
        else:
            print "Unknown file type"



    def analyze_file(fileObject):
        # filenamedate = analyze.common.extract_date_from_string(os.path.basename(path))
        # print "Date in filename: ", filenamedate

        file_name_noext = util.disk.get_file_name_noext(path)
        analyze.fuzzy_date_parser.try_parse_date(file_name_noext)


        # Determine mime type and run analysis based on result.
        type = analyze.analyzer.determine_file_type(path)


        analyzer = analyze.analyzer.AnalyzerBase(path)
        analyzer.run()
        # print "determined file type: ", type
        # print '------------------------------------------------------------'

        if type == "JPEG":
            print "will run image routine"
            # run_image_routine()
        elif type == "PDF":
            print "will run pdf routine"
        else:
            print "not sure what to do with file type"








