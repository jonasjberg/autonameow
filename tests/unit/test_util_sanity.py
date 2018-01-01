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

from unittest import TestCase

from core import constants as C
from core.exceptions import EncodingBoundaryViolation
from util import sanity


class TestSanityCheckInternalBytestring(TestCase):
    def test_check_passes(self):
        def _assert_valid(test_input):
            sanity.check_internal_bytestring(test_input)

        _assert_valid(b'')
        _assert_valid(b'foo')

    def test_raises_exception_for_non_bytes_values(self):
        def _assert_raises(test_input):
            with self.assertRaises(EncodingBoundaryViolation):
                sanity.check_internal_bytestring(test_input)

        _assert_raises(None)
        _assert_raises('')
        _assert_raises('foo')


class TestSanityCheckInternalString(TestCase):
    def test_check_passes(self):
        def _assert_valid(test_input):
            sanity.check_internal_string(test_input)

        _assert_valid('')
        _assert_valid('foo')
        _assert_valid(b'foo'.decode(C.DEFAULT_ENCODING))

    def test_raises_exception_for_non_bytes_values(self):
        def _assert_raises(test_input):
            with self.assertRaises(EncodingBoundaryViolation):
                sanity.check_internal_string(test_input)

        _assert_raises(None)
        _assert_raises(b'')
        _assert_raises(b'foo')
