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
import os
import re
import shutil
import sys
import traceback

import unit.constants as uuconst
import unit.utils as uu
from core import constants as C
from core import (
    exceptions,
    types,
    ui
)
from util import encoding as enc
from util import (
    disk,
    sanity
)


log = logging.getLogger(__name__)


TERMINAL_WIDTH, _ = shutil.get_terminal_size(fallback=(120, 48))


# TODO: [TD0121] Generate regression tests from manual invocations.


class RegressionTestError(exceptions.AutonameowException):
    """Error caused by an invalid regression test."""


def read_plaintext_file(file_path, ignore_errors=None):
    try:
        with open(file_path, 'r', encoding=C.DEFAULT_ENCODING) as fh:
            contents = fh.read()
    except (FileNotFoundError, UnicodeDecodeError) as e:
        if ignore_errors:
            return ''
        else:
            raise RegressionTestError(e)
    else:
        return contents


class TerminalReporter(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

        self.MAX_DESCRIPTION_LENGTH = TERMINAL_WIDTH - 70
        assert self.MAX_DESCRIPTION_LENGTH > 0, 'Terminal is not wide enough ..'

    def msg_test_success(self):
        _label = ui.colorize('[SUCCESS]', fore='GREEN')
        if self.verbose:
            print('{} All assertions passed!'.format(_label))
        else:
            print(' ' + _label + ' ', end='')

    def msg_test_failure(self):
        _label = ui.colorize('[FAILURE]', fore='RED')
        if self.verbose:
            print('{} One or more assertions FAILED!'.format(_label))
        else:
            print(' ' + _label + ' ', end='')

    @staticmethod
    def _center_with_fill(text):
        padded_text = '  ' + text + '  '
        return padded_text.center(TERMINAL_WIDTH, '=')

    def msg_overall_success(self):
        print(ui.colorize(self._center_with_fill('ALL TESTS PASSED!'),
                          fore='GREEN', style='BRIGHT'))

    def msg_overall_failure(self):
        print(ui.colorize(self._center_with_fill('SOME TESTS FAILED'),
                          fore='RED', style='BRIGHT'))

    def msg_overall_noop(self):
        print(ui.colorize(self._center_with_fill('DID NOT RUN ANY TESTS'),
                          fore='YELLOW', style='BRIGHT'))

    def msg_overall_stats(self, count_total, count_skipped, count_success,
                          count_failure, elapsed_time):
        print('\n')

        _skipped = '{} skipped'.format(count_skipped)
        if count_skipped > 0:
            _skipped = ui.colorize(_skipped, fore='YELLOW')

        _failure = '{} failed'.format(count_failure)
        if count_failure == 0:
            if count_total == 0:
                self.msg_overall_noop()
            else:
                self.msg_overall_success()
        else:
            self.msg_overall_failure()
            # Make the failed count red if any test failed.
            _failure = ui.colorize(_failure, fore='RED')

        _runtime = '{:.6f}s'.format(elapsed_time)

        _stats = 'Regression Test Summary:  {} total, {}, {} passed, {}  ' \
                 'in {} seconds'.format(count_total, _skipped,
                                        count_success, _failure, _runtime)

        print()
        print(_stats)
        print('_' * TERMINAL_WIDTH)

    def msg_test_start(self, shortname, description):
        if self.verbose:
            _desc = ui.colorize(description, style='DIM')
            print()
            print('Running "{}"'.format(shortname))
            print(_desc)
        else:
            maxlen = self.MAX_DESCRIPTION_LENGTH
            _desc_len = len(description)
            if _desc_len > maxlen:
                _desc = description[0:maxlen] + '..'
            else:
                _desc = description + ' '*(2 + maxlen - _desc_len)

            _colordesc = ui.colorize(_desc, style='DIM')
            print('{:30.30s} {!s} '.format(shortname, _colordesc), end='')

    def msg_test_skipped(self, shortname, description):
        if self.verbose:
            print()
            _label = ui.colorize('[SKIPPED]', fore='YELLOW')
            _desc = ui.colorize(description, style='DIM')
            print('{} "{!s}"'.format(_label, shortname))
            print(_desc)
        else:
            maxlen = self.MAX_DESCRIPTION_LENGTH
            _desc_len = len(description)
            if _desc_len > maxlen:
                _desc = description[0:maxlen] + '..'
            else:
                _desc = description + ' '*(2 + maxlen - _desc_len)

            _colordesc = ui.colorize(_desc, style='DIM')
            _label = ui.colorize('[SKIPPED]', fore='YELLOW')
            print('{:30.30s} {!s}  {} '.format(shortname, _colordesc, _label), end='')

    def msg_test_runtime(self, elapsed_time, captured_time):
        if captured_time:
            _captured = '{:.6f}s)'.format(captured_time)
        else:
            _captured = 'N/A)'

        if elapsed_time:
            _elapsed = '{:.6f}s'.format(elapsed_time)
        else:
            _elapsed = 'N/A'

        _time_1 = '{:10.10s}'.format(_elapsed)
        _time_2 = '{:10.10s}'.format(_captured)
        if self.verbose:
            print(' '*10 + 'Runtime: {} (captured {}'.format(_time_1, _time_2))
        else:
            print('  {} ({}'.format(_time_1, _time_2))

    @staticmethod
    def msg_captured_stderr(stderr):
        _header = ui.colorize('Captured stderr:', fore='RED')
        _stderr = ui.colorize(stderr, fore='RED')
        print('\n' + _header)
        print(_stderr)

    @staticmethod
    def msg_captured_stdout(stdout):
        print('\nCaptured stdout:')
        print(stdout)


class RegressionTestLoader(object):
    BASENAME_DESCRIPTION = b'description'
    BASENAME_SKIP = b'skip'
    BASENAME_YAML_OPTIONS = b'options.yaml'
    BASENAME_YAML_ASSERTS = b'asserts.yaml'

    def __init__(self, abspath):
        assert isinstance(abspath, bytes)
        self.abspath = abspath
        self.skiptest = False

    def _get_test_setup_dict_from_files(self):
        _abspath_desc = self._joinpath(self.BASENAME_DESCRIPTION)
        _description = read_plaintext_file(_abspath_desc, ignore_errors=True)

        _abspath_opts = self._joinpath(self.BASENAME_YAML_OPTIONS)
        try:
            _options = disk.load_yaml_file(_abspath_opts)
        except exceptions.FilesystemError as e:
            raise RegressionTestError(e)

        if not _options:
            log.warning(
                'Read empty options from file: "{!s}"'.format(_abspath_opts)
            )
            _options = dict()
        _options = self._set_testfile_path(_options)
        _options = self._set_config_path(_options)

        _abspath_asserts = self._joinpath(self.BASENAME_YAML_ASSERTS)
        try:
            _asserts = disk.load_yaml_file(_abspath_asserts)
        except exceptions.FilesystemError as e:
            raise RegressionTestError(e)

        if not _asserts:
            raise RegressionTestError(
                'Read empty asserts from file: "{!s}"'.format(_abspath_asserts)
            )

        _abspath_skip = self._joinpath(self.BASENAME_SKIP)
        if uu.file_exists(_abspath_skip):
            _skiptest = True
        else:
            _skiptest = False

        assert isinstance(_asserts, dict)
        assert isinstance(_options, dict)
        return {
            'asserts': _asserts,
            'description': _description.strip() or '(description unavailable)',
            'options': _options,
            'skiptest': _skiptest
        }

    @staticmethod
    def _set_testfile_path(options):
        """
        Replaces '$TESTFILES' with the full absolute path to the 'test_files'
        directory.
        For instance; '$TESTFILES/foo.txt' --> '$SRCROOT/test_files/foo.txt',
        where '$SRCROOT' is the full absolute path to the autonameow sources.
        """
        if 'input_paths' not in options:
            return options

        _fixed_paths = []
        for path in options['input_paths']:
            if path == '$TESTFILES':
                # Substitute "variable".
                _abspath = uuconst.TEST_FILES_DIR
            elif path.startswith('$TESTFILES/'):
                # Substitute "variable".
                _basename = path.replace('$TESTFILES/', '')
                _abspath = uu.abspath_testfile(_basename)
            else:
                # Normalize path.
                try:
                    _abspath_bytes = types.AW_PATH.normalize(path)
                except types.AWTypeError as e:
                    raise RegressionTestError('Invalid path in "input_paths":'
                                              '"{!s}" :: {!s}'.format(path, e))
                else:
                    # NOTE(jonas): Iffy ad-hoc string coercion..
                    _abspath = types.force_string(_abspath_bytes)

            # Allow non-existent but not empty paths.
            if not _abspath.strip():
                raise RegressionTestError(
                    'Path is empty after processing: "{!s}"'.format(path)
                )
            _fixed_paths.append(_abspath)

        options['input_paths'] = _fixed_paths
        return options

    def _set_config_path(self, options):
        """
        Modifies the 'config_path' entry in the options dict.

        If the 'config_path' entry..

          * .. is missing, the path of the default (unit test) config is used.

               --> 'config_path': (Path to the default config)

          * .. starts with '$TESTFILES/', the full absolute path to the
               'test_files' directory is inserted in place of '$TESTFILES/'.

                   'config_path': '$TESTFILES/config.yaml'
               --> 'config_path': '$SRCROOT/test_files/config.yaml'

          * .. starts with '$THISTEST/', the full absolute path to the current
               regression test directory is inserted in place of '$THISTEST/'.

                   'config_path': '$THISTEST/config.yaml'
               --> 'config_path': 'self.abspath/config.yaml'
        """
        _options = dict(options)

        _path = types.force_string(_options.get('config_path'))
        if not _path:
            # Use default config.
            _abspath = uu.abspath_testconfig()
        elif _path.startswith('$TESTFILES/'):
            # Substitute "variable".
            _basename = _path.replace('$TESTFILES/', '').strip()
            _abspath = uu.abspath_testfile(_basename)
        elif _path.startswith('$THISTEST/'):
            # Substitute "variable".
            _basename = _path.replace('$THISTEST/', '').strip()
            try:
                _bytes_basename = types.AW_PATHCOMPONENT(_basename)
            except types.AWTypeError as e:
                raise RegressionTestError(e)
            _abspath = self._joinpath(_bytes_basename)
        else:
            # Assume absolute path.
            _abspath = _path

        if not uu.file_exists(_abspath):
            raise RegressionTestError(
                'Invalid "config_path": "{!s}"'.format(_path)
            )

        log.debug('Set config_path "{!s}" to "{!s}"'.format(_path, _abspath))
        _options['config_path'] = enc.normpath(_abspath)
        return _options

    def _joinpath(self, leaf):
        assert isinstance(leaf, bytes)
        return os.path.join(
            enc.syspath(self.abspath), enc.syspath(leaf)
        )

    def load(self):
        _setup_dict = self._get_test_setup_dict_from_files()
        _setup_dict['test_abspath'] = self.abspath
        _setup_dict['test_dirname'] = os.path.basename(
            enc.syspath(self.abspath)
        )
        return _setup_dict


class AutonameowWrapper(object):
    """
    Autonameow class wrapper used by the regression tests.

    Wraps an instance of the 'Autonameow' class and overrides ("monkey-patches")
    some of its methods in order to capture data needed to evaluate the tests.
    """
    def __init__(self, opts=None):
        if opts:
            assert isinstance(opts, dict)
            self.opts = opts
        else:
            self.opts = dict()

        self.captured_exitcode = None
        self.captured_stderr = None
        self.captured_stdout = None
        self.captured_renames = dict()
        self.captured_runtime_secs = None
        self.captured_exception = None
        self.captured_exception_traceback = None

    def mock_exit_program(self, exitcode):
        self.captured_exitcode = exitcode

    def mock_rename_file(self, from_path, new_basename):
        # TODO: [hack] Mocking is too messy to be reliable ..
        # NOTE(jonas): Iffy ad-hoc string coercion..
        _from_basename = types.force_string(disk.file_basename(from_path))
        _new_basename = types.force_string(new_basename)

        # Check for collisions that might cause erroneous test results.
        if _from_basename in self.captured_renames:
            _existing_new_basename = self.captured_renames[_from_basename]
            raise RegressionTestError(
                'Already captured rename: "{!s}" -> "{!s}" (Now "{!s}")'.format(
                    _from_basename, _existing_new_basename, _new_basename
                )
            )
        self.captured_renames[_from_basename] = _new_basename

    def __call__(self):
        # TODO: [TD0158] Evaluate assertions of "skipped renames".
        from core.autonameow import Autonameow

        # Monkey-patch method of 'Autonameow' *class*
        Autonameow.exit_program = self.mock_exit_program

        with uu.capture_stdout() as stdout, uu.capture_stderr() as stderr:
            try:
                with Autonameow(self.opts) as ameow:
                    # TODO: Mock 'FileRenamer' class instead of single method
                    assert hasattr(ameow, 'renamer')
                    assert hasattr(ameow.renamer, '_rename_file')

                    # Monkey-patch method of 'FileRenamer' *instance*
                    ameow.renamer._rename_file = self.mock_rename_file

                    ameow.run()

                    # Store runtime recorded by the 'Autonameow' class.
                    self.captured_runtime_secs = ameow.runtime_seconds
            except Exception as e:
                typ, val, tb = sys.exc_info()
                exception_info = ''.join(traceback.format_exception(typ, val, tb))
                self.captured_exception = e
                self.captured_exception_traceback = exception_info

        self.captured_stdout = stdout.getvalue()
        self.captured_stderr = stderr.getvalue()


REGRESSIONTESTS_ROOT_ABSPATH = None


def get_regressiontests_rootdir():
    global REGRESSIONTESTS_ROOT_ABSPATH
    if not REGRESSIONTESTS_ROOT_ABSPATH:
        _rootdir = os.path.join(
            C.AUTONAMEOW_SRCROOT_DIR, 'tests', 'regression'
        )
        REGRESSIONTESTS_ROOT_ABSPATH = enc.normpath(_rootdir)

    assert disk.isdir(REGRESSIONTESTS_ROOT_ABSPATH)
    return REGRESSIONTESTS_ROOT_ABSPATH


def regtest_abspath(basename):
    _root = get_regressiontests_rootdir()
    try:
        _abspath = os.path.join(
            enc.syspath(_root),
            enc.syspath(basename)
        )
        _normalized_abspath = enc.normpath(_abspath)
    except Exception:
        raise AssertionError

    assert disk.isdir(_normalized_abspath)
    return _normalized_abspath


RE_REGRESSIONTEST_DIRNAME = re.compile(rb'\d{4}(_[\w]+)?')


def get_regressiontest_dirs():
    _tests_root_dir = get_regressiontests_rootdir()
    _dirs = [
        regtest_abspath(d)
        for d in os.listdir(_tests_root_dir)
        if RE_REGRESSIONTEST_DIRNAME.match(d)
    ]

    return _dirs


def load_regressiontests():
    out = []

    _paths = get_regressiontest_dirs()
    for p in _paths:
        try:
            loaded_test = RegressionTestLoader(p).load()
        except RegressionTestError as e:
            print('Unable to load test case :: ' + str(e))
        else:
            out.append(loaded_test)

    return sorted(out, key=lambda x: x.get('test_dirname'))


def check_renames(actual, expected):
    if not isinstance(actual, dict):
        raise RegressionTestError('Expected argument "actual" of type dict')
    if not isinstance(expected, dict):
        raise RegressionTestError('Expected argument "expected" of type dict')

    if not actual and not expected:
        # Did not expect anything and nothing happened.
        return True
    elif actual and not expected:
        # Something unexpected happened.
        return False
    elif expected and not actual:
        # Expected something to happen but it didn't.
        return False

    # Compare dict of expected from-tos to the dict of actual from-tos.
    return bool(expected == actual)


def check_stdout_asserts(test, captured_stdout):
    failures = 0
    if 'asserts' not in test:
        return failures
    if 'stdout' not in test['asserts']:
        return failures

    stdout_match_asserts = []
    stdout_matches = test['asserts']['stdout'].get('matches', [])
    for regexp in stdout_matches:
        try:
            stdout_match_asserts.append(re.compile(regexp, re.MULTILINE))
        except (ValueError, TypeError) as e:
            print('Bad stdout match regexp "{!s}" :: {!s}'.format(regexp, e))
            continue

    for regexp in stdout_match_asserts:
        if not regexp.match(captured_stdout):
            print('Match assertion failed for "{!s}"'.format(regexp))
            failures += 1

    stdout_not_match_asserts = []
    stdout_not_matches = test['asserts']['stdout'].get('does_not_match', [])
    for regexp in stdout_not_matches:
        try:
            stdout_not_match_asserts.append(re.compile(regexp, re.MULTILINE))
        except (ValueError, TypeError) as e:
            print(str(e))
            continue

    for regexp in stdout_not_match_asserts:
        if regexp.match(captured_stdout):
            print('Non-match assertion failed for "{!s}"'.format(regexp))
            failures += 1

    return failures


def _commandline_args_for_testcase(loaded_test):
    """
    Converts a regression test to a list of command-line arguments.

    Given a loaded "regression test case", it returns command-line components
    that would result in equivalent behaviour.
    The returned arguments would be used when invoking autonameow "manually"
    from the command-line.

    Args:
        loaded_test: Regression "test case" returned from
                     'load_regressiontests()', as type dict.

    Returns:
        Command-line arguments as a list of Unicode strings.
    """
    # TODO: [hardcoded] Generate from 'autonameow/core/ui/cli/options.py'.
    # TODO: Add '--list_rulematch'
    TESTOPTION_CMDARG_MAP = {
        'debug': '--debug',
        'dry_run': '--dry-run',
        'dump_config': '--dump-config',
        'dump_meowuris': '--dump-meowuris',
        'dump_options': '--dump-options',
        'list_all': '--list-all',
        'mode_automagic': '--automagic',
        'mode_batch': '--batch',
        'mode_interactive': '--interactive',
        'mode_timid': '--timid',
        'mode_postprocess_only': '--postprocess-only',
        'quiet': '--quiet',
        'recurse_paths': '--recurse',
        'show_version': '--version',
        'verbose': '--verbose',
    }

    arguments = []
    loaded_options = loaded_test.get('options')
    if loaded_options:
        for opt, arg in TESTOPTION_CMDARG_MAP.items():
            if loaded_options.get(opt):
                arguments.append(arg)

        # For more consistent output and easier testing, sort before adding
        # positional and "key-value"-type options.
        arguments = sorted(arguments)

        _config_path = loaded_options.get('config_path')
        if _config_path:
            _str_config_path = types.force_string(_config_path)
            assert _str_config_path != ''
            arguments.append("--config-path '{}'".format(_str_config_path))

        _input_paths = loaded_options.get('input_paths')
        if _input_paths:
            # Mark end of options, start of arguments (input paths)
            arguments.append('--')
            for p in _input_paths:
                arguments.append("'{}'".format(p))

    return arguments


def commandline_for_testcase(loaded_test):
    """
    Converts a regression test to a equivalent command-line invocation string.

    Given a loaded "regression test case", it returns a full command that
    could be pasted into a terminal to produce  behaviour equivalent to the
    given regression test case.

    Args:
        loaded_test: Regression "test case" returned from
                     'load_regressiontests()', as type dict.

    Returns:
        Full equivalent command-line as a Unicode string.
    """
    sanity.check_isinstance(loaded_test, dict)
    arguments = _commandline_args_for_testcase(loaded_test)
    argument_string = ' '.join(arguments)
    commandline = 'autonameow ' + argument_string
    return commandline.strip()


def glob_filter(glob, bytestring):
    """
    Evaluates if a string (test basename) matches a given "glob".

    Matching is case-sensitive. The asterisk matches anything.
    If the glob starts with '!', the matching is negated.
    Examples:
                    string          glob            Returns
                    ---------------------------------------
                    'foo bar'       'foo bar'       True
                    'foo bar'       'foo*'          True
                    'foo x bar'     '*x*'           True
                    'bar'           'foo*'          False
                    'bar'           '!foo'          True
                    'foo x bar'     '!foo*'         False
    """
    if not isinstance(bytestring, bytes):
        raise RegressionTestError(
            'Expected type bytes for argument "bytestring". '
            'Got {} ({!s})'.format(type(bytestring), bytestring)
        )
    try:
        # Coercing to "AW_PATHCOMPONENT" because there is no "AW_BYTES".
        bytes_glob = types.AW_PATHCOMPONENT(glob)
    except types.AWTypeError as e:
        raise RegressionTestError(e)

    regexp = bytes_glob.replace(b'*', b'.*')
    if regexp.startswith(b'!'):
        regexp = regexp[1:]
        return not bool(re.match(regexp, bytestring))

    return bool(re.match(regexp, bytestring))


def regexp_filter(expression, bytestring):
    """
    Evaluates if a string (test basename) matches a given regular expression.
    """
    if not isinstance(bytestring, bytes):
        raise RegressionTestError(
            'Expected type bytes for argument "bytestring". '
            'Got {} ({!s})'.format(type(bytestring), bytestring)
        )
    try:
        # Coercing to "AW_PATHCOMPONENT" because there is no "AW_BYTES".
        bytes_expr = types.AW_PATHCOMPONENT(expression)
    except types.AWTypeError as e:
        raise RegressionTestError(e)

    try:
        regexp = re.compile(bytes_expr)
    except (TypeError, ValueError, re.error) as e:
        raise RegressionTestError(e)

    return bool(regexp.match(bytestring))
