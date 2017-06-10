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
import sys
import time

from core import (
    config,
    constants
)
from core import options
from core.analysis import Analysis
from core.config.configuration import Configuration
from core.evaluate.filter import ResultFilter
from core.evaluate.namebuilder import NameBuilder
from core.exceptions import (
    InvalidFileArgumentError,
    ConfigurationSyntaxError,
    AutonameowException,
    NameBuilderError,
    ConfigError
)
from core.fileobject import FileObject
from core.util import (
    cli,
    misc,
    diskutils
)
from . import version


exit_code = constants.EXIT_SUCCESS


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
            self.exit_program(constants.EXIT_SUCCESS)

        # Handle the command line arguments.
        self.args = options.parse_args(self.opts)

        # Display various information depending on verbosity level.
        if self.args.verbose or self.args.debug:
            cli.print_start_info()

        # Display startup banner with program version and exit.
        if self.args.show_version:
            cli.print_ascii_banner()
            self.exit_program(constants.EXIT_SUCCESS)

        # Check configuration file. If no alternate config file path is
        # provided and no config file is found at default paths; copy the
        # template config and tell the user.
        if self.args.config_path:
            try:
                log.info('Using configuration file: '
                         '"{!s}"'.format(self.args.config_path))
                self.config.load(self.args.config_path)
            except ConfigError as e:
                log.critical('Failed to load configuration file!')
                log.debug(str(e))
                self.exit_program(constants.EXIT_ERROR)
        else:
            _config_path = config.config_file_path()

            if not config.has_config_file():
                log.info('No configuration file was found. Writing default ..')

                try:
                    config.write_default_config()
                except PermissionError:
                    log.critical('Unable to write configuration file to path: '
                                 '"{!s}"'.format(_config_path))
                    self.exit_program(constants.EXIT_ERROR)
                else:
                    cli.msg('A template configuration file was written to '
                            '"{!s}"'.format(_config_path), type='info')
                    cli.msg('Use this file to configure {}. '
                            'Refer to the documentation for additional '
                            'information.'.format(version.__title__),
                            type='info')
                    self.exit_program(constants.EXIT_SUCCESS)
            else:
                log.info('Using configuration: "{}"'.format(_config_path))
                try:
                    self.config.load(_config_path)
                except ConfigurationSyntaxError as e:
                    log.critical('Configuration syntax error: "{!s}"'.format(e))

        # TODO: Integrate filter settings in configuration (file).
        self.filter = ResultFilter().configure_filter(self.args)

        if self.args.dump_options:
            include_opts = {'config_file_path': config.config_file_path()}
            options.prettyprint_options(self.args, include_opts)

        if self.args.dump_config:
            log.info('Dumping active configuration ..')
            cli.msg('Active Configuration:', type='heading')
            cli.msg(str(self.config))
            self.exit_program(constants.EXIT_SUCCESS)

        # Exit if no files are specified, for now.
        if not self.args.input_paths:
            log.warning('No input files specified ..')
            self.exit_program(constants.EXIT_SUCCESS)

        # Iterate over command line arguments ..
        self._handle_files()
        self.exit_program(exit_code)

    def _handle_files(self):
        """
        Main loop. Iterates over passed arguments (paths/files).
        """
        for arg in self.args.input_paths:
            log.info('Processing: "{!s}"'.format(arg))

            # Try to create a file object representing the current argument.
            try:
                current_file = FileObject(arg, self.config)
            except InvalidFileArgumentError as e:
                log.warning('{!s} - SKIPPING: "{!s}"'.format(e, arg))
                continue

            # Begin analysing the file.
            analysis = Analysis(current_file)
            try:
                analysis.start()
            except AutonameowException as e:
                log.critical('Analysis FAILED: {!s}'.format(e))
                log.critical('Skipping file "{}" ..'.format(current_file))
                set_exit_code(constants.EXIT_WARNING)
                continue

            list_any = (self.args.list_datetime or self.args.list_title
                        or self.args.list_all)
            if list_any:
                cli.msg(('File: "{}"'.format(current_file.abspath)))

            if self.args.list_all:
                log.info('Listing ALL analysis results ..')
                cli.msg('Legacy Results Data', type='heading', log=True)
                cli.msg(misc.dump(analysis.results.get_all()))
                cli.msg('Redesigned Results Data', type='heading', log=True)
                cli.msg(misc.dump(analysis.results.new_data))
            else:
                if self.args.list_datetime:
                    log.info('Listing "datetime" analysis results ..')
                    cli.msg(misc.dump(analysis.results.get('datetime')))
                if self.args.list_title:
                    log.info('Listing "title" analysis results ..')
                    cli.msg(misc.dump(analysis.results.get('title')))

            if self.args.prepend_datetime:
                # TODO: Prepend datetime to filename.
                log.warning('[UNIMPLEMENTED FEATURE] prepend_datetime')
                self.exit_program(constants.EXIT_ERROR)

            if self.args.automagic:
                # Create a name builder.
                try:
                    self.builder = NameBuilder(current_file, analysis.results,
                                               self.config)
                    new_name = self.builder.build()
                except NotImplementedError:
                    log.critical('TODO: [BL010] Implement NameBuilder.')
                    set_exit_code(constants.EXIT_WARNING)
                except NameBuilderError as e:
                    log.critical('Name assembly FAILED: {!s}'.format(e))
                    set_exit_code(constants.EXIT_WARNING)
                    continue
                else:
                    # TODO: Respect '--quiet' option. Suppress output.
                    cli.msg('New name: "{}"'.format(new_name))
                    renamed_ok = self.do_rename(current_file.abspath, new_name,
                                                dry_run=self.args.dry_run)
                    if renamed_ok:
                        set_exit_code(constants.EXIT_SUCCESS)
                    else:
                        set_exit_code(constants.EXIT_WARNING)

            elif self.args.interactive:
                # TODO: Create a interactive interface.
                # TODO: [BL013] Interactive mode in 'interactive.py'.
                log.warning('[UNIMPLEMENTED FEATURE] interactive mode')

        return exit_code

    def exit_program(self, exit_code_):
        """
        Main program exit point.  Shuts down this autonameow instance/session.

        Args:
            exit_code_: Integer exit code to pass to the parent process.
                Indicate success with 0, failure non-zero.
        """
        elapsed_time = time.time() - self.start_time

        exit_code = set_exit_code(exit_code_)

        if self.args:
            if self.args.verbose:
                cli.print_exit_info(exit_code, elapsed_time)

        log.debug('Exiting with exit code: {}'.format(exit_code))
        log.debug('Total execution time: {:.6f} seconds'.format(elapsed_time))
        sys.exit(exit_code)

    def do_rename(self, from_path, new_basename, dry_run=True):
        """
        Renames a file at the given path to a new base name.

        Args:
            from_path: Path to the file to rename.
            new_basename: The new basename for the file.
            dry_run: Controls whether the renaming is actually performed.

        Returns:
            0 for success, 1 for errors

        """
        dest_basename = diskutils.sanitize_filename(new_basename)
        from_basename = diskutils.file_basename(from_path)
        log.debug('Sanitized basename: "{!s}"'.format(dest_basename))

        if dry_run is False:
            try:
                diskutils.rename_file(from_path, dest_basename)
            except (FileNotFoundError, FileExistsError, OSError) as e:
                log.error('Rename FAILED: {!s}'.format(e))
                return False
            else:
                message = 'Renamed "{!s}" -> "{!s}"'
                cli.msg(message.format(from_basename, dest_basename),
                        type='color_quoted')
                return True
        else:
            message = 'Would have renamed "{!s}" -> "{!s}"'
            cli.msg(message.format(from_basename, dest_basename),
                    type='color_quoted')
            return True


def set_exit_code(value):
    """
    Updates the global program exit code value.

    The exit code is only actually updated if the given value is greater
    than the current value. This makes errors take precedence over warnings.

    Args:
        value: The new exit status as an integer, preferably one of
        the values in 'constants.py' prefixed 'EXIT_'.

    Returns:
        The current exit code as an integer.
    """
    global exit_code

    if value > exit_code:
        log.debug('Global exit code updated: {} -> {}'.format(exit_code, value))
        exit_code = value

    return exit_code
