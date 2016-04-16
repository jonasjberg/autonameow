#!/usr/bin/env python
# coding=utf-8

# autonameow
# ~~~~~~~~~~
# written by Jonas Sjöberg
# jomeganas@gmail.com
# ____________________________________________________________________________

import sys
import os
import argparse
import logging

import analyze.analyzer
import util.disk
import analyze.fuzzy_date_parser
from analyze.file_object import FileObject
from analyze.analyzer import AnalyzerBase
from analyze.image import ImageAnalyzer
from analyze.pdf import PdfAnalyzer


def handle_logging():
    if args.verbose:
        FORMAT = "%(levelname)-8s %(asctime)-15s %(message)s"
        logging.basicConfig(level=logging.DEBUG, format=FORMAT)
    elif args.quiet:
        FORMAT = "%(levelname)-8s %(message)s"
        logging.basicConfig(level=logging.ERROR, format=FORMAT)
    else:
        FORMAT = "%(levelname)-8s %(message)s"
        logging.basicConfig(level=logging.INFO, format=FORMAT)


def main():
    # Main program entry point
    handle_logging()

    # Iterate over command line arguments ..
    if args.input_files:
        for file in args.input_files:
            if util.disk.is_readable_file(file):
                logging.info('Processing file \"%s\"' % str(file))

                # Create a new FileObject representing the current arg.
                file = FileObject(file)

                # Select analyzer based on detected file type.
                if file.get_type() == "JPEG":
                    logging.debug('File is of type [JPEG]')
                    analyzer = ImageAnalyzer(file)
                elif file.get_type() == "PDF":
                    logging.debug('File is of type [PDF]')
                    analyzer = PdfAnalyzer(file)
                else:
                    # Create a basic analyzer, common to all file types.
                    logging.debug('File is of type [unknown]')
                    analyzer = AnalyzerBase(file)

                analyzer.run()

                if analyzer.hasResults():
                    file.assembleNewName(analyzer.getResults())


            else:
                # Unable to read file. Skip ..
                logging.error('Unable to read file \"%s\"' % str(file))
                continue

    else:
        logging.info("No input files specified. Exiting.")
        exit(1)






parser = argparse.ArgumentParser(
    description='Automatic renaming of files from analysis of several sources of information.')

output_control_group = parser.add_mutually_exclusive_group()
output_control_group.add_argument("-v", "--verbose",
                                  dest='verbose',
                                  action="store_true",
                                  help='verbose mode')

output_control_group.add_argument("-q", "--quiet",
                                  dest='quiet',
                                  action="store_true",
                                  help='quiet mode')

parser.add_argument(dest='input_files',
                    metavar='filename',
                    nargs='*',
                    help='input file(s)')

parser.add_argument('-d', '--dry-run',
                    dest='dry_run',
                    action='store',
                    help='simulate what would happen but do not actually write any changes to disk')

args = parser.parse_args()


if __name__ == '__main__':
    main()

