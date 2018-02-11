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
import sys

"""
Interface to third-party code stored under the 'thirdparty' directory.

Auxiliary code included as Git submodules might be missing or the code might
be broken in some other way. Always import third-party modules from this file.
"""


THIRDPARTY_ROOT_DIR = os.path.dirname(os.path.realpath(__file__))


try:
    from .pyexiftool import exiftool as pyexiftool
except ImportError:
    pyexiftool = None


MODULE_NAMEPARSER_DIR = 'nameparser'
_nameparser_path = os.path.join(THIRDPARTY_ROOT_DIR, MODULE_NAMEPARSER_DIR)

if os.path.isdir(_nameparser_path):
    sys.path.insert(0, _nameparser_path)

    try:
        import nameparser
    except ImportError:
        nameparser = None
else:
    nameparser = None
