import magic
import os


def determine_file_type(f):
    # m = magic.Magic(mimetype=True)
    # file_type = m.from_file(f)
    #
    # return file_type

    ms = magic.open(magic.MAGIC_NONE)
    ms.load()
    type = ms.file(f)
    print type

    ff = file(f, "r")
    bffr = ff.read(4096)
    ff.close()

    type = ms.buffer(bffr)
    print type

    ms.close()


def check_arg(arg):
    print "checking arg:" + arg

    if os.path.isfile(arg) and os.access(arg, os.R_OK):
        print "File exists and is readable"
        return True
    else:
        print "File is either missing or not readable"
        return False
