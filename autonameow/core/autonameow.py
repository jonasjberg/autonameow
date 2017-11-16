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

from core import (
    analysis,
    config,
    disk,
    exceptions,
    extraction,
    interactive,
    namebuilder,
    persistence,
    providers,
    repository,
    ui,
    util
)
from core import constants as C
from core.config.configuration import Configuration
from core.evaluate import (
    TemplateFieldDataResolver,
    RuleMatcher
)
from core.fileobject import FileObject
from core.plugin_handler import PluginHandler
from core.util import sanity


log = logging.getLogger(__name__)


class Autonameow(object):
    """
    Main class to manage a running "autonameow" instance.
    """

    def __init__(self, opts):
        """
        Main program entry point.  Initializes a autonameow instance/session.

        Args:
            opts: Dict with parsed and validated options.
        """
        assert isinstance(opts, dict)
        self.opts = self.check_option_combinations(opts)

        # For calculating the total runtime.
        self.start_time = time.time()

        self.active_config = None
        self._exit_code = C.EXIT_SUCCESS

    @staticmethod
    def check_option_combinations(options):
        opts = dict(options)

        # Check legality of option combinations.
        if opts.get('mode_automagic') and opts.get('mode_interactive'):
            log.warning('Operating mode must be either one of "automagic" or '
                        '"interactive", not both. Reverting to default: '
                        '[interactive mode].')
            opts['mode_automagic'] = False
            opts['mode_interactive'] = True

        if (not opts.get('mode_automagic') and not opts.get('mode_rulematch')
                and opts.get('mode_batch')):
            log.warning('Running in "batch" mode without specifying an '
                        'operating mode ("automagic" or rule-matching) does '
                        'not make any sense.  Nothing to do!')

        if opts.get('mode_batch'):
            if opts.get('mode_interactive'):
                log.warning('Operating mode must be either one of "batch" or '
                            '"interactive", not both.  Disabling "batch"..')
                opts['mode_batch'] = False

            if opts.get('mode_timid'):
                log.warning('Operating mode must be either one of "batch" or '
                            '"timid", not both. Disabling "batch"..')
                opts['mode_batch'] = False

        if opts.get('mode_interactive'):
            if opts.get('mode_timid'):
                log.warning('Operating mode "interactive" implies "timid". '
                            'Disabling "timid"..')
                opts['mode_timid'] = False

        if not opts.get('mode_automagic') and not opts.get('mode_rulematch'):
            log.info('No operating-mode selected!')

        if not opts.get('mode_rulematch'):
            log.info('Enabled rule-matching..')
            opts['mode_rulematch'] = True

        return opts

    def __enter__(self):
        # Set up singletons for this process.
        repository.initialize(self)
        providers.initialize()

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        repository.shutdown(self)

    def run(self):
        if self.opts.get('quiet'):
            ui.silence()

        # Display various information depending on verbosity level.
        if self.opts.get('verbose') or self.opts.get('debug'):
            ui.print_start_info()

        # Display startup banner with program version and exit.
        if self.opts.get('show_version'):
            ui.print_version_info(verbose=self.opts.get('verbose'))
            self.exit_program(C.EXIT_SUCCESS)

        # Check configuration file. If no alternate config file path is
        # provided and no config file is found at default paths; copy the
        # template config and tell the user.
        if self.opts.get('config_path'):
            self._load_config_from_alternate_path()
        else:
            if not config.has_config_file():
                self._write_template_config_to_default_path_and_exit()
            else:
                self._load_config_from_default_path()

        if not self.active_config:
            log.critical('Unable to load configuration -- Aborting ..')
            self.exit_program(C.EXIT_ERROR)

        # Set globally accessible configuration instance.
        config.set_active(self.active_config)

        if self.opts.get('dump_options'):
            _config_path = persistence.get_config_persistence_path()
            _default_config_path = config.DefaultConfigFilePath
            include_opts = {
                'config_file_path': '"{!s}"'.format(
                    util.enc.displayable_path(_default_config_path)
                ),
                'cache_directory_path': '"{!s}"'.format(
                    util.enc.displayable_path(_config_path)
                )
            }
            ui.options.prettyprint_options(self.opts, include_opts)

        if self.opts.get('dump_config'):
            self._dump_active_config_and_exit()

        if self.opts.get('dump_meowuris'):
            self._dump_registered_meowuris()

        # Handle any input paths/files. Abort early if input paths are missing.
        if not self.opts.get('input_paths'):
            log.warning('No input files specified ..')
            self.exit_program(C.EXIT_SUCCESS)

        # Path name encoding boundary. Returns list of paths in internal format.
        files_to_process = disk.normpaths_from_opts(
            self.opts.get('input_paths'),
            self.active_config.options['FILESYSTEM_OPTIONS']['ignore'],
            self.opts.get('recurse_paths')
        )
        log.info('Got {} files to process'.format(len(files_to_process)))

        self._handle_files(files_to_process)
        self.exit_program(self.exit_code)

    def load_config(self, path):
        try:
            self.active_config = Configuration.from_file(path)
        except exceptions.ConfigError as e:
            log.critical('Unable to load configuration -- {!s}'.format(e))

    def _dump_active_config_and_exit(self):
        log.info('Dumping active configuration ..')
        ui.msg('Active Configuration:', style='heading')
        ui.msg(str(self.active_config))
        self.exit_program(C.EXIT_SUCCESS)

    def _dump_registered_meowuris(self):
        ui.msg('Registered MeowURIs', style='heading')

        if not self.opts.get('debug'):
            _meowuris = sorted(providers.Registry.mapped_meowuris)
            for _meowuri in _meowuris:
                ui.msg(str(_meowuri))
        else:
            cf = ui.ColumnFormatter()

            for _type in C.MEOWURI_ROOTS_SOURCES:
                cf.addemptyrow()
                sourcemap = providers.Registry.meowuri_sources.get(_type, {})
                for _meowuri, _klasses in sourcemap.items():
                    cf.addrow(_meowuri, str(_klasses.pop()))
                    if _klasses:
                        for k in _klasses:
                            cf.addrow(None, str(k))
            ui.msg(str(cf))

        ui.msg('\n')

    def _load_config_from_default_path(self):
        _dp = util.enc.displayable_path(config.DefaultConfigFilePath)
        log.info('Using configuration: "{}"'.format(_dp))
        self.load_config(config.DefaultConfigFilePath)

    def _write_template_config_to_default_path_and_exit(self):
        log.info('No configuration file was found. Writing default ..')
        _dp = util.enc.displayable_path(config.DefaultConfigFilePath)
        try:
            config.write_default_config()
        except exceptions.ConfigError:
            log.critical('Unable to write template configuration file to path: '
                         '"{!s}"'.format(_dp))
            self.exit_program(C.EXIT_ERROR)
        else:
            ui.msg('A template configuration file was written to '
                   '"{!s}"'.format(_dp), style='info')
            ui.msg('Use this file to configure {}. '
                   'Refer to the documentation for additional '
                   'information.'.format(C.STRING_PROGRAM_NAME),
                   style='info')
            self.exit_program(C.EXIT_SUCCESS)

    def _load_config_from_alternate_path(self):
        log.info('Using configuration file: "{!s}"'.format(
            util.enc.displayable_path(self.opts.get('config_path'))
        ))
        self.load_config(self.opts.get('config_path'))

    def _handle_files(self, file_paths):
        """
        Main loop. Iterate over input paths/files.
        Assume all state is setup and completely reset for each loop iteration.
        It is not currently possible to share "information" between runs.
        """
        for file_path in file_paths:
            log.info('Processing: "{!s}"'.format(
                util.enc.displayable_path(file_path))
            )

            # Sanity checking the "file_path" is part of 'FileObject' init.
            try:
                current_file = FileObject(file_path)
            except (exceptions.InvalidFileArgumentError,
                    exceptions.FilesystemError) as e:
                log.warning('{!s} - SKIPPING: "{!s}"'.format(
                    e, util.enc.displayable_path(file_path))
                )
                continue

            try:
                self._handle_file(current_file)
            except exceptions.AutonameowException:
                log.critical('Skipping file "{}" ..'.format(
                    util.enc.displayable_path(file_path))
                )
                self.exit_code = C.EXIT_WARNING
                continue

        if self.opts.get('list_all'):
            log.info('Listing session repository contents ..')
            ui.msg('Session Repository Data', style='heading',
                   add_info_log=True)

            if len(repository.SessionRepository) == 0:
                ui.msg('The session repository does not contain any data ..\n')
            else:
                ui.msg(str(repository.SessionRepository))

            # TODO:  TEMPORARY debugging experiment --- Remove!
            # repository.SessionRepository.to_filedump('/tmp/repository_{:10.10}.state'.format(self.start_time))

    def _handle_file(self, current_file):
        should_list_any_results = (self.opts.get('list_datetime')
                                   or self.opts.get('list_title')
                                   or self.opts.get('list_all'))

        # Extract data from the file.
        required_extractors = providers.get_sources_for_meowuris(
            self.active_config.referenced_meowuris,
            include_roots=['extractor']
        )
        _run_extraction(
            current_file,
            require_extractors=required_extractors,

            # Run all extractors so that all possible data is included
            # when listing any (all) results later on.
            run_all_extractors=should_list_any_results
        )

        # Begin analysing the file.
        _run_analysis(current_file, self.active_config)

        # Run plugins.
        required_plugins = providers.get_sources_for_meowuris(
            self.active_config.referenced_meowuris,
            include_roots=['plugin']
        )
        _run_plugins(
            current_file,
            require_plugins=required_plugins,

            # Run all plugins so that all possible data is included
            # when listing any (all) results later on.
            run_all_plugins=should_list_any_results
        )

        # Determine matching rule.
        matcher = _run_rule_matcher(current_file, self.active_config)

        # Perform actions.
        if self.opts.get('mode_automagic'):
            # TODO: [TD0100] Run rule-matching by default.
            self._perform_automagic_actions(current_file, matcher)
        elif self.opts.get('mode_interactive'):
            # TODO: Create a interactive interface.
            # TODO: [TD0023][TD0024][TD0025] Implement interactive mode.
            log.warning('[UNIMPLEMENTED FEATURE] interactive mode')

    def _perform_automagic_actions(self, current_file, rule_matcher):
        # TODO: [TD0100] Rewrite as per 'notes/modes.md'.
        best_match = None
        name_template = None

        if self.opts.get('mode_batch'):
            if not rule_matcher.best_match:
                log.warning('No rule matched, name template unknown.')
                self.exit_code = C.EXIT_WARNING
                return

            else:
                _best_match_score = rule_matcher.best_match_score()
                if _best_match_score == 0:
                    log.warning('Best matched rule score: {} --- Require user '
                                'confirmmation.'.format(_best_match_score))
                    log.info('Skipping file ..')
                    return
                else:
                    best_match = rule_matcher.best_match

        # TODO: [TD0100] Rewrite as per 'notes/modes.md'.
        else:
            if rule_matcher.best_match:
                _best_match_score = rule_matcher.best_match_score()
                if _best_match_score > 0:
                    best_match = rule_matcher.best_match
                else:
                    log.debug('Best matched rule score: {} --- Require user '
                              'confirmation.'.format(_best_match_score))
                    ok = interactive.ask_confirm(
                        'Best matched rule "{!s}" score: {}\n'
                        'Proceed with this rule?'.format(
                            rule_matcher.best_match.description,
                            _best_match_score
                        )
                    )
                    log.debug('User response: "{!s}"'.format(ok))
                    if ok:
                        best_match = rule_matcher.best_match
            else:
                # TODO: [TD0023][TD0024][TD0025] Implement Interactive mode.
                candidates = None
                choice = interactive.select_template(candidates)
                #if choice != ui.action.ABORT:
                #    name_template = choice
                #else:
                #    name_template = None
                name_template = None

                best_match = rule_matcher.best_match

        # TODO: [TD0100] Rewrite as per 'notes/modes.md'.
        if best_match and not name_template:
            name_template = best_match.name_template
            log.info(
                'Using rule: "{!s}"'.format(rule_matcher.best_match.description)
            )

        if not name_template:
            log.warning('No valid name template chosen. Aborting.')
            return

        resolver = TemplateFieldDataResolver(current_file, name_template)
        resolver.add_known_sources(rule_matcher.best_match.data_sources)

        if self.opts.get('mode_batch'):
            if not resolver.mapped_all_template_fields():
                log.error('All name template placeholder fields must be '
                          'given a data source; Check the configuration!')
                self.exit_code = C.EXIT_WARNING
                return

        resolver.collect()

        # TODO: [TD0100] Rewrite as per 'notes/modes.md'.
        if not resolver.collected_all():
            if self.opts.get('mode_batch'):
                log.warning('Unable to populate name.')
                self.exit_code = C.EXIT_WARNING
                return
            else:
                # TODO: [TD0023][TD0024][TD0025] Implement Interactive mode.
                while not resolver.collected_all():
                    log.info('Resolver has not collected all fields ..')
                    for field in resolver.unresolved:
                        candidates = resolver.lookup_candidates(field)
                        choice = None
                        if candidates:
                            log.info('Resolver found {} candidates'.format(len(candidates)))
                            choice = interactive.select_field(field, candidates)
                        else:
                            log.info('Resolver did not find any candidates ..')

                        if choice is None:
                            _m = 'Specify source for field {!s}'.format(field)
                            choice = interactive.meowuri_prompt(_m)

                        if not choice or choice == interactive.Choice.ABORT:
                            log.info('Aborting ..')
                            return

                        resolver.add_known_source(field, choice)

                    resolver.collect()

        # TODO: [TD0024] Should be able to handle fields not in sources.
        # Add automatically resolving missing sources from possible candidates.
        if not resolver.collected_all():
            # TODO: Abort if running in "batch mode". Otherwise, ask the user.
            log.warning('Unable to populate name. Missing field data.')
            self.exit_code = C.EXIT_WARNING
            return

        try:
            new_name = namebuilder.build(
                config=self.active_config,
                name_template=name_template,
                field_data_map=resolver.fields_data
            )
        except exceptions.NameBuilderError as e:
            log.critical('Name assembly FAILED: {!s}'.format(e))
            raise exceptions.AutonameowException

        log.info('New name: "{}"'.format(
            util.enc.displayable_path(new_name))
        )
        self.do_rename(
            from_path=current_file.abspath,
            new_basename=new_name,
            dry_run=self.opts.get('dry_run')
        )

    @property
    def runtime_seconds(self):
        return time.time() - self.start_time

    def exit_program(self, exit_code_):
        """
        Main program exit point.  Shuts down this autonameow instance/session.

        Args:
            exit_code_: Integer exit code to pass to the parent process.
                Indicate success with 0, failure non-zero.
        """
        self.exit_code = exit_code_

        _elapsed_time = self.runtime_seconds
        if self.opts and self.opts.get('verbose'):
            ui.print_exit_info(self.exit_code, _elapsed_time)

        log.debug('Exiting with exit code: {}'.format(self.exit_code))
        log.debug('Total execution time: {:.6f} seconds'.format(_elapsed_time))

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
        sanity.check_internal_bytestring(from_path)
        sanity.check_internal_string(new_basename)

        # Encoding boundary.  Internal str --> internal filename bytestring
        dest_basename = util.enc.bytestring_path(new_basename)
        log.debug('Destination basename (bytestring): "{!s}"'.format(
            util.enc.displayable_path(dest_basename))
        )
        sanity.check_internal_bytestring(dest_basename)

        from_basename = disk.file_basename(from_path)

        if disk.compare_basenames(from_basename, dest_basename):
            _msg = (
                'Skipped "{!s}" because the current name is the same as '
                'the new name'.format(util.enc.displayable_path(from_basename),
                                      util.enc.displayable_path(dest_basename))
            )
            log.debug(_msg)
            ui.msg(_msg)
        else:
            if dry_run is False:
                try:
                    disk.rename_file(from_path, dest_basename)
                except (FileNotFoundError, FileExistsError, OSError) as e:
                    log.error('Rename FAILED: {!s}'.format(e))
                    raise exceptions.AutonameowException

            ui.msg_rename(from_basename, dest_basename, dry_run=dry_run)

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

    def __hash__(self):
        return hash((util.process_id(), self.start_time))


def _run_extraction(fileobject, require_extractors, run_all_extractors=False):
    """
    Sets up and executes data extraction for the given file.

    Args:
        fileobject: The file object to extract data from.
        require_extractors: List of extractor classes that should be included.
        run_all_extractors: Whether all data extractors should be included.

    Raises:
        AutonameowException: An unrecoverable error occurred during extraction.
    """
    try:
        extraction.start(fileobject,
                         require_extractors=require_extractors,
                         require_all_extractors=run_all_extractors is True)
    except exceptions.AutonameowException as e:
        log.critical('Extraction FAILED: {!s}'.format(e))
        raise


def _run_plugins(fileobject, require_plugins=None, run_all_plugins=False):
    """
    Instantiates, executes and returns a 'PluginHandler' instance.

    Args:
        fileobject: The current file object to pass to plugins.
        require_plugins: List of plugin classes that should be included.
        run_all_plugins: Whether all plugins should be included.

    Returns:
        An instance of the 'PluginHandler' class that has executed successfully.

    Raises:
        AutonameowException: An unrecoverable error occurred during analysis.
    """
    plugin_handler = PluginHandler()
    try:
        plugin_handler.start(fileobject,
                             require_plugins=require_plugins,
                             run_all_plugins=run_all_plugins is True)
    except exceptions.AutonameowPluginError as e:
        log.critical('Plugins FAILED: {!s}'.format(e))
        raise exceptions.AutonameowException(e)


def _run_analysis(fileobject, active_config):
    """
    Sets up and executes "analysis" of the given file.

    Args:
        fileobject: The file object to analyze.
        active_config: An instance of the 'Configuration' class.

    Raises:
        AutonameowException: An unrecoverable error occurred during analysis.
    """
    try:
        analysis.start(fileobject, active_config)
    except exceptions.AutonameowException as e:
        log.critical('Analysis FAILED: {!s}'.format(e))
        raise


def _run_rule_matcher(fileobject, active_config):
    """
    Instantiates, executes and returns a 'RuleMatcher' instance.

    Args:
        active_config: An instance of the 'Configuration' class.

    Returns:
        An instance of the 'RuleMatcher' class that has executed successfully.

    Raises:
        AutonameowException: An unrecoverable error occurred during execution.
    """
    matcher = RuleMatcher(fileobject, active_config)
    try:
        matcher.start()
    except exceptions.AutonameowException as e:
        log.critical('Rule Matching FAILED: {!s}'.format(e))
        raise
    else:
        return matcher
