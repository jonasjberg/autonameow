#!/usr/bin/env python
# coding=utf-8

# autonameow
# ~~~~~~~~~~
# written by Jonas Sjöberg
# jomeganas@gmail.com
# ____________________________________________________________________________

import sys
import os

import analyze.analyzer
import util.disk
import analyze.fuzzy_date_parser
from analyze.file_object import FileObject
from analyze.analyzer import AnalyzerBase


def main():
    # Main program entry point


    # Iterate over command line arguments ..
    for arg in sys.argv[1:]:
        if util.disk.is_readable_file(arg):
            # print '------------------------------------------------------------'
            # io.disk.print_ltstat_info(arg)

            # Create a new FileObject representing the current arg.
            f = FileObject(arg)

            # Create a basic analyzer, common to all file types.
            a = AnalyzerBase(f)

        else:
            # Basic sanity check failed, skip to next argument
            continue



if __name__ == '__main__':
    main()

