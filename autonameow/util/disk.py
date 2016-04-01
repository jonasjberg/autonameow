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


def is_readable_file(arg):
    # print "checking arg:" + arg

    if os.path.isfile(arg) and os.access(arg, os.R_OK):
        # print "File exists and is readable"
        return True
    else:
        # print "File is either missing or not readable"
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


def get_file_extension(path, make_lowercase=True):
    base, ext = os.path.splitext(path)

    if ext.lower() in ['.z', '.gz', '.bz2']:
        ext = os.path.splitext(base)[1] + ext

    if make_lowercase:
        ext = ext.lower()

    if ext and ext.strip():
        return ext
    else:
        return None


def get_file_name_noext(path):
    base = os.path.basename(path)
    name_noext = os.path.splitext(base)[0]

    if name_noext and name_noext.strip():
        return name_noext
    else:
        return None


if __name__ == "__main__":
    test_paths = (
        "/home/user/document.txt",
        "~/document.txt",
        "/tmp/archive.tar.gz",
        "/test 1.0/file-1",
        "/1.2.3a/document.md",
        "/1.2.3a/document",
    )

    for tp in test_paths:
        print "PATH: ", tp
        print "NAME: ", get_file_name_noext(tp)
        print "EXT : ", get_file_extension(tp)
        print ""
