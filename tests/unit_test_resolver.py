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

import unit_utils as uu
from core.evaluate.resolver import dedupe_list_of_datadicts


class TestDedupeListOfDatadicts(TestCase):
    def _t(self, given, expect):
        actual = dedupe_list_of_datadicts(given)
        self.assertEqual(actual, expect)

    def test_dedupes_list_with_one_element(self):
        self._t(
            given=[{'value': 'foo'}],
            expect=[{'value': 'foo'}]
        )

    def test_dedupes_two_equivalent_values(self):
        self._t(
            given=[{'value': 'foo'}, {'value': 'foo'}],
            expect=[{'value': 'foo'}]
        )

    def test_dedupes_three_equivalent_values(self):
        given = [{'value': 'foo'}, {'value': 'foo'}, {'value': 'foo'}]
        expect = [{'value': 'foo'}]
        actual = dedupe_list_of_datadicts(given)
        self.assertEqual(actual, expect)

        self._t(
            given=[{'value': 'foo'}, {'value': 'foo'}, {'value': 'foo'}],
            expect=[{'value': 'foo'}]
        )

    def test_returns_list_of_only_unique_values_as_is(self):
        given = [{'value': 'foo'}, {'value': 'bar'}]
        expect = [{'value': 'foo'}, {'value': 'bar'}]
        actual = dedupe_list_of_datadicts(given)
        self.assertEqual(actual, expect)

        self._t(
            given=[{'value': 'foo'}, {'value': 'bar'}],
            expect=[{'value': 'foo'}, {'value': 'bar'}]
        )

    def test_dedupes_two_duplicate_values_and_returns_one_as_is(self):
        given = [{'value': 'foo'}, {'value': 'bar'}, {'value': 'foo'}]
        expect = [{'value': 'foo'}, {'value': 'bar'}]
        actual = dedupe_list_of_datadicts(given)
        self.assertEqual(actual, expect)

        self._t(
            given=[{'value': 'foo'}, {'value': 'bar'}, {'value': 'foo'}],
            expect=[{'value': 'foo'}, {'value': 'bar'}]
        )
