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

from datetime import datetime

import util.disk
from analyze.analysis import Analysis
from file_object import FileObject


def arg_is_year(value):
    """
    Check if "value" is a year, as in 4 digits and 0 >= year > 9999 ..
    :return:
    """
    ivalue = None
    try:
        ivalue = int(value.strip())
    except ValueError:
        pass

    if ivalue:
        if len(str(ivalue)) == 4 and ivalue >= 0:
            return ivalue

    raise argparse.ArgumentTypeError('\"{}\" is not a valid year'.format(value))
    return None


class Autonameow(object):
    """
    Main class to manage "autonameow" instance.
    """

    def __init__(self):
        """
        Main program entry point
        """
        # Handle the command line arguments.
        self.filters = []
        self.args = self.parse_args()
        if self.args.verbose:
            self.display_options(self.args)

        # Iterate over command line arguments ..
        if not self.args.input_files:
            logging.critical('No input files specified. Exiting.')
            exit(1)
        else:
            try:
                self.handle_files()
            except KeyboardInterrupt:
                logging.critical('Received keyboard interrupt; Exiting ..')
                sys.exit()

    def handle_files(self):
        for arg in self.args.input_files:
            if os.path.isfile(arg) and os.access(arg, os.R_OK):
                # print "File exists and is readable"
                logging.info('Processing file \"%s\"' % str(arg))

                # Create a file object representing the current arg.
                curfile = FileObject(arg)

                # Begin analysing the file.
                analysis = Analysis(curfile, self.filters)
                analysis.run()

                if self.args.add_datetime:
                    print('File: \"%s\"' % curfile.path)
                    analysis.print_all_datetime_info()
                    analysis.find_most_probable_datetime()
                    # analysis.print_oldest_datetime()
                    # analysis.prefix_date_to_filename()
                    print('')

            else:
                # Unable to read file. Skip ..
                # File is either missing or not readable. Skip ..
                logging.error('Unable to read file \"%s\"' % str(file))
                continue

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
        optgrp_output.add_argument('-z', '--debug',
                                   # const=0, default='0', type=int,
                                   # nargs="?",
                                   # dest='debug',
                                   # help='debug verbosity: 0 = none, 1 = some, '
                                   #      '2 = more, 3 = everything. '
                                   #      'No number means some. '
                                   #      'Default is no debug verbosity.')
                                   dest='debug',
                                   action='store_true',
                                   help='debug mode')

        optgrp_output.add_argument('-v', '--verbose',
                                   dest='verbose',
                                   action='store_true',
                                   help='verbose mode')

        optgrp_output.add_argument('-q', '--quiet',
                                   dest='quiet',
                                   action='store_true',
                                   help='quiet mode')

        optgrp_action = parser.add_mutually_exclusive_group()
        optgrp_action.add_argument('--add-datetime',
                                   dest='add_datetime',
                                   action='store_true',
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

        optgrp_filter = parser.add_argument_group()
        optgrp_filter.add_argument('--ignore-year',
                                   metavar='',
                                   type=arg_is_year,
                                   default=[],
                                   nargs='*',
                                   dest='filter_ignore_year',
                                   action='store',
                                   help='ignore date/time-information '
                                        'containing this year')

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
        # if args.debug == 0:
        if args.debug:
            FORMAT = '%(asctime)s %(levelname)8.8s %(funcName)-25.25s (%(lineno)3d) -- %(message)-130.130s'
            logging.basicConfig(level=logging.DEBUG, format=FORMAT,
                                datefmt='%Y-%m-%d %H:%M:%S')
        # elif args.debug == 1:
        #     # TODO: Fix debug logging verbosity.
        #     pass
        #
        # elif args.debug == 2:
        #     # TODO: Fix debug logging verbosity.
        #     pass
        #
        # elif args.debug == 3:
        #     # TODO: Fix debug logging verbosity.
        #     pass

        elif args.verbose:
            FORMAT = '%(asctime)s %(levelname)-6s -- %(message)s'
            logging.basicConfig(level=logging.INFO, format=FORMAT,
                                datefmt='%Y-%m-%d %H:%M:%S')
        elif args.quiet:
            FORMAT = '%(levelname)s -- %(message)s'
            logging.basicConfig(level=logging.CRITICAL, format=FORMAT)
        else:
            FORMAT = '%(levelname)s -- %(message)s'
            logging.basicConfig(level=logging.WARNING, format=FORMAT)

        # TODO: Fix this and overall filter handling.
        if args.filter_ignore_year is not None and args.filter_ignore_year:
            for year in args.filter_ignore_year:
                try:
                    dt = datetime.strptime(str(year), '%Y')
                except ValueError as e:
                    logging.warning('Erroneous date format: {}'.format(e.message))
                else:
                    self.filters.append(dt)

            print self.filters

        # Display help/usage information if no arguments are provided.
        if len(sys.argv) < 2:
            parser.print_help()
            exit(0)

        return args

    def display_options(self, args):
        def print_line(k, v):
            print('{:<8}{:<20}  :  {:<60}'.format(' ', k, v))

        print('Output')
        print_line('debug mode', args.debug)
        print_line('verbose mode', args.verbose)
        print_line('quiet mode', args.quiet)
        print('Action')
        print_line('add datetime', args.add_datetime)
        print('Behavior')
        print_line('dry run', args.dry_run)
        print('Filter')
        print_line('ignore year', args.filter_ignore_year)
        print('Positional')
        print_line('input files', args.input_files)


    def get_args(self):
        """
        Return the command line arguments/options.
        :return: command line arguments
        """
        return self.args
