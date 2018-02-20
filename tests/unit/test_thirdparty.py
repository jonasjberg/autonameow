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

from unittest import TestCase

import unit.utils as uu
import unit.constants as uuconst


THIRDPARTY_ROOT_DIR = os.path.join(uuconst.PATH_AUTONAMEOW_SRCROOT, 'thirdparty')


class TestThirdPartyPath(TestCase):
    def test_thirdparty_root_dir_exists(self):
        self.assertTrue(uu.dir_exists(THIRDPARTY_ROOT_DIR))

    def test_thirdparty_root_dir_is_readable(self):
        self.assertTrue(uu.path_is_readable(THIRDPARTY_ROOT_DIR))


class TestThirdPartyImports(TestCase):
    def test_import_or_return_none_pyexiftool(self):
        from thirdparty import pyexiftool as _
