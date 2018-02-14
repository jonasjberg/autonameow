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
    check_stdout_asserts,
    commandline_for_testcase,
    glob_filter,
    load_regressiontests,
    regexp_filter,
    TerminalReporter
)


VERBOSE = False
_this_dir = os.path.abspath(os.path.dirname(__file__))
PERSISTENCE_DIR_ABSPATH = types.AW_PATH.normalize(_this_dir)
PERSISTENCE_BASENAME_PREFIX = '.regressionrunner'


log = logging.getLogger('regression_runner')
msg_label_pass = ui.colorize('PASS', fore='GREEN')
msg_label_fail = ui.colorize('FAIL', fore='RED')


class TestResults(object):
    def __init__(self, failure_count, runtime, stdout, stderr, raised_exception):
        self.failure_count = failure_count
        self.captured_runtime = runtime
        self.captured_stdout = stdout
        self.captured_stderr = stderr
        self.raised_exception = raised_exception


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
            print('\nCaptured exception:')
            print(str(aw.captured_exception))
            print('\nCaptured traceback:')
            print(str(aw.captured_exception_traceback))

        return TestResults(failure_count=0, runtime=None,
                           stdout=aw.captured_stdout, stderr=aw.captured_stderr,
                           raised_exception=True)

    captured_runtime = aw.captured_runtime_secs
    fail_count = 0

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
            fail_count += 1

    actual_renames = aw.captured_renames
    if check_renames(actual_renames, expect_renames):
        _msg_run_test_success('Renamed {} files as expected'.format(len(actual_renames)))

        for _in, _out in actual_renames.items():
            _msg_run_test_success('Renamed "{!s}" -> "{!s}"'.format(_in, _out))
    else:
        fail_count += 1
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

    # TODO: [TD0158] Evaluate assertions of "skipped renames".

    captured_stdout = str(aw.captured_stdout)
    captured_stderr = str(aw.captured_stderr)

    stdout_assert_failures = check_stdout_asserts(test, captured_stdout)
    if stdout_assert_failures:
        assert isinstance(stdout_assert_failures, list)

        fail_count += len(stdout_assert_failures)

        for match_type, regexp in stdout_assert_failures:
            assert match_type in ('matches', 'does_not_match')
            if match_type == 'matches':
                _msg_run_test_failure(
                    'Expected stdout to match {!s}'.format(regexp)
                )
            elif match_type == 'does_not_match':
                _msg_run_test_failure(
                    'Expected stdout to NOT match {!s}'.format(regexp)
                )

    return TestResults(fail_count, captured_runtime, captured_stdout,
                       captured_stderr, raised_exception=False)


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


def print_test_info(tests):
    if VERBOSE:
        cf = ui.ColumnFormatter()
        for t in tests:
            _test_dirname = types.force_string(t.get('test_dirname'))
            _test_description = types.force_string(t.get('description'))
            cf.addrow(_test_dirname, _test_description)
        print(cf)
    else:
        _test_dirnames = [
            types.force_string(t.get('test_dirname')) for t in tests
        ]
        print('\n'.join(_test_dirnames))


def print_test_commandlines(tests):
    for test in tests:
        test_dirname = types.force_string(test.get('test_dirname'))
        arg_string = commandline_for_testcase(test)
        print('# {!s}\n{!s}\n'.format(test_dirname, arg_string))


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

        results = None
        start_time = time.time()
        try:
            results = run_test(test)
        except KeyboardInterrupt:
            # Move cursor two characters back and print spaces over "^C".
            print('\b\b  \n')
            log.critical('Received keyboard interrupt. Skipping remaining ..')
            should_abort = True
        elapsed_time = time.time() - start_time

        if results:
            captured_stdout = results.captured_stdout
            captured_stderr = results.captured_stderr
            if results.raised_exception:
                if print_stderr and captured_stderr:
                    reporter.msg_captured_stderr(captured_stderr)
                if print_stdout and captured_stdout:
                    reporter.msg_captured_stdout(captured_stdout)

                # TODO: Fix formatting of failure due to top-level exception error.
                count_failure += 1
                failed_tests.append(test)
                continue

            failures = int(results.failure_count)
            if failures == 0:
                reporter.msg_test_success()
                count_success += 1
            elif failures > 0:
                reporter.msg_test_failure()
                count_failure += 1
                failed_tests.append(test)

            reporter.msg_test_runtime(elapsed_time, results.captured_runtime)

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


def filter_tests(tests, filter_func, expr):
    assert callable(filter_func)
    return [t for t in tests if filter_func(expr, t.get('test_dirname', b''))]


def main(args):
    _description = '{} {} -- regression test suite runner'.format(
        C.STRING_PROGRAM_NAME, C.STRING_PROGRAM_VERSION)
    _epilog = 'Project website:  {}'.format(C.STRING_URL_REPO)

    parser = ui.cli.get_argparser(description=_description, epilog=_epilog)
    parser.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='store_true',
        default=False,
        help='Enables verbose mode, prints additional information.'
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

    optgrp_select = parser.add_argument_group(
        'Test Selection',
        'Selection is performed in the order in which the options are listed '
        'here. I.E. first any glob filtering, then selecting last failed, etc.'
    )
    optgrp_select.add_argument(
        '-f', '--filter',
        dest='filter_glob',
        metavar='GLOB',
        action='append',
        help='Select tests whose "TEST_NAME" (dirname) matches "GLOB". '
             'Matching is case-sensitive. An asterisk matches anything '
             'and if "GLOB" begins with "!", the matching is inverted. '
             'Give this option more than once to chain the filters.'
    )
    optgrp_select.add_argument(
        '--last-failed',
        dest='filter_lastfailed',
        action='store_true',
        default=False,
        help='Select only the test cases that failed during the last completed '
             'run. Selects all if none failed.'
    )

    optgrp_action = parser.add_argument_group(
        'Actions to Perform',
        'Only the first active option is used, ordered as per this listing.'
    )
    optgrp_action.add_argument(
        '--list',
        dest='list_tests',
        action='store_true',
        default=False,
        help='Print the "short name" (directory basename) of the selected '
             'test case(s) and exit. '
             'Enable verbose mode for additional information.'
    )
    optgrp_action.add_argument(
        '--get-cmd',
        dest='get_cmd',
        action='store_true',
        default=False,
        help='Print equivalent command-line invocations for the selected '
             'test case(s) and exit. '
             'If executed "manually", these would produce the same behaviour '
             'and results as the corresponding regression test. '
             'Each result is printed as two lines; first being "# TEST_NAME", '
             'where "TEST_NAME" is the directory basename of the test case. '
             'The second line is the equivalent command-line. '
             'Use "test selection" options to narrow down the results.'
    )
    optgrp_action.add_argument(
        '--run',
        dest='run_tests',
        action='store_true',
        default=True,
        help='Run the selected test case(s). (DEFAULT: True)'
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

    # Start test selection based on any criteria given with the options.
    if opts.filter_glob:
        all_filtered = list()
        tests_to_filter = list(loaded_tests)
        for filter_expression in opts.filter_glob:
            filtered = filter_tests(tests_to_filter, glob_filter,
                                    expr=filter_expression)
            log.info('Filter expression "{!s}" matched {} test case(s)'.format(
                filter_expression, len(filtered)))
            tests_to_filter = filtered
            all_filtered = filtered
        log.info('Filtering selected {} test case(s)'.format(len(all_filtered)))
        selected_tests = all_filtered
    else:
        selected_tests = loaded_tests

    if opts.filter_lastfailed:
        _failed_lastrun = load_failed_tests()
        if _failed_lastrun:
            # TODO: Improve comparing regression test cases.
            # Fails if any option is modified. Compare only directory basenames?
            selected_tests = [t for t in selected_tests if t in _failed_lastrun]
            log.info('Selected {} of {} test case(s) that failed during the '
                     'last completed run ..'.format(len(selected_tests),
                                                    len(_failed_lastrun)))
        else:
            log.info('Selected all {} test case(s) as None failed during the '
                     'last completed run ..'.format(len(selected_tests)))

    log.info('Selected {} of {} test case(s) ..'.format(len(selected_tests),
                                                        len(loaded_tests)))
    # End of test selection.
    if not selected_tests:
        log.warning('None of the loaded tests were selected ..')

    # Perform actions on the selected tests.
    if opts.list_tests:
        print_test_info(selected_tests)
        return C.EXIT_SUCCESS

    if opts.get_cmd:
        print_test_commandlines(selected_tests)
        return C.EXIT_SUCCESS

    if opts.run_tests:
        failed = 0
        failed = run_regressiontests(selected_tests,
                                     print_stderr=bool(opts.print_stderr),
                                     print_stdout=bool(opts.print_stdout))

        # TODO: Rework passing number of failures between high-level functions.
        if failed:
            return C.EXIT_WARNING

    return C.EXIT_SUCCESS


def print_traceback():
    DELIM = '-' * 80
    print('\n' + DELIM)
    import traceback
    traceback.print_exc()
    print(DELIM)


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
        print('\n\nUnhandled exception reached regression __main__ (!)')
        print('[ERROR] {!s}'.format(e))
        print_traceback()
        exit_code = C.EXIT_ERROR
    finally:
        sys.exit(exit_code)
