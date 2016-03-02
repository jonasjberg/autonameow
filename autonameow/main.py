import sys

from io.disk import determine_file_type, check_arg


def main():
    print "in main"

    for arg in sys.argv[1:]:
        # For every argument ..
        if check_arg(arg):
            t = determine_file_type(arg)
            print "file type: ", t

            analyze_file(arg, t)
        else:
            continue


def analyze_file(path, type):
    if type == "JPEG":
        run_image_routine()


if __name__ == "__main__":
    main()
