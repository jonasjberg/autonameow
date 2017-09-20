#!/usr/bin/env python3
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
Execute autonameow by running either one of;

  $ python3 autonameow/__main__.py
  $ python3 -m autonameow

"""

import sys

from core.exceptions import AWAssertionError
from core.main import Autonameow

if __package__ is None and not hasattr(sys, 'frozen'):
    # It is a direct call to __main__.py
    import os.path
    path = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(path)))


def print_error(message):
    print(message, file=sys.stderr)


if __name__ == '__main__':
    try:
        autonameow = Autonameow(sys.argv[1:])
        autonameow.run()
    except KeyboardInterrupt:
        sys.exit('\nReceived keyboard interrupt; Exiting ..')
    except AWAssertionError as e:
        print_error('******************************************************')
        print_error('             INTERNAL SANITY-CHECK FAILED')
        print_error('Something that really should NOT happen just happened!')
        print_error('******************************************************')
        print_error('')
        print_error('This is most likely a BUG that should be reported ..')
        print_error('.. TODO: Information on how to report issues.')
        print_error('')
        print_error('')
        print_error(str(e))
        sys.exit(3)
