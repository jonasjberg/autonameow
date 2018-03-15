#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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

import util
from core import constants as C
from core import (
    config,
    exceptions,
    FileObject,
    interactive,
    logs,
    persistence,
    master_provider,
    providers,
    repository,
)
from core.context import FilesContext
from core.namebuilder import FilenamePostprocessor
from core.renamer import FileRenamer
from util import encoding as enc
from util import disk


log = logging.getLogger(__name__)


class Autonameow(object):
    """
    Main class to manage a running "autonameow" instance.
    """

    def __init__(self, opts, ui):
        """
        Main program entry point.  Initializes a autonameow instance/session.

        Args:
            opts: Dict with parsed and validated options.
        """
        assert isinstance(opts, dict)
        self.opts = check_option_combinations(opts)

        # Package in 'autonameow/core/view' or equivalent interface.
        self.ui = ui

        # For calculating the total runtime.
        self.start_time = time.time()

        self.active_config = None
        self.renamer = None
        self.master_provider = None

        self._exit_code = C.EXIT_SUCCESS

    def __enter__(self):
        # Set up singletons for this process.
        repository.initialize(self)
        providers.initialize()

        self.renamer = FileRenamer(
            dry_run=self.opts.get('dry_run'),
            timid=self.opts.get('mode_timid')
        )

        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Reset singletons.
        repository.shutdown(self)
        providers.shutdown()

    def run(self):
        if self.opts.get('quiet'):
            self.ui.silence()

        # Display various information depending on verbosity level.
        if self.opts.get('verbose') or self.opts.get('debug'):
            self.ui.print_start_info()

        # Display startup banner with program version and exit.
        if self.opts.get('show_version'):
            self.ui.print_version_info(verbose=self.opts.get('verbose'))
            self.exit_program(C.EXIT_SUCCESS)

        # Check configuration file. If no alternate config file path is
        # provided and no config file is found at default paths; copy the
        # template config and tell the user.
        if self.opts.get('config_path'):
            self._load_config_from_alternate_path()
        else:
            if not config.has_config_file():
                log.info('No configuration file was found.')
                self._write_template_config_to_default_path_and_exit()
            else:
                self._load_config_from_default_path()

        if not self.active_config:
            log.critical('Unable to load configuration --- Aborting ..')
            self.exit_program(C.EXIT_ERROR)

        # Set globally accessible configuration instance.
        config.set_active(self.active_config)

        if self.opts.get('dump_options'):
            self._dump_options()

        if self.opts.get('dump_config'):
            # TODO: [TD0148] Fix '!!python/object' in '--dump-config' output.
            self._dump_active_config_and_exit()

        if self.opts.get('dump_meowuris'):
            self._dump_registered_meowuris()

        # Abort early if input paths are missing.
        if not self.opts.get('input_paths'):
            log.warning('No input files specified ..')
            self.exit_program(C.EXIT_SUCCESS)

        # Path name encoding boundary. Returns list of paths in internal format.
        files_to_process = self._collect_path_from_opts()
        log.info('Got {} files to process'.format(len(files_to_process)))

        # Initialize the global master data provider.
        master_provider.initialize(self.active_config)
        self.master_provider = master_provider

        # Handle any input paths/files.
        self._handle_files(files_to_process)

        stats = 'Processed {t} files. Renamed {r}  Skipped {s}  ' \
                'Failed {f}'.format(t=len(files_to_process),
                                    r=self.renamer.stats['renamed'],
                                    s=self.renamer.stats['skipped'],
                                    f=self.renamer.stats['failed'])
        log.info(stats)

        self.exit_program(self.exit_code)

    def _collect_path_from_opts(self):
        path_collector = disk.PathCollector(
            ignore_globs=self.active_config.options['FILESYSTEM']['ignore'],
            recurse=self.opts.get('recurse_paths')
        )
        path_collector.collect_from(self.opts.get('input_paths'))

        for error in path_collector.errors:
            log.warning(str(error))

        return list(path_collector.filepaths)

    @logs.log_func_runtime(log)
    def load_config(self, path):
        try:
            self.active_config = config.load_config_from_file(path)
        except exceptions.ConfigError as e:
            log.critical('Unable to load configuration --- {!s}'.format(e))

    def _dump_options(self):
        filepath_config = persistence.get_config_persistence_path()
        filepath_default_config = config.DefaultConfigFilePath
        include_opts = {
            'config_file_path': '"{!s}"'.format(
                enc.displayable_path(filepath_default_config)
            ),
            'cache_directory_path': '"{!s}"'.format(
                enc.displayable_path(filepath_config)
            )
        }
        self.ui.options.prettyprint_options(self.opts, include_opts)

    def _dump_active_config_and_exit(self):
        self.ui.msg('Active Configuration:', style='heading')
        self.ui.msg(str(self.active_config))
        self.exit_program(C.EXIT_SUCCESS)

    def _dump_registered_meowuris(self):
        self.ui.msg('Registered MeowURIs', style='heading')

        if self.opts.get('debug'):
            cf = self.ui.ColumnFormatter()
            for _type in C.MEOWURI_ROOTS_SOURCES:
                cf.addemptyrow()
                sourcemap = providers.Registry.meowuri_sources.get(_type, {})
                # Sorted by MeowURI within "root sections", separated by blank lines.
                for uri, _klass in sorted(sourcemap.items(), key=lambda x: str(x[0])):
                    cf.addrow(str(uri), str(_klass))
            self.ui.msg(str(cf))
        else:
            _meowuris = sorted(providers.Registry.mapped_meowuris)
            for uri in _meowuris:
                self.ui.msg(str(uri))

        self.ui.msg('\n')

    def _load_config_from_default_path(self):
        default_config_path = config.DefaultConfigFilePath
        str_path = enc.displayable_path(default_config_path)
        log.info('Using configuration: "{}"'.format(str_path))
        self.load_config(default_config_path)

    def _write_template_config_to_default_path_and_exit(self):
        str_path = enc.displayable_path(config.DefaultConfigFilePath)
        try:
            config.write_default_config()
        except exceptions.ConfigError as e:
            log.critical('Unable to write template configuration file to path: '
                         '"{!s}" --- {!s}'.format(str_path, e))
            self.exit_program(C.EXIT_ERROR)

        message = 'Wrote default configuration file to "{!s}"'.format(str_path)
        self.ui.msg(message, style='info')
        self.exit_program(C.EXIT_SUCCESS)

    def _load_config_from_alternate_path(self):
        opts_config_path = self.opts.get('config_path')
        str_path = enc.displayable_path(opts_config_path)
        log.info('Using configuration file: "{!s}"'.format(str_path))
        self.load_config(opts_config_path)

    def _handle_files(self, file_paths):
        """
        Main loop. Iterate over input paths/files.
        Assume all state is setup and completely reset for each loop iteration.
        It is not currently possible to share "information" between runs.
        """
        aggregate_repository_contents = []

        context = FilesContext(
            ui=self.ui,
            autonameow_exit_code=self.exit_code,
            options=self.opts,
            active_config=self.active_config,
            master_provider=self.master_provider
        )

        for file_path in file_paths:
            str_file_path = enc.displayable_path(file_path)
            log.info('Processing: "{!s}"'.format(str_file_path))

            # Sanity checking the "file_path" is part of 'FileObject' init.
            try:
                current_file = FileObject(file_path)
            except (exceptions.InvalidFileArgumentError,
                    exceptions.FilesystemError) as e:
                log.warning(
                    '{!s} --- SKIPPING: "{!s}"'.format(e, str_file_path)
                )
                continue

            if self.opts.get('list_all'):
                log.debug('Calling provider.delegate_every_possible_meowuri()')
                master_provider.delegate_every_possible_meowuri(current_file)

            try:
                new_name = context.find_new_name(current_file)
            except exceptions.AutonameowException as e:
                log.critical(
                    '{!s} --- SKIPPING: "{!s}"'.format(e, str_file_path)
                )
                self.exit_code = C.EXIT_WARNING
                continue

            if new_name:
                postprocessor = FilenamePostprocessor(
                    lowercase_filename=self.active_config.get(
                        ['POST_PROCESSING', 'lowercase_filename']),
                    uppercase_filename=self.active_config.get(
                        ['POST_PROCESSING', 'uppercase_filename']),
                    regex_replacements=self.active_config.get(
                        ['POST_PROCESSING', 'replacements']),
                    simplify_unicode=self.active_config.get(
                        ['POST_PROCESSING', 'simplify_unicode'])
                )
                before = str(new_name)
                postprocessed_new_name = postprocessor(new_name)
                after = str(postprocessed_new_name)
                if before != after:
                    self.ui.msg_filename_replacement(before, after)

                self.renamer.add_pending(
                    from_path=current_file.abspath,
                    new_basename=postprocessed_new_name,
                )

            for filename_delta in self.renamer.skipped:
                message = (
                    'Skipped "{!s}" because the current name is the same as '
                    'the new name'.format(filename_delta.displayable_old)
                )
                self.ui.msg(message)

            for filename_delta in self.renamer.needs_confirmation:
                # TODO: [cleanup] The renamer is a mess. Why pass 'timid'?
                log.debug('Timid mode enabled. Asking user to confirm ..')
                if interactive.ask_confirm_rename(filename_delta.displayable_old,
                                                  filename_delta.displayable_new):
                    self.renamer.confirm(filename_delta)

            # TODO: Display renames as they actually happen?
            for filename_delta in self.renamer.pending:
                self.ui.msg_rename(
                    filename_delta.displayable_old,
                    filename_delta.displayable_new,
                    dry_run=self.opts.get('dry_run')
                )

            try:
                self.renamer.do_renames()
            except exceptions.FilesystemError as e:
                log.error('Rename FAILED: {!s}'.format(e))

            # TODO: [TD0131] Hack!
            aggregate_repository_contents.append(str(repository.SessionRepository))

            # TODO: [TD0131] Limit repository size! Do not remove everything!
            # TODO: [TD0131] Keep all but very bulky data like extracted text.
            if current_file in repository.SessionRepository.data:
                repository.SessionRepository.remove(current_file)

        if self.opts.get('list_all'):
            if not aggregate_repository_contents:
                str_repo = 'The session repository does not contain any data ..\n'
            else:
                str_repo = '\n'.join(aggregate_repository_contents)

            self.ui.msg('Session Repository Data', style='heading')
            self.ui.msg(str_repo)

    @property
    def runtime_seconds(self):
        return time.time() - self.start_time

    def exit_program(self, exit_code_value):
        """
        Main program exit point.  Shuts down this autonameow instance/session.

        Args:
            exit_code_value: Integer exit code to pass to the parent process.
                Indicate success with 0, failure non-zero.
        """
        self.exit_code = exit_code_value

        elapsed_time = self.runtime_seconds
        if self.opts and self.opts.get('verbose'):
            self.ui.print_exit_info(self.exit_code, elapsed_time)

        logs.log_previously_logged_runtimes(log)
        log.debug('Exiting with exit code: {}'.format(self.exit_code))
        log.debug('Total execution time: {:.6f} seconds'.format(elapsed_time))

        sys.exit(self.exit_code)

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
            log.debug('Exit code updated: {} -> {}'.format(self._exit_code, value))
            self._exit_code = value

    def __hash__(self):
        return hash((util.process_id(), self.start_time))


def check_option_combinations(options):
    opts = dict(options)

    # TODO: [cleanup] This is pretty messy ..
    # Check legality of option combinations.
    if opts.get('mode_automagic') and opts.get('mode_interactive'):
        log.warning('Operating mode must be either one of "automagic" or '
                    '"interactive", not both. Reverting to default: '
                    '[interactive mode].')
        opts['mode_automagic'] = False
        opts['mode_interactive'] = True

    if not opts.get('mode_rulematch'):
        log.info('Enabled rule-matching..')
        opts['mode_rulematch'] = True

    if (not opts.get('mode_automagic') and not opts.get('mode_rulematch')
            and opts.get('mode_batch')):
        log.warning('Running in "batch" mode without specifying an '
                    'operating mode ("automagic" or rule-matching) does '
                    'not make any sense.  Nothing to do!')

    if opts.get('mode_batch'):
        if opts.get('mode_interactive'):
            log.warning('Operating mode "batch" can not be used with '
                        '"interactive".  Disabling "interactive"..')
            opts['mode_interactive'] = False

        if opts.get('mode_timid'):
            log.warning('Operating mode must be either one of "batch" or '
                        '"timid", not both. Disabling "timid"..')
            opts['mode_timid'] = False

    if opts.get('mode_interactive'):
        if opts.get('mode_timid'):
            log.warning('Operating mode "interactive" implies "timid". '
                        'Disabling "timid"..')
            opts['mode_timid'] = False

    if opts.get('mode_postprocess_only'):
        # Do not figure out a new name; do "post-processing" on existing.
        if opts.get('mode_automagic'):
            log.warning('Operating mode "automagic" can not be used with '
                        '"post-process only". Disabling "automagic".')
            opts['mode_automagic'] = False
        if opts.get('mode_interactive'):
            log.warning('Operating mode "interactive" can not be used with '
                        '"post-process only". Disabling "interactive".')
            opts['mode_interactive'] = False
    else:
        if not opts.get('mode_automagic') and not opts.get('mode_rulematch'):
            log.info('No operating-mode selected!')

    return opts
