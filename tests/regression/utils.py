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

import functools
import logging
import os
import re
import shutil
import sys
import traceback
from collections import defaultdict

import unit.constants as uuconst
import unit.utils as uu
from core import constants as C
from core.view import cli
from core import (
    exceptions,
    types
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
        if not ignore_errors:
            raise RegressionTestError(e)
        return ''
    else:
        return types.force_string(contents)


# Redefined print functions with disabled buffering.
_println = functools.partial(print, flush=True)
_print = functools.partial(print, flush=True, end='')


class TerminalReporter(object):
    def __init__(self, verbose=False):
        self.verbose = verbose

        self.MAX_DESCRIPTION_LENGTH = TERMINAL_WIDTH - 70
        assert self.MAX_DESCRIPTION_LENGTH > 0, 'Terminal is not wide enough ..'

        self.msg_label_pass = cli.colorize('PASS', fore='GREEN')
        self.msg_label_fail = cli.colorize('FAIL', fore='RED')

    def msg(self, string):
        if self.verbose:
            _println(string)

    def msg_run_test_success(self, string):
        if self.verbose:
            _println('{} {!s}'.format(self.msg_label_pass, string))

    def msg_run_test_failure(self, string):
        if self.verbose:
            _println('{} {!s}'.format(self.msg_label_fail, string))

    def msg_test_success(self):
        _label = cli.colorize('[SUCCESS]', fore='GREEN')
        if self.verbose:
            _println('{} All assertions passed!'.format(_label))
        else:
            _print(' ' + _label + ' ')

    def msg_test_failure(self):
        _label = cli.colorize('[FAILURE]', fore='RED')
        if self.verbose:
            _println('{} One or more assertions FAILED!'.format(_label))
        else:
            _print(' ' + _label + ' ')

    @staticmethod
    def _center_with_fill(text):
        padded_text = '  ' + text + '  '
        return padded_text.center(TERMINAL_WIDTH, '=')

    def msg_overall_success(self):
        _println(cli.colorize(
            self._center_with_fill('ALL TESTS PASSED!'),
            fore='GREEN', style='BRIGHT'
        ))

    def msg_overall_failure(self):
        _println(cli.colorize(
            self._center_with_fill('SOME TESTS FAILED'),
            fore='RED', style='BRIGHT'
        ))

    def msg_overall_noop(self):
        _println(cli.colorize(
            self._center_with_fill('DID NOT RUN ANY TESTS'),
            fore='YELLOW', style='BRIGHT'
        ))

    def msg_overall_stats(self, count_total, count_skipped, count_success,
                          count_failure, elapsed_time):
        _println('\n')

        _skipped = '{} skipped'.format(count_skipped)
        if count_skipped > 0:
            _skipped = cli.colorize(_skipped, fore='YELLOW')

        _failure = '{} failed'.format(count_failure)
        if count_failure == 0:
            if count_total == 0:
                self.msg_overall_noop()
            else:
                self.msg_overall_success()
        else:
            self.msg_overall_failure()
            # Make the failed count red if any test failed.
            _failure = cli.colorize(_failure, fore='RED')

        _runtime = '{:.6f}s'.format(elapsed_time)

        _stats = 'Regression Test Summary:  {} total, {}, {} passed, {}  ' \
                 'in {} seconds'.format(count_total, _skipped,
                                        count_success, _failure, _runtime)

        _println()
        _println(_stats)
        _println('_' * TERMINAL_WIDTH)

    def msg_test_start(self, shortname, description):
        if self.verbose:
            _desc = cli.colorize(description, style='DIM')
            _println('\nRunning "{}"'.format(shortname))
            _println(_desc)
        else:
            maxlen = self.MAX_DESCRIPTION_LENGTH
            _desc_len = len(description)
            if _desc_len > maxlen:
                _desc = description[0:maxlen] + '..'
            else:
                _desc = description + ' '*(2 + maxlen - _desc_len)

            _colordesc = cli.colorize(_desc, style='DIM')
            _print('{:30.30s} {!s} '.format(shortname, _colordesc))

    def msg_test_skipped(self, shortname, description):
        if self.verbose:
            _println()
            _label = cli.colorize('[SKIPPED]', fore='YELLOW')
            _desc = cli.colorize(description, style='DIM')
            _println('{} "{!s}"'.format(_label, shortname))
            _println(_desc)
        else:
            maxlen = self.MAX_DESCRIPTION_LENGTH
            _desc_len = len(description)
            if _desc_len > maxlen:
                _desc = description[0:maxlen] + '..'
            else:
                _desc = description + ' '*(2 + maxlen - _desc_len)

            _colordesc = cli.colorize(_desc, style='DIM')
            _label = cli.colorize('[SKIPPED]', fore='YELLOW')
            _print('{:30.30s} {!s}  {} '.format(shortname, _colordesc, _label))

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
            _println(' ' * 10 + 'Runtime: {} (captured {}'.format(_time_1, _time_2))
        else:
            _println('  {} ({}'.format(_time_1, _time_2))

    def msg_captured_exception(self, exception_info):
        assert isinstance(exception_info, dict)
        if self.verbose:
            exception_str = exception_info.get('exception', '(N/A)')
            traceback_str = exception_info.get('traceback', '(N/A)')
            _println(
                cli.colorize('    CAUGHT TOP-LEVEL EXCEPTION    ', back='RED')
                + '  ' + cli.colorize(exception_str, fore='RED')
            )
            _println('Captured traceback:\n' + traceback_str)
        else:
            _println(' ' + cli.colorize('    CAUGHT TOP-LEVEL EXCEPTION    ',
                                        back='RED'))

    @staticmethod
    def msg_captured_stderr(stderr):
        _header = cli.colorize('Captured stderr:', fore='RED')
        _stderr = cli.colorize(stderr, fore='RED')
        _println('\n' + _header)
        _println(_stderr)

    @staticmethod
    def msg_captured_stdout(stdout):
        _println('\nCaptured stdout:')
        _println(stdout)


class RegressionTestSuite(object):
    def __init__(self, abspath, dirname, asserts, options, skip, description=None):
        assert isinstance(abspath, bytes)
        assert isinstance(dirname, bytes)
        self.abspath = abspath
        self.dirname = dirname
        self.asserts = asserts or dict()
        self.options = options or dict()
        self.should_skip = bool(skip)

        if description:
            self.description = types.force_string(description).strip()
        else:
            self.description = '(UNDESCRIBED)'

    @property
    def str_abspath(self):
        return types.force_string(self.abspath)

    @property
    def str_dirname(self):
        return types.force_string(self.dirname)

    def __hash__(self):
        return hash(
            (self.abspath, self.asserts, self.options, self.should_skip)
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return (
            self.abspath == other.abspath
            and self.asserts == other.asserts
            and self.options == other.options
            and self.should_skip == other.should_skip
        )

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.dirname < other.dirname
        return False

    def __gt__(self, other):
        return not self < other


class RegressionTestLoader(object):
    # Optional description of the test.
    BASENAME_DESCRIPTION = b'description'
    # The test is skipped if this file exists.
    BASENAME_SKIP = b'skip'
    # Options like those passed to the main() entry points.
    BASENAME_YAML_OPTIONS = b'options.yaml'
    # Test assertions.
    BASENAME_YAML_ASSERTS = b'asserts.yaml'

    def __init__(self, abspath):
        assert isinstance(abspath, bytes)
        self.test_abspath = abspath
        self.test_dirname = os.path.basename(enc.syspath(abspath))

    def load(self):
        setup_dict = self._get_test_setup_dict_from_files()
        loaded_regressiontest = RegressionTestSuite(
            abspath=self.test_abspath,
            dirname=self.test_dirname,
            asserts=setup_dict['asserts'],
            options=setup_dict['options'],
            skip=setup_dict['skiptest'],
            description=setup_dict['description']
        )
        return loaded_regressiontest

    def _get_test_setup_dict_from_files(self):
        description = self._load_file_description()
        assert isinstance(description, str)

        options = self._load_file_options()
        options = self._modify_options_input_paths(options)
        options = self._modify_options_config_path(options)
        assert isinstance(options, dict)

        asserts = self._load_file_asserts()
        assert isinstance(asserts, dict)

        should_skip = self._load_file_skip()
        assert isinstance(should_skip, bool)

        return {
            'asserts': asserts,
            'description': description,
            'options': options,
            'skiptest': should_skip
        }

    def _load_file_description(self):
        abspath_desc = self._joinpath(self.BASENAME_DESCRIPTION)
        description = read_plaintext_file(abspath_desc, ignore_errors=True)
        one_line_description = re.sub(r'\s+', ' ', description)
        return one_line_description.strip()

    def _load_file_asserts(self):
        abspath_asserts = self._joinpath(self.BASENAME_YAML_ASSERTS)
        try:
            asserts = disk.load_yaml_file(abspath_asserts)
        except exceptions.FilesystemError as e:
            raise RegressionTestError('Error reading asserts from file: '
                                      '"{!s}" :: {!s}'.format(abspath_asserts, e))

        if not asserts:
            log.warning('Read empty asserts from file: '
                        '"{!s}"'.format(abspath_asserts))
            asserts = dict()
        return asserts

    def _load_file_options(self):
        abspath_opts = self._joinpath(self.BASENAME_YAML_OPTIONS)
        try:
            options = disk.load_yaml_file(abspath_opts)
        except exceptions.FilesystemError as e:
            raise RegressionTestError('Error reading options from file: '
                                      '"{!s}" :: {!s}'.format(abspath_opts, e))
        if not options:
            log.warning('Read empty options from file: '
                        '"{!s}"'.format(abspath_opts))
            options = dict()
        return options

    def _load_file_skip(self):
        _abspath_skip = self._joinpath(self.BASENAME_SKIP)
        return bool(uu.file_exists(_abspath_skip))

    @staticmethod
    def _modify_options_input_paths(options):
        assert isinstance(options, dict)
        if 'input_paths' not in options:
            return options

        input_paths = options['input_paths']
        modified_options = dict(options)
        modified_options['input_paths'] = _expand_input_paths_variables(input_paths)
        return modified_options

    def _modify_options_config_path(self, options):
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
        assert isinstance(options, dict)

        config_path = types.force_string(options.get('config_path'))
        if not config_path:
            # Use default config.
            modified_path = uu.abspath_testconfig()
        elif config_path.startswith('$TESTFILES/'):
            # Substitute "variable".
            config_path_basename = config_path.replace('$TESTFILES/', '').strip()
            modified_path = uu.abspath_testfile(config_path_basename)
        elif config_path.startswith('$THISTEST/'):
            # Substitute "variable".
            config_path_basename = config_path.replace('$THISTEST/', '').strip()
            try:
                bytestring_basename = types.AW_PATHCOMPONENT(config_path_basename)
            except types.AWTypeError as e:
                raise RegressionTestError(e)

            modified_path = self._joinpath(bytestring_basename)
        else:
            # Assume absolute path.
            modified_path = config_path

        if not uu.file_exists(modified_path):
            raise RegressionTestError(
                'Invalid "config_path": "{!s}"'.format(config_path)
            )

        log.debug('Set config_path "{!s}" to "{!s}"'.format(config_path, modified_path))
        modified_options = dict(options)
        modified_options['config_path'] = enc.normpath(modified_path)
        return modified_options

    def _joinpath(self, leaf):
        assert isinstance(leaf, bytes)
        return os.path.join(
            enc.syspath(self.test_abspath), enc.syspath(leaf)
        )


def _expand_input_paths_variables(input_paths):
    """
    Replaces '$TESTFILES' with the full absolute path to the 'test_files'
    directory.
    For instance; '$TESTFILES/foo.txt' --> '$SRCROOT/test_files/foo.txt',
    where '$SRCROOT' is the full absolute path to the autonameow sources.
    """
    assert isinstance(input_paths, list)

    results = []
    for path in input_paths:
        if path == '$TESTFILES':
            # Substitute "variable".
            modified_path = uuconst.PATH_TEST_FILES
        elif path.startswith('$TESTFILES/'):
            # Substitute "variable".
            path_basename = path.replace('$TESTFILES/', '')
            modified_path = uu.abspath_testfile(path_basename)
        else:
            # Normalize path.
            try:
                bytestring_path = types.AW_PATH.normalize(path)
            except types.AWTypeError as e:
                raise RegressionTestError(
                    'Invalid path: "{!s}" :: {!s}'.format(path, e)
                )
            else:
                # NOTE(jonas): Iffy ad-hoc string coercion..
                modified_path = types.force_string(bytestring_path)

        # Allow non-existent but not empty paths.
        if not modified_path.strip():
            raise RegressionTestError(
                'Path is empty after processing: "{!s}"'.format(path)
            )

        results.append(modified_path)

    return results


class MockUI(object):
    """
    Mock view that should be functionally equivalent to the 'view' modules.

    Instances of this class should expose an interface that matches that of
    the 'view' module.  For instance, instead of:

        from core import view as ui
        ui.msg('foo')

    One should be able to do this:

        ui = MockUI()
        ui.msg('foo')

    NOTE(jonas): Would it be better to re-use library mocking functionality?
    """
    def __init__(self):
        self.mock_call_history = defaultdict(list)

    def __getattr__(self, item):
        # Argument 'item' is 'msg' if callers use mock like 'ui.msg('foo')'.
        if item == 'ColumnFormatter':
            # TODO: [TD0171] Separate logic from user interface.
            return cli.ColumnFormatter

        return lambda *args, **kwargs: self.mock_call_history[item].append((args, kwargs))


def fetch_mock_ui_messages(mock_ui):
    messages = list()
    for captured_msg_call in mock_ui.mock_call_history.get('msg', list()):
        text = ''.join(captured_msg_call[0])
        messages.append(text)

    return '\n'.join(messages)


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
        _from_basename = types.force_string(disk.basename(from_path))
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

        mock_ui = MockUI()

        with uu.capture_stdout() as stdout, uu.capture_stderr() as stderr:
            try:
                with Autonameow(self.opts, ui=mock_ui) as ameow:
                    # TODO: Mock 'FileRenamer' class instead of single method
                    assert hasattr(ameow, 'renamer')
                    assert hasattr(ameow.renamer, '_rename_file')
                    assert callable(ameow.renamer._rename_file)

                    # Monkey-patch method of 'FileRenamer' *instance*
                    ameow.renamer._rename_file = self.mock_rename_file

                    ameow.run()

                    # Store runtime recorded by the 'Autonameow' class.
                    self.captured_runtime_secs = ameow.runtime_seconds
            except Exception as e:
                # Capture "top-level" exception.
                typ, val, tb = sys.exc_info()
                exception_info = ''.join(traceback.format_exception(typ, val, tb))
                self.captured_exception = e
                self.captured_exception_traceback = exception_info

            self.captured_stdout = stdout.getvalue()
            self.captured_stderr = stderr.getvalue()

            # TODO: [hack] Pretty ugly but works for simple regex matching assertions.
            captured_mock_ui_messages = fetch_mock_ui_messages(mock_ui)
            self.captured_stdout += '\n' + captured_mock_ui_messages


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


def _testsuite_abspath(suite_basename):
    root_dir = get_regressiontests_rootdir()
    try:
        suite_abspath = os.path.join(
            enc.syspath(root_dir),
            enc.syspath(suite_basename)
        )
        normalized_suite_abspath = enc.normpath(suite_abspath)
    except Exception:
        raise AssertionError

    assert disk.isdir(normalized_suite_abspath)
    return normalized_suite_abspath


RE_REGRESSIONTEST_DIRNAME = re.compile(rb'\d{4}(_[\w]+)?')


def get_all_testsuite_dirpaths():
    root_dir = get_regressiontests_rootdir()
    return [
        _testsuite_abspath(d)
        for d in os.listdir(root_dir)
        if RE_REGRESSIONTEST_DIRNAME.match(d)
    ]


def load_regression_testsuites():
    all_loaded_tests = []

    testsuite_paths = get_all_testsuite_dirpaths()
    for suite_path in testsuite_paths:
        try:
            loaded_test = RegressionTestLoader(suite_path).load()
        except RegressionTestError as e:
            print('Unable to load test suite :: ' + str(e), file=sys.stderr)
        else:
            all_loaded_tests.append(loaded_test)

    return sorted(all_loaded_tests)


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


class RegexMatchingResult(object):
    def __init__(self, passed, assert_type, regex):
        self.passed = passed
        self.assert_type = assert_type
        self.regex = regex.pattern


def _load_assertion_regexes(asserts_dict, filedescriptor, assert_type):
    # TODO: Load and validate regexes before running the test!
    expressions = asserts_dict[filedescriptor].get(assert_type, []) or list()
    if not isinstance(expressions, list):
        assert expressions, (
            'Expected non-empty assertion expressions. '
            'Got {!s} :: {!s}'.format(type(expressions), expressions)
        )
        expressions = [expressions]

    regexes = []
    for expression in expressions:
        try:
            regexes.append(re.compile(expression, re.MULTILINE))
        except (ValueError, TypeError) as e:
            errormsg = 'Bad {} matches expression: "{!s}" -- {!s}'.format(
                filedescriptor, expression, e)
            raise RegressionTestError(errormsg)
    return regexes


def check_stdout_asserts(suite, captured_stdout):
    results = list()
    if not suite.asserts:
        return results
    if 'stdout' not in suite.asserts:
        return results

    # TODO: Load and validate regexes before running the test!
    should_match_regexes = _load_assertion_regexes(suite.asserts, 'stdout', 'matches')
    for regexp in should_match_regexes:
        # Pass if there is a match
        if regexp.search(captured_stdout):
            results.append(RegexMatchingResult(
                passed=True, assert_type='matches', regex=regexp
            ))
        else:
            results.append(RegexMatchingResult(
                passed=False, assert_type='matches', regex=regexp
            ))

    # TODO: Load and validate regexes before running the test!
    should_not_match_regexes = _load_assertion_regexes(suite.asserts, 'stdout', 'does_not_match')
    for regexp in should_not_match_regexes:
        # Pass if there is NOT a match
        if not regexp.search(captured_stdout):
            results.append(RegexMatchingResult(
                passed=True, assert_type='does_not_match', regex=regexp
            ))
        else:
            results.append(RegexMatchingResult(
                passed=False, assert_type='does_not_match', regex=regexp
            ))

    return results


def _commandline_args_for_testsuite(suite):
    """
    Converts a regression test to a list of command-line arguments.

    Given a loaded regression "test suite", it returns command-line components
    that would result in equivalent behaviour.
    The returned arguments would be used when invoking autonameow "manually"
    from the command-line.

    Args:
        suite: Regression "test suite" returned from 'load_regression_testsuites()',
               as an instance of 'RegressionTestSuite'.

    Returns:
        Command-line arguments as a list of Unicode strings.
    """
    # TODO: [hardcoded] Generate from 'autonameow/core/view/cli/options.py'.
    TESTOPTION_CMDARG_MAP = {
        'debug': '--debug',
        'dry_run': '--dry-run',
        'dump_config': '--dump-config',
        'dump_meowuris': '--dump-meowuris',
        'dump_options': '--dump-options',
        'list_all': '--list-all',
        'list_rulematch': '--list-rulematch',
        'mode_automagic': '--automagic',
        'mode_batch': '--batch',
        'mode_interactive': '--interactive',
        'mode_timid': '--timid',
        'quiet': '--quiet',
        'recurse_paths': '--recurse',
        'show_version': '--version',
        'verbose': '--verbose',
    }

    arguments = []
    suite_options = suite.options
    if suite_options:
        for opt, arg in TESTOPTION_CMDARG_MAP.items():
            if suite_options.get(opt):
                arguments.append(arg)

        # For more consistent output and easier testing, sort before adding
        # positional and "key-value"-type options.
        arguments = sorted(arguments)

        options_config_path = suite_options.get('config_path')
        if options_config_path:
            str_config_path = types.force_string(options_config_path)
            assert str_config_path != ''
            arguments.append("--config-path '{}'".format(str_config_path))

        options_input_paths = suite_options.get('input_paths')
        if options_input_paths:
            # Mark end of options, start of arguments (input paths)
            arguments.append('--')
            for p in options_input_paths:
                arguments.append("'{}'".format(p))

    return arguments


def commandline_for_testsuite(suite):
    """
    Converts a regression test to a equivalent command-line invocation string.

    Given a loaded regression "test suite", it returns a full command that
    could be pasted into a terminal to produce  behaviour equivalent to the
    given regression test suite.

    Args:
        suite: Regression "test suite" returned from 'load_regression_testsuites()',
               as an instance of 'RegressionTestSuite'.

    Returns:
        Full equivalent command-line as a Unicode string.
    """
    sanity.check_isinstance(suite, RegressionTestSuite)
    arguments = _commandline_args_for_testsuite(suite)
    argument_string = ' '.join(arguments)
    commandline = 'autonameow ' + argument_string
    return commandline.strip()


def glob_filter(glob, bytestring):
    """
    Evaluates if a string (suite basename) matches a given "glob".

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
    Evaluates if a string (suite basename) matches a given regular expression.
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


def print_test_info(tests, verbose):
    if verbose:
        cf = cli.ColumnFormatter()
        for t in tests:
            cf.addrow(t.str_dirname, t.description)
        print(cf)
    else:
        test_dirnames = [t.str_dirname for t in tests]
        print('\n'.join(test_dirnames))
