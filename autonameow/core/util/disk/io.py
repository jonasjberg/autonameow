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

import os

from core import (
    exceptions,
    util
)


def isdir(path):
    try:
        return os.path.isdir(util.syspath(path))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)


def isfile(path):
    try:
        return os.path.isfile(util.syspath(path))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)


