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

import os
import sys

_self_dirpath = os.path.abspath(
    os.path.dirname(os.path.realpath(__file__))
)
VENDOR_DIRPATH = os.path.normpath(os.path.join(
    _self_dirpath, os.path.pardir, 'vendor'
))
assert os.access(VENDOR_DIRPATH, os.R_OK | os.X_OK), (
    'Expected readable directory at path "{}"'.format(VENDOR_DIRPATH)
)
sys.path.insert(0, VENDOR_DIRPATH)

from . import version
from .fileobject import FileObject
