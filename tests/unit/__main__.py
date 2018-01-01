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

import os
import unittest

from unit import build_testsuite


runner = unittest.TextTestRunner(verbosity=1, buffer=True)

# suite_all_tests = build_testsuite()
suite_excluding_property_based_tests = build_testsuite(
    filename_filter=lambda x: not x.startswith('test_property_')
)


# print('Loaded {} all test cases ..'.format(suite_all_tests.countTestCases()))
print('Loaded {} test cases. Excluded property-based tests..'.format(suite_excluding_property_based_tests.countTestCases()))

os.chdir(os.pardir)
runner.run(suite_excluding_property_based_tests)
