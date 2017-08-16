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
    options,
    util,
    exceptions,
)
from core.analysis import Analysis
from core.config.configuration import Configuration
from core.evaluate.filter import ResultFilter
from core.evaluate.namebuilder import NameBuilder
from core.evaluate.rulematcher import RuleMatcher
from core.extraction import Extraction
from core.fileobject import FileObject
from core.plugin_handler import PluginHandler
from core.repository import Repository
from core.util import (
    cli,
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
        self.active_config = None

        # TODO: [TD0073] Fix or remove the 'SessionDataPool' class.
        # self.session_data = container.SessionDataPool()
        self.session_data = {}

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
            self._load_config_from_alternate_path()
        else:
            if not config.has_config_file():
                self._write_template_config_to_default_path_and_exit()
            else:
                self._load_config_from_default_path()

        if not self.active_config:
            log.critical('Unable to load configuration -- Aborting ..')
            self.exit_program(constants.EXIT_ERROR)

        # TODO: [TD0034][TD0035][TD0043] Store filter settings in configuration.
        self.filter = ResultFilter().configure_filter(self.opts)

        if self.opts.dump_options:
            include_opts = {
                'config_file_path': util.displayable_path(config.ConfigFilePath)
            }
            options.prettyprint_options(self.opts, include_opts)

        if self.opts.dump_config:
            self._dump_active_config_and_exit()

        # Handle any input paths/files. Abort early if input paths are missing.
        if not self.opts.input_paths:
            log.warning('No input files specified ..')
            self.exit_program(constants.EXIT_SUCCESS)

        # Path name encoding boundary. Returns list of paths in internal format.
        files_to_process = self._get_files_to_process()
        log.info('Got {} files to process'.format(len(files_to_process)))

        self._handle_files(files_to_process)
        self.exit_program(self.exit_code)

    def _get_files_to_process(self):
        file_list = []

        for path in self.opts.input_paths:
            if not path:
                continue

            # Path name encoding boundary. Convert to internal format.
            path = util.normpath(path)
            try:
                file_list += diskutils.get_files(
                    path, recurse=self.opts.recurse_paths
                )
            except FileNotFoundError:
                log.error('File(s) not found: "{}"'.format(
                    util.displayable_path(path))
                )

        return file_list

    def load_config(self, dict_or_yaml):
        try:
            self.active_config = Configuration(dict_or_yaml)
        except exceptions.ConfigError as e:
            log.critical('Unable to load configuration: {!s}'.format(e))

    def _dump_active_config_and_exit(self):
        log.info('Dumping active configuration ..')
        cli.msg('Active Configuration:', style='heading')
        cli.msg(str(self.active_config))
        self.exit_program(constants.EXIT_SUCCESS)

    def _load_config_from_default_path(self):
        _displayable_config_path = util.displayable_path(config.ConfigFilePath)
        log.info('Using configuration: "{}"'.format(_displayable_config_path))
        self.load_config(config.ConfigFilePath)

    def _write_template_config_to_default_path_and_exit(self):
        log.info('No configuration file was found. Writing default ..')
        _displayable_config_path = util.displayable_path(config.ConfigFilePath)
        try:
            config.write_default_config()
        except exceptions.ConfigError:
            log.critical('Unable to write template configuration file to path: '
                         '"{!s}"'.format(_displayable_config_path))
            self.exit_program(constants.EXIT_ERROR)
        else:
            cli.msg('A template configuration file was written to '
                    '"{!s}"'.format(_displayable_config_path), style='info')
            cli.msg('Use this file to configure {}. '
                    'Refer to the documentation for additional '
                    'information.'.format(version.__title__),
                    style='info')
            self.exit_program(constants.EXIT_SUCCESS)

    def _load_config_from_alternate_path(self):
        log.info('Using configuration file: "{!s}"'.format(
            util.displayable_path(self.opts.config_path)
        ))
        self.load_config(self.opts.config_path)

    def collect_data(self, file_object, label, data):
        util.nested_dict_set(self.session_data, [file_object, label], data)

    def request_data(self, file_object, label):
        try:
            d = util.nested_dict_get(self.session_data, [file_object, label])
        except KeyError as e:
            log.debug('Data pool request raised KeyError: {!s}'.format(e))
            return None
        else:
            return d

    def _handle_files(self, file_paths):
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

        Assume all state is setup and completely reset for each loop iteration.
        It is not currently possible to share "information" between runs.
        """
        for file_path in file_paths:
            log.info('Processing: "{!s}"'.format(
                util.displayable_path(file_path))
            )

            # Sanity checking the "file_path" is part of 'FileObject' init.
            try:
                current_file = FileObject(file_path, self.active_config)
            except exceptions.InvalidFileArgumentError as e:
                log.warning('{!s} - SKIPPING: "{!s}"'.format(
                    e, util.displayable_path(file_path))
                )
                continue

            try:
                self._handle_file(current_file)
            except exceptions.AutonameowException:
                log.critical('Skipping file "{}" ..'.format(
                    util.displayable_path(file_path))
                )
                self.exit_code = constants.EXIT_WARNING
                continue

    def _handle_file(self, current_file):
        should_list_any_results = (self.opts.list_datetime
                                   or self.opts.list_title
                                   or self.opts.list_all)

        # Extract data from the file.
        # Run all extractors so that all possible data is included
        # when listing any (all) results later on.
        extraction = _run_extraction(current_file,
                                     add_pool_data_callback=self.collect_data,
                                     run_all_extractors=should_list_any_results)

        # Begin analysing the file.
        analysis = _run_analysis(current_file,
                                 add_pool_data_callback=self.collect_data,
                                 request_data_callback=self.request_data)

        plugin_handler = _run_plugins(current_file,
                                      add_pool_data_callback=self.collect_data,
                                      request_data_callback=self.request_data)

        # Determine matching rule.
        matcher = _run_rule_matcher(current_file,
                                    active_config=self.active_config,
                                    request_data_callback=self.request_data)

        # Present results.
        if should_list_any_results:
            cli.msg(('File: "{}"\n'.format(
                util.displayable_path(current_file.abspath)))
            )

        if self.opts.list_all:
            _list_all_analysis_results(analysis)
            _list_all_extracted_data(extraction)
        else:
            if self.opts.list_datetime:
                _list_analysis_results_field(analysis, 'datetime')
            if self.opts.list_title:
                _list_analysis_results_field(analysis, 'title')

        # Perform actions.
        if self.opts.automagic:
            self._perform_automagic_actions(current_file, matcher)
        elif self.opts.interactive:
            # TODO: Create a interactive interface.
            # TODO: [TD0023][TD0024][TD0025] Implement interactive mode.
            log.warning('[UNIMPLEMENTED FEATURE] interactive mode')

    def _perform_automagic_actions(self, current_file, rule_matcher):
        if not rule_matcher.best_match:
            log.info('None of the rules seem to apply')
            return

        log.info('Using file rule: "{!s}"'.format(
            rule_matcher.best_match.description)
        )
        new_name = _build_new_name(current_file,
                                   active_config=self.active_config,
                                   active_rule=rule_matcher.best_match,
                                   request_data_callback=self.request_data)
        # TODO: [TD0042] Respect '--quiet' option. Suppress output.
        log.info('New name: "{}"'.format(
            util.displayable_path(new_name))
        )
        self.do_rename(from_path=current_file.abspath,
                       new_basename=new_name,
                       dry_run=self.opts.dry_run)

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

        If the basenames of the file at "from_path" and "new_basename" are
        equal, the renaming operation is skipped and True is returned.

        Args:
            from_path: Path to the file to rename as an "internal" byte string.
            new_basename: The new basename for the file as a Unicode string.
            dry_run: Controls whether the renaming is actually performed.

        Returns:
            True if the rename succeeded or would be a NO-OP, otherwise False.
        """
        assert(isinstance(from_path, bytes))
        assert(isinstance(new_basename, str))

        # TODO: [TD0071] Move "sanitation" to the 'NameBuilder' or elsewhere.
        if self.active_config.get(['FILESYSTEM_OPTIONS', 'sanitize_filename']):
            if self.active_config.get(['FILESYSTEM_OPTIONS', 'sanitize_strict']):
                log.debug('Sanitizing filename (restricted=True)')
                new_basename = diskutils.sanitize_filename(new_basename,
                                                           restricted=True)
            else:
                log.debug('Sanitizing filename')
                new_basename = diskutils.sanitize_filename(new_basename)

            log.debug('Sanitized basename (unicode): "{!s}"'.format(
                util.displayable_path(new_basename))
            )
        else:
            log.debug('Skipped sanitizing filename')

        # Encoding boundary.  Internal str --> internal filename bytestring
        dest_basename = util.bytestring_path(new_basename)
        log.debug('Destination basename (bytestring): "{!s}"'.format(
            util.displayable_path(dest_basename))
        )

        from_basename = diskutils.file_basename(from_path)
        if diskutils.compare_basenames(from_basename, dest_basename):
            _msg = 'Skipped "{!s}" because the current name is the same as ' \
                   'the new name'.format(util.displayable_path(from_basename),
                                         util.displayable_path(dest_basename))
            log.debug(_msg)
            cli.msg(_msg, style='color_quoted')
        else:
            if dry_run is False:
                try:
                    diskutils.rename_file(from_path, dest_basename)
                except (FileNotFoundError, FileExistsError, OSError) as e:
                    log.error('Rename FAILED: {!s}'.format(e))
                    raise exceptions.AutonameowException

            cli.msg_rename(from_basename, dest_basename, dry_run=dry_run)

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


def _build_new_name(file_object, active_config, active_rule,
                    request_data_callback):
    try:
        builder = NameBuilder(file_object, active_config, active_rule,
                              request_data_callback)

        # TODO: Do not return anything from 'build()', use property.
        new_name = builder.build()
    except exceptions.NameBuilderError as e:
        log.critical('Name assembly FAILED: {!s}'.format(e))
        raise exceptions.AutonameowException
    else:
        return new_name


def _run_extraction(file_object, add_pool_data_callback,
                    run_all_extractors=False):
    """
    Instantiates, executes and returns an 'Extraction' instance.

    Args:
        file_object: The file object to extract data from.
        add_pool_data_callback: Callback function for storing data.
        run_all_extractors: Whether all data extractors should be included.

    Returns:
        An instance of the 'Extraction' class that has executed successfully.
    Raises:
        AutonameowException: An unrecoverable error occurred during extraction.
    """
    extraction = Extraction(file_object, add_pool_data_callback)
    try:
        # TODO: [TD0056] Determine required extractors for current file.

        # Assume slower execution speed is tolerable when the user
        # wants to display any results, also for completeness. Run all.
        extraction.start(
            require_all_extractors=run_all_extractors is True
        )
    except exceptions.AutonameowException as e:
        log.critical('Extraction FAILED: {!s}'.format(e))
        raise
    else:
        return extraction


def _run_plugins(file_object, add_pool_data_callback, request_data_callback):
    """
    Instantiates, executes and returns a 'PluginHandler' instance.

    Args:
        file_object: The current file object to pass to plugins.
        add_pool_data_callback: Callback function for storing data.
        request_data_callback: Callback function for accessing "session" data.

    Returns:
        An instance of the 'PluginHandler' class that has executed successfully.
    Raises:
        AutonameowException: An unrecoverable error occurred during analysis.
    """
    plugin_handler = PluginHandler(file_object, add_pool_data_callback,
                                   request_data_callback)
    try:
        plugin_handler.start()
    except exceptions.AutonameowPluginError as e:
        log.critical('Analysis FAILED: {!s}'.format(e))
        raise exceptions.AutonameowException(e)
    else:
        return plugin_handler


def _run_analysis(file_object, add_pool_data_callback, request_data_callback):
    """
    Instantiates, executes and returns an 'Analysis' instance.

    Args:
        file_object: The file object to analyze.
        add_pool_data_callback: Callback function for storing data.
        request_data_callback: Callback function for accessing "session" data.

    Returns:
        An instance of the 'Analysis' class that has executed successfully.
    Raises:
        AutonameowException: An unrecoverable error occurred during analysis.
    """
    analysis = Analysis(file_object, add_pool_data_callback,
                        request_data_callback)
    try:
        analysis.start()
    except exceptions.AutonameowException as e:
        log.critical('Analysis FAILED: {!s}'.format(e))
        raise
    else:
        return analysis


def _run_rule_matcher(file_object, active_config, request_data_callback):
    """
    Instantiates, executes and returns a 'RuleMatcher' instance.

    Args:
        active_config: An instance of the 'Configuration' class.
        request_data_callback: Callback function for accessing "session" data.

    Returns:
        An instance of the 'RuleMatcher' class that has executed successfully.
    Raises:
        AutonameowException: An unrecoverable error occurred during execution.
    """
    matcher = RuleMatcher(file_object, active_config, request_data_callback)
    try:
        matcher.start()
    except exceptions.AutonameowException as e:
        log.critical('Rule Matching FAILED: {!s}'.format(e))
        raise
    else:
        return matcher


def _list_all_extracted_data(extraction):
    log.info('Listing ALL extraction results ..')
    cli.msg('Extraction Results Data', style='heading', log=True)
    cli.msg('TODO: Re-implement this after moving to shared data pool storage.')
    # cli.msg(str(extraction.data))


def _list_all_analysis_results(analysis):
    log.info('Listing ALL analysis results ..')
    cli.msg('Analysis Results Data', style='heading', log=True)
    cli.msg('TODO: Re-implement this after moving to shared data pool storage.')
    # cli.msg(str(analysis.results))


def _list_analysis_results_field(analysis, results_field):
    log.info('Listing "{}" analysis results ..'.format(results_field))
    # TODO: [TD0066] Handle all encoding properly.

    cli.msg('TODO: Re-implement this after moving to shared data pool storage.')
    # cli.msg(util.dump(analysis.results.get(results_field)))
