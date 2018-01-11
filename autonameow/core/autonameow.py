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
    logs,
    persistence,
    provider,
    providers,
    repository,
    ui,
)
from core.evaluate import RuleMatcher
from core.context import FilesContext
from core.fileobject import FileObject
from util import encoding as enc
from util import (
    disk,
    sanity
)


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
        self.matcher = None
        self.rename_stats = {
            'failed': 0,
            'skipped': 0,
            'renamed': 0,
        }
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
                    enc.displayable_path(_default_config_path)
                ),
                'cache_directory_path': '"{!s}"'.format(
                    enc.displayable_path(_config_path)
                )
            }
            ui.options.prettyprint_options(self.opts, include_opts)

        if self.opts.get('dump_config'):
            # TODO: [TD0148] Fix '!!python/object' in '--dump-config' output.
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
            self.active_config.options['FILESYSTEM']['ignore'],
            self.opts.get('recurse_paths')
        )
        log.info('Got {} files to process'.format(len(files_to_process)))

        rules = self.active_config.rules
        if not rules:
            log.warning('Configuration does not contain any rules!')

        self.matcher = RuleMatcher(rules, self.opts.get('list_rulematch'))

        provider.initialize(self.active_config)

        self._handle_files(files_to_process)

        _rename_stats = 'Processed {t} files. Renamed {r}  Skipped {s}  ' \
                        'Failed {f}'.format(t=len(files_to_process),
                                            r=self.rename_stats['renamed'],
                                            s=self.rename_stats['skipped'],
                                            f=self.rename_stats['failed'])
        log.info(_rename_stats)

        self.exit_program(self.exit_code)

    @logs.log_func_runtime(log)
    def load_config(self, path):
        try:
            self.active_config = config.load_config_from_file(path)
        except exceptions.ConfigError as e:
            log.critical('Unable to load configuration -- {!s}'.format(e))

    def _dump_active_config_and_exit(self):
        log.info('Dumping active configuration ..')
        ui.msg('Active Configuration:', style='heading')
        ui.msg(str(self.active_config))
        self.exit_program(C.EXIT_SUCCESS)

    def _dump_registered_meowuris(self):
        ui.msg('Registered MeowURIs', style='heading')

        if self.opts.get('debug'):
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
        else:
            _meowuris = sorted(providers.Registry.mapped_meowuris)
            for _meowuri in _meowuris:
                ui.msg(str(_meowuri))

        ui.msg('\n')

    def _load_config_from_default_path(self):
        _dp = enc.displayable_path(config.DefaultConfigFilePath)
        log.info('Using configuration: "{}"'.format(_dp))
        self.load_config(config.DefaultConfigFilePath)

    def _write_template_config_to_default_path_and_exit(self):
        log.info('No configuration file was found. Writing default ..')
        _dp = enc.displayable_path(config.DefaultConfigFilePath)
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
            enc.displayable_path(self.opts.get('config_path'))
        ))
        self.load_config(self.opts.get('config_path'))

    def _handle_files(self, file_paths):
        """
        Main loop. Iterate over input paths/files.
        Assume all state is setup and completely reset for each loop iteration.
        It is not currently possible to share "information" between runs.
        """
        results_to_list = []

        context = FilesContext(autonameow_instance=self,
                               options=self.opts,
                               active_config=self.active_config,
                               rule_matcher=self.matcher)

        for file_path in file_paths:
            _displayable_file_path = enc.displayable_path(file_path)
            log.info('Processing: "{!s}"'.format(_displayable_file_path))

            # Sanity checking the "file_path" is part of 'FileObject' init.
            try:
                current_file = FileObject(file_path)
            except (exceptions.InvalidFileArgumentError,
                    exceptions.FilesystemError) as e:
                log.warning(
                    '{!s} - SKIPPING: "{!s}"'.format(e, _displayable_file_path)
                )
                continue

            try:
                new_name = context.handle_file(current_file)
            except exceptions.AutonameowException as e:
                log.critical(
                    '{!s} - SKIPPING: "{!s}"'.format(e, _displayable_file_path)
                )
                self.exit_code = C.EXIT_WARNING
                continue

            if new_name:
                self.do_rename(
                    from_path=current_file.abspath,
                    new_basename=new_name,
                    dry_run=self.opts.get('dry_run')
                )

            # TODO: [TD0131] Hack!
            # _repositorysize = sys.getsizeof(repository.SessionRepository)
            results_to_list.append(str(repository.SessionRepository))

            # TODO: [TD0131] Limit repository size!
            repository.SessionRepository.data.pop(current_file)

        if self.opts.get('list_all'):
            log.info('Listing session repository contents ..')
            ui.msg('Session Repository Data', style='heading',
                   add_info_log=True)

            if not results_to_list:
                ui.msg('The session repository does not contain any data ..\n')
            else:
                ui.msg('\n'.join(results_to_list))

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
        # TODO: [TD0143] Add option to execute "hooks" at certain events.
        # TODO: [TD0092] Add storing history and ability to "undo" renames.
        sanity.check_internal_bytestring(from_path)
        sanity.check_internal_string(new_basename)

        # Encoding boundary.  Internal str --> internal filename bytestring
        dest_basename = enc.bytestring_path(new_basename)
        log.debug('Destination basename (bytestring): "{!s}"'.format(
            enc.displayable_path(dest_basename)))
        sanity.check_internal_bytestring(dest_basename)

        from_basename = disk.file_basename(from_path)

        if disk.compare_basenames(from_basename, dest_basename):
            self.rename_stats['skipped'] += 1
            _msg = (
                'Skipped "{!s}" because the current name is the same as '
                'the new name'.format(enc.displayable_path(from_basename),
                                      enc.displayable_path(dest_basename))
            )
            log.debug(_msg)
            ui.msg(_msg)
        else:
            self.rename_stats['renamed'] += 1
            if dry_run is False:
                try:
                    disk.rename_file(from_path, dest_basename)
                except (FileNotFoundError, FileExistsError, OSError) as e:
                    self.rename_stats['failed'] += 1
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
