#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging
import os
import platform
import sys
import time

from colorama import Back
from colorama import Fore
from datetime import datetime

import version
from core import options
from core.analyze.analysis import Analysis
from core.fileobject import FileObject

terminal_width = 100


def display_start_banner():
    """
    Prints a "banner" with some ASCII art, program information and credits.
    """
    # TODO: Text alignment depends on manually hardcoding spaces! FIX!
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    print(Fore.LIGHTYELLOW_EX +
    '''
   ###   ### ### ####### #####  ###  ##   ###   ##   ## ####### #####  ### ###
  #####  ### ###   ###  ### ### #### ##  #####  # # ### ####   ####### ### ###
 ### ### ### ###   ###  ### ### ####### ### ### ####### ###### ### ### #######
 ####### #######   ###  ####### ### ### ####### ### ### ####   ### ### ### ###
 ### ###  ### ##   ###   #####  ### ### ### ### ### ### ####### #####  ##   ##
    ''' +
          Fore.RESET)
    colortitle=Back.LIGHTBLACK_EX + Fore.LIGHTYELLOW_EX + \
               ' ' + version.__title__.lower() + \
               ' ' + Back.RESET + Fore.RESET
    toplineleft = ' {colortitle}  version {version}'.format(colortitle=colortitle,
                                                    version=version.__version__)
    toplineright = 'Copyright(c)2016 ' + version.__author__
    print('{:<}{:>50}'.format(toplineleft, toplineright))
    print('{:>78}'.format(version.__url__))
    print('{:>78}'.format(version.__email__))
    print('')
    print(Fore.LIGHTBLACK_EX +
          'Started at {date} by {user} on {platform}'.format(
              date=date,
              user=os.environ.get('USER'),
              platform=' '.join(platform.uname()[:3])) +
          Fore.RESET)


def display_end_banner(exit_code, elapsed_time):
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    print(Fore.LIGHTBLACK_EX +
          'Stopped at {} (total execution time: {:.6f} seconds) '
          'with exit code [{}]'.format(date, elapsed_time, exit_code) +
          Fore.RESET)
    # TODO: Format the execution time to minutes and seconds if it exceeds
    #       60 seconds, hours, minutes and seconds if it exceeds 60 minutes ..


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
    print_line_section('Actions to be performed')
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

    def __init__(self, opts):
        """
        Main program entry point
        """
        # Save time of startup for later calculation of total runtime.
        self.start_time = time.time()

        self.opts = opts

    def run(self):
        # Display help/usage information if no arguments are provided.
        if len(self.opts) < 2:
            print('Add "--help" to display usage information.')
            self.exit_program(0)

        # TODO: Fix the filtering! Not completed as-is.
        self.filter = {'ignore_years': [],
                       'ignore_before_year': None,
                       'ignore_after_year': None}

        # Handle the command line arguments.
        self.args = options.parse_args()

        # TODO: Fix this and overall filter handling.
        if self.args.filter_ignore_years:
            for year in self.args.filter_ignore_years:
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

        if self.args.filter_ignore_to_year:
            try:
                dt = datetime.strptime(str(self.args.filter_ignore_to_year),
                                       '%Y')
            except ValueError as e:
                logging.warning('Erroneous date format: {}'.format(e.message))
            else:
                logging.debug('Using filter: ignore date/time-information that'
                              ' predate year {}'.format(dt.year))
                self.filter['ignore_before_year'] = dt

        if self.args.filter_ignore_from_year:
            try:
                dt = datetime.strptime(str(self.args.filter_ignore_from_year),
                                       '%Y')
            except ValueError as e:
                logging.warning('Erroneous date format: {}'.format(e.message))
            else:
                logging.debug('Using filter: ignore date/time-information that'
                              ' follow year {}'.format(dt.year))
                self.filter['ignore_after_year'] = dt

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
            logging.error('No input files specified.')
            return
        for arg in self.args.input_files:
            if not self._check_file(arg):
                continue
            else:
                logging.info('Processing file "{}"'.format(str(arg)))

                # Create a file object representing the current arg.
                current_file = FileObject(arg)

                # Begin analysing the file.
                analysis = Analysis(current_file, self.filter)

                if self.args.list_datetime:
                    print('File: "{}"'.format(current_file.path))
                    analysis.print_all_datetime_info()
                    print('')

                if self.args.list_title:
                    print('File: "{}"'.format(current_file.path))
                    analysis.print_title_info()
                    print('')

                if self.args.list_all:
                    print('File: "{}"'.format(current_file.path))
                    analysis.print_all_results_info()
                    print('')

                # Create a action object.
                # TODO: Implement this or something similar to it.
                # action = None
                # action = RenameAction(current_file, results)

    def _check_file(self, file):
        if not os.path.exists(file):
            logging.warning('Skipping non-existent file/directory '
                            '"{}"'.format(str(file)))
            return False
        elif os.path.isdir(file):
            logging.warning('Skipping directory "{}"'.format(str(file)))
            return False
        elif os.path.islink(file):
            logging.warning('Skipping symbolic link "{}"'.format(str(file)))
            return False
        elif not os.access(file, os.R_OK):
            logging.error('Not authorized to read file '
                          '"{}"'.format(str(file)))
            return False
        else:
            # File exists and is readable.
            return True

    def exit_program(self, exit_code=0):
        try:
            exit_code = int(exit_code)
        except TypeError:
            exit_code = 1

        elapsed_time = time.time() - self.start_time

        try:
            if self.args.verbose:
                display_end_banner(exit_code, elapsed_time)
        except AttributeError:
            pass

        logging.debug('Exiting with exit code: {}'.format(exit_code))
        logging.debug('Total execution time: '
                      '{:.6f} seconds'.format(elapsed_time))
        sys.exit(exit_code)
