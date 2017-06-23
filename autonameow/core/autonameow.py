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
    constants,
    util
)
from core import options
from core.analysis import Analysis
from core.config.configuration import Configuration
from core.evaluate.filter import ResultFilter
from core.evaluate.namebuilder import NameBuilder
from core.evaluate.rulematcher import RuleMatcher
from core.exceptions import (
    InvalidFileArgumentError,
    ConfigurationSyntaxError,
    AutonameowException,
    NameBuilderError,
    ConfigError
)
from core.extraction import Extraction
from core.fileobject import FileObject
from core.util import (
    cli,
    misc,
    diskutils
)
from . import version


class Autonameow(object):
    """
    Main class to manage a running "autonameow" instance.
    """

    def __init__(self, args):
        """
        Main program entry point.  Initializes a autonameow instance/session.

        Args:
            args: Option arguments as a list of strings.
        """
        self._exit_code = constants.EXIT_SUCCESS

        # For calculating the total runtime.
        self.start_time = time.time()

        self.args = args        # "Raw" option arguments as list of strings.
        self.opts = None        # Parsed options returned by argparse.

        self.filter = None
        self.config = Configuration()

    def run(self):
        # Display help/usage information if no arguments are provided.
        if not self.args:
            print('Add "--help" to display usage information.')
            self.exit_program(constants.EXIT_SUCCESS)

        # Handle the command line arguments and setup logging.
        self.opts = options.initialize(self.args)

        # Display various information depending on verbosity level.
        if self.opts.verbose or self.opts.debug:
            cli.print_start_info()

        # Display startup banner with program version and exit.
        if self.opts.show_version:
            cli.print_ascii_banner()
            self.exit_program(constants.EXIT_SUCCESS)

        # Check configuration file. If no alternate config file path is
        # provided and no config file is found at default paths; copy the
        # template config and tell the user.
        if self.opts.config_path:
            try:
                log.info('Using configuration file: "{!s}"'.format(
                    util.displayable_path(self.opts.config_path)
                ))
                self.config.load(self.opts.config_path)
            except ConfigError as e:
                log.critical('Failed to load configuration file!')
                log.debug(str(e))
                self.exit_program(constants.EXIT_ERROR)
        else:

            _disp_config_path = util.displayable_path(config.ConfigFilePath)
            if not config.has_config_file():
                log.info('No configuration file was found. Writing default ..')

                try:
                    config.write_default_config()
                except PermissionError:
                    log.critical('Unable to write configuration file to path: '
                                 '"{!s}"'.format(_disp_config_path))
                    self.exit_program(constants.EXIT_ERROR)
                else:
                    cli.msg('A template configuration file was written to '
                            '"{!s}"'.format(_disp_config_path), style='info')
                    cli.msg('Use this file to configure {}. '
                            'Refer to the documentation for additional '
                            'information.'.format(version.__title__),
                            style='info')
                    self.exit_program(constants.EXIT_SUCCESS)
            else:
                log.info('Using configuration: "{}"'.format(_disp_config_path))
                try:
                    self.config.load(config.ConfigFilePath)
                except ConfigurationSyntaxError as e:
                    log.critical('Configuration syntax error: "{!s}"'.format(e))

        # TODO: Integrate filter settings in configuration (file).
        self.filter = ResultFilter().configure_filter(self.opts)

        if self.opts.dump_options:
            include_opts = {
                'config_file_path': util.displayable_path(config.ConfigFilePath)
            }
            options.prettyprint_options(self.opts, include_opts)

        if self.opts.dump_config:
            log.info('Dumping active configuration ..')
            cli.msg('Active Configuration:', style='heading')
            cli.msg(str(self.config))
            self.exit_program(constants.EXIT_SUCCESS)

        # Handle any input paths/files.
        if not self.opts.input_paths:
            log.warning('No input files specified ..')
            self.exit_program(constants.EXIT_SUCCESS)

        self._handle_files()
        self.exit_program(self.exit_code)

    def _handle_files(self):
        """
        Main loop. Iterate over input paths/files.

        For each file:
        1. Create 'FileObject' representing the file.
        2. Extract data from the file with an instance of the 'Extraction' class
        3. Perform analysis of the file with an instance of the 'Analysis' class
        4. Determine which rules match the given file.
        5. Do any reporting of results to the user.
        6. (automagic mode) Use a 'NameBuilder' instance to assemble the name.
        7. (automagic mode and not --dry-run) Rename the file.
        """
        for input_path in self.opts.input_paths:
            input_path = util.bytestring_path(input_path)
            log.info('Processing: "{!s}"'.format(
                util.displayable_path(input_path))
            )

            # Sanity checking the "input_path" is part of 'FileObject' init.
            try:
                current_file = FileObject(input_path, self.config)
            except InvalidFileArgumentError as e:
                log.warning('{!s} - SKIPPING: "{!s}"'.format(
                    e, util.displayable_path(input_path))
                )
                continue

            # Extract data from the file.
            extraction = Extraction(current_file)
            try:
                extraction.start()
            except AutonameowException as e:
                log.critical('Extraction FAILED: {!s}'.format(e))
                log.critical('Skipping file "{}" ..'.format(
                    util.displayable_path(current_file))
                )
                self.exit_code = constants.EXIT_WARNING
                continue

            # Begin analysing the file.
            analysis = Analysis(current_file, extraction.data)
            try:
                analysis.start()
            except AutonameowException as e:
                log.critical('Analysis FAILED: {!s}'.format(e))
                log.critical('Skipping file "{}" ..'.format(
                    util.displayable_path(current_file))
                )
                self.exit_code = constants.EXIT_WARNING
                continue

            # Determine matching rule.
            matcher = RuleMatcher(current_file, analysis.results, self.config)
            try:
                matcher.start()
            except AutonameowException as e:
                log.critical('Rule Matching FAILED: {!s}'.format(e))
                log.critical('Skipping file "{}" ..'.format(
                    util.displayable_path(current_file))
                )
                self.exit_code = constants.EXIT_WARNING
                continue

            # Present results.
            list_any = (self.opts.list_datetime or self.opts.list_title
                        or self.opts.list_all)
            if list_any:
                cli.msg(('File: "{}"\n'.format(
                    util.displayable_path(current_file.abspath)))
                )

            if self.opts.list_all:
                log.info('Listing ALL analysis results ..')
                cli.msg('Analysis Results Data', style='heading', log=True)
                cli.msg(misc.dump(analysis.results.get_all()))
                cli.msg('Extraction Results Data', style='heading', log=True)
                cli.msg(misc.dump(analysis.results.new_data))
            else:
                if self.opts.list_datetime:
                    log.info('Listing "datetime" analysis results ..')
                    cli.msg(misc.dump(analysis.results.get('datetime')))
                if self.opts.list_title:
                    log.info('Listing "title" analysis results ..')
                    cli.msg(misc.dump(analysis.results.get('title')))

            # Perform actions.
            if self.opts.prepend_datetime:
                # TODO: Prepend datetime to filename.
                log.warning('[UNIMPLEMENTED FEATURE] prepend_datetime')

            if self.opts.automagic:
                if not matcher.best_match:
                    log.info('None of the rules seem to apply')
                    continue

                log.info('Using file rule: "{!s}"'.format(
                    matcher.best_match.description)
                )
                try:
                    self.builder = NameBuilder(current_file, analysis.results,
                                               self.config, matcher.best_match)
                    new_name = self.builder.build()
                except NameBuilderError as e:
                    log.critical('Name assembly FAILED: {!s}'.format(e))
                    self.exit_code = constants.EXIT_WARNING
                    continue
                else:
                    # TODO: Respect '--quiet' option. Suppress output.
                    log.info('New name: "{}"'.format(
                        util.displayable_path(new_name))
                    )
                    renamed_ok = self.do_rename(current_file.abspath, new_name,
                                                dry_run=self.opts.dry_run)
                    if renamed_ok:
                        self.exit_code = constants.EXIT_SUCCESS
                    else:
                        self.exit_code = constants.EXIT_WARNING

            elif self.opts.interactive:
                # TODO: Create a interactive interface.
                # TODO: [BL013] Interactive mode in 'interactive.py'.
                log.warning('[UNIMPLEMENTED FEATURE] interactive mode')

    def exit_program(self, exit_code_):
        """
        Main program exit point.  Shuts down this autonameow instance/session.

        Args:
            exit_code_: Integer exit code to pass to the parent process.
                Indicate success with 0, failure non-zero.
        """
        elapsed_time = time.time() - self.start_time
        self.exit_code = exit_code_

        if self.opts and self.opts.verbose:
            cli.print_exit_info(self.exit_code, elapsed_time)
        log.debug('Exiting with exit code: {}'.format(self.exit_code))
        log.debug('Total execution time: {:.6f} seconds'.format(elapsed_time))

        sys.exit(self.exit_code)

    def do_rename(self, from_path, new_basename, dry_run=True):
        """
        Renames a file at the given path to the specified basename.

        Args:
            from_path: Path to the file to rename.
            new_basename: The new basename for the file.
            dry_run: Controls whether the renaming is actually performed.

        Returns:
            True if the rename succeeded, otherwise False.
        """
        dest_basename = diskutils.sanitize_filename(new_basename)
        from_basename = diskutils.file_basename(from_path)
        log.debug('Sanitized basename: "{!s}"'.format(
            util.displayable_path(dest_basename))
        )

        if dry_run is False:
            try:
                diskutils.rename_file(from_path, dest_basename)
            except (FileNotFoundError, FileExistsError, OSError) as e:
                log.error('Rename FAILED: {!s}'.format(e))
                return False
            else:
                _message = 'Renamed "{!s}" -> "{!s}"'
                cli.msg(_message.format(util.displayable_path(from_basename),
                                        util.displayable_path(dest_basename)),
                        style='color_quoted')
                return True
        else:
            _message = 'Would have renamed "{!s}" -> "{!s}"'
            cli.msg(_message.format(util.displayable_path(from_basename),
                                    util.displayable_path(dest_basename)),
                    style='color_quoted')
            return True

    @property
    def exit_code(self):
        """
        Returns:
            The current exit code for this autonameow instance as an integer.
        """
        return self._exit_code

    @exit_code.setter
    def exit_code(self, value):
        """
        Updates the exit code value for this autonameow instance.

        The exit code is only actually updated if the given value is greater
        than the current value. This makes errors take precedence over warnings.

        Args:
            value: Optional new exit status as an integer, preferably one of
                   the values in 'constants.py' prefixed 'EXIT_'.
        """
        if isinstance(value, int) and value > self._exit_code:
            log.debug('Exit code updated: {} -> {}'.format(self._exit_code,
                                                           value))
            self._exit_code = value
