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

from regression_utils import (
    get_regressiontest_dirs,
    RegressionTestError,
    RegressionTestLoader
)
import unit_utils as uu


class AutonameowWrapper(object):
    def __init__(self, opts=None):
        if opts:
            assert isinstance(opts, dict)
            self.opts = opts
        else:
            self.opts = {}

        self.exit_code = None
        self.captured_stderr = None
        self.captured_stdout = None

    def mock_exit_program(self, exit_code):
        self.exit_code = exit_code

    def __call__(self):
        from core.autonameow import Autonameow
        Autonameow.exit_program = self.mock_exit_program

        with uu.capture_stdout() as stdout, uu.capture_stderr() as stderr:
            with Autonameow(self.opts) as ameow:
                ameow.run()

        self.captured_stdout = stdout.getvalue()
        self.captured_stderr = stderr.getvalue()


def get_regressiontests():
    out = []

    _paths = get_regressiontest_dirs()
    for p in _paths:
        try:
            loaded_test = RegressionTestLoader(p).load()
        except RegressionTestError as e:
            print('Unable to load test case :: ' + str(e))
        else:
            out.append(loaded_test)

    return out


def main(args):
    # TODO: [TD0117] Implement automated regression tests
    testcases = get_regressiontests()

    print('Found {} regression test case(s) ..'.format(len(testcases)))
    for testcase in testcases:
        print('-' * 40)
        print('Running "{!s}"'.format(testcase.get('description', '?')))

        aw = AutonameowWrapper(testcase.get('options'))

        try:
            aw()
        except Exception as e:
            print('!TESTCASE FAILED!')
            print(str(e))

        print('-' * 40)


if __name__ == '__main__':
    main(sys.argv[1:])
