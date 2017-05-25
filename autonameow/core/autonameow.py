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

import logging
import os
import platform
import sys
import time

from core import config
from core import options
from core.analyze.analysis import Analysis
from core.config import config_defaults
from core.evaluate.filter import ResultFilter
from core.evaluate.matcher import RuleMatcher
from core.evaluate.namebuilder import NameBuilder
from core.fileobject import FileObject
from core.options import display_start_banner, display_end_banner
from core.util import misc
from . import version

terminal_width = 100
PYTHON_VERSION = sys.version.replace('\n', '')


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
        self.args = options.parse_args(self.opts)

        # Display detailed information in debug mode.
        if self.args.debug:
            logging.debug('Started {} version {}'.format(version.__title__,
                                                         version.__version__))
            logging.debug('Running on Python {}'.format(PYTHON_VERSION))
            logging.debug('Hostname: {}'.format(' '.join(platform.uname()[:3])))
            logging.debug('Process ID: {}'.format(os.getpid()))

        # Display startup banner with program version and exit.
        if self.args.show_version:
            display_start_banner()
            self.exit_program(0)

        # Check configuration file. If no alternate config file path is
        # provided and no config file is found at default paths; copy the
        # template config and tell the user.
        # TODO: [BL004] Implement storing settings in configuration file.
        if not self.args.config_path:
            if not config.has_config_file():
                logging.warning('No configuration file was found.')

                _new_config = config.write_default_config()
                if _new_config:
                    logging.info('A configuration file template with example '
                                 'settings has been written to '
                                 '"{}"'.format(str(_new_config)))
                    logging.info('Use this file to configure '
                                 '{}.'.format(version.__title__))
                else:
                    logging.error('Unable to write template config file')
                    # TODO: Handle this ..

        # Setup results filtering
        self.filter = ResultFilter().configure_filter(self.args)

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

                # Create a rule matcher
                rule_matcher = RuleMatcher(current_file, config_defaults.rules)

                if self.args.prepend_datetime:
                    # TODO: Prepend datetime to filename.
                    logging.critical('[UNIMPLEMENTED FEATURE] prepend_datetime')
                    self.exit_program(1)

                if self.args.automagic:
                    # Create a name builder.
                    # TODO: [BL010] Implement NameBuilder.
                    name_builder = NameBuilder(current_file, analysis.results,
                                               rule_matcher.active_rule)
                    name_builder.build()

                    if self.args.dry_run:
                        logging.info('Automagically built filename: '
                                     '"{}"'.format(name_builder.new_name))
                    else:
                        # TODO: [BL011] Rename files.
                        logging.critical('[UNIMPLEMENTED FEATURE] not dry_run')
                        pass

                elif self.args.interactive:
                    # Create a interactive interface.
                    # TODO: [BL013] Interactive mode in 'interactive.py'.
                    logging.critical('[UNIMPLEMENTED FEATURE] interactive mode')
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
