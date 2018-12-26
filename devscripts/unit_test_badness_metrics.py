#!/usr/bin/env python3

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import re
from collections import Counter
from collections import defaultdict
from collections import namedtuple

# TODO(jonas): INCOMPLETE!

# NOTE: First run this to generate the 'smother.csv' file read by this script:
#
#   $ PYTHONPATH=autonameow:tests py.test --smother autonameow tests/unit/test_*.py
#   $ PYTHONPATH=autonameow:tests smother csv smother.csv


Visit = namedtuple('Line', ('dut_filepath', 'dut_linenum', 'test_filepath', 'test_class', 'test_method'))

visits = list()

with open('smother.csv', 'r', encoding='utf8') as fh:
    for line in fh.readlines():
        match = re.match(r'(.*):(\d+),(.*)::(.*)::(.*)', line.strip())
        if match:
            dut_filepath = match.group(1)
            dut_path_part_to_strip = '/home/jonas/dev/projects/autonameow.git/autonameow/'
            if dut_filepath.startswith(dut_path_part_to_strip):
                dut_filepath = dut_filepath[len(dut_path_part_to_strip):]

            test_filepath = match.group(3)
            test_path_part_to_strip = 'tests/unit/'
            if test_filepath.startswith(test_path_part_to_strip):
                test_filepath = test_filepath[len(test_path_part_to_strip):]

            visits.append(Visit(
                dut_filepath=dut_filepath,
                dut_linenum=match.group(2),
                test_filepath=test_filepath,
                test_class=match.group(4),
                test_method=match.group(5),
            ))

# for v in visits:
#     print(v)


tests_by_dutpath = defaultdict(Counter)
for v in visits:
    if v.dut_filepath.startswith('vendor/'):
        # Allow unit tests to cover the vendored packages because .....
        continue

    maybe_substring = v.dut_filepath.replace('/', '_')[:-3]
    if maybe_substring in v.test_filepath:
        # Uninteresting case where the unit test covers the file it is supposed to cover .....
        continue

    tests_by_dutpath[v.dut_filepath][v.test_filepath] += 1


def display_simple_results():
    for dutpath, counter in sorted(tests_by_dutpath.items()):
        print('\n' + dutpath)
        for testpath, count in counter.most_common():
            print('    {:6} {}'.format(testpath, count))


def display_worst_offenders():
    results = list()

    for dutpath, counter in sorted(tests_by_dutpath.items()):
        total = sum(c[1] for c in counter.most_common())
        results.append((total, dutpath))

    print('\nDUT FILEPATHS sorted from least to most number of calls from other unit test files than their own')
    for total, dutpath in sorted(results, key=lambda x: x[0]):
        print('{:6} {}'.format(total, dutpath))


display_simple_results()
display_worst_offenders()
