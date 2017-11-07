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
from core import (
    disk,
    types
)
from regression_utils import load_regressiontests
import unit_utils as uu


class AutonameowWrapper(object):
    def __init__(self, opts=None):
        if opts:
            assert isinstance(opts, dict)
            self.opts = opts
        else:
            self.opts = {}

        self.captured_exitcode = None
        self.captured_stderr = None
        self.captured_stdout = None
        self.captured_renames = dict()

    def mock_exit_program(self, exitcode):
        self.captured_exitcode = exitcode

    def mock_do_rename(self, from_path, new_basename, dry_run=True):
        _from_basename = types.force_string(disk.file_basename(from_path))
        self.captured_renames[_from_basename] = new_basename

    def __call__(self):
        from core.autonameow import Autonameow
        Autonameow.exit_program = self.mock_exit_program
        Autonameow.do_rename = self.mock_do_rename

        with uu.capture_stdout() as stdout, uu.capture_stderr() as stderr:
            with Autonameow(self.opts) as ameow:
                ameow.run()

        self.captured_stdout = stdout.getvalue()
        self.captured_stderr = stderr.getvalue()


def run_test(testcase):
    opts = testcase.get('options')
    expect_exitcode = testcase['asserts'].get('exit_status', C.EXIT_SUCCESS)
    expect_renames = testcase['asserts'].get('renames', {})

    aw = AutonameowWrapper(opts)
    try:
        aw()
    except Exception as e:
        print('!TESTCASE FAILED!')
        print(str(e))

    actual_exitcode = aw.captured_exitcode
    if actual_exitcode != expect_exitcode:
        print('TEST FAILED :: Expected exit code {!s} but got {!s}'.format(
            expect_exitcode, actual_exitcode
        ))

    actual_renames = aw.captured_renames
    if actual_renames:
        for _in, _out in actual_renames.items():
            print('  Actual:  "{!s}" -> "{!s}"'.format(_in, _out))

    if expect_renames:
        for _in, _out in expect_renames.items():
            print('Expected:  "{!s}" -> "{!s}"'.format(_in, _out))

    if expect_renames:
        if not actual_renames:
            print('TEST FAILED :: No files were renamed!')
            return False
        else:
            if expect_renames != actual_renames:
                print('TEST FAILED :: Renames differ')
                return False
    else:
        if actual_renames:
            print('TEST FAILED :: Files were unexpectedly renamed!')
            return False

    # print('\nCAPTURED STDOUT:')
    # print(str(aw.captured_stdout))

    # print('\nCAPTURED STDERR:')
    # print(str(aw.captured_stderr))


def check_renames(actual, expected):
    # TODO: ..
    return None


def main(args):
    # TODO: [TD0117] Implement automated regression tests
    testcases = load_regressiontests()

    print('Found {} regression test(s) ..'.format(len(testcases)))
    for testcase in testcases:
        print('=' * 60)
        print('Running "{!s}"'.format(testcase.get('description', '?')))

        run_test(testcase)

        print('=' * 60)


if __name__ == '__main__':
    main(sys.argv[1:])
