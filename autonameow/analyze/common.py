# Analysis relevant to all files, regardless of file mime type.
# Examines:
#   * file names
#   * file system metadata (modified, created, ..)


# TODO: Check file name
#       Basically a bunch of regexes matching preset patterns:
#       * date-/timestamp
#       * incrementer (file ends with a number)


from dateutil.parser import parse as parseTime


def extract_date_from_string(str):
    bla=parseTime(str)
    print bla

