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

import sys
import time

from core import constants as C
from core import (
    types,
    ui
)
from regression_utils import (
    AutonameowWrapper,
    check_renames,
    load_regressiontests
)


TERMINAL_WIDTH = 80
msg_label_pass = ui.colorize('P', fore='GREEN')
msg_label_fail = ui.colorize('F', fore='RED')


def run_test(testcase):
    opts = testcase.get('options')
    expect_exitcode = testcase['asserts'].get('exit_code', C.EXIT_SUCCESS)
    expect_renames = testcase['asserts'].get('renames', {})

    aw = AutonameowWrapper(opts)
    try:
        aw()
    except Exception as e:
        print(ui.colorize('    CAUGHT TOP-LEVEL EXCEPTION    ', back='RED'))
        print(str(e))

    captured_runtime = aw.captured_runtime_secs
    failures = 0

    def _msg_run_test_failure(msg):
        print('{} {!s}'.format(msg_label_fail, msg))

    def _msg_run_test_success(msg):
        print('{} {!s}'.format(msg_label_pass, msg))

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
        _msg_run_test_failure('Renames differ')
        if actual_renames:
            for _in, _out in actual_renames.items():
                print('  Actual:  "{!s}" -> "{!s}"'.format(_in, _out))
        else:
            print('  Actual:  No files were renamed')

        if expect_renames:
            for _in, _out in expect_renames.items():
                print('Expected:  "{!s}" -> "{!s}"'.format(_in, _out))
        else:
            print('Expected:  Expected no files to be renamed')

        failures += 1

    return failures, captured_runtime


def msg_overall_success():
    print(ui.colorize('[ ALL TESTS PASSED! ]', fore='GREEN'))


def msg_overall_failure():
    print(ui.colorize('[ SOME TESTS FAILED ]', fore='RED'))


def msg_test_success():
    _label = ui.colorize('[SUCCESS]', fore='GREEN')
    print('{} All assertions passed!'.format(_label))


def msg_test_failure():
    _label = ui.colorize('[FAILURE]', fore='RED')
    print('{} One or more assertions FAILED!'.format(_label))


def msg_test_runtime(elapsed_time, captured_time):
    if captured_time:
        _captured = '{:.6f} seconds'.format(captured_time)
    else:
        _captured = 'N/A'

    _test_time = '{:.6f} seconds'.format(elapsed_time)
    print(' '*10 + 'Runtime: {}  (captured {})'.format(_test_time, _captured))


def msg_overall_stats(count_total, count_skipped, count_success, count_failure):
    print('\n')

    _skipped = '{} skipped'.format(count_skipped)
    if count_skipped > 0:
        _skipped = ui.colorize(_skipped, fore='YELLOW')

    _failure = '{} failed'.format(count_failure)
    if count_failure == 0:
        msg_overall_success()
    else:
        msg_overall_failure()
        _failure = ui.colorize(_failure, fore='RED')

    _stats = 'Regression Test Summary:  {} total, {}, {} passed, {}'.format(
        count_total, _skipped, count_success, _failure
    )

    print('~' * TERMINAL_WIDTH)
    print(_stats)
    print('=' * TERMINAL_WIDTH)


def main(args):
    testcases = load_regressiontests()

    count_success = 0
    count_failure = 0
    count_skipped = 0
    count_total = len(testcases)
    should_abort = False

    print('Found {} regression test(s) ..'.format(len(testcases)))
    for testcase in testcases:
        print()

        if should_abort:
            count_skipped += count_total - count_success - count_failure
            break

        _dirname = types.force_string(testcase.get('test_dirname', '(?)'))
        _description = testcase.get('description', '(UNDESCRIBED)')

        if testcase.get('skiptest'):
            print('Skipped "{!s}"'.format(_dirname))
            count_skipped += 1
            continue

        print('Running "{}"'.format(_dirname))
        print(ui.colorize(_description, style='DIM'))

        failures = 0
        captured_time = None
        start_time = time.time()
        try:
            failures, captured_time = run_test(testcase)
        except KeyboardInterrupt:
            print('\nReceived keyboard interrupt. Skipping remaining tests ..')
            should_abort = True
        elapsed_time = time.time() - start_time

        if failures == 0:
            msg_test_success()
            count_success += 1
        else:
            msg_test_failure()
            count_failure += 1

        msg_test_runtime(elapsed_time, captured_time)

    msg_overall_stats(count_total, count_skipped, count_success, count_failure)


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt:
        print('\nReceived keyboard interrupt. Exiting ..')
        sys.exit(0)
