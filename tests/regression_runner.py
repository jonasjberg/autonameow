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

from core import constants as C
from regression_utils import (
    AutonameowWrapper,
    load_regressiontests
)


def run_test(testcase):
    opts = testcase.get('options')
    expect_exitcode = testcase['asserts'].get('exit_status', C.EXIT_SUCCESS)
    expect_renames = testcase['asserts'].get('renames', {})

    aw = AutonameowWrapper(opts)
    try:
        aw()
    except Exception as e:
        print('!!! CAUGHT TOP-LEVEL EXCEPTION !!!')
        print(str(e))

    failures = 0

    actual_exitcode = aw.captured_exitcode
    if actual_exitcode != expect_exitcode:
        print('FAILED :: Expected exit code {!s} but got {!s}'.format(
            expect_exitcode, actual_exitcode
        ))
        failures += 1

    actual_renames = aw.captured_renames
    # if actual_renames:
    #     for _in, _out in actual_renames.items():
    #         print('  Actual:  "{!s}" -> "{!s}"'.format(_in, _out))
    #
    # if expect_renames:
    #     for _in, _out in expect_renames.items():
    #         print('Expected:  "{!s}" -> "{!s}"'.format(_in, _out))

    # print('\nCAPTURED STDOUT:')
    # print(str(aw.captured_stdout))

    # print('\nCAPTURED STDERR:')
    # print(str(aw.captured_stderr))

    if expect_renames:
        if not actual_renames:
            print('FAILED :: No files were renamed!')
            failures += 1
        else:
            if expect_renames != actual_renames:
                print('FAILED :: Renames differ')
                failures += 1
    else:
        if actual_renames:
            print('FAILED :: Files were unexpectedly renamed!')
            failures += 1

    return bool(failures == 0)


def main(args):
    # TODO: [TD0117] Implement automated regression tests
    testcases = load_regressiontests()

    count_success = 0
    count_failure = 0
    count_skipped = 0
    count_total = len(testcases)

    print('Found {} regression test(s) ..'.format(len(testcases)))
    for testcase in testcases:
        print('_' * 70)
        _description = testcase.get('description', '?')

        if testcase.get('skiptest'):
            print('Skipped "{!s}"'.format(_description))
            count_skipped += 1
            continue

        print('Running "{!s}"'.format(_description))

        succeeded = run_test(testcase)
        if succeeded:
            count_success += 1
        else:
            count_failure += 1

    print('\n')
    print('~' * 70)
    if count_failure == 0:
        print('[ ALL TESTS PASSED ]')
    else:
        print('[ SOME TESTS FAILED ]')

    print('Regression Test Summary:  {} total, {} skipped, {} passed, {} '
          'failed'.format(count_total, count_skipped, count_success,
                          count_failure))
    print('=' * 70)


if __name__ == '__main__':
    main(sys.argv[1:])
