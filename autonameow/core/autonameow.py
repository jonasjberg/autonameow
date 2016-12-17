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

from . import version
from core import config_defaults
from core import options
from core.analyze.analysis import Analysis
from core.evaluate.filter import ResultFilter
from core.evaluate.matcher import RuleMatcher
from core.evaluate.namebuilder import NameBuilder
from core.fileobject import FileObject

terminal_width = 100


def display_start_banner():
    """
    Prints a "banner" with some ASCII art, program information and credits.
    """
    # TODO: Text alignment depends on manually hardcoding spaces! FIX!
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    print((Fore.LIGHTBLUE_EX +
    '''
   ###   ### ### ####### #####  ###  ##   ###   ##   ## ####### #####  ### ###
  #####  ### ###   ###  ### ### #### ##  #####  # # ### ####   ####### ### ###
 ### ### ### ###   ###  ### ### ####### ### ### ####### ###### ### ### #######
 ####### #######   ###  ####### ### ### ####### ### ### ####   ### ### ### ###
 ### ###  ### ##   ###   #####  ### ### ### ### ### ### ####### #####  ##   ##
    ''' + Fore.RESET))
    colortitle=Back.BLUE + Fore.BLACK + \
               ' ' + version.__title__.lower() + \
               ' ' + Back.RESET + Fore.RESET
    toplineleft = ' {title}  version {ver}'.format(title=colortitle,
                                                   ver=version.__version__)
    toplineright = version.__copyright__
    print(('{:<}{:>50}'.format(toplineleft, toplineright)))
    print(('{:>78}'.format(version.__url__)))
    print(('{:>78}'.format(version.__email__)))
    print('')
    print((Fore.LIGHTBLACK_EX +
          'Started at {date} by {user} on {platform}'.format(
              date=date,
              user=os.environ.get('USER'),
              platform=' '.join(platform.uname()[:3])) +
          Fore.RESET))


def display_end_banner(exit_code, elapsed_time):
    date = datetime.today().strftime('%Y-%m-%d %H:%M:%S')
    print((Fore.LIGHTBLACK_EX +
          'Stopped at {} (total execution time: {:.6f} seconds) '
          'with exit code [{}]'.format(date, elapsed_time, exit_code) +
          Fore.RESET))
    # TODO: Format the execution time to minutes and seconds if it exceeds
    #       60 seconds, hours, minutes and seconds if it exceeds 60 minutes ..


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
        self.args = None
        self.filter = None

    def run(self):
        # Display help/usage information if no arguments are provided.
        if not self.opts:
            print('Add "--help" to display usage information.')
            self.exit_program(0)

        # Handle the command line arguments.
        # TODO: What is parsed and why? opts or args? Where does it end up?
        self.args = options.parse_args(self.opts)

        # Setup results filtering
        self.filter = ResultFilter().configure_filter(self.args)

        # Display startup banner and other information if applicable.
        if self.args.verbose:
            display_start_banner()
        if self.args.dump_options:
            options.prettyprint_options(self.args)

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
                analysis = Analysis(current_file)

                # TODO: Fix this here below temporary printing of results.
                if self.args.list_datetime:
                    print(('File: "{}"'.format(current_file.path)))
                    analysis.print_all_datetime_info()
                    print('')

                if self.args.list_title:
                    print(('File: "{}"'.format(current_file.path)))
                    analysis.print_title_info()
                    print('')

                if self.args.list_all:
                    print(('File: "{}"'.format(current_file.path)))
                    analysis.print_all_results_info()
                    print('')

                # Create a rule matcher
                rule_matcher = RuleMatcher(current_file, config_defaults.rules)

                if self.args.prepend_datetime:
                    # TODO: Prepend datetime to filename.
                    logging.critical('This feature is not implemented yet.')
                    self.exit_program(1)

                if self.args.automagic:
                    # Create a name builder.
                    name_builder = NameBuilder(current_file, analysis.results,
                                               rule_matcher.active_rule)
                    name_builder.build()

                    if self.args.dry_run:
                        logging.info('Automagically built filename: '
                                     '"{}"'.format(name_builder.new_name))
                    else:
                        # TODO: Do actual file renaming.
                        pass

                elif self.args.interactive:
                    # Create a interactive interface.
                    pass

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
