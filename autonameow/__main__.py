#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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

"""
Main autonameow entry point.

Execute autonameow by running either;

  python3 autonameow/__main__.py

Or, as a module;

  PYTHONPATH=autonameow python3 -m autonameow

"""

import sys


if __package__ is None and not hasattr(sys, 'frozen'):
    # It is a direct call to this file ('__main__.py')
    import os
    SELF_ABSPATH = os.path.realpath(os.path.abspath(__file__))
    sys.path.insert(0, os.path.dirname(os.path.dirname(SELF_ABSPATH)))


if __name__ == '__main__':
    from core.main import cli_main
    cli_main(argv=sys.argv[1:])
