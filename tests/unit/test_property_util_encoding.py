# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

from unittest import SkipTest, TestCase

try:
    from hypothesis import given
    from hypothesis import strategies as st
except ImportError:
    raise SkipTest('Unable to import "hypothesis". Skipping ..')

from util.encoding import decode_
from util.encoding import displayable_path
from util.encoding import encode_


class TestEncodeDoesNotRaiseException(TestCase):
    def _assert_noraise(self, s):
        try:
            _ = encode_(s)
        except Exception as e:
            raise AssertionError('encode_("{!s}") raised: {!s}'.format(s, e))

    @given(st.text())
    def test_text_input(self, s):
        self._assert_noraise(s)

    @given(st.characters())
    def test_character_input(self, s):
        self._assert_noraise(s)

    @given(st.binary())
    def test_binary_input(self, s):
        self._assert_noraise(s)


class TestDecodeDoesNotRaiseException(TestCase):
    def _assert_noraise(self, s):
        try:
            _ = decode_(s)
        except Exception as e:
            raise AssertionError('decode_("{!s}") raised: {!s}'.format(s, e))

    @given(st.text())
    def test_text_input(self, s):
        self._assert_noraise(s)

    @given(st.characters())
    def test_character_input(self, s):
        self._assert_noraise(s)

    @given(st.binary())
    def test_binary_input(self, s):
        self._assert_noraise(s)


class TestRoundtripEncodeDecode(TestCase):
    @given(st.text())
    def test_decode_inverts_encode_given_text_input(self, s):
        self.assertEqual(decode_(encode_(s)), s)

    @given(st.text())
    def test_decode_inverts_encode_inverts_decode_given_text_input(self, s):
        self.assertEqual(decode_(encode_(decode_(s))), s)

    # @given(st.binary())
    # def test_decode_inverts_encode_given_binary_input(self, s):
    #     self.assertEqual(decode_(encode_(s)), s)

    # @given(st.binary())
    # def test_encode_inverts_decode_given_binary_input(self, s):
    #     self.assertEqual(encode_(decode_(s)), s)


class TestDisplayablePath(TestCase):
    def _assert_noraise(self, s):
        try:
            _ = displayable_path(s)
        except Exception as e:
            raise AssertionError('displayable_path("{!s}") raised: {!s}'.format(s, e))

    def _assert_return_type_str(self, s):
        actual = displayable_path(s)
        self.assertIsInstance(actual, str)

    @given(st.binary())
    def test_does_not_raise_exception_given_binary_input(self, s):
        self._assert_noraise(s)

    @given(st.characters())
    def test_does_not_raise_exception_given_character_input(self, s):
        self._assert_noraise(s)

    @given(st.text())
    def test_does_not_raise_exception_given_string_input(self, s):
        self._assert_noraise(s)

    @given(st.binary())
    def test_returns_value_of_type_str_given_binary_input(self, s):
        self._assert_return_type_str(s)

    @given(st.characters())
    def test_returns_value_of_type_str_given_character_input(self, s):
        self._assert_return_type_str(s)

    @given(st.text())
    def test_returns_value_of_type_str_given_string_input(self, s):
        self._assert_return_type_str(s)
