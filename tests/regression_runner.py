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

import os
import sys
import time

from core import constants as C
from core import (
    types,
    ui
)
from core.persistence import get_persistence
from regression_utils import (
    AutonameowWrapper,
    check_renames,
    load_regressiontests,
    TerminalReporter
)


msg_label_pass = ui.colorize('P', fore='GREEN')
msg_label_fail = ui.colorize('F', fore='RED')


VERBOSE = False
PERSISTENCE_BASENAME_PREFIX = '.regressionrunner'
_this_dir = os.path.abspath(os.path.dirname(__file__))
PERSISTENCE_DIR_ABSPATH = types.AW_PATH.normalize(_this_dir)


def run_test(test):
    opts = test.get('options')
    expect_exitcode = test['asserts'].get('exit_code', None)
    expect_renames = test['asserts'].get('renames', {})

    aw = AutonameowWrapper(opts)
    aw()
    if aw.captured_exception:
        print(' '
              + ui.colorize('    CAUGHT TOP-LEVEL EXCEPTION    ', back='RED'))
        if VERBOSE:
            print(aw.captured_exception)

        # TODO: Fix magic number return for exceptions for use when formatting.
        return -10, None, aw.captured_stdout, aw.captured_stderr

    captured_runtime = aw.captured_runtime_secs
    failures = 0

    def _msg_run_test_failure(msg):
        if VERBOSE:
            print('{} {!s}'.format(msg_label_fail, msg))

    def _msg_run_test_success(msg):
        if VERBOSE:
            print('{} {!s}'.format(msg_label_pass, msg))

    def _msg(msg):
        if VERBOSE:
            print(msg)

    if expect_exitcode is not None:
        actual_exitcode = aw.captured_exitcode
        if actual_exitcode == expect_exitcode:
            _msg_run_test_success('Exit code is {} as expected'.format(actual_exitcode))
        else:
            _msg_run_test_failure(
                'Expected exit code {!s} but got {!s}'.format(
                    expect_exitcode, actual_exitcode
                )
            )
            failures += 1

    actual_renames = aw.captured_renames
    if check_renames(actual_renames, expect_renames):
        _msg_run_test_success('Renamed {} files as expected'.format(len(actual_renames)))

        for _in, _out in actual_renames.items():
            _msg_run_test_success('Renamed "{!s}" -> "{!s}"'.format(_in, _out))
    else:
        failures += 1
        _msg_run_test_failure(
            'Renames differ. Expected {} files to be renamed. '
            '{} files were renamed.'.format(len(expect_renames), len(actual_renames))
        )

        if expect_renames:
            if not actual_renames:
                _msg('  Expected {} files to be renamed but none were!'.format(len(expect_renames)))
                for _in, _out in expect_renames.items():
                    _msg('  Expected rename:  "{!s}" -> "{!s}"'.format(_in, _out))
            else:
                # Expected renames and got renames.
                for _expect_in, _expect_out in expect_renames.items():
                    if _expect_in not in actual_renames:
                        _msg('  Not renamed. Expected:  "{!s}" -> "{!s}"'.format(_expected_in, _expected_out))
                    else:
                        assert _expect_in in actual_renames
                        _actual_out = actual_renames.get(_expect_in)
                        if _actual_out != _expect_out:
                            _msg('  New file name differs from expected file name.')
                            _msg('  Expected: "{!s}"'.format(_expect_out))
                            _msg('  Actual:   "{!s}"'.format(_actual_out))

                for _actual_in, _actual_out in actual_renames.items():
                    if _actual_in not in expect_renames:
                        _msg('  Unexpected rename:  "{!s}" -> "{!s}"'.format(_actual_in, _actual_out))
                    else:
                        assert _actual_in in expect_renames
                        _expect_out = expect_renames.get(_actual_in)
                        if _expect_out != _actual_out:
                            _msg('  New file name differs from expected file name.')
                            _msg('  Expected: "{!s}"'.format(_expect_out))
                            _msg('  Actual:   "{!s}"'.format(_actual_out))
        else:
            if actual_renames:
                _msg('  Did not expect any files to be renamed but {} were!'.format(len(actual_renames)))
                for _in, _out in actual_renames.items():
                    _msg('  Unexpected rename:  "{!s}" -> "{!s}"'.format(_in, _out))
            else:
                # All good
                pass

    return failures, captured_runtime, aw.captured_stdout, aw.captured_stderr


def write_failed_tests(tests):
    p = get_persistence(file_prefix=PERSISTENCE_BASENAME_PREFIX,
                        persistence_dir_abspath=PERSISTENCE_DIR_ABSPATH)
    if p:
        p.set('lastrun', {'failed': tests})


def load_failed_tests():
    p = get_persistence(file_prefix=PERSISTENCE_BASENAME_PREFIX,
                        persistence_dir_abspath=PERSISTENCE_DIR_ABSPATH)
    if p:
        try:
            lastrun = p.get('lastrun')
        except KeyError:
            pass
        else:
            if lastrun and isinstance(lastrun, dict):
                return lastrun.get('failed', [])
    return []


def run_regressiontests(tests, print_stderr, print_stdout):
    reporter = TerminalReporter(VERBOSE)
    count_total = len(tests)
    count_success = 0
    count_failure = 0
    count_skipped = 0
    should_abort = False

    failed_tests = []

    for test in tests:
        if should_abort:
            count_skipped += count_total - count_success - count_failure
            break

        _dirname = types.force_string(test.get('test_dirname', '(?)'))
        _description = test.get('description', '(UNDESCRIBED)')
        if test.get('skiptest'):
            reporter.msg_test_skipped(_dirname, _description)
            reporter.msg_test_runtime(None, None)
            count_skipped += 1
            continue

        reporter.msg_test_start(_dirname, _description)

        failures = 0
        captured_time = None
        captured_stderr = ''
        captured_stdout = ''
        start_time = time.time()
        try:
            (failures, captured_time, captured_stdout,
             captured_stderr) = run_test(test)
        except KeyboardInterrupt:
            print('\nReceived keyboard interrupt. Skipping remaining tests ..')
            should_abort = True

        elapsed_time = time.time() - start_time

        if failures == -10:
            if print_stderr and captured_stderr:
                reporter.msg_captured_stderr(captured_stderr)
            if print_stdout and captured_stdout:
                reporter.msg_captured_stdout(captured_stdout)

            # TODO: Fix formatting of failure due to top-level exception error.
            count_failure += 1
            failed_tests.append(test)
            continue

        if failures == 0:
            reporter.msg_test_success()
            count_success += 1
        elif failures > 0:
            reporter.msg_test_failure()
            count_failure += 1
            failed_tests.append(test)

        reporter.msg_test_runtime(elapsed_time, captured_time)

        if print_stderr and captured_stderr:
            reporter.msg_captured_stderr(captured_stderr)
        if print_stdout and captured_stdout:
            reporter.msg_captured_stdout(captured_stdout)

    reporter.msg_overall_stats(count_total, count_skipped, count_success,
                               count_failure)

    if not should_abort:
        # Store failed tests only if all tests were executed.
        # Otherwise all tests would have to be re-run in order to "catch"
        # the failed tests, if re-running the failed tests and aborting
        # before completion..
        write_failed_tests(failed_tests)


def main(args):
    _description = '{} {} -- regression test suite runner'.format(
        C.STRING_PROGRAM_NAME, C.STRING_PROGRAM_VERSION)
    _epilog = 'Project website:  {}'.format(C.STRING_REPO_URL)

    parser = ui.cli.get_argparser(description=_description, epilog=_epilog)
    parser.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='Enables verbose mode, prints additional information.'
    )
    parser.add_argument(
        '--last-failed',
        dest='run_lastfailed',
        action='store_true',
        default=False,
        help='Run only the test cases that failed during the last completed '
             'run, or all if none failed.'
    )
    parser.add_argument(
        '--stderr',
        dest='print_stderr',
        action='store_true',
        default=False,
        help='Print captured stderr.'
    )
    parser.add_argument(
        '--stdout',
        dest='print_stdout',
        action='store_true',
        default=False,
        help='Print captured stdout.'
    )

    opts = parser.parse_args(args)

    # TODO: [TD0124] Add option (script?) to get command-line of failed tests.

    global VERBOSE
    if opts.verbose:
        VERBOSE = True
    else:
        VERBOSE = False

    loaded_tests = load_regressiontests()
    print('Loaded {} regression test(s) ..'.format(len(loaded_tests)))
    if not loaded_tests:
        return

    if opts.run_lastfailed:
        _failed_lastrun = load_failed_tests()
        if _failed_lastrun:
            # TODO: Improve comparing regression test cases.
            # Fails if any option is modified. Compare only directory basenames?
            tests_to_run = [t for t in loaded_tests if t in _failed_lastrun]
            print('Running {} of the {} test case(s) that failed during the '
                  'last completed run ..'.format(len(tests_to_run),
                                                 len(_failed_lastrun)))
        else:
            tests_to_run = list(loaded_tests)
            print('Running all {} test case(s) as None failed during the '
                  'last completed run ..'.format(len(tests_to_run)))
    else:
        tests_to_run = list(loaded_tests)
        print('Running {} test case(s) ..'.format(len(tests_to_run)))

    print()
    run_regressiontests(tests_to_run,
                        print_stderr=bool(opts.print_stderr),
                        print_stdout=bool(opts.print_stdout))


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print('\nReceived keyboard interrupt. Exiting ..')
        sys.exit(0)
