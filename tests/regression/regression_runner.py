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
import os
import re
import sys
import time

from core import constants as C
from core import (
    types,
    ui
)
from core.persistence import get_persistence
from regression.utils import (
    AutonameowWrapper,
    check_renames,
    commandline_for_testcase,
    load_regressiontests,
    TerminalReporter
)


VERBOSE = False
_this_dir = os.path.abspath(os.path.dirname(__file__))
PERSISTENCE_DIR_ABSPATH = types.AW_PATH.normalize(_this_dir)
PERSISTENCE_BASENAME_PREFIX = '.regressionrunner'


log = logging.getLogger('regression_runner')
msg_label_pass = ui.colorize('P', fore='GREEN')
msg_label_fail = ui.colorize('F', fore='RED')


def run_test(test):
    opts = test.get('options')
    expect_exitcode = test['asserts'].get('exit_code', None)
    expect_renames = test['asserts'].get('renames', {})
    expect_stdout_matches = test['asserts'].get('renames', {})

    aw = AutonameowWrapper(opts)
    aw()
    if aw.captured_exception:
        print(' '
              + ui.colorize('    CAUGHT TOP-LEVEL EXCEPTION    ', back='RED'))
        if VERBOSE:
            print('\nCaptured exception:')
            print(str(aw.captured_exception))
            print('\nCaptured traceback:')
            print(str(aw.captured_exception_traceback))

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
                        _msg('  Not renamed. Expected:  "{!s}" -> "{!s}"'.format(_expect_in, _expect_out))
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


def print_test_dirnames(tests):
    _test_dirnames = [types.force_string(t.get('test_dirname')) for t in tests]
    print('\n'.join(_test_dirnames))


def check_asserts_stdout(test, captured_stdout):
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
            print(str(e))
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


def run_regressiontests(tests, print_stderr, print_stdout):
    reporter = TerminalReporter(VERBOSE)
    count_total = len(tests)
    count_success = 0
    count_failure = 0
    count_skipped = 0
    should_abort = False

    failed_tests = []

    global_start_time = time.time()

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
            print('\n')
            log.critical('Received keyboard interrupt. Skipping remaining ..')
            should_abort = True

        elapsed_time = time.time() - start_time

        failures += check_asserts_stdout(test, captured_stdout)

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

    global_elapsed_time = time.time() - global_start_time
    reporter.msg_overall_stats(count_total, count_skipped, count_success,
                               count_failure, global_elapsed_time)

    if not should_abort:
        # Store failed tests only if all tests were executed.
        # Otherwise all tests would have to be re-run in order to "catch"
        # the failed tests, if re-running the failed tests and aborting
        # before completion..
        write_failed_tests(failed_tests)

    return count_failure


def glob_filter(expression, string):
    if b'*' not in expression:
        return expression == string

    regexp = expression.replace(b'*', b'.*')
    return bool(re.match(regexp, string))


def filter_loaded_tests(expression, loaded_tests):
    # TODO: ...
    pass


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
    parser.add_argument(
        '--get-cmd',
        dest='get_cmd',
        nargs='+',
        metavar='TEST_NAME',
        help='Print equivalent command-line invocations for the specified '
             'test case(s). If executed "manually", these would produce the '
             'same behaviour and results as the corresponding regression test. '
             'Each result is printed as two lines; first being "# TEST_NAME", '
             'where "TEST_NAME" is the dirname of the test case. '
             'The second line is the equivalent command-line. '
             'Valid arguments can be found with the "--list" option.'
    )
    parser.add_argument(
        '--list',
        dest='list_tests',
        action='store_true',
        default=False,
        help='Print the ("short name") test directory basename of all loaded '
             'tests and exit. '
    )
    parser.add_argument(
        '-f', '--flter',
        dest='filter_tests',
        nargs='+',
        metavar='BASENAME_GLOB',
        help='Filter tests '
    )


    opts = parser.parse_args(args)

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(name)s %(levelname)-9.9s %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    global VERBOSE
    if opts.verbose:
        VERBOSE = True
        log.setLevel(logging.INFO)
    else:
        VERBOSE = False
        log.setLevel(logging.WARNING)

    loaded_tests = load_regressiontests()
    log.info('Loaded {} regression test(s) ..'.format(len(loaded_tests)))
    if not loaded_tests:
        return

    if opts.list_tests:
        # List the "short name" (dirname) of all tests and exit.
        print_test_dirnames(loaded_tests)
        sys.exit(0)

    if opts.get_cmd:
        # Get equivalent command-lines for the specified test dirnames.
        filter_loaded_tests()
        matched_tests = []
        for _basename_glob in opts.get_cmd:
            # Must convert to bytes in order to do the comparison.
            try:
                _basename_glob_bytes = types.AW_PATHCOMPONENT(_basename_glob)
            except types.AWTypeError as e:
                print(str(e))
                continue

            matches = [
                t for t in loaded_tests
                if glob_filter(_basename_glob_bytes, t.get('test_dirname', b''))
            ]
            if matches:
                matched_tests.extend(matches)
            else:
                log.warning('Not a loaded test: "{!s}"'.format(_basename_glob))

        if not matched_tests:
            _get_cmd = '"{!s}"'.format('", "'.join(opts.get_cmd))
            log.warning('Does not match any loaded test: {!s}'.format(_get_cmd))
            # print('\nLoaded tests:')
            # print_test_dirnames(loaded_tests)
            sys.exit(1)
        else:
            for test in matched_tests:
                test_dirname = types.force_string(test.get('test_dirname'))
                arg_string = commandline_for_testcase(test)
                print('# {!s}\n{!s}\n'.format(test_dirname, arg_string))
            sys.exit(0)

    if opts.run_lastfailed:
        _failed_lastrun = load_failed_tests()
        if _failed_lastrun:
            # TODO: Improve comparing regression test cases.
            # Fails if any option is modified. Compare only directory basenames?
            tests_to_run = [t for t in loaded_tests if t in _failed_lastrun]
            log.info('Running {} of the {} test case(s) that failed during the '
                     'last completed run ..'.format(len(tests_to_run),
                                                    len(_failed_lastrun)))
        else:
            tests_to_run = list(loaded_tests)
            log.info('Running all {} test case(s) as None failed during the '
                     'last completed run ..'.format(len(tests_to_run)))
    else:
        tests_to_run = list(loaded_tests)
        log.info('Running {} test case(s) ..'.format(len(tests_to_run)))

    failed = 0
    failed = run_regressiontests(tests_to_run,
                                 print_stderr=bool(opts.print_stderr),
                                 print_stdout=bool(opts.print_stdout))

    # TODO: Rework passing number of failures between high-level functions.
    if not failed:
        return C.EXIT_SUCCESS
    else:
        return C.EXIT_WARNING


if __name__ == '__main__':
    exit_code = C.EXIT_SUCCESS
    try:
        exit_code = main(sys.argv[1:])
    except KeyboardInterrupt:
        print('\nReceived keyboard interrupt. Exiting ..')
    except AssertionError as e:
        print('\nCaught AssertionError in __main__ (!)')
        print(str(e))
        exit_code = C.EXIT_SANITYFAIL
    except Exception as e:
        print('\nUnhandled exception reached regression __main__ (!)')
        print(str(e))
        exit_code = C.EXIT_ERROR
    finally:
        sys.exit(exit_code)
