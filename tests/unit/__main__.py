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

import functools
import os
import sys
import time
import unittest

from core import constants as C
from core import view
from unit import (
    build_testsuite,
    unit_test_glob
)


"""
Alternative (WIP) unit test runner.
Run this from the repository root for up-to-date help:

    PYTHONPATH=autonameow:tests python3 -m unit --help

"""


def without_endline(f):
    @functools.wraps(f)
    def func(*args, **kwargs):
        self = f.__self__
        orig = self.stream.writeln
        self.stream.writeln = self.stream.write
        try:
            return f(*args, **kwargs)
        finally:
            self.stream.writeln = orig
    return func


class TestResult(unittest.TextTestResult):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.NUMBER_SLOW_TESTS_TO_DISPLAY = 5
        self.start_times = {}
        self.run_times = {}

        for x in ('Error', 'ExpectedFailure', 'Failure', 'Skip', 'Success',
                  'UnexpectedSuccess'):
            x = 'add' + x
            setattr(self, x, without_endline(getattr(self, x)))

    def startTest(self, test):
        self.start_times[test] = time.time()
        return super(TestResult, self).startTest(test)

    def stopTest(self, test):
        orig = self.stream.writeln
        self.stream.writeln = self.stream.write

        super(TestResult, self).stopTest(test)

        now = time.time()
        elapsed = now - self.start_times.get(test, now)
        self.run_times[test] = elapsed * 1000  # milliseconds
        self.stream.writeln = orig
        self.stream.writeln('  ({:.6f} ms)'.format(elapsed))

    def stopTestRun(self):
        super(TestResult, self).stopTestRun()

        if self.wasSuccessful():
            tests = sorted(self.run_times, key=self.run_times.get, reverse=True)

            assert len(tests) > self.NUMBER_SLOW_TESTS_TO_DISPLAY
            slowest = [
                '{} ({:.6f} ms)'.format(t.id(), self.run_times[t])
                for t in tests[:self.NUMBER_SLOW_TESTS_TO_DISPLAY]
            ]
            if len(slowest) > 1:
                self.stream.writeln('\n\nSlowest tests:\n')
                self.stream.writeln('\n'.join(slowest))


def parse_options(args):
    _description = '{} {} -- unit test runner'.format(
        C.STRING_PROGRAM_NAME, C.STRING_PROGRAM_VERSION)
    _epilog = 'Project website:  {}'.format(C.STRING_URL_REPO)

    parser = view.cli.get_argparser(description=_description, epilog=_epilog)
    parser.add_argument(
        '-v', '--verbose',
        dest='verbose',
        action='count',
        default=0,
        help='Enables additional output verbosity in increments; '
             '"-v", "-vv", "-vvv", etc.'
    )
    optgrp_select = parser.add_argument_group(
        'Test Selection',
    )
    optgrp_select.add_argument(
        '-f', '--filter',
        dest='filter_glob',
        metavar='GLOB',
        nargs=1,
        help='Select tests whose "TEST_NAME" (dirname) matches "GLOB". '
             'Matching is case-sensitive. An asterisk matches anything '
             'and if "GLOB" begins with "!", the matching is inverted. '
             'This option can be given more than once, which ORs the filters.'
    )
    optgrp_select.add_argument(
        '--skip-slow',
        dest='skip_slow',
        action='store_true',
        default=False,
        help='Skip all "slow" unit tests.'
    )
    optgrp_select.add_argument(
        '--skip-hypothesis',
        dest='skip_hypothesis',
        action='store_true',
        default=False,
        help='Skip "property-based" tests using hypothesis.'
    )
    return parser.parse_args(args)


opts = parse_options(sys.argv[1:])

# TODO: Allow combining filtering and skipping of certain tests.
if opts.skip_slow:
    print('Excluded all "slow" (property-based and extractor) tests ..')
    suite = build_testsuite(
        filename_filter=lambda f: not (f.startswith('test_property_')
                                       or f.startswith('test_extractors_')
                                       or f.startswith('test_core_main'))
    )
elif opts.skip_hypothesis:
    print('Excluded property-based tests ..')
    suite = build_testsuite(
        filename_filter=lambda f: not f.startswith('test_property_')
    )
elif opts.filter_glob:
    glob_expression = opts.filter_glob[0]

    def _glob_filter(filename):
        return unit_test_glob(glob_expression, filename)

    print('Including tests matching glob "{!s}" ..'.format(glob_expression))
    suite = build_testsuite(
        filename_filter=_glob_filter
    )
else:
    suite = build_testsuite()

current_dir = os.getcwd()
os.chdir(os.pardir)

print('Loaded {} test cases ..'.format(suite.countTestCases()))

runner = unittest.TextTestRunner
runner.buffer = True
runner.resultclass = unittest.TextTestResult if opts.verbose < 2 else TestResult

result = runner(verbosity=opts.verbose, buffer=True).run(suite)
if not result.wasSuccessful():
    raise SystemExit(1)

os.chdir(current_dir)

raise SystemExit(0)
