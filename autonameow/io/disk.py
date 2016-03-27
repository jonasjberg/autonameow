import magic
import os
from datetime import datetime as dt


FTYPES = {
    'JPEG' : 'jpg',
    'GIF' : 'gif',
    'PNG' : 'png',
}


def determine_file_type(f):
    ms = magic.open(magic.MAGIC_NONE)
    ms.load()
    type = ms.file(f)
    # print type

    # ff = file(f, "r")
    # bffr = ff.read(4096)
    # ff.close()
    #
    # type = ms.buffer(bffr)
    # print type

    ms.close()
    return type.split()[0]


def check_arg(arg):
    print "checking arg:" + arg

    if os.path.isfile(arg) and os.access(arg, os.R_OK):
        print "File exists and is readable"
        return True
    else:
        print "File is either missing or not readable"
        return False



def print_ltstat_info(path):
    stat_info = os.lstat(path)
    atime = dt.utcfromtimestamp(stat_info.st_atime)
    mtime = dt.utcfromtimestamp(stat_info.st_mtime)
    ctime = dt.utcfromtimestamp(stat_info.st_ctime)
    print 'ltstat info:'
    print '  File mode bits:       %s' % oct(stat_info.st_mode)
    print '  Inode number:         %d' % stat_info.st_ino
    print '  Owner UID:            %d' % stat_info.st_uid
    print '  Group GID:            %d' % stat_info.st_gid
    print '  File size:    (bytes) %d' % stat_info.st_size
    print '  Last read:    (atime) %s' % atime.isoformat(' ')
    print '  Last write:   (mtime) %s' % mtime.isoformat(' ')
    print '  Inode change: (ctime) %s' % ctime.isoformat(' ')


