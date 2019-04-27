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

from unittest import TestCase, skip
from unittest.mock import Mock

import unit.constants as uuconst
import unit.utils as uu
from core.evaluate.resolver import dedupe_list_of_databundles
from core.evaluate.resolver import FieldDataCandidate
from core.evaluate.resolver import sort_by_mapped_weights
from core.evaluate.resolver import TemplateFieldDataResolver


class TestDedupeListOfDatabundles(TestCase):
    def _t(self, given, expected):
        from core.datastore.repository import DataBundle

        bundles = [DataBundle.from_dict(g) for g in given]
        actual = dedupe_list_of_databundles(bundles)
        expect = [DataBundle.from_dict(x) for x in expected]
        self.assertEqual(expect, actual)

    def test_dedupes_two_identical_generic_titles(self):
        from core.model import genericfields as gf
        databundle_a = {
            'generic_field': gf.GenericTitle,
            'value': 'Mysticism and Logic and Other Essays'
        }
        databundle_b = {
            'generic_field': gf.GenericTitle,
            'value': 'Mysticism and Logic and Other Essays'
        }
        self._t(given=[databundle_a, databundle_b], expected=[databundle_a])


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
        cls.tfdr = TemplateFieldDataResolver(fo, name_template, None)

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
            generic_field='generic_field_klass'
        )
        actual = repr(fdc)
        self.assertIn('foo', actual)


class TestSortDatadictsByMappingWeights(TestCase):
    @classmethod
    def setUpClass(cls):
        from core.datastore.repository import DataBundle
        from core.model import WeightedMapping
        from core.namebuilder import fields

        cls.fields_Author = fields.Author
        cls.fields_Creator = fields.Creator
        cls.fields_Publisher = fields.Publisher
        cls.fields_Title = fields.Title

        # extractor.metadata.exiftool.XMP:Creator
        cls.d1 = DataBundle.from_dict({
            'mapped_fields': [
                WeightedMapping(cls.fields_Author, weight=0.5),
                WeightedMapping(cls.fields_Creator, weight=1),
                WeightedMapping(cls.fields_Publisher, weight=0.02),
                WeightedMapping(cls.fields_Title, weight=0.01)
            ]
        })
        # extractor.metadata.exiftool.XMP:CreatorFile-as
        cls.d2 = DataBundle.from_dict({
            'mapped_fields': [
                WeightedMapping(cls.fields_Author, weight=0.5),
                WeightedMapping(cls.fields_Creator, weight=1),
                WeightedMapping(cls.fields_Publisher, weight=0.03),
                WeightedMapping(cls.fields_Title, weight=0.02)
            ]
        })
        # extractor.metadata.exiftool.XMP:Contributor
        cls.d3 = DataBundle.from_dict({
            'mapped_fields': [
                WeightedMapping(cls.fields_Author, weight=0.75),
                WeightedMapping(cls.fields_Creator, weight=0.5),
                WeightedMapping(cls.fields_Publisher, weight=0.02),
            ]
        })
        # analyzer.filename.publisher
        cls.d4 = DataBundle.from_dict({
            'mapped_fields': [
                WeightedMapping(cls.fields_Publisher, weight=1),
            ]
        })

    def _check_sorting(self, given, primary_field, secondary_field, expect):
        actual_a = sort_by_mapped_weights(given, primary_field, secondary_field)
        self.assertEqual(expect, actual_a)

        actual_b = sort_by_mapped_weights(list(reversed(given)), primary_field, secondary_field)
        self.assertEqual(expect, actual_b)

    def test_sorting_field_not_in_given_element(self):
        self._check_sorting(
            given=[self.d4],
            primary_field=self.fields_Author,
            secondary_field=None,
            expect=[self.d4]
        )

    def test_one_element_by_mapped_author(self):
        self._check_sorting(
            given=[self.d1],
            primary_field=self.fields_Author,
            secondary_field=None,
            expect=[self.d1]
        )

    def test_two_elements_by_mapped_author_equal_secondary_different(self):
        self._check_sorting(
            given=[self.d1, self.d2],
            primary_field=self.fields_Author,
            secondary_field=self.fields_Title,
            expect=[self.d2, self.d1]
        )

    def test_two_elements_by_mapped_author_one_not_mapped_to_primary(self):
        self._check_sorting(
            given=[self.d1, self.d4],
            primary_field=self.fields_Author,
            secondary_field=None,
            expect=[self.d1, self.d4]
        )
        self._check_sorting(
            given=[self.d1, self.d4],
            primary_field=self.fields_Author,
            secondary_field=self.fields_Creator,  # This should not matter
            expect=[self.d1, self.d4]
        )

    def test_one_element_by_mapped_title(self):
        self._check_sorting(
            given=[self.d1],
            primary_field=self.fields_Title,
            secondary_field=None,
            expect=[self.d1]
        )

    def test_two_elements_by_mapped_title(self):
        self._check_sorting(
            given=[self.d1, self.d2],
            primary_field=self.fields_Title,
            secondary_field=None,
            expect=[self.d2, self.d1]
        )

    def test_two_elements_by_mapped_title_secondary_author_equal(self):
        self._check_sorting(
            given=[self.d1, self.d2],
            primary_field=self.fields_Title,
            secondary_field=self.fields_Author,
            expect=[self.d2, self.d1]
        )
