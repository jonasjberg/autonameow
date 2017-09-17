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
import sys
import time

import core
from core import (
    analysis,
    config,
    constants,
    exceptions,
    extraction,
    namebuilder,
    options,
    repository,
    util,
)
from core.config import DefaultConfigFilePath
from core.config.configuration import Configuration
from core.evaluate.resolver import Resolver
from core.evaluate.rulematcher import RuleMatcher
from core.fileobject import FileObject
from core.filter import ResultFilter
from core.plugin_handler import PluginHandler
from core.util import (
    cli,
    diskutils
)


log = logging.getLogger(__name__)


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

    def run(self):
        # Display help/usage information if no arguments are provided.
        if not self.args:
            print('Add "--help" to display usage information.')
            self.exit_program(constants.EXIT_SUCCESS)

        # Handle the command line arguments and setup logging.
        self.opts = options.parse_args(self.args)

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
                'config_file_path': util.displayable_path(DefaultConfigFilePath)
            }
            options.prettyprint_options(self.opts, include_opts)

        if self.opts.dump_config:
            self._dump_active_config_and_exit()

        # Handle any input paths/files. Abort early if input paths are missing.
        if not self.opts.input_paths:
            log.warning('No input files specified ..')
            self.exit_program(constants.EXIT_SUCCESS)

        # Path name encoding boundary. Returns list of paths in internal format.
        files_to_process = diskutils.normpaths_from_opts(
            self.opts.input_paths,
            self.active_config.options['FILESYSTEM_OPTIONS']['ignore'],
            self.opts.recurse_paths
        )
        log.info('Got {} files to process'.format(len(files_to_process)))

        self._handle_files(files_to_process)
        self.exit_program(self.exit_code)

    def load_config(self, path):
        try:
            self.active_config = Configuration.from_file(path)
        except exceptions.ConfigError as e:
            log.critical('Unable to load configuration: {!s}'.format(e))

    def _dump_active_config_and_exit(self):
        log.info('Dumping active configuration ..')
        cli.msg('Active Configuration:', style='heading')
        cli.msg(str(self.active_config))
        self.exit_program(constants.EXIT_SUCCESS)

    def _load_config_from_default_path(self):
        _displayable_config_path = util.displayable_path(DefaultConfigFilePath)
        log.info('Using configuration: "{}"'.format(_displayable_config_path))
        self.load_config(DefaultConfigFilePath)

    def _write_template_config_to_default_path_and_exit(self):
        log.info('No configuration file was found. Writing default ..')
        _displayable_config_path = util.displayable_path(DefaultConfigFilePath)
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
                    'information.'.format(core.version.__title__),
                    style='info')
            self.exit_program(constants.EXIT_SUCCESS)

    def _load_config_from_alternate_path(self):
        log.info('Using configuration file: "{!s}"'.format(
            util.displayable_path(self.opts.config_path)
        ))
        self.load_config(self.opts.config_path)

    def _handle_files(self, file_paths):
        """
        Main loop. Iterate over input paths/files.

        For each file:
        1. Create a 'FileObject' representing the current file.
        2. Extract data from the file with suitable and/or required extractors.
        3. Perform analysis of the file with suitable analyzers.
        4. Run any available plugins.
        5A -- "AUTOMAGIC MODE"
            1. Determine which rules match the given file.
            2. Use the "name template" and "data sources" specified in the
               highest ranked rule, if any.
            3. Use a 'Resolver' to collect data from "data sources" to be used
               to populate "name template".
            4. Construct a file name with the "name builder" if all required
               data is available.
            5. If not --dry-run; rename the file to the new file name.
        5B -- "INTERACTIVE MODE"
          1. Not implemented yet!
        6. Do any reporting of results to the user.

        Assume all state is setup and completely reset for each loop iteration.
        It is not currently possible to share "information" between runs.
        """
        for file_path in file_paths:
            log.info('Processing: "{!s}"'.format(
                util.displayable_path(file_path))
            )

            # Sanity checking the "file_path" is part of 'FileObject' init.
            try:
                current_file = FileObject(file_path)
            except exceptions.InvalidFileArgumentError as e:
                log.warning('{!s} - SKIPPING: "{!s}"'.format(
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

        if self.opts.list_all:
            log.info('Listing session repository contents ..')
            cli.msg('Session Repository Data', style='heading',
                    add_info_log=True)
            # cli.msg(str(repository.SessionRepository))
            cli.msg(repository.SessionRepository.human_readable_contents())
        # else:
        #     if self.opts.list_datetime:
        #         _list_analysis_results_field(analysis, 'datetime')
        #     if self.opts.list_title:
        #         _list_analysis_results_field(analysis, 'title')

    def _handle_file(self, current_file):
        should_list_any_results = (self.opts.list_datetime
                                   or self.opts.list_title
                                   or self.opts.list_all)

        # Extract data from the file.
        required_extractors = repository.get_sources_for_meowuris(
            self.active_config.referenced_meowuris,
            includes=['extractors']
        )
        _run_extraction(
            current_file,
            require_extractors=required_extractors,

            # Run all extractors so that all possible data is included
            # when listing any (all) results later on.
            run_all_extractors=should_list_any_results
        )

        # Begin analysing the file.
        _run_analysis(current_file)

        # Run plugins.
        required_plugins = repository.get_sources_for_meowuris(
            self.active_config.referenced_meowuris,
            includes=['plugins']
        )
        _run_plugins(current_file, required_plugins)

        # Determine matching rule.
        matcher = _run_rule_matcher(current_file, self.active_config)

        # # Present results.
        # if should_list_any_results:
        #     cli.msg(('File: "{}"\n'.format(
        #         util.displayable_path(current_file.abspath)))
        #     )

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

        log.info(
            'Using rule: "{!s}"'.format(rule_matcher.best_match.description)
        )
        name_template = rule_matcher.best_match.name_template

        resolver = Resolver(current_file, name_template)
        for _field, _meowuri in rule_matcher.best_match.data_sources.items():
            resolver.add_known_source(_field, _meowuri)

        if not resolver.mapped_all_template_fields():
            # TODO: Abort if running in "batch mode". Otherwise, ask the user.
            log.error('All name template placeholder fields must be '
                      'given a data source; Check the configuration!')
            self.exit_code = constants.EXIT_WARNING
            return

        # TODO: [TD0024][TD0017] Should be able to handle fields not in sources.
        # Add automatically resolving missing sources from possible candidates.
        resolver.collect()
        if not resolver.collected_data_for_all_fields():
            # TODO: Abort if running in "batch mode". Otherwise, ask the user.
            log.warning('Unable to populate name. Missing field data.')
            self.exit_code = constants.EXIT_WARNING
            return

        try:
            new_name = namebuilder.build(config=self.active_config,
                                         name_template=name_template,
                                         field_data_map=resolver.fields_data)
        except exceptions.NameBuilderError as e:
            log.critical('Name assembly FAILED: {!s}'.format(e))
            raise exceptions.AutonameowException

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


def _run_extraction(file_object, require_extractors, run_all_extractors=False):
    """
    Sets up and executes data extraction for the given file.

    Args:
        file_object: The file object to extract data from.
        require_extractors: List of extractor classes that should be included.
        run_all_extractors: Whether all data extractors should be included.

    Raises:
        AutonameowException: An unrecoverable error occurred during extraction.
    """
    try:
        extraction.start(file_object,
                         require_extractors=require_extractors,
                         require_all_extractors=run_all_extractors is True)
    except exceptions.AutonameowException as e:
        log.critical('Extraction FAILED: {!s}'.format(e))
        raise


def _run_plugins(file_object, required_plugins=None):
    """
    Instantiates, executes and returns a 'PluginHandler' instance.

    Args:
        file_object: The current file object to pass to plugins.

    Returns:
        An instance of the 'PluginHandler' class that has executed successfully.
    Raises:
        AutonameowException: An unrecoverable error occurred during analysis.
    """
    if not required_plugins:
        return

    plugin_handler = PluginHandler()
    plugin_handler.use_plugins(required_plugins)
    try:
        plugin_handler.execute_plugins(file_object)
    except exceptions.AutonameowPluginError as e:
        log.critical('Plugins FAILED: {!s}'.format(e))
        raise exceptions.AutonameowException(e)


def _run_analysis(file_object):
    """
    Sets up and executes "analysis" of the given file.

    Args:
        file_object: The file object to analyze.

    Raises:
        AutonameowException: An unrecoverable error occurred during analysis.
    """
    try:
        analysis.start(file_object)
    except exceptions.AutonameowException as e:
        log.critical('Analysis FAILED: {!s}'.format(e))
        raise


def _run_rule_matcher(file_object, active_config):
    """
    Instantiates, executes and returns a 'RuleMatcher' instance.

    Args:
        active_config: An instance of the 'Configuration' class.

    Returns:
        An instance of the 'RuleMatcher' class that has executed successfully.
    Raises:
        AutonameowException: An unrecoverable error occurred during execution.
    """
    matcher = RuleMatcher(file_object, active_config)
    try:
        matcher.start()
    except exceptions.AutonameowException as e:
        log.critical('Rule Matching FAILED: {!s}'.format(e))
        raise
    else:
        return matcher


def _list_analysis_results_field(analysis, results_field):
    log.info('Listing "{}" analysis results ..'.format(results_field))
    # TODO: [TD0066] Handle all encoding properly.

    cli.msg('TODO: Re-implement this after moving to shared data pool storage.')
    # cli.msg(util.dump(analysis.results.get(results_field)))
