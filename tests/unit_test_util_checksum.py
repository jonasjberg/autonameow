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

import unittest
from unittest import TestCase

from core.util import checksum
import unit_utils as uu


TESTFILE_REALLY_BIG_FILE = 'TODO: Insert path to huge file here'


def really_big_testfile_unavailable():
    _file_ok = (
        uu.file_exists(TESTFILE_REALLY_BIG_FILE) and
        uu.path_is_readable(TESTFILE_REALLY_BIG_FILE)
    )
    return _file_ok is None, 'TESTFILE_REALLY_BIG_FILE is not a readable file'


class TestHashlibDigest(TestCase):
    def setUp(self):
        self.testfile_empty = uu.abspath_testfile('empty')

    def test_raises_value_error_given_bad_algorithm(self):
        def _aR(algorithm):
            with self.assertRaises(ValueError):
                checksum.hashlib_digest(self.testfile_empty, algorithm)

        _aR('')
        _aR('sha529')
        _aR('mja003')


class TestSha256Digest(TestCase):
    def setUp(self):
        self.testfile_empty = uu.abspath_testfile('empty')
        self.testfile_magictxt = uu.abspath_testfile('magic_txt.txt')

    def test_returns_expected(self):
        a = checksum.sha256digest(self.testfile_empty)
        self.assertEqual(
            a,
            'e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855'
        )

        b = checksum.sha256digest(self.testfile_magictxt)
        self.assertEqual(
            b,
            'b9e68e1bea3e5b19ca6b2f98b73a54b73daafaa250484902e09982e07a12e733'
        )

    def test_returns_expected_type(self):
        a = checksum.sha256digest(self.testfile_empty)
        self.assertTrue(uu.is_internalstring(a))

        b = checksum.sha256digest(self.testfile_magictxt)
        self.assertTrue(uu.is_internalstring(b))

    def test_returns_unique_values(self):
        a = checksum.sha256digest(self.testfile_empty)
        b = checksum.sha256digest(self.testfile_magictxt)

        self.assertNotEqual(a, b)

    @unittest.skipIf(*really_big_testfile_unavailable())
    def test_big_file(self):
        a = checksum.sha256digest(TESTFILE_REALLY_BIG_FILE)
        self.assertTrue(uu.is_internalstring(a))


