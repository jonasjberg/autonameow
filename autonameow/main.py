#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import argparse
import logging
import os
import sys
import platform

from colorama import Fore
from colorama import Back
from datetime import datetime

import util.disk
import version
from analyze.analysis import Analysis
from file_object import FileObject

terminal_width = 100


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
            self.display_start_banner()
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
        """
        Iterate over passed arguments, which should be paths to files.
        """
        for arg in self.args.input_files:
            if not os.path.exists(arg):
                logging.error('Skipping non-existent file/directory ' '\"{}\"'.format(str(arg)))
                continue
            elif os.path.isdir(arg):
                logging.error('Skipping directory \"{}\"'.format(str(arg)))
                continue
            elif os.path.islink(arg):
                logging.error('Skipping symbolic link \"{}\"'.format(str(arg)))
                continue
            elif not os.access(arg, os.R_OK):
                logging.error('Not authorized to read file '
                              '\"{}\"'.format(str(arg)))
                continue
            else:
                # print "File exists and is readable"
                logging.info('Processing file \"%s\"'.format(str(arg)))

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
                            action='store_true',
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
            FORMAT = Fore.LIGHTBLACK_EX + '%(asctime)s' + Fore.RESET + \
                     ' %(levelname)-8.8s %(funcName)-25.25s (%(lineno)3d) ' \
                     '-- %(message)-130.130s'
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
            FORMAT = Fore.LIGHTBLACK_EX + '%(asctime)s' + Fore.RESET + \
                     ' %(levelname)-8.8s' + Fore.LIGHTBLACK_EX + ' -- ' + Fore.RESET + '%(message)-130.130s'
            logging.basicConfig(level=logging.INFO, format=FORMAT,
                                datefmt='%Y-%m-%d %H:%M:%S')
        elif args.quiet:
            FORMAT = '%(levelname)s -- %(message)s'
            logging.basicConfig(level=logging.CRITICAL, format=FORMAT)
        else:
            FORMAT = '%(levelname)s -- %(message)s'
            logging.basicConfig(level=logging.WARNING, format=FORMAT)

        # TODO: Fix this and overall filter handling.
        if args.filter_ignore_year and args.filter_ignore_year is not None:
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
            logging.critical('Add "--help" to display usage information.')
            # parser.print_help()
            exit(0)

        return args

    def display_options(self, args):
        def print_line(k, v):
            print('{:<4}{:<20}  :  {:<60}'.format(' ', k, v))

        def print_line_section(text):
            if not text.strip():
                return

            pad_left = 2
            pad_right = terminal_width - len(text) - 2
            strbuf = '\n'
            strbuf += Back.LIGHTBLACK_EX + Fore.LIGHTWHITE_EX
            strbuf += ' ' * pad_left
            strbuf += text.upper() + ' ' * pad_right
            strbuf += Back.RESET + Fore.RESET
            print(strbuf)

        print_line_section('Output options')
        print_line('debug mode', 'TRUE' if args.debug else 'FALSE')
        print_line('verbose mode', 'TRUE' if args.verbose else 'FALSE')
        print_line('quiet mode', 'TRUE' if args.quiet else 'FALSE')
        print_line_section('Actions to performed')
        print_line('add datetime', 'TRUE' if args.add_datetime else 'FALSE')
        print_line_section('Behavior configuration')
        print_line('dry run', 'TRUE' if args.dry_run else 'FALSE')
        print_line_section('Results filtering')
        print_line('ignore year', 'TRUE' if args.filter_ignore_year else 'FALSE')
        print_line_section('Positional arguments')
        print_line('input files', 'TRUE' if args.input_files else 'FALSE')
        print('')

    def get_args(self):
        """
        Return the command line arguments/options.
        :return: command line arguments
        """
        return self.args

    def display_start_banner(self):
        """
        Prints a "banner" with program information and credits.
        """
        # TODO: Text alignment depends on manually hardcoding spaces! FIX!
        print('')
        date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
        username = os.environ.get('USER')
        hostname = ' '.join(platform.uname()[:3])
        credits1 = '  written by ' + version.__author__
        credits2 = ' ' * 26 + version.__url__
        credits3 = ' ' * 26 + version.__email__
        copyright1 = ' ' * 15 + 'Copyright(c)2016 Jonas Sjoberg'
        license1 = ' ' * 15 + 'Please see "LICENSE.md" for licensing details.'
        print(' ' + Back.LIGHTBLACK_EX + Fore.LIGHTYELLOW_EX + ' ' + version.__title__.upper() + ' ' + Back.RESET + Fore.RESET + '  version ' + version.__version__)
        print(' ' + Back.LIGHTBLACK_EX + Fore.LIGHTYELLOW_EX + ' ' + len(version.__title__) * '~' + ' ' + Back.RESET + Fore.RESET + credits1)
        print(credits2)
        print(credits3)
        print(copyright1)
        print(license1)
        print('')
        print(Fore.LIGHTBLACK_EX + 'Started at {} by {} on {}'.format(date, username, hostname) + Fore.RESET)
