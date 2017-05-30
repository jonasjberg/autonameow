#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2017 Jonas Sjöberg
#   Personal site:   http://www.jonasjberg.com
#   GitHub:          https://github.com/jonasjberg
#   University mail: js224eh[a]student.lnu.se
#
#   This file is part of autonameow.
#
#   autonameow is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation.
#
#   autonameow is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with autonameow.  If not, see <http://www.gnu.org/licenses/>.

import logging as log
import os
import platform
import sys
import time

from core import config
from core import options
from core.analysis import Analysis
from core.config.configuration import Configuration
from core.evaluate.filter import ResultFilter
from core.evaluate.namebuilder import NameBuilder
from core.exceptions import InvalidFileArgumentError
from core.fileobject import FileObject
from core.options import print_ascii_banner, print_exit_info, print_start_info
from core.util import misc
from . import version

terminal_width = 100
PYTHON_VERSION = sys.version.replace('\n', '')


class Autonameow(object):
    """
    Main class to manage a running "autonameow" instance.
    """

    def __init__(self, opts):
        """
        Main program entry point.  Initializes a autonameow instance/session.

        Args:
            opts: Option arguments as a list of strings.
        """
        # Save time of startup for later calculation of total runtime.
        self.start_time = time.time()

        self.opts = opts        # "Raw" option arguments as list of strings.
        self.args = None        # Parsed options returned by argparse.

        self.filter = None
        self.config = Configuration()

    def run(self):
        # Display help/usage information if no arguments are provided.
        if not self.opts:
            print('Add "--help" to display usage information.')
            self.exit_program(0)

        # Handle the command line arguments.
        self.args = options.parse_args(self.opts)

        # Display various information depending on verbosity level.
        if self.args.verbose:
            print_start_info()

        if self.args.debug:
            log.debug('Started {} version {}'.format(version.__title__,
                                                         version.__version__))
            log.debug('Running on Python {}'.format(PYTHON_VERSION))
            log.debug('Hostname: {}'.format(' '.join(platform.uname()[:3])))
            log.debug('Process ID: {}'.format(os.getpid()))

        # Display startup banner with program version and exit.
        if self.args.show_version:
            print_ascii_banner()
            self.exit_program(0)

        # Check configuration file. If no alternate config file path is
        # provided and no config file is found at default paths; copy the
        # template config and tell the user.
        if self.args.config_path:
            self.config.load_from_disk(self.args.config_path)
        else:
            _config_path = config.config_file_path()

            if not config.has_config_file():
                log.warning('No configuration file was found.')

                try:
                    config.write_default_config()
                except PermissionError:
                    log.critical('Unable to write config file to path: '
                                 '"{!s}"'.format(_config_path))
                    self.exit_program(1)
                else:
                    log.info('A template configuration file was written to '
                             '"{!s}"'.format(_config_path))
                    log.info('Use this file to configure '
                             '{}.'.format(version.__title__))
            else:
                log.debug('Using configuration: "{}"'.format(_config_path))
                self.config.load_from_disk(_config_path)

        # Setup results filtering
        self.filter = ResultFilter().configure_filter(self.args)

        if self.args.dump_options:
            options.prettyprint_options(self.args)

        # Exit if no files are specified, for now.
        if not self.args.input_paths:
            log.warning('No input files specified ..')
            self.exit_program(1)

        # Iterate over command line arguments ..
        exit_code = self._handle_files()
        self.exit_program(exit_code)

    def _handle_files(self):
        """
        Main loop. Iterates over passed arguments (paths/files).
        """
        exit_code = 0
        for arg in self.args.input_paths:
            log.info('Processing: "{!s}"'.format(arg))

            # Try to create a file object representing the current argument.
            try:
                current_file = FileObject(arg)
            except InvalidFileArgumentError as e:
                log.warning('{!s} - SKIPPING: "{!s}"'.format(e, arg))
                continue

            # Begin analysing the file.
            analysis = Analysis(current_file)

            # TODO: [BL007] Move results printing to separate module/class.
            if self.args.list_datetime:
                print(('File: "{}"'.format(current_file.path)))
                misc.dump(analysis.results.get('datetime'))
                print('')

            # TODO: [BL007] Move results printing to separate module/class.
            if self.args.list_title:
                print(('File: "{}"'.format(current_file.path)))
                misc.dump(analysis.results.get('title'))
                print('')

            # TODO: [BL007] Move results printing to separate module/class.
            if self.args.list_all:
                print(('File: "{}"'.format(current_file.path)))
                misc.dump(analysis.results.get_all())
                print('')

            if self.args.prepend_datetime:
                # TODO: Prepend datetime to filename.
                log.critical('[UNIMPLEMENTED FEATURE] prepend_datetime')
                self.exit_program(1)

            if self.args.automagic:
                log.critical('[UNIMPLEMENTED FEATURE] automagic mode')
                exit_code &= 1

                # Create a name builder.
                # TODO: [BL010] Implement NameBuilder.
                name_builder = NameBuilder(current_file, analysis.results,
                                           self.config)
                try:
                    new_name = name_builder.build()
                except NotImplementedError:
                    log.critical('TODO: [BL010] Implement NameBuilder.')

                if self.args.dry_run:
                    log.info('Automagically built filename: '
                             '"{}"'.format(new_name))
                else:
                    # TODO: [BL011] Rename files.
                    log.critical('[UNIMPLEMENTED FEATURE] not dry_run')
                    exit_code &= 1

            elif self.args.interactive:
                # Create a interactive interface.
                # TODO: [BL013] Interactive mode in 'interactive.py'.
                log.critical('[UNIMPLEMENTED FEATURE] interactive mode')
                exit_code &= 1

        return exit_code

    def exit_program(self, exit_code):
        """
        Main program exit point.  Shuts down this autonameow instance/session.

        Args:
            exit_code: Integer exit code to pass to the parent process.
                Indicate success with 0, failure non-zero.
        """
        elapsed_time = time.time() - self.start_time

        try:
            if self.args.verbose:
                print_exit_info(exit_code, elapsed_time)
        except AttributeError:
            pass

        log.debug('Exiting with exit code: {}'.format(exit_code))
        log.debug('Total execution time: {:.6f} seconds'.format(elapsed_time))
        sys.exit(exit_code)
