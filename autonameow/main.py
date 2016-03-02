import sys

from io.disk import determine_file_type, check_arg


def main():
    print "in main"

    for a in sys.argv[1:]:
        # For every argument ..
        if check_arg(a):
            t = determine_file_type(a)
            print "type:", t
        else:
            continue


if __name__ == "__main__":
    main()
