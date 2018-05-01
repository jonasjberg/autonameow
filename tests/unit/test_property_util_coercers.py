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

from unittest import SkipTest, TestCase

try:
    from hypothesis import given
    from hypothesis.strategies import binary
    from hypothesis.strategies import booleans
    from hypothesis.strategies import characters
    from hypothesis.strategies import integers
    from hypothesis.strategies import text
except ImportError:
    raise SkipTest('Unable to import "hypothesis". Skipping ..')

from util import coercers


class TestForceStringRaisesOnlyExpectedException(TestCase):
    @given(text())
    def test_text_input(self, s):
        try:
            _ = coercers.force_string(s)
        except coercers.AWTypeError:
            pass
        except Exception as e:
            raise AssertionError('force_string("{!s}") raised: {!s}'.format(s,
                                                                            e))

    @given(characters())
    def test_character_input(self, s):
        try:
            _ = coercers.force_string(s)
        except coercers.AWTypeError:
            pass
        except Exception as e:
            raise AssertionError('force_string("{!s}") raised: {!s}'.format(s,
                                                                            e))

    @given(binary())
    def test_binary_input(self, s):
        try:
            _ = coercers.force_string(s)
        except coercers.AWTypeError:
            pass
        except Exception as e:
            raise AssertionError('force_string("{!s}") raised: {!s}'.format(s,
                                                                            e))


class TestCoerceString(TestCase):
    @given(text())
    def test_text_input(self, s):
        self.assertIsInstance(s, str, 'Expected hypothesis data of type str')

        coerced_string = coercers.AW_STRING(s)
        self.assertIsInstance(coerced_string, str)
        self.assertEqual(coerced_string, s)

    @given(characters())
    def test_character_input(self, s):
        self.assertIsInstance(s, str, 'Expected hypothesis data of type str')

        coerced_string = coercers.AW_STRING(s)
        self.assertIsInstance(coerced_string, str)
        self.assertEqual(coerced_string, s)

    @given(binary())
    def test_binary_input_raises_only_expected_exception(self, s):
        try:
            _ = coercers.AW_STRING(s)
        except coercers.AWTypeError:
            pass
        except Exception as e:
            raise AssertionError('AW_STRING("{!s}") raised: {!s}'.format(s, e))

    @given(integers())
    def test_integer_input(self, s):
        coerced_string = coercers.AW_STRING(s)
        self.assertIsInstance(coerced_string, str)
        self.assertEqual(coerced_string, str(s))

    @given(booleans())
    def test_boolean_input(self, s):
        coerced_string = coercers.AW_STRING(s)
        self.assertIsInstance(coerced_string, str)
        self.assertIn(coerced_string, ('True', 'False'))
