import sys
import os

import analyze.common
import util.disk
import analyze.fuzzy_date_parser


def main():
    # Main program entry point

    # Loop over arguments ..
    for arg in sys.argv[1:]:
        if util.disk.check_arg(arg):
            print '------------------------------------------------------------'
            # Determine mime type and run analysis based on result.
            type = util.disk.determine_file_type(arg)
            print "determined file type: ", type
            # print '------------------------------------------------------------'
            # io.disk.print_ltstat_info(arg)

            print '------------------------------------------------------------'
            analyze_file(arg, type)

        else:
            # Basic sanity check failed, skip to next argument
            continue


def analyze_file(path, type):
    # filenamedate = analyze.common.extract_date_from_string(os.path.basename(path))
    # print "Date in filename: ", filenamedate

    file_basename = os.path.basename(path)
    file_basename_noext = os.path.splitext(path)[1]

    print "file_basename: ", file_basename
    print "file_basename_noext: ", file_basename_noext

    analyze.fuzzy_date_parser.try_parse_date(file_basename_noext)

    if type == "JPEG":
        print "will run image routine"
        # run_image_routine()
    elif type == "PDF":
        print "will run pdf routine"
    else:
        print "not sure what to do with file type"


if __name__ == '__main__':
    main()

