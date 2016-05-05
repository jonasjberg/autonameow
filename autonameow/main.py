#!/usr/bin/env python
# coding=utf-8

# autonameow
# ~~~~~~~~~~
# written by Jonas Sjöberg
# jomeganas@gmail.com
# ____________________________________________________________________________

import argparse
import logging
import os
import sys

import util.disk
from analyze.analysis import Analysis
from file_object import FileObject


class Autonameow(object):
    """
    Main class to manage "autonameow" instance.
    """

    def __init__(self):
        """
        Handle the command line arguments.
        """
        self.args = self.parse_args()

    def main(self):
        # Main program entry point
        pass

    def init_argparser(self):
        """
        Initialize the argparser. Add all arguments/options.
        :return: the argument parser
        """
        parser = argparse.ArgumentParser(
            prog='autonameow',
            description='Automatic renaming of files from analysis of '
                        'several sources of information.',
            epilog='Example usage: TODO ..')

        optgrp_output = parser.add_mutually_exclusive_group()
        optgrp_output.add_argument("-z", "--debug",
                                   const=0, default=0, type=int,
                                   nargs="?",
                                   dest='debug',
                                   help='debug verbosity: 0 = some, 1 = more, '
                                        '2 = detailed, 3 = everything. '
                                        'No number means some. '
                                        'Default is no debug verbosity.')

        optgrp_output.add_argument("-v", "--verbose",
                                   dest='verbose',
                                   action="store_true",
                                   help='verbose mode')

        optgrp_output.add_argument("-q", "--quiet",
                                   dest='quiet',
                                   action="store_true",
                                   help='quiet mode')

        optgrp_action = parser.add_mutually_exclusive_group()
        optgrp_action.add_argument("--add-datetime",
                                   dest='add_datetime',
                                   action="store_true",
                                   help='only add datetime to file name')

        parser.add_argument(dest='input_files',
                            metavar='filename',
                            nargs='*',
                            help='input file(s)')

        parser.add_argument('-d', '--dry-run',
                            dest='dry_run',
                            action='store',
                            help='simulate what would happen but do not '
                                 'actually write any changes to disk')

        return parser

    def parse_args(self):
        """
        Parse command line arguments.
        Check combination legality, print debug info.
        Apply selected options.
        """
        parser = self.init_argparser()
        args = parser.parse_args()

        # Setup logging output format.
        if args.debug == 0:
            FORMAT = "%(asctime)s %(levelname)7.7s %(funcName)-25.25s (%(lineno)3d) -- %(message)-130.130s"
            logging.basicConfig(level=logging.DEBUG, format=FORMAT,
                                datefmt='%Y-%m-%d %H:%M:%S')
        elif args.debug == 1:
            # TODO: Fix debug logging verbosity.
            pass

        elif args.debug == 2:
            # TODO: Fix debug logging verbosity.
            pass

        elif args.debug == 3:
            # TODO: Fix debug logging verbosity.
            pass

        elif args.verbose:
            FORMAT = "%(asctime)s %(levelname)-6s -- %(message)s"
            logging.basicConfig(level=logging.INFO, format=FORMAT,
                                datefmt='%Y-%m-%d %H:%M:%S')
        elif args.quiet:
            FORMAT = "%(levelname)s -- %(message)s"
            logging.basicConfig(level=logging.CRITICAL, format=FORMAT)
        else:
            FORMAT = "%(levelname)s -- %(message)s"
            logging.basicConfig(level=logging.WARNING, format=FORMAT)

        # Display help/usage information if no arguments are provided.
        if len(sys.argv) < 2:
            parser.print_help()
            exit(0)

        # Iterate over command line arguments ..
        if not args.input_files:
            logging.critical("No input files specified. Exiting.")
            exit(1)
        else:
            for arg in args.input_files:
                if os.path.isfile(arg) and os.access(arg, os.R_OK):
                    # print "File exists and is readable"
                    logging.info('Processing file \"%s\"' % str(arg))

                    # Create a file object representing the current arg.
                    f = FileObject(arg)

                    # Begin analysing the file.
                    analysis = Analysis(f)
                    analysis.run()

                    if args.add_datetime:
                        print('File: \"%s\"' % f.path)
                        analysis.print_all_datetime_info()
                        # analysis.print_oldest_datetime()
                        # analysis.prefix_date_to_filename()
                        print('')

                else:
                    # Unable to read file. Skip ..
                    # File is either missing or not readable. Skip ..
                    logging.error('Unable to read file \"%s\"' % str(file))
                    continue

        return args

    def get_args(self):
        """
        Return the command line arguments/options.
        :return: command line arguments
        """
        return self.args
