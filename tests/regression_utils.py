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
import re

from core import constants as C
from core import (
    disk,
    exceptions,
    util
)
from core.util import enc


class RegressionTestError(exceptions.AutonameowException):
    """Error caused by an invalid regression test."""


# TODO: [TD0117] Implement automated regression tests


def read_plaintext_file(file_path):
    try:
        with open(file_path, 'r', encoding=C.DEFAULT_ENCODING) as fh:
            contents = fh.read()
    except (FileNotFoundError, UnicodeDecodeError) as e:
        raise RegressionTestError(e)
    else:
        return contents


class RegressionTestInfo(object):
    BASENAME_ARGS = b'args'
    BASENAME_DESCRIPTION = b'description'
    BASENAME_YAML_RENAMES = b'params.yaml'
    BASENAME_YAML_CONFIGFILE = b'config.yaml'

    def __init__(self, description):
        self.args = []

        assert isinstance(description, str)
        self.description = description.rstrip()

    @classmethod
    def frompath(cls, abspath):
        _desc_abspath = os.path.join(enc.syspath(abspath),
                                     enc.syspath(cls.BASENAME_DESCRIPTION))
        _description = read_plaintext_file(_desc_abspath)
        return cls(description=_description)


REGRESSIONTESTS_ROOT_ABSPATH = None


def get_regressiontests_rootdir():
    global REGRESSIONTESTS_ROOT_ABSPATH
    if not REGRESSIONTESTS_ROOT_ABSPATH:
        _rootdir = os.path.join(
            C.AUTONAMEOW_SRCROOT_DIR, 'test_files', 'regression'
        )
        REGRESSIONTESTS_ROOT_ABSPATH = util.enc.normpath(_rootdir)

    assert disk.isdir(REGRESSIONTESTS_ROOT_ABSPATH)
    return REGRESSIONTESTS_ROOT_ABSPATH


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


RE_REGRESSIONTEST_DIRNAME = re.compile(rb'\d{4}(_[\w]+)?')


def get_regressiontest_dirs():
    _tests_root_dir = get_regressiontests_rootdir()
    _dirs = [
        regtest_abspath(d)
        for d in os.listdir(_tests_root_dir)
        if RE_REGRESSIONTEST_DIRNAME.match(d)
    ]

    return _dirs

