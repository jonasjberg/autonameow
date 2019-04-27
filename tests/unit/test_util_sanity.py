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

from unittest import TestCase

import unit.utils as uu
from unit import constants as uuconst
from util import sanity


class TestCheckIsinstanceMeowuri(TestCase):
    def test_check_passes(self):
        def _assert_valid(test_input):
            sanity.check_isinstance_meowuri(test_input)
            sanity.check_isinstance_meowuri(test_input, msg='foo')

        from core.model import MeowURI
        _assert_valid(MeowURI(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE))
        _assert_valid(MeowURI(uuconst.MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE))
        _assert_valid(MeowURI(uuconst.MEOWURI_FS_FILETAGS_EXTENSION))

    def test_raises_exception_for_not_instances_of_meowuri(self):
        def _assert_raises(test_input):
            with self.assertRaises(AssertionError):
                sanity.check_isinstance_meowuri(test_input)

            with self.assertRaises(AssertionError):
                sanity.check_isinstance_meowuri(test_input, msg='foo')

        _assert_raises(None)
        _assert_raises(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        _assert_raises(uuconst.MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE)
        _assert_raises(uuconst.MEOWURI_FS_FILETAGS_EXTENSION)


class TestCheckIsinstanceFileObject(TestCase):
    def test_check_passes(self):
        def _assert_valid(test_input):
            sanity.check_isinstance_fileobject(test_input)
            sanity.check_isinstance_fileobject(test_input, msg='foo')

        _assert_valid(uu.fileobject_testfile('empty'))

    def test_raises_exception_for_not_instances_of_fileobject(self):
        def _assert_raises(test_input):
            with self.assertRaises(AssertionError):
                sanity.check_isinstance_fileobject(test_input)

            with self.assertRaises(AssertionError):
                sanity.check_isinstance_fileobject(test_input, msg='foo')

        _assert_raises(None)
        _assert_raises('foo')
        _assert_raises(object())
