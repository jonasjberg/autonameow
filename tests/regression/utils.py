# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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
import pprint
import re
import shutil
import sys
import textwrap
import traceback
from collections import defaultdict
from collections import deque
from functools import lru_cache

import unit.constants as uuconst
import unit.utils as uu
from core import constants as C
from core import exceptions
from core.view import cli
from util import coercers
from util import disk
from util import encoding as enc


log = logging.getLogger('regression_runner')


TERMINAL_WIDTH, _ = shutil.get_terminal_size(fallback=(120, 48))


# TODO: [TD0121] Generate regression tests from manual invocations.


class RegressionTestError(exceptions.AutonameowException):
    """Error caused by an invalid regression test."""

    def __init__(self, msg='Error loading regression test', *args, **kwargs):
        # super().__init__(msg, *args, **kwargs)

        sourcefile = kwargs.get('sourcefile')
        if sourcefile is not None:
            self.sourcefile = enc.displayable_path(sourcefile)


def read_plaintext_file(filepath, ignore_errors=None):
    try:
        with open(filepath, 'r', encoding=C.DEFAULT_ENCODING) as fh:
            contents = fh.read()
    except (FileNotFoundError, UnicodeDecodeError) as e:
        if not ignore_errors:
            raise RegressionTestError(e)
        return ''
    else:
        return coercers.force_string(contents)


# Redefined print functions with disabled buffering.
_println = functools.partial(print, flush=True)
_print = functools.partial(print, flush=True, end='')


class TerminalReporter(object):
    def __init__(self, verbose=False, print_stdout=False, print_stderr=False):
        self.verbose = verbose
        self.print_stdout = print_stdout
        self.print_stderr = print_stderr

        self.MAX_DESCRIPTION_LENGTH = TERMINAL_WIDTH - 75
        assert self.MAX_DESCRIPTION_LENGTH > 0, 'Terminal is not wide enough ..'

        self.msg_label_assert_pass = cli.colorize('PASS', fore='GREEN')
        self.msg_label_assert_fail = cli.colorize('FAIL', fore='RED')
        self.msg_label_suite_success = cli.colorize('[SUCCESS]', fore='GREEN')
        self.msg_label_suite_failure = cli.colorize('[FAILURE]', fore='RED')
        self.msg_label_suite_skipped = cli.colorize('[SKIPPED]', fore='YELLOW')

        # Unicode character "ballot box with check" (U+2611)
        self.msg_mark_history_pass = cli.colorize('\u2611', fore='GREEN')
        # Unicode character "ballot box with x" (U+2612)
        self.msg_mark_history_fail = cli.colorize('\u2612', fore='RED')
        # Unicode character "ballot box" (U+2610)
        self.msg_mark_history_skip = cli.colorize('\u2610', fore='YELLOW')
        self.msg_mark_history_unknown = self.msg_mark_history_skip

    def msg(self, strng):
        if self.verbose:
            _println(strng)

    def msg_run_test_success(self, strng):
        if self.verbose:
            _println('{} {!s}'.format(self.msg_label_assert_pass, strng))

    def msg_run_test_failure(self, strng):
        if self.verbose:
            _println('{} {!s}'.format(self.msg_label_assert_fail, strng))

    def msg_testsuite_success(self):
        if self.verbose:
            _print(self.msg_label_suite_success + ' Suite passed all assertions')
        else:
            _print(' ' + self.msg_label_suite_success + ' ')

    def msg_testsuite_failure(self, failure_count):
        if self.verbose:
            _print(self.msg_label_suite_failure + ' Suite failed {} assertions'.format(failure_count))
        else:
            _print(' ' + self.msg_label_suite_failure + ' ')

    def msg_testsuite_skipped(self):
        if self.verbose:
            _print(self.msg_label_suite_skipped)
        else:
            _print(' ' + self.msg_label_suite_skipped + ' ')

    def msg_testsuite_history(self, history):
        if self.verbose:
            NUM_HISTORY_ENTRIES = 59
        else:
            NUM_HISTORY_ENTRIES = 5

        padded_history = list(history)
        while len(padded_history) < NUM_HISTORY_ENTRIES:
            padded_history.append(RunResultsHistory.RESULT_UNKNOWN)

        if self.verbose:
            _print('\nHistory: ')

        for result in padded_history[:NUM_HISTORY_ENTRIES]:
            if result == RunResultsHistory.RESULT_FAIL:
                _print(self.msg_mark_history_fail)
            elif result == RunResultsHistory.RESULT_PASS:
                _print(self.msg_mark_history_pass)
            elif result == RunResultsHistory.RESULT_SKIP:
                _print(self.msg_mark_history_skip)
            elif result == RunResultsHistory.RESULT_UNKNOWN:
                _print(self.msg_mark_history_unknown)
            else:
                log.warning('Invalid testuite history result: %s', result)
                _print(self.msg_mark_history_unknown)

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

        str_skipped = '{} skipped'.format(count_skipped)
        if count_skipped > 0:
            str_skipped = cli.colorize(str_skipped, fore='YELLOW')

        str_failure = '{} failed'.format(count_failure)
        if count_failure == 0:
            if count_total == 0:
                self.msg_overall_noop()
            else:
                self.msg_overall_success()
        else:
            self.msg_overall_failure()
            # Make the failed count red if any test failed.
            str_failure = cli.colorize(str_failure, fore='RED')

        str_runtime = '{:.6f} seconds'.format(elapsed_time)
        str_stats = 'Regression Test Summary:  {} total, {}, {} passed, {}  ' \
                    'in {}'.format(count_total, str_skipped, count_success,
                                   str_failure, str_runtime)
        _println()
        _println(str_stats)
        _println('_' * TERMINAL_WIDTH)

    def _format_description(self, description):
        def __colorize(s):
            return cli.colorize(s, style='DIM')

        if self.verbose:
            normalized_description = normalize_description_whitespace(description)
            return __colorize(normalized_description)

        else:
            single_line_description = collapse_all_whitespace(description)
            MAXLEN = self.MAX_DESCRIPTION_LENGTH

            description_len = len(single_line_description)
            if description_len > MAXLEN:
                fixed_width_description = single_line_description[0:MAXLEN] + '..'
            else:
                padding_len = 2 + MAXLEN - description_len
                fixed_width_description = single_line_description + ' ' * padding_len

            return __colorize(fixed_width_description)

    def msg_testsuite_start(self, shortname, description):
        formatted_description = self._format_description(description)

        if self.verbose:
            message = '\nRunning "{}"'.format(shortname)
            colorized_message = cli.colorize(message, style='BRIGHT')
            _println(colorized_message)
            _println(formatted_description)
        else:
            _print('{:28.28s} {!s} '.format(shortname, formatted_description))

    def msg_test_skipping(self, shortname, description):
        formatted_description = self._format_description(description)

        if self.verbose:
            message = '\nSkipping "{}"'.format(shortname)
            colorized_message = cli.colorize(message, style='BRIGHT')
            _println(colorized_message)
            _println(formatted_description)
        else:
            _print('{:28.28s} {!s} '.format(shortname, formatted_description))

    def msg_testsuite_runtime(self, elapsed_time, captured_time, time_delta_ms=None):
        if captured_time:
            str_captured = '{:.3f}s)'.format(captured_time)
        else:
            str_captured = 'N/A)'

        if elapsed_time:
            str_elapsed = '{:.3f}s'.format(elapsed_time)
        else:
            str_elapsed = 'N/A'

        if time_delta_ms is not None:
            assert isinstance(time_delta_ms, float)

            # Positive time delta means this run was slower.
            if time_delta_ms > 0:
                time_delta_color = 'RED'
            else:
                time_delta_color = 'GREEN'

            formatted_time_delta = _format_ms_time_delta(time_delta_ms)
            if abs(time_delta_ms) > 50:
                # Huge difference, highlight color to stand out.
                str_delta = cli.colorize(formatted_time_delta, fore=time_delta_color, style='BRIGHT')
            elif abs(time_delta_ms) > 25:
                # Noticeably different, use normal color.
                str_delta = cli.colorize(formatted_time_delta, fore=time_delta_color)
            else:
                str_delta = cli.colorize(formatted_time_delta, fore=time_delta_color, style='DIM')
        else:
            str_delta = cli.colorize('   N/A', style='DIM')

        str_time_1 = '{:6.6s}'.format(str_elapsed)
        str_time_2 = '{:7.7s}'.format(str_captured)
        str_time_3 = '{:>s}'.format(str_delta)
        if self.verbose:
            _println('\nRuntime: {} (captured {}  Previous runtime delta: {}'.format(str_time_1, str_time_2, str_time_3))
        else:
            _println('  {} ({} {}'.format(str_time_1, str_time_2, str_time_3))

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
            _println(' '
                     + cli.colorize('      CAUGHT TOP-LEVEL EXCEPTION       ',
                                    back='RED'))

    def msg_captured_stderr(self, stderr):
        if not self.print_stderr:
            return

        _header = cli.colorize('Captured stderr:', fore='RED')
        _stderr = cli.colorize(stderr, fore='RED')
        _println('\n' + _header)
        _println(_stderr)

    def msg_captured_stdout(self, stdout):
        if not self.print_stdout:
            return

        _println('\nCaptured stdout:')
        _println(stdout)


def _format_ms_time_delta(time_delta):
    time_delta = float(time_delta)

    if abs(time_delta) >= 1000:
        # Above or equal to 1 second
        str_delta = '{:.2f} s'.format(time_delta / 1000)
    else:
        # Milliseconds
        str_delta = '{:.2f}ms'.format(time_delta)

    if time_delta > 0:
        str_delta = '+' + str_delta

    result = '{0: >9}'.format(str(str_delta))
    return result


class RegressionTestSuite(object):
    def __init__(self, abspath, dirname, asserts, options, skip, description=None):
        assert isinstance(abspath, bytes)
        assert isinstance(dirname, bytes)
        self.abspath = abspath
        self.dirname = dirname
        self.asserts = asserts or dict()
        self.options = options or dict()
        self.should_skip = bool(skip)
        self.description = description or '(UNDESCRIBED)'

    @property
    def str_abspath(self):
        return coercers.force_string(self.abspath)

    @property
    def str_dirname(self):
        return coercers.force_string(self.dirname)

    def __hash__(self):
        return hash(
            (self.abspath, self.dirname)
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
        return description.strip()

    def _load_file_asserts(self):
        abspath_asserts = self._joinpath(self.BASENAME_YAML_ASSERTS)
        try:
            asserts = disk.load_yaml_file(abspath_asserts)
        except exceptions.FilesystemError as e:
            raise RegressionTestError(e, sourcefile=abspath_asserts)

        if not asserts:
            log.warning('Read empty asserts from file: "%s"', abspath_asserts)
            asserts = dict()

        return asserts

    def _load_file_options(self):
        abspath_opts = self._joinpath(self.BASENAME_YAML_OPTIONS)

        try:
            options = disk.load_yaml_file(abspath_opts)
        except exceptions.FilesystemError as e:
            raise RegressionTestError(e, sourcefile=abspath_opts)

        if not options:
            log.warning('Read empty options from file: "%s"', abspath_opts)
            options = dict()

        input_paths = options.get('input_paths')
        if input_paths:
            if (not isinstance(input_paths, list) or
                    any(not p or not isinstance(p, str) for p in input_paths)):
                raise RegressionTestError(
                    'Expected "input_paths" to be a list of non-empty strings.',
                    sourcefile=abspath_opts,
                )

        return options

    def _load_file_skip(self):
        _abspath_skip = self._joinpath(self.BASENAME_SKIP)
        return bool(uu.file_exists(_abspath_skip))

    @staticmethod
    def _modify_options_input_paths(options):
        assert isinstance(options, dict)

        input_paths = options.get('input_paths')
        if not input_paths:
            return options

        modified_options = dict(options)
        modified_options['input_paths'] = _expand_input_paths_variables(input_paths)
        return modified_options

    def _modify_options_config_path(self, options):
        """
        Modifies the 'config_path' entry in the options dict.

        If the 'config_path' entry..

          * .. is missing, the path of the default (unit test) config is used.

               --> 'config_path': (Path to the default config)

          * .. starts with '$SAMPLEFILES/', the full absolute path to the
               'samplefiles' directory is inserted in place of '$SAMPLEFILES/'.

                   'config_path': '$SAMPLEFILES/config.yaml'
               --> 'config_path': '$SRCROOT/tests/samplefiles/config.yaml'

          * .. starts with '$THISTEST/', the full absolute path to the current
               regression test directory is inserted in place of '$THISTEST/'.

                   'config_path': '$THISTEST/config.yaml'
               --> 'config_path': 'self.abspath/config.yaml'
        """
        assert isinstance(options, dict)

        config_path = coercers.force_string(options.get('config_path'))
        if not config_path:
            # Use default config.
            modified_path = uu.samplefile_config_abspath()
        elif config_path.startswith('$SAMPLEFILES/'):
            # Substitute "variable".
            config_path_basename = config_path.replace('$SAMPLEFILES/', '').strip()
            modified_path = uu.samplefile_abspath(config_path_basename)
        elif config_path.startswith('$THISTEST/'):
            # Substitute "variable".
            config_path_basename = config_path.replace('$THISTEST/', '').strip()
            try:
                bytestring_basename = coercers.AW_PATHCOMPONENT(config_path_basename)
            except coercers.AWTypeError as e:
                raise RegressionTestError(e)

            modified_path = self._joinpath(bytestring_basename)
        else:
            # Assume absolute path.
            modified_path = config_path

        if not uu.file_exists(modified_path):
            raise RegressionTestError(
                'File at "config_path" does not exist: "{!s}"'.format(config_path)
            )

        log.debug('Set config_path "%s" to "%s"', config_path, modified_path)
        modified_options = dict(options)
        modified_options['config_path'] = enc.normpath(modified_path)
        return modified_options

    def _joinpath(self, leaf):
        assert isinstance(leaf, bytes)
        return os.path.join(
            enc.syspath(self.test_abspath), enc.syspath(leaf)
        )


def collapse_all_whitespace(s):
    assert isinstance(s, str)
    normalized_string = re.sub(r'\s+', ' ', s)
    return normalized_string.strip()


def normalize_description_whitespace(s):
    """
    Fixes up whitespace in multi-line text.

    Intended to be used to clean up test suite descriptions.
    Removes messy whitespace, such as tabs. Replaces single line breaks (E.G.
    hard wrapped column width) with spaces.
    Replaces more than two consecutive new lines with a single new line, to
    keep some of the spacing from the original text.
    """
    assert isinstance(s, str)

    def _replace_single_linebreak(_match):
        _match_group = _match.group()
        _match_first = _match_group[0]
        _match_last = _match_group[-1]
        if '\n' not in (_match_first, _match_last):
            _match_without_newline = _match_first + ' ' + _match_last
            return _match_without_newline

    cleaned = re.sub(r'[ \t\r\f\v]', ' ', s)
    removed_linebreaks = re.sub(r'.\n.', _replace_single_linebreak, cleaned)
    collapsed_newlines = re.sub(r'\n{2,}', '\n', removed_linebreaks, re.MULTILINE)
    normalized = collapsed_newlines.replace('  ', ' ').strip()
    return normalized


def _expand_input_paths_variables(input_paths):
    """
    Replaces '$SAMPLEFILES' with the full absolute path to the 'samplefiles'
    directory.
    For instance; '$SAMPLEFILES/foo.txt' --> '$SRCROOT/tests/samplefiles/foo.txt',
    where '$SRCROOT' is the full absolute path to the autonameow sources.
    """
    assert isinstance(input_paths, list)

    results = list()
    for path in input_paths:
        if path == '$SAMPLEFILES':
            # Substitute "variable".
            modified_path = uuconst.DIRPATH_SAMPLEFILES
        elif path.startswith('$SAMPLEFILES/'):
            # Substitute "variable".
            path_basename = path.replace('$SAMPLEFILES/', '')
            modified_path = uu.samplefile_abspath(path_basename)
        else:
            # Normalize path.
            try:
                bytestring_path = coercers.coerce_to_normalized_path(path)
            except coercers.AWTypeError as e:
                raise RegressionTestError(
                    'Invalid path: "{!s}" :: {!s}'.format(path, e)
                )
            else:
                # NOTE(jonas): Iffy ad-hoc string coercion..
                modified_path = coercers.force_string(bytestring_path)

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
        # Dictionary keyed by members 'ui' storing call arguments.
        # Using a new MockUI once like this:
        #
        #     ui.msg('foo', bar=42)
        #
        # Stores the following:
        #
        #     mock_call_history == {
        #         'msg': [
        #             (('foo',), {'bar': 42})
        #         ]
        #     }
        #
        self.mock_call_history = defaultdict(list)

    def __getattr__(self, item):
        # Argument 'item' is 'msg' if callers use mock like 'ui.msg('foo')'.
        if item == 'ColumnFormatter':
            # TODO: [TD0171] Separate logic from user interface.
            return cli.ColumnFormatter
        if item == 'colorize':
            # Pass-through string unchanged.
            return lambda x, **kwargs: x
        if item == 'msg_columnate':
            # TODO: [TD0171] Separate logic from user interface.
            return cli.msg_columnate

        return lambda *args, **kwargs: self.mock_call_history[item].append((args, kwargs))


def fetch_mock_ui_messages(mock_ui):
    messages = list()
    for captured_msg_call in mock_ui.mock_call_history.get('msg', list()):
        try:
            text = ''.join(captured_msg_call[0])
        except TypeError:
            raise AssertionError(str(captured_msg_call))
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

    def mock_rename_file(self, from_path, dest_basename):
        # TODO: [hack] Mocking is too messy to be reliable ..
        # NOTE(jonas): Iffy ad-hoc string coercion..
        str_from_basename = coercers.force_string(disk.basename(from_path))
        str_dest_basename = coercers.force_string(dest_basename)

        # Check for collisions that might cause erroneous test results.
        if str_from_basename in self.captured_renames:
            existing_dest_basename = self.captured_renames[str_from_basename]
            raise RegressionTestError(
                'Already captured rename: "{!s}" -> "{!s}" (Now "{!s}")'.format(
                    str_from_basename, existing_dest_basename, str_dest_basename
                )
            )
        self.captured_renames[str_from_basename] = str_dest_basename

    def __call__(self):
        # TODO: [TD0158] Evaluate assertions of "skipped renames".
        from core.autonameow import Autonameow

        mock_ui = MockUI()

        with uu.capture_stdout() as stdout, uu.capture_stderr() as stderr:
            try:
                with Autonameow(self.opts, ui=mock_ui) as ameow:
                    # TODO: [hack] Mocking is too messy to be reliable ..
                    # TODO: Mock 'FileRenamer' class instead of single method?
                    #       Requires reworking the 'FileRenamer' class.
                    assert hasattr(ameow, 'renamer')
                    assert hasattr(ameow.renamer, '_rename_file')
                    assert callable(ameow.renamer._rename_file)

                    # Monkey-patch method of 'FileRenamer' *instance*
                    ameow.renamer._rename_file = self.mock_rename_file

                    ameow.run()
                    self.captured_exitcode = ameow.exit_code

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
    all_loaded_tests = list()

    testsuite_paths = get_all_testsuite_dirpaths()
    for suite_path in testsuite_paths:
        loader = RegressionTestLoader(suite_path)
        try:
            loaded_test = loader.load()
        except RegressionTestError as e:
            log.error('Unable to load test suite "%s"',
                      enc.displayable_path(loader.test_dirname))
            if hasattr(e, 'sourcefile'):
                log.error('Problematic file: "%s"', e.sourcefile)
            log.error(e)
        else:
            all_loaded_tests.append(loaded_test)

    return sorted(all_loaded_tests)


def check_renames(actual, expected):
    assert isinstance(actual, dict)
    assert isinstance(expected, dict)

    if not actual and not expected:
        # Did not expect anything and nothing happened.
        return True
    elif actual and not expected:
        # Something unexpectedly happened.
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

    regexes = list()
    for expression in expressions:
        try:
            regexes.append(re.compile(expression, re.MULTILINE))
        except (ValueError, TypeError) as e:
            error_msg = 'Bad {} matches expression: "{!s}" -- {!s}'.format(
                filedescriptor, expression, e
            )
            raise RegressionTestError(error_msg)

    return regexes


def check_stdout_asserts(suite, captured_stdout):
    results = list()

    if not suite.asserts or 'stdout' not in suite.asserts:
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


@lru_cache()
def _suite_option_to_cli_option_mapping():
    from core.view.cli.options import get_optional_argparser_options
    argparser_options = get_optional_argparser_options()
    return {
        option.dest: option.long for option in argparser_options
    }


def _commandline_args_for_testsuite(testsuite):
    """
    Converts a regression testsuite to a list of command-line arguments.

    Returns positional command-line argument strings that would result in
    equivalent behaviour as the given regression test suite, if used when
    executing autonameow from the command-line.

    Args:
        testsuite: Testsuite from which to produce equivalent command-line
                   arguments, as an instance of 'RegressionTestSuite'.

    Returns:
        Positional command-line arguments as a list of Unicode strings.
    """
    testsuite_options = testsuite.options
    assert isinstance(testsuite_options, dict)
    if not testsuite_options:
        return list()

    # NOTE(jonas): Assumes all options are booleans --- any undefined options
    #              are treated as if they were defined with the value False.
    arguments = [
        argument
        for option, argument in _suite_option_to_cli_option_mapping().items()
        if testsuite_options.get(option)
    ]

    # For more consistent output and easier testing, sort before adding
    # positional and "key-value"-type options.
    arguments = sorted(arguments)

    config_path = testsuite_options.get('config_path')
    if config_path:
        str_config_path = coercers.force_string(config_path)
        assert str_config_path, repr(config_path)
        arguments.append("--config-path '{}'".format(str_config_path))

    input_paths = testsuite_options.get('input_paths')
    if input_paths:
        # Mark end of options, start of arguments (input paths)
        arguments.append('--')
        arguments.extend("'{}'".format(p) for p in input_paths)

    return arguments


def commandline_for_testsuite(testsuite):
    """
    Converts a regression test to a equivalent command-line invocation string.

    Given a loaded regression "test suite", it returns a full command that
    could be pasted into a terminal to produce  behaviour equivalent to the
    given regression test suite.

    Args:
        testsuite: A "test suite" returned from 'load_regression_testsuites()',
                   as an instance of 'RegressionTestSuite'.

    Returns:
        Full equivalent command-line as a Unicode string.
    """
    assert isinstance(testsuite, RegressionTestSuite)

    arguments = _commandline_args_for_testsuite(testsuite)
    commandline = 'autonameow ' + ' '.join(arguments)
    return commandline.strip()


def glob_filter(glob, bytestring):
    """
    Evaluates if a bytestring (suite basename) matches a given "glob".

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
        bytes_glob = coercers.AW_PATHCOMPONENT(glob)
    except coercers.AWTypeError as e:
        raise RegressionTestError(e)

    regexp = bytes_glob.replace(b'*', b'.*')
    if regexp.startswith(b'!'):
        regexp = regexp[1:]
        return not bool(re.match(regexp, bytestring))

    return bool(re.match(regexp, bytestring))


def regexp_filter(expression, bytestring):
    """
    Evaluates a bytestring (suite basename) against a given regular expression.
    """
    if not isinstance(bytestring, bytes):
        raise RegressionTestError(
            'Expected type bytes for argument "bytestring". '
            'Got {} ({!s})'.format(type(bytestring), bytestring)
        )
    try:
        # Coercing to "AW_PATHCOMPONENT" because there is no "AW_BYTES".
        bytes_expr = coercers.AW_PATHCOMPONENT(expression)
    except coercers.AWTypeError as e:
        raise RegressionTestError(e)

    try:
        regexp = re.compile(bytes_expr)
    except (TypeError, ValueError, re.error) as e:
        raise RegressionTestError(e)

    return bool(regexp.match(bytestring))


def print_testsuite_info(testsuites, verbose):
    textwrapper = textwrap.TextWrapper(
        width=TERMINAL_WIDTH,
        initial_indent="  ",
        subsequent_indent="",
        expand_tabs=True,
        replace_whitespace=True,
        fix_sentence_endings=True,
        break_long_words=True,
        drop_whitespace=True,
        break_on_hyphens=True,
        tabsize=4,
    )

    def _bold(s):
        return cli.colorize(s, style='BRIGHT')

    def _stringify_dict(d):
        return pprint.pformat(
            d,
            indent=2,
            compact=False,
            width=TERMINAL_WIDTH,
        )

    lines = list()

    if verbose:
        for testsuite in testsuites:
            lines.append(_bold('  TESTSUITE: ') + testsuite.str_dirname)
            lines.append(_bold('    SKIPPED: ') + ('Yes' if testsuite.should_skip else 'No'))
            lines.append(_bold('DESCRIPTION:'))
            lines.append('\n'.join(textwrapper.wrap(testsuite.description)))
            lines.append(_bold('    ASSERTS:'))
            lines.append(_stringify_dict(testsuite.asserts))
            lines.append(_bold('    OPTIONS:'))
            lines.append(_stringify_dict(testsuite.options))
            lines.append('\n')
    else:
        lines = [t.str_dirname for t in testsuites]

    print('\n'.join(lines))


class RunResultsHistory(object):
    # Enum-like
    RESULT_PASS = 'pass'
    RESULT_SKIP = 'skip'
    RESULT_FAIL = 'fail'
    RESULT_UNKNOWN = 'unknown'

    # TODO: [hack][cleanup] Refactor ..
    # TODO: [incomplete] Only the "Enum-like" is used!
    def __init__(self, maxlen):
        assert isinstance(maxlen, int)
        self._run_results = deque(maxlen=maxlen)

    def add(self, run_results):
        self._run_results.appendleft(run_results)

    def __len__(self):
        return len(self._run_results)

    def __getitem__(self, item):
        run_results_list = list(self._run_results)
        return run_results_list[item]
