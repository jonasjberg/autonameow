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

"""
Allow user to run Autonameow as a module from a directory or zip file.
Execute with:

  $ python autonameow/__main__.py (2.6)
  $ python -m autonameow          (2.7+)

"""

import sys
from core.autonameow import Autonameow

if __package__ is None and not hasattr(sys, 'frozen'):
    # It is a direct call to __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))

if __name__ == '__main__':
    try:
        autonameow = Autonameow(sys.argv[1:])
        autonameow.run()
    except KeyboardInterrupt:
        sys.exit('\nReceived keyboard interrupt; Exiting ..')
