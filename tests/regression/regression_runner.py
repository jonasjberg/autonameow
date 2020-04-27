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

import logging
import sys
import time

from core import constants as C
from core.view import cli
from regression import history
from regression.utils import AutonameowWrapper
from regression.utils import check_renames
from regression.utils import check_stdout_asserts
from regression.utils import commandline_for_testsuite
from regression.utils import glob_filter
from regression.utils import load_regression_testsuites
from regression.utils import print_testsuite_info
from regression.utils import RunResultsHistory
from regression.utils import TerminalReporter


log = logging.getLogger('regression_runner')


class TestSuiteResults(object):
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


def run_testsuite(testsuite, reporter):
    expected_exitcode = testsuite.asserts.get('exit_code', None)
    expected_renames = testsuite.asserts.get('renames', {})

    instance_wrapper = AutonameowWrapper(testsuite.options)
    instance_wrapper()
    if instance_wrapper.captured_exception:
        return TestSuiteResults(
            failure_count=0,
            runtime=None,
            stdout=instance_wrapper.captured_stdout,
            stderr=instance_wrapper.captured_stderr,
            captured_exception={
                'exception': str(instance_wrapper.captured_exception),
                'traceback': str(instance_wrapper.captured_exception_traceback)
            }
        )

    fail_count = 0

    if expected_exitcode is not None:
        actual_exitcode = instance_wrapper.captured_exitcode
        if actual_exitcode == expected_exitcode:
            reporter.msg_run_test_success(
                'Exit code is {!s} as expected'.format(actual_exitcode)
            )
        else:
            reporter.msg_run_test_failure(
                'Expected exit code {!s} but got {!s}'.format(expected_exitcode, actual_exitcode)
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

    actual_renames = instance_wrapper.captured_renames
    if check_renames(actual_renames, expected_renames):
        assert len(actual_renames) == len(expected_renames)
        reporter.msg_run_test_success(
            'Renamed {} files as expected'.format(len(expected_renames))
        )
        for actual_old, actual_new in actual_renames.items():
            reporter.msg_run_test_success(
                'Renamed "{!s}" -> "{!s}"'.format(actual_old, actual_new)
            )
    else:
        # TODO: Keep count of individual rename assertions?
        fail_count += 1
        if expected_renames:
            if not actual_renames:
                reporter.msg_run_test_failure(
                    'Expected {} files to be renamed but none were!'.format(len(expected_renames))
                )
            # Expected renames and got renames.
            for expect_old, expect_new in expected_renames.items():
                if expect_old not in actual_renames:
                    reporter.msg_run_test_failure(
                        'Not renamed. Expected:  "{!s}" -> "{!s}"'.format(expect_old, expect_new)
                    )
                else:
                    actual_new = actual_renames.get(expect_old)
                    if actual_new != expect_new:
                        _report_differing_filenames(expect_new, actual_new)

            for actual_old, actual_new in actual_renames.items():
                if actual_old not in expected_renames:
                    _report_unexpected_rename(actual_old, actual_new)
                else:
                    expect_new = expected_renames.get(actual_old)
                    if expect_new != actual_new:
                        _report_differing_filenames(expect_new, actual_new)
        else:
            if actual_renames:
                for actual_old, actual_new in actual_renames.items():
                    _report_unexpected_rename(actual_old, actual_new)

    # TODO: [TD0158] Evaluate assertions of "skipped renames".

    captured_stdout = str(instance_wrapper.captured_stdout)
    stdout_match_results = check_stdout_asserts(testsuite, captured_stdout)
    assert isinstance(stdout_match_results, list)

    for match_result in stdout_match_results:
        result_assert_type = str(match_result.assert_type)

        msg_template = {
            'matches': 'Expected stdout to match "{!s}"',
            'does_not_match': 'Expected stdout to NOT match "{!s}"',
        }.get(result_assert_type)

        if not msg_template:
            raise AssertionError(
                'Unexpected RegexMatchingResult.assert_type: '
                '{!s}'.format(result_assert_type)
            )

        msg = msg_template.format(match_result.regex)
        if match_result.passed:
            reporter.msg_run_test_success(msg)
        else:
            fail_count += 1
            reporter.msg_run_test_failure(msg)

    return TestSuiteResults(
        failure_count=fail_count,
        runtime=instance_wrapper.captured_runtime_secs,
        stdout=captured_stdout,
        stderr=str(instance_wrapper.captured_stderr),
        captured_exception=None
    )


def load_testsuite_history(testsuite, previous_runs):
    """
    Returns a list of historical test results for a given testsuite.
    """
    past_outcomes = list()

    for run_results in previous_runs:
        if testsuite in run_results.failed:
            past_outcomes.append(RunResultsHistory.RESULT_FAIL)
        elif testsuite in run_results.passed:
            past_outcomes.append(RunResultsHistory.RESULT_PASS)
        elif testsuite in run_results.skipped:
            past_outcomes.append(RunResultsHistory.RESULT_SKIP)
        else:
            past_outcomes.append(RunResultsHistory.RESULT_UNKNOWN)

    return past_outcomes


def print_testsuite_commandlines(testsuites):
    for testsuite in testsuites:
        arg_string = commandline_for_testsuite(testsuite)
        print('# {!s}\n{!s}\n'.format(testsuite.str_dirname, arg_string))


def run_regression_testsuites(testsuites, reporter):
    run_results_history = history.load_run_results_history()
    run_results = RunResults()
    should_abort = False
    global_start_time = time.time()

    for testsuite in testsuites:
        if should_abort:
            remaining = [t for t in testsuites if t not in run_results.all]
            run_results.skipped.update(remaining)
            break

        if testsuite.should_skip:
            reporter.msg_test_skipping(testsuite.str_dirname, testsuite.description)
            run_results.skipped.add(testsuite)

            reporter.msg_testsuite_skipped()

            # TODO: [hack] Refactor ..
            testsuite_history = load_testsuite_history(testsuite, run_results_history)
            assert isinstance(testsuite_history, list)
            reporter.msg_testsuite_history(testsuite_history)

            reporter.msg_testsuite_runtime(None, None)
            continue

        reporter.msg_testsuite_start(testsuite.str_dirname, testsuite.description)

        results = None
        start_time = time.time()
        try:
            results = run_testsuite(testsuite, reporter)
        except KeyboardInterrupt:
            # Move cursor two characters back and print spaces over "^C".
            print('\b\b  \n', flush=True)
            log.critical('Received keyboard interrupt. Skipping remaining ..')
            should_abort = True

        elapsed_time = time.time() - start_time
        if not results:
            continue

        captured_stdout = results.captured_stdout
        captured_stderr = results.captured_stderr
        if results.captured_exception:
            reporter.msg_captured_exception(results.captured_exception)

            if captured_stderr:
                reporter.msg_captured_stderr(captured_stderr)
            if captured_stdout:
                reporter.msg_captured_stdout(captured_stdout)

            run_results.failed.add(testsuite)
            continue

        failures = int(results.failure_count)
        testsuite_passed = failures == 0
        if testsuite_passed:
            reporter.msg_testsuite_success()
            run_results.passed.add(testsuite)
        else:
            reporter.msg_testsuite_failure(failure_count=failures)
            run_results.failed.add(testsuite)

        # TODO: [hack] Refactor ..
        testsuite_history = load_testsuite_history(testsuite, run_results_history)
        assert isinstance(testsuite_history, list)
        reporter.msg_testsuite_history(testsuite_history)

        captured_runtime = results.captured_runtime
        assert captured_runtime is not None

        previous_runtime = history.load_captured_runtime(testsuite)
        if previous_runtime is not None:
            time_delta_ms = (captured_runtime - previous_runtime) * 1000
        else:
            time_delta_ms = None
        reporter.msg_testsuite_runtime(elapsed_time, captured_runtime, time_delta_ms)

        # TODO: [hack] Refactor .. Clean up persistence.
        history.write_captured_runtime(testsuite, captured_runtime)

        if captured_stderr:
            reporter.msg_captured_stderr(captured_stderr)
        if captured_stdout:
            reporter.msg_captured_stdout(captured_stdout)

    reporter.msg_overall_stats(
        count_total=len(testsuites),
        count_skipped=len(run_results.skipped),
        count_success=len(run_results.passed),
        count_failure=len(run_results.failed),
        elapsed_time=time.time() - global_start_time
    )

    if not should_abort:
        # Store failed tests only if all tests were executed.
        # Otherwise all tests would have to be re-run in order to "catch"
        # the failed tests, if re-running the failed tests and aborting
        # before completion..
        history.write_failed_testsuites(run_results.failed)
        history.write_run_results_history(run_results)

    return run_results


def filter_testsuites(testsuites, filter_func, expr):
    assert callable(filter_func)
    return [t for t in testsuites if filter_func(expr, t.dirname)]


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
        dest='list_testsuites',
        action='store_true',
        default=False,
        help='Print the "short name" (directory basename) of the selected '
             'test suite(s) and exit. '
             'Enable verbose mode for additional information.'
    )
    optgrp_action.add_argument(
        '--get-cmd',
        dest='get_testsuite_cmdline',
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
        dest='run_testsuites',
        action='store_true',
        default=True,
        help='Run the selected test suite(s). (DEFAULT: True)'
    )

    opts = parser.parse_args(args)

    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(name)s %(levelname)-9.9s %(message)s')
    handler.setFormatter(formatter)
    log.addHandler(handler)
    verbose_mode = bool(opts.verbose)
    if verbose_mode:
        log.setLevel(logging.INFO)
    else:
        log.setLevel(logging.WARNING)

    loaded_testsuites = load_regression_testsuites()
    log.info('Loaded %d regression test suite(s) ..', len(loaded_testsuites))
    if not loaded_testsuites:
        return C.EXIT_WARNING

    # Start test selection based on any criteria given with the options.
    selected_testsuites = loaded_testsuites

    if opts.filter_globs:
        for filter_expression in opts.filter_globs:
            selected_testsuites = filter_testsuites(
                testsuites=selected_testsuites,
                filter_func=glob_filter,
                expr=filter_expression
            )
            log.info('Filter expression "%s" matched %d test suite(s)',
                     filter_expression, len(selected_testsuites))

        log.info('Filtering selected %d test suite(s)', len(selected_testsuites))

    if opts.filter_lastfailed:
        testsuites_failed_last_run = history.load_failed_testsuites()
        if testsuites_failed_last_run:
            # TODO: Improve comparing regression test suites.
            # Fails if any option is modified. Compare only directory basenames?
            selected_testsuites = [
                t for t in selected_testsuites if t in testsuites_failed_last_run
            ]
            log.info('Selected %d of %d test suite(s) that failed during the '
                     'last completed run ..',
                     len(selected_testsuites), len(testsuites_failed_last_run))
        else:
            log.info('Selected all %d test suite(s) as None failed during the '
                     'last completed run ..', len(selected_testsuites))

    log.info('Selected %d of %d test suite(s) ..',
             len(selected_testsuites), len(loaded_testsuites))

    if not selected_testsuites:
        log.warning('None of the loaded tests were selected ..')
        return C.EXIT_SUCCESS

    if opts.list_testsuites:
        print_testsuite_info(selected_testsuites, verbose_mode)
        return C.EXIT_SUCCESS

    if opts.get_testsuite_cmdline:
        print_testsuite_commandlines(selected_testsuites)
        return C.EXIT_SUCCESS

    if opts.run_testsuites:
        run_results = run_regression_testsuites(
            testsuites=selected_testsuites,
            reporter=TerminalReporter(
                verbose=verbose_mode,
                print_stdout=bool(opts.print_stdout),
                print_stderr=bool(opts.print_stderr),
            ),
        )
        if run_results.failed:
            return C.EXIT_WARNING

    return C.EXIT_SUCCESS


def print_exception_with_traceback(exception):
    # Calling 'str()' on instances of 'AssertionError' returns an empty string.
    excstr = str(exception) or repr(exception)
    print(
        'CRITICAL: Caught {!s} in {!s}.__main__()\n'.format(excstr, __file__),
        file=sys.stderr,
    )
    import traceback
    traceback.print_exc(
        chain=True,
        file=sys.stderr,
        limit=None,
    )


if __name__ == '__main__':
    exit_code = C.EXIT_SUCCESS
    try:
        exit_code = main(sys.argv[1:])
    except KeyboardInterrupt:
        print('\nReceived keyboard interrupt. Exiting ..')
    except AssertionError as e:
        print_exception_with_traceback(e)
        exit_code = C.EXIT_SANITYFAIL
    except Exception as e:
        print_exception_with_traceback(e)
        exit_code = C.EXIT_ERROR
    finally:
        sys.exit(exit_code)
