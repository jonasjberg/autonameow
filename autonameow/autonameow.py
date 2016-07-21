#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import argparse
import logging
import os
import sys
import platform
import time

from colorama import Fore
from colorama import Back
from datetime import datetime

import version
from analyze.analysis import Analysis
from file_object import FileObject
from util import dateandtime

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
    else:
        if ivalue:
            if len(str(ivalue)) == 4 and ivalue >= 0:
                return ivalue
    raise argparse.ArgumentTypeError('"{}" is not a valid year'.format(value))
    return None


def display_start_banner():
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
    print(' ' + Back.LIGHTBLACK_EX + Fore.LIGHTYELLOW_EX +
          ' ' + version.__title__.upper() +
          ' ' + Back.RESET + Fore.RESET +
          '  version ' + version.__version__)
    print(' ' + Back.LIGHTBLACK_EX + Fore.LIGHTYELLOW_EX +
          ' ' + len(version.__title__) * '~' +
          ' ' + Back.RESET + Fore.RESET + credits1)
    print(credits2)
    print(credits3)
    print(copyright1)
    print(license1)
    print('')
    print(Fore.LIGHTBLACK_EX +
          'Started at {} by {} on {}'.format(date, username, hostname) +
          Fore.RESET)


def display_end_banner(exit_code, elapsed_time):
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    print(Fore.LIGHTBLACK_EX +
          'Terminated at {} (total execution time: {:.6f} seconds) '
          'with exit code [{}]'.format(date, elapsed_time, exit_code) +
          Fore.RESET)


def display_options(args):
    """
    Display details on the command line options that are in effect.
    Mainly for debug purposes.
    :param args: arguments to display
    """

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
    print_line('add datetime', 'TRUE' if args.list_datetime else 'FALSE')
    print_line_section('Behavior configuration')
    print_line('dry run', 'TRUE' if args.dry_run else 'FALSE')
    print_line_section('Results filtering')
    print_line('ignore year',
               'TRUE' if args.filter_ignore_years else 'FALSE')
    print_line_section('Positional arguments')
    print_line('input files', 'TRUE' if args.input_files else 'FALSE')
    print('')


class Autonameow(object):
    """
    Main class to manage "autonameow" instance.
    """

    def __init__(self):
        """
        Main program entry point
        """
        # Save time of startup for later calculation of total runtime.
        self.start_time = time.time()

        # Display help/usage information if no arguments are provided.
        if len(sys.argv) < 2:
            print('Add "--help" to display usage information.')
            self.exit_program(0)

        # TODO: Fix the filtering! Not completed as-is.
        self.filter = {'ignore_years': [],
                       'ignore_before_year': None,
                       'ignore_after_year': None}

        # Handle the command line arguments.
        self.args = self._parse_args()

        # Display startup banner and other information if applicable.
        if self.args.verbose:
            display_start_banner()
        if self.args.dump_options:
            display_options(self.args)

        # Exit if no files are specified, for now.
        if not self.args.input_files:
            logging.warn('No input files specified ..')
            self.exit_program(1)

        # Iterate over command line arguments ..
        self._handle_files()
        self.exit_program()

    def _handle_files(self):
        """
        Iterate over passed arguments, which should be paths to files.
        """
        exit_code = 0
        if len(self.args.input_files) < 1:
            logging.critical('No input files specified.')
            return
        for arg in self.args.input_files:
            if not os.path.exists(arg):
                logging.error('Skipping non-existent file/directory '
                              '"{}"'.format(str(arg)))
                continue
            elif os.path.isdir(arg):
                logging.error('Skipping directory "{}"'.format(str(arg)))
                continue
            elif os.path.islink(arg):
                logging.error('Skipping symbolic link "{}"'.format(str(arg)))
                continue
            elif not os.access(arg, os.R_OK):
                logging.error('Not authorized to read file '
                              '"{}"'.format(str(arg)))
                continue
            else:
                # File exists and is readable.
                logging.info('Processing file "{}"'.format(str(arg)))

                # Create a file object representing the current arg.
                current_file = FileObject(arg)

                # Begin analysing the file.
                analysis = Analysis(current_file, self.filter)

                if self.args.list_datetime:
                    print('File: "{}"'.format(current_file.path))
                    analysis.print_all_datetime_info()
                    # analysis.print_oldest_datetime()
                    # analysis.prefix_date_to_filename()
                    print('')

                # Create a action object.
                # TODO: Implement this or something similar to it.
                # action = None
                # action = RenameAction(current_file, results)

    def _init_argparser(self):
        """
        Initialize the argparser. Add all arguments/options.
        :return: the argument parser
        """
        parser = argparse.ArgumentParser(
            prog='autonameow',
            description='Automatic renaming of files from analysis of '
                        'several sources of information.',
            epilog='Example usage: TODO ..')

        # Add option group for controlling what is printed to stdout.
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

        parser.add_argument('--dump-options',
                            dest='dump_options',
                            action='store_true',
                            help='dump options to stdout')

        # Add option group for actions to be performed.
        optgrp_action = parser.add_argument_group('Action options')
        optgrp_action.add_argument('--list-datetime',
                                   dest='list_datetime',
                                   action='store_true',
                                   help='list all found date/time-information')

        optgrp_action.add_argument('--prepend-datetime',
                                   dest='prepend_datetime',
                                   action='store_true',
                                   help='prepend most probable '
                                        'date/time-information to file name')

        parser.add_argument(dest='input_files',
                            metavar='filename',
                            nargs='*',
                            help='input file(s)')

        parser.add_argument('-d', '--dry-run',
                            dest='dry_run',
                            action='store_true',
                            help='simulate what would happen but do not '
                                 'actually write any changes to disk')

        # Add option group for filter options.
        optgrp_filter = parser.add_argument_group('Processing options')
        ignore_to_year_default = str(dateandtime.YEAR_LOWER_LIMIT.strftime('%Y'))
        optgrp_filter.add_argument('--ignore-before-year',
                                   metavar='YYYY',
                                   type=arg_is_year,
                                   default=ignore_to_year_default,
                                   nargs='?',
                                   dest='filter_ignore_to_year',
                                   action='store',
                                   help='ignore date/time-information from '
                                        'this year and the years prior. '
                                        'Default: {}'.format(
                                         ignore_to_year_default))

        ignore_from_year_default = str(dateandtime.YEAR_UPPER_LIMIT.strftime('%Y'))
        optgrp_filter.add_argument('--ignore-after-year',
                                   metavar='YYYY',
                                   type=arg_is_year,
                                   default=ignore_from_year_default,
                                   nargs='?',
                                   dest='filter_ignore_from_year',
                                   action='store',
                                   help='ignore date/time-information from '
                                        'this year onward. '
                                        'Default: {}'.format(
                                         ignore_from_year_default))

        optgrp_filter.add_argument('--ignore-years',
                                   metavar='YYYY',
                                   type=arg_is_year,
                                   default=[],
                                   nargs='*',
                                   dest='filter_ignore_years',
                                   action='store',
                                   help='ignore date/time-information '
                                        'from year(s)')

        return parser

    def _parse_args(self):
        """
        Parse command line arguments.
        Check combination legality, print debug info.
        Apply selected options.
        """
        parser = self._init_argparser()
        args = parser.parse_args()

        # Setup logging output format.
        # if args.debug == 0:
        if args.debug:
            fmt = Fore.LIGHTBLACK_EX + '%(asctime)s' + Fore.RESET + \
                  Fore.LIGHTBLUE_EX + ' %(levelname)-8.8s' + Fore.RESET + \
                  ' %(funcName)-25.25s (%(lineno)3d) ' + \
                  Fore.LIGHTBLACK_EX + ' -- ' + Fore.RESET + \
                  '%(message)-120.120s'
            logging.basicConfig(level=logging.DEBUG, format=fmt,
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
            fmt = Fore.LIGHTBLACK_EX + '%(asctime)s' + Fore.RESET + \
                  Fore.LIGHTBLUE_EX + ' %(levelname)-8.8s' + Fore.RESET + \
                  Fore.LIGHTBLACK_EX + ' -- ' + Fore.RESET + \
                  '%(message)-130.130s'
            logging.basicConfig(level=logging.INFO, format=fmt,
                                datefmt='%Y-%m-%d %H:%M:%S')
        elif args.quiet:
            fmt = '%(levelname)s -- %(message)s'
            logging.basicConfig(level=logging.CRITICAL, format=fmt)
        else:
            fmt = '%(levelname)s -- %(message)s'
            logging.basicConfig(level=logging.WARNING, format=fmt)

        # TODO: Fix this and overall filter handling.
        if args.filter_ignore_years:
            for year in args.filter_ignore_years:
                try:
                    dt = datetime.strptime(str(year), '%Y')
                except ValueError as e:
                    logging.warning('Erroneous date format: '
                                    '"{}"'.format(e.message))
                else:
                    if dt not in self.filter['ignore_years']:
                        self.filter['ignore_years'].append(dt)

            ignored_years = ', '.join((str(yr.year)
                                       for yr in self.filter['ignore_years']))
            logging.debug('Using filter: ignore date/time-information for these'
                          ' years: {}'.format(ignored_years))

        if args.filter_ignore_to_year:
            try:
                dt = datetime.strptime(str(args.filter_ignore_to_year), '%Y')
            except ValueError as e:
                logging.warning('Erroneous date format: {}'.format(e.message))
            else:
                logging.debug('Using filter: ignore date/time-information that'
                              ' predate year {}'.format(dt.year))
                self.filter['ignore_before_year'] = dt

        if args.filter_ignore_from_year:
            try:
                dt = datetime.strptime(str(args.filter_ignore_from_year), '%Y')
            except ValueError as e:
                logging.warning('Erroneous date format: {}'.format(e.message))
            else:
                logging.debug('Using filter: ignore date/time-information that'
                              ' follow year {}'.format(dt.year))
                self.filter['ignore_after_year'] = dt

        return args

    def exit_program(self, exit_code=0):
        try:
            exit_code = int(exit_code)
        except TypeError:
            exit_code = 1

        elapsed_time = time.time() - self.start_time

        if self.args.verbose:
            display_end_banner(exit_code, elapsed_time)

        logging.debug('Exiting with exit code: {}'.format(exit_code))
        logging.debug('Total execution time: '
                      '{:.6f} seconds'.format(elapsed_time))
        sys.exit(exit_code)
