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



def determine_file_type(f):
    ms = magic.open(magic.MAGIC_NONE)
    ms.load()
    type = ms.file(f)
    ms.close()
    return type.split()[0]