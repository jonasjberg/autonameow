# Analysis relevant to all files, regardless of file mime type.
# Examines:
#   * file names
#   * file system metadata (modified, created, ..)


# TODO: Check file name
#       Basically a bunch of regexes matching preset patterns:
#       * date-/timestamp
#       * incrementer (file ends with a number)


# from dateutil.parser import parse as parseTime
from datetime import datetime as dt
from os import lstat


def print_ltstat_info(path):
    stat_info = lstat(path)
    atime = dt.utcfromtimestamp(stat_info.st_atime)
    mtime = dt.utcfromtimestamp(stat_info.st_mtime)
    ctime = dt.utcfromtimestamp(stat_info.st_ctime)
    print 'ltstat info:'
    print '  File mode bits       : %s' % oct(stat_info.st_mode)
    print '  Inode number         : %d' % stat_info.st_ino
    print '  Owner UID            : %d' % stat_info.st_uid
    print '  Group GID            : %d' % stat_info.st_gid
    print '  File size    (bytes) : %d' % stat_info.st_size
    print '  Last read    (atime) : %s' % atime.isoformat(' ')
    print '  Last write   (mtime) : %s' % mtime.isoformat(' ')
    print '  Inode change (ctime) : %s' % ctime.isoformat(' ')


def extract_date_from_string(str):
    return None
    # bla=parseTime(str)
    # print bla

