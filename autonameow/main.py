import sys
from autonameow.io import disk


def main():
    for a in sys.argv[1:]:
        if disk.check_arg(a):
            t = disk.determine_file_type(a)
            print t
        else:
            continue
        print(a)

# f = open()
