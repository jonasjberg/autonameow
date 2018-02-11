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

from unittest import TestCase, skip
from unittest.mock import Mock

import unit.constants as uuconst
import unit.utils as uu
from core.evaluate.resolver import (
    dedupe_list_of_databundles,
    FieldDataCandidate,
    TemplateFieldDataResolver
)


@skip('TODO: Fix or remove')
class TestDedupeListOfDatabundles(TestCase):
    def _t(self, given, expect):
        from core.repository import DataBundle

        bundles = [DataBundle.from_dict(g) for g in given]
        actual = dedupe_list_of_databundles(bundles)
        self.assertEqual(actual, expect)

    def test_returns_list_with_one_element_as_is(self):
        self._t(given=['A'], expect=['A'])

    def test_returns_list_of_only_unique_values_as_is(self):
        self._t(given=['A', 'B'], expect=['A', 'B'])

    def test_dedupes_two_equivalent_values(self):
        self._t(given=['A', 'A'], expect=['A'])

    def test_dedupes_three_equivalent_values(self):
        self._t(given=['A', 'A', 'A'], expect=['A'])

    def test_dedupes_two_duplicate_values_and_returns_one_as_is(self):
        self._t(given=['A', 'B', 'A'], expect=['A', 'b'])


@skip('TODO: Fix or remove')
class TestDedupeListOfDatadictsContainingMultipleValues(TestCase):
    def _t(self, given, expect):
        actual = dedupe_list_of_databundles(given)
        self.assertEqual(actual, expect)

    def test_returns_one_dict_with_one_list_element_as_is(self):
        self._t(
            given=[{'value': ['A']}],
            expect=[{'value': ['A']}]
        )

    def test_returns_two_dicts_with_one_unique_list_element_each_as_is(self):
        self._t(
            given=[{'value': ['A']}, {'value': ['B']}],
            expect=[{'value': ['A']}, {'value': ['B']}]
        )

    def test_dedupes_two_dicts_with_one_list_element_equivalent_values(self):
        self._t(
            given=[{'value': ['A']}, {'value': ['A']}],
            expect=[{'value': ['A']}]
        )

    def test_dedupes_three_dicts_one_list_element_equivalent_values(self):
        self._t(
            given=[{'value': ['A']}, {'value': ['A']}, {'value': ['A']}],
            expect=[{'value': ['A']}]
        )

    def test_dedupes_three_dicts_two_duplicate_values_one_unique(self):
        self._t(
            given=[{'value': ['A']}, {'value': ['B']}, {'value': ['A']}],
            expect=[{'value': ['A']}, {'value': ['B']}]
        )

    def test_dedupes_three_dicts_two_duplicate_values_one_unique_A(self):
        self._t(
            given=[{'value': ['A', 'B']}, {'value': ['C']},
                   {'value': ['B', 'A']}],
            expect=[{'value': ['A', 'B']}, {'value': ['C']}]
        )

    def test_dedupes_three_dicts_two_duplicate_values_one_unique_B(self):
        self._t(
            given=[{'value': ['A', 'B']}, {'value': ['C']},
                   {'value': ['A', 'B']}],
            expect=[{'value': ['A', 'B']}, {'value': ['C']}]
        )

    def test_returns_list_with_two_elements_as_is(self):
        self._t(
            given=[{'value': ['A', 'B']}],
            expect=[{'value': ['A', 'B']}]
        )

    def test_returns_two_dicts_two_elements_in_different_order_as_is(self):
        self._t(
            given=[{'value': ['A', 'B']}, {'value': ['B', 'A']}],
            expect=[{'value': ['A', 'B']}]
        )

    def test_returns_two_dicts_diff_number_of_unique_list_elements_as_is(self):
        self._t(
            given=[{'value': ['A', 'B']}, {'value': ['C']}],
            expect=[{'value': ['A', 'B']}, {'value': ['C']}]
        )

    def test_returns_two_dicts_with_diff_number_of_list_elements_as_is(self):
        self._t(
            given=[{'value': ['A', 'B']}, {'value': ['A']}],
            expect=[{'value': ['A', 'B']}, {'value': ['A']}]
        )


@skip('TODO: Fix or remove')
class TestTemplateFieldDataResolverTypeAssertions(TestCase):
    @classmethod
    def setUpClass(cls):
        fo = uu.get_mock_fileobject()
        name_template = '{datetime} {title}.{extension}',
        cls.tfdr = TemplateFieldDataResolver(fo, name_template)

    def test_add_known_source_not_given_instance_of_meowuri(self):
        mock_field = Mock()
        invalid_meowuri = uuconst.MEOWURI_FS_XPLAT_MIMETYPE
        with self.assertRaises(AssertionError):
            self.tfdr.add_known_source(mock_field, invalid_meowuri)

    def test_add_known_source_not_given_none_meowuri(self):
        mock_field = Mock()
        invalid_meowuri = None
        with self.assertRaises(AssertionError):
            self.tfdr.add_known_source(mock_field, invalid_meowuri)


class TestFieldDataCandidate(TestCase):
    def test___repr__(self):
        fdc = FieldDataCandidate(
            string_value='foo',
            source='klass',
            probability=0.01,
            meowuri='meowuri',
            coercer='coercer',
            generic_field='generic_field_klass'
        )
        actual = repr(fdc)
        self.assertIn('foo', actual)
