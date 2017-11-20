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

from unittest import TestCase

try:
    from hypothesis import given
    from hypothesis.strategies import (
        binary,
        characters,
        text
    )
except ImportError:
    hypothesis = None
# TODO: Skip tests if 'hypothesis' is unavailable.

from core import types


class TestForceStringRaisesOnlyExpectedException(TestCase):
    @given(text())
    def test_text_input(self, s):
        try:
            coerced_string = types.force_string(s)
        except types.AWTypeError:
            return
        except Exception as e:
            raise AssertionError('force_string("{!s}") raised: {!s}'.format(s,
                                                                            e))

    @given(characters())
    def test_character_input(self, s):
        try:
            coerced_string = types.force_string(s)
        except types.AWTypeError:
            return
        except Exception as e:
            raise AssertionError('force_string("{!s}") raised: {!s}'.format(s,
                                                                            e))

    @given(binary())
    def test_binary_input(self, s):
        try:
            coerced_string = types.force_string(s)
        except types.AWTypeError:
            return
        except Exception as e:
            raise AssertionError('force_string("{!s}") raised: {!s}'.format(s,
                                                                            e))


class TestCoerceString(TestCase):
    @given(text())
    def test_text_input(self, s):
        coerced_string = types.AW_STRING(s)
        self.assertEqual(coerced_string, s)

    @given(characters())
    def test_character_input(self, s):
        coerced_string = types.AW_STRING(s)
        self.assertEqual(coerced_string, s)
