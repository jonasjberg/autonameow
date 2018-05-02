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
    from hypothesis.strategies import characters
    from hypothesis.strategies import lists
    from hypothesis.strategies import sampled_from
    from hypothesis.strategies import text
    from hypothesis.strategies import tuples
except ImportError:
    raise SkipTest('Unable to import "hypothesis". Skipping ..')

import unit.constants as uuconst
from core.exceptions import InvalidMeowURIError
from core.model import MeowURI
from core.model.meowuri import force_meowuri


class TestMeowURIRaisesOnlyExpectedException(TestCase):
    def _assert_raises_only_expected_exception(self, sample):
        try:
            _ = MeowURI(sample)
        except InvalidMeowURIError:
            pass
        except Exception as e:
            raise AssertionError(
                'MeowURI("{!s}") raised {!s}'.format(sample, e)
            )

    @given(text())
    def test_text_input(self, s):
        self._assert_raises_only_expected_exception(s)

    @given(characters())
    def test_character_input(self, s):
        self._assert_raises_only_expected_exception(s)

    @given(binary())
    def test_binary_input(self, s):
        self._assert_raises_only_expected_exception(s)

    @given(lists(text()))
    def test_lists_of_text_input(self, s):
        self._assert_raises_only_expected_exception(s)

    @given(lists(characters()))
    def test_lists_of_character_input(self, s):
        self._assert_raises_only_expected_exception(s)

    @given(lists(binary()))
    def test_lists_of_binary_input(self, s):
        self._assert_raises_only_expected_exception(s)

    @given(tuples(text()))
    def test_tuples_of_text_input(self, s):
        self._assert_raises_only_expected_exception(s)

    @given(tuples(characters()))
    def test_tuples_of_character_input(self, s):
        self._assert_raises_only_expected_exception(s)

    @given(tuples(binary()))
    def test_tuples_of_binary_input(self, s):
        self._assert_raises_only_expected_exception(s)


class TestForceMeowURIRaisesOnlyExpectedException(TestCase):
    def _assert_returns_meowuri_or_none(self, sample):
        actual = force_meowuri(sample)
        if actual is not None:
            self.assertIsInstance(actual, MeowURI)

    @given(text())
    def test_text_input(self, s):
        self._assert_returns_meowuri_or_none(s)

    @given(characters())
    def test_character_input(self, s):
        self._assert_returns_meowuri_or_none(s)

    @given(binary())
    def test_binary_input(self, s):
        self._assert_returns_meowuri_or_none(s)

    @given(lists(text()))
    def test_lists_of_text_input(self, s):
        self._assert_returns_meowuri_or_none(s)

    @given(lists(characters()))
    def test_lists_of_character_input(self, s):
        self._assert_returns_meowuri_or_none(s)

    @given(lists(binary()))
    def test_lists_of_binary_input(self, s):
        self._assert_returns_meowuri_or_none(s)

    @given(tuples(text()))
    def test_tuples_of_text_input(self, s):
        self._assert_returns_meowuri_or_none(s)

    @given(tuples(characters()))
    def test_tuples_of_character_input(self, s):
        self._assert_returns_meowuri_or_none(s)

    @given(tuples(binary()))
    def test_tuples_of_binary_input(self, s):
        self._assert_returns_meowuri_or_none(s)

    @given(lists(tuples(text())))
    def test_lists_of_tuples_of_text_input(self, s):
        self._assert_returns_meowuri_or_none(s)

    @given(lists(tuples(characters())))
    def test_lists_of_tuples_of_character_input(self, s):
        self._assert_returns_meowuri_or_none(s)

    @given(lists(tuples(binary())))
    def test_lists_of_tuples_of_binary_input(self, s):
        self._assert_returns_meowuri_or_none(s)


class TestMeowURIParsesValidMeowURIs(TestCase):
    def _assert_valid_meowuri(self, sample):
        try:
            m = MeowURI(sample)
        except Exception as e:
            raise AssertionError(
                'MeowURI("{!s}") raised {!s}'.format(sample, e)
            )
        else:
            self.assertIsInstance(m, MeowURI)

    @given(sampled_from(list(uuconst.ALL_FULL_MEOWURIS)))
    def test_full_meowuris_defined_in_unit_test_constants(self, s):
        self._assert_valid_meowuri(s)
