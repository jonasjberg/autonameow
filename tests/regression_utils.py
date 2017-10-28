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

from core import constants as C
from core import (
    disk,
    util
)


REGRESSIONTESTS_ROOT_ABSPATH = None


class RegressionTestInfo(object):
    BASENAME_ARGS = b'args'
    BASENAME_CONFIG = b'config.yaml'
    BASENAME_DESC = b'description'
    BASENAME_EXPECT = b'expect'
    BASENAME_TESTFILES = b'testfiles'

    def __init__(self):
        self.args = []
        self.description = ''
        self.expect = []
        self.testfiles = []

    @classmethod
    def frompath(cls, abspath):
        # TODO: [TD0117] Implement automated regression tests
        pass


def regtest_abspath(basename):
    _root = get_regressiontests_rootdir()
    try:
        _abspath = os.path.join(
            util.enc.syspath(_root),
            util.enc.syspath(basename)
        )
        _normalized_abspath = util.enc.normpath(_abspath)
    except Exception:
        raise AssertionError

    assert disk.isdir(_normalized_abspath)
    return _normalized_abspath


def get_regressiontests_rootdir():
    global REGRESSIONTESTS_ROOT_ABSPATH
    if not REGRESSIONTESTS_ROOT_ABSPATH:
        _rootdir = os.path.join(
            C.AUTONAMEOW_SRCROOT_DIR, 'test_files', 'regression'
        )
        REGRESSIONTESTS_ROOT_ABSPATH = util.enc.normpath(_rootdir)

    assert disk.isdir(REGRESSIONTESTS_ROOT_ABSPATH)
    return REGRESSIONTESTS_ROOT_ABSPATH
