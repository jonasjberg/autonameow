#!/usr/bin/env python
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
import logging


log = logging.getLogger(__name__)


class InteractiveCLI(object):
    # TODO: Implement this class.
    def __init__(self):
        pass

    def confirm(self, question):
        while True:
            # Possibly redundant check for Python 2.
            # TODO: Assume running with Python 3+. Add checks/asserts elsewhere.
            if sys.version_info[0] < 3:
                log.warning('Using potentially unsafe Python 2 "raw_input"')
                answer = raw_input(question + ' [Yes|No]').lower()
            else:
                answer = input(question + ' (Yes|No)').lower()

            if answer == 'yes' or answer == 'y':
                confirmed = True
                break
            if answer == 'no' or answer == 'n':
                confirmed = False
                break

        return confirmed
