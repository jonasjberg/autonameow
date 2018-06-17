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
from core.persistence import get_persistence
from core.view import cli
from regression.utils import AutonameowWrapper
from regression.utils import check_renames
from regression.utils import check_stdout_asserts
from regression.utils import commandline_for_testsuite
from regression.utils import glob_filter
from regression.utils import load_regression_testsuites
from regression.utils import print_test_info
from regression.utils import RunResultsHistory
from regression.utils import TerminalReporter
from util import coercers


_this_dir = os.path.abspath(os.path.dirname(__file__))
PERSISTENCE_DIR_ABSPATH = coercers.coerce_to_normalized_path(_this_dir)
PERSISTENCE_BASENAME_PREFIX = '.regressionrunner'


log = logging.getLogger('regression_runner')


class TestResults(object):
    def __init__(self, failure_count, runtime, stdout, stderr, captured_exception):
        self.failure_count = failure_count
        self.captured_runtime = runtime
        self.captured_stdout = stdout
        self.captured_stderr = stderr
        self.captured_exception = captured_exception


class RunResults(object):
    def __init__(self):
        self.failed = set()
        self.passed = set()
        self.skipped = set()

    @property
    def all(self):
        return self.failed.union(self.passed).union(self.skipped)

    def __len__(self):
        return len(self.all)


def run_test(test, reporter):
    expect_exitcode = test.asserts.get('exit_code', None)
    expect_renames = test.asserts.get('renames', {})

    aw = AutonameowWrapper(test.options)
    aw()
    if aw.captured_exception:
        exception_info = {
            'exception': str(aw.captured_exception),
            'traceback': str(aw.captured_exception_traceback)
        }
        return TestResults(failure_count=0, runtime=None,
                           stdout=aw.captured_stdout, stderr=aw.captured_stderr,
                           captured_exception=exception_info)

    captured_runtime = aw.captured_runtime_secs
    fail_count = 0

    if expect_exitcode is not None:
        actual_exitcode = aw.captured_exitcode
        if actual_exitcode == expect_exitcode:
            reporter.msg_run_test_success(
                'Exit code is {!s} as expected'.format(actual_exitcode)
            )
        else:
            reporter.msg_run_test_failure(
                'Expected exit code {!s} but got {!s}'.format(expect_exitcode, actual_exitcode)
            )
            fail_count += 1

    # TODO: [cleanup] This is way too messy ..
    def _report_differing_filenames(_expected, _actual):
        reporter.msg_run_test_failure('New file name differs from expected file name.')
        reporter.msg('     Expected: "{!s}"'.format(_expected))
        reporter.msg('     Actual:   "{!s}"'.format(_actual))

    def _report_unexpected_rename(_old, _new):
        reporter.msg_run_test_failure(
            'Unexpected rename:  "{!s}" -> "{!s}"'.format(_old, _new)
        )

    actual_renames = aw.captured_renames
    if check_renames(actual_renames, expect_renames):
        assert len(actual_renames) == len(expect_renames)
        reporter.msg_run_test_success(
            'Renamed {} files as expected'.format(len(expect_renames))
        )
        for actual_old, actual_new in actual_renames.items():
            reporter.msg_run_test_success(
                'Renamed "{!s}" -> "{!s}"'.format(actual_old, actual_new)
            )
    else:
        # TODO: Keep count of individual rename assertions?
        fail_count += 1
        if expect_renames:
            if not actual_renames:
                reporter.msg_run_test_failure(
                    'Expected {} files to be renamed but none were!'.format(len(expect_renames))
                )
            # Expected renames and got renames.
            for expect_old, expect_new in expect_renames.items():
                if expect_old not in actual_renames:
                    reporter.msg_run_test_failure(
                        'Not renamed. Expected:  "{!s}" -> "{!s}"'.format(expect_old, expect_new)
                    )
                else:
                    actual_new = actual_renames.get(expect_old)
                    if actual_new != expect_new:
                        _report_differing_filenames(expect_new, actual_new)

            for actual_old, actual_new in actual_renames.items():
                if actual_old not in expect_renames:
                    _report_unexpected_rename(actual_old, actual_new)
                else:
                    expect_new = expect_renames.get(actual_old)
                    if expect_new != actual_new:
                        _report_differing_filenames(expect_new, actual_new)
        else:
            if actual_renames:
                for actual_old, actual_new in actual_renames.items():
                    _report_unexpected_rename(actual_old, actual_new)

    # TODO: [TD0158] Evaluate assertions of "skipped renames".

    captured_stdout = str(aw.captured_stdout)
    captured_stderr = str(aw.captured_stderr)

    stdout_match_results = check_stdout_asserts(test, captured_stdout)
    assert isinstance(stdout_match_results, list)

    for match_result in stdout_match_results:
        result_assert_type = str(match_result.assert_type)
        if result_assert_type == 'matches':
            msg_template = 'Expected stdout to match "{!s}"'
        elif result_assert_type == 'does_not_match':
            msg_template = 'Expected stdout to NOT match "{!s}"'
        else:
            raise AssertionError('Unexpected RegexMatchingResult.assert_type: '
                                 '{!s}'.format(result_assert_type))

        msg = msg_template.format(match_result.regex)
        if match_result.passed:
            reporter.msg_run_test_success(msg)
        else:
            fail_count += 1
            reporter.msg_run_test_failure(msg)

    return TestResults(fail_count, captured_runtime, captured_stdout,
                       captured_stderr, captured_exception=None)


def _get_persistence(file_prefix=PERSISTENCE_BASENAME_PREFIX,
                     persistence_dir_abspath=PERSISTENCE_DIR_ABSPATH):
    persistence_mechanism = get_persistence(file_prefix, persistence_dir_abspath)
    if not persistence_mechanism:
        log.critical('Unable to retrieve any mechanism for persistent storage')
    return persistence_mechanism


def load_testsuite_history(testsuite, history):
    """
    Returns a list of historical test results for a given testsuite.
    """
    past_outcomes = list()

    for run_results in history:
        if testsuite in run_results.failed:
            past_outcomes.append(RunResultsHistory.RESULT_FAIL)
        elif testsuite in run_results.passed:
            past_outcomes.append(RunResultsHistory.RESULT_PASS)
        elif testsuite in run_results.skipped:
            past_outcomes.append(RunResultsHistory.RESULT_SKIP)
        else:
            past_outcomes.append(RunResultsHistory.RESULT_UNKNOWN)

    return past_outcomes


def load_run_results_history():
    # TODO: [hack] Refactor ..
    persistent_storage = _get_persistence()
    if persistent_storage:
        try:
            history = persistent_storage.get('history')
        except KeyError:
            pass
        else:
            if history:
                assert isinstance(history, list)
                return history
    return list()


def write_run_results_history(run_results, max_entry_count=10):
    assert isinstance(max_entry_count, int)

    # TODO: [hack] Refactor ..
    history = load_run_results_history()
    assert isinstance(history, list)

    # TODO: [hack] Refactor ..
    history.insert(0, run_results)
    history = history[:max_entry_count]

    persistent_storage = _get_persistence()
    if persistent_storage:
        persistent_storage.set('history', history)


def write_failed_testsuites(suites):
    persistent_storage = _get_persistence()
    if persistent_storage:
        suites_list = list(suites)
        persistent_storage.set('lastrun', {'failed': suites_list})


def load_failed_testsuites():
    persistent_storage = _get_persistence()
    if persistent_storage:
        try:
            lastrun = persistent_storage.get('lastrun')
        except KeyError:
            pass
        else:
            if lastrun:
                assert isinstance(lastrun, dict)
                return lastrun.get('failed', list())
    return list()


def print_test_commandlines(tests):
    for test in tests:
        arg_string = commandline_for_testsuite(test)
        print('# {!s}\n{!s}\n'.format(test.str_dirname, arg_string))


def run_regressiontests(tests, verbose, print_stderr, print_stdout):
    history = load_run_results_history()
    reporter = TerminalReporter(verbose)
    run_results = RunResults()
    should_abort = False
    global_start_time = time.time()

    for testsuite in tests:
        if should_abort:
            remaining = [t for t in tests if t not in run_results.all]
            run_results.skipped.update(remaining)
            break

        if testsuite.should_skip:
            reporter.msg_test_skipping(testsuite.str_dirname, testsuite.description)
            run_results.skipped.add(testsuite)

            reporter.msg_test_skipped()

            # TODO: [hack] Refactor ..
            testsuite_history = load_testsuite_history(testsuite, history)
            assert isinstance(testsuite_history, list)
            reporter.msg_test_history(testsuite_history)

            reporter.msg_test_runtime(None, None)
            continue

        reporter.msg_test_start(testsuite.str_dirname, testsuite.description)

        results = None
        start_time = time.time()
        try:
            results = run_test(testsuite, reporter)
        except KeyboardInterrupt:
            # Move cursor two characters back and print spaces over "^C".
            print('\b\b  \n', flush=True)
            log.critical('Received keyboard interrupt. Skipping remaining ..')
            should_abort = True
        elapsed_time = time.time() - start_time

        if results:
            captured_stdout = results.captured_stdout
            captured_stderr = results.captured_stderr
            if results.captured_exception:
                reporter.msg_captured_exception(results.captured_exception)

                if print_stderr and captured_stderr:
                    reporter.msg_captured_stderr(captured_stderr)
                if print_stdout and captured_stdout:
                    reporter.msg_captured_stdout(captured_stdout)

                run_results.failed.add(testsuite)
                continue

            failures = int(results.failure_count)
            test_passed = failures == 0
            if test_passed:
                reporter.msg_test_success()
                run_results.passed.add(testsuite)
            else:
                reporter.msg_test_failure()
                run_results.failed.add(testsuite)

            # TODO: [hack] Refactor ..
            testsuite_history = load_testsuite_history(testsuite, history)
            assert isinstance(testsuite_history, list)
            reporter.msg_test_history(testsuite_history)
            reporter.msg_test_runtime(elapsed_time, results.captured_runtime)

            if print_stderr and captured_stderr:
                reporter.msg_captured_stderr(captured_stderr)
            if print_stdout and captured_stdout:
                reporter.msg_captured_stdout(captured_stdout)

    global_elapsed_time = time.time() - global_start_time
    reporter.msg_overall_stats(
        len(tests),
        count_skipped=len(run_results.skipped),
        count_success=len(run_results.passed),
        count_failure=len(run_results.failed),
        elapsed_time=global_elapsed_time
    )

    if not should_abort:
        # Store failed tests only if all tests were executed.
        # Otherwise all tests would have to be re-run in order to "catch"
        # the failed tests, if re-running the failed tests and aborting
        # before completion..
        write_failed_testsuites(run_results.failed)
        write_run_results_history(run_results)

    return run_results


def filter_tests(tests, filter_func, expr):
    assert callable(filter_func)
    return [t for t in tests if filter_func(expr, t.dirname)]


def main(args):
    _description = '{} {} -- regression test suite runner'.format(
        C.STRING_PROGRAM_NAME, C.STRING_PROGRAM_VERSION)
    _epilog = 'Project website:  {}'.format(C.STRING_URL_REPO)

    parser = cli.get_argparser(description=_description, epilog=_epilog)
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
        dest='filter_globs',
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
        help='Select only the test suites that failed during the last '
             'completed run. Selects all if none failed.'
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
             'test suite(s) and exit. '
             'Enable verbose mode for additional information.'
    )
    optgrp_action.add_argument(
        '--get-cmd',
        dest='get_cmd',
        action='store_true',
        default=False,
        help='Print equivalent command-line invocations for the selected '
             'test suite(s) and exit. '
             'If executed "manually", these would produce the same behaviour '
             'and results as the corresponding regression test. '
             'Each result is printed as two lines; first being "# TEST_NAME", '
             'where "TEST_NAME" is the directory basename of the test suite. '
             'The second line is the equivalent command-line. '
             'Use "test selection" options to narrow down the results.'
    )
    optgrp_action.add_argument(
        '--run',
        dest='run_tests',
        action='store_true',
        default=True,
        help='Run the selected test suite(s). (DEFAULT: True)'
    )

    opts = parser.parse_args(args)

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(name)s %(levelname)-9.9s %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    verbose = bool(opts.verbose)
    if verbose:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)

    loaded_tests = load_regression_testsuites()
    log.info('Loaded {} regression test(s) ..'.format(len(loaded_tests)))
    if not loaded_tests:
        return

    # Start test selection based on any criteria given with the options.
    if opts.filter_globs:
        all_filtered = list()
        tests_to_filter = list(loaded_tests)
        for filter_expression in opts.filter_globs:
            filtered = filter_tests(tests_to_filter, glob_filter,
                                    expr=filter_expression)
            log.info('Filter expression "{!s}" matched {} test suite(s)'.format(
                filter_expression, len(filtered)))
            tests_to_filter = filtered
            all_filtered = filtered
        log.info('Filtering selected {} test suite(s)'.format(len(all_filtered)))
        selected_tests = all_filtered
    else:
        selected_tests = loaded_tests

    if opts.filter_lastfailed:
        failed_lastrun = load_failed_testsuites()
        if failed_lastrun:
            # TODO: Improve comparing regression test suites.
            # Fails if any option is modified. Compare only directory basenames?
            selected_tests = [t for t in selected_tests if t in failed_lastrun]
            log.info('Selected {} of {} test suite(s) that failed during the '
                     'last completed run ..'.format(len(selected_tests),
                                                    len(failed_lastrun)))
        else:
            log.info('Selected all {} test suite(s) as None failed during the '
                     'last completed run ..'.format(len(selected_tests)))

    log.info('Selected {} of {} test suite(s) ..'.format(len(selected_tests),
                                                        len(loaded_tests)))
    # End of test selection.
    if not selected_tests:
        log.warning('None of the loaded tests were selected ..')

    # Perform actions on the selected tests.
    if opts.list_tests:
        print_test_info(selected_tests, verbose)
        return C.EXIT_SUCCESS

    if opts.get_cmd:
        print_test_commandlines(selected_tests)
        return C.EXIT_SUCCESS

    if opts.run_tests:
        run_results = run_regressiontests(
            selected_tests, verbose,
            print_stderr=bool(opts.print_stderr),
            print_stdout=bool(opts.print_stdout)
        )
        if run_results.failed:
            return C.EXIT_WARNING

    return C.EXIT_SUCCESS


def print_traceback():
    def _print_separator():
        print('_' * 80 + '\n', file=sys.stderr)

    _print_separator()
    import traceback
    traceback.print_exc(file=sys.stderr, limit=None, chain=True)
    _print_separator()


def print_exception_error(message, exception):
    print('\n\n{!s}'.format(message), file=sys.stderr)
    print(str(exception), file=sys.stderr)


if __name__ == '__main__':
    exit_code = C.EXIT_SUCCESS
    try:
        exit_code = main(sys.argv[1:])
    except KeyboardInterrupt:
        print('\nReceived keyboard interrupt. Exiting ..')
    except AssertionError as e:
        print_exception_error(
            'Caught AssertionError in regression_runner.__main__()', e
        )
        print_traceback()
        exit_code = C.EXIT_SANITYFAIL
    except Exception as e:
        print_exception_error(
            'Unhandled exception reached regression_runner.__main__()', e
        )
        print_traceback()
        exit_code = C.EXIT_ERROR
    finally:
        sys.exit(exit_code)
