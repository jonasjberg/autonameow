import sys
import os

from analyze.common import extract_date_from_string, print_ltstat_info
from io.disk import determine_file_type, check_arg


def main():
    # Main program entry point

    # Loop over arguments ..
    for arg in sys.argv[1:]:
        if check_arg(arg):
            print '------------------------------------------------------------'
            # Determine mime type and run analysis based on result.
            type = determine_file_type(arg)
            print "determined file type: ", type
            print '------------------------------------------------------------'
            print_ltstat_info(arg)

            print '------------------------------------------------------------'
            analyze_file(arg, type)

        else:
            # Basic sanity check failed, skip to next argument
            continue


def analyze_file(path, type):
    filenamedate = extract_date_from_string(os.path.basename(path))
    print "Date in filename: ", filenamedate
    if type == "JPEG":
        print "will run image routine"
        # run_image_routine()
    elif type == "PDF":
        print "will run pdf routine"
    else:
        print "not sure what to do with file type"


if __name__ == '__main__':
    main()

