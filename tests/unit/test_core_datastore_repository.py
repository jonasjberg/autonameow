# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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
from unittest.mock import Mock

import unit.constants as uuconst
import unit.utils as uu
from core.datastore.query import QueryResponseFailure
from core.datastore.repository import DataBundle
from core.datastore.repository import Repository


class TestRepositoryRetrieval(TestCase):
    def setUp(self):
        self.r = Repository()
        mock_fileobject = Mock()
        mock_fileobject.hash_partial = '123456789'
        self.fo = mock_fileobject

    def test_query_with_none_meowuri_returns_query_response_failure(self):
        actual = self.r.query(self.fo, None)
        self.assertFalse(actual)
        self.assertIsInstance(actual, QueryResponseFailure)

    def test_query_for_non_existent_data_returns_query_response_failure(self):
        actual = self.r.query(self.fo,
                              uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE))
        self.assertFalse(actual)
        self.assertIsInstance(actual, QueryResponseFailure)


class TestRepositoryStorage(TestCase):
    def setUp(self):
        self.r = Repository()
        self.fileobject = uu.get_mock_fileobject(mime_type='text/plain')

    def test_repository_init_in_expected_state(self):
        self.assertIsInstance(self.r._data, dict)
        self.assertEqual(len(self.r), 0)

    def test_storing_data_increments_len(self):
        valid_uri = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        self.r.store(self.fileobject, valid_uri, {'value': 'foo'})
        self.assertEqual(len(self.r), 1)

    def test_storing_data_with_different_meowuris_increments_len(self):
        first_valid_uri = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        self.r.store(self.fileobject, first_valid_uri, {'value': 'foo'})
        self.assertEqual(len(self.r), 1)

        second_valid_uri = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        self.r.store(self.fileobject, second_valid_uri, {'value': 'foo'})
        self.assertEqual(len(self.r), 2)

    def test_adding_data_with_same_meowuri_increments_len(self):
        first_valid_uri = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        self.r.store(self.fileobject, first_valid_uri, {'value': 'foo'})
        self.assertEqual(len(self.r), 1)

        second_valid_uri = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        self.r.store(self.fileobject, second_valid_uri, {'value': 'foo'})
        self.assertEqual(len(self.r), 2)

    def test_adding_one_result_increments_len_once(self):
        _field = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        _results = {'value': 'foo'}
        self.r.store(self.fileobject, _field, _results)

        self.assertEqual(len(self.r), 1)

    def test_adding_two_results_increments_len_twice(self):
        _field_one = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        _field_two = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        _result_one = {'value': 'foo'}
        _result_two = {'value': 'bar'}
        self.r.store(self.fileobject, _field_one, _result_one)
        self.r.store(self.fileobject, _field_two, _result_two)

        self.assertEqual(len(self.r), 2)

    def test_adding_one_result_for_two_files_increments_len_twice(self):
        _field = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        _results = {'value': 'foo'}

        fo_A = self.fileobject
        fo_B = uu.get_mock_fileobject(mime_type='image/jpeg')
        self.r.store(fo_A, _field, _results)
        self.r.store(fo_B, _field, _results)

        self.assertEqual(len(self.r), 2)

    def test_adding_two_results_for_two_files_increments_len_four_times(self):
        _field_one = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        _field_two = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        _result_one = {'value': 'foo'}
        _result_two = {'value': 'bar'}

        fo_A = self.fileobject
        fo_B = uu.get_mock_fileobject(mime_type='image/jpeg')
        self.r.store(fo_A, _field_one, _result_one)
        self.r.store(fo_A, _field_two, _result_two)
        self.r.store(fo_B, _field_one, _result_one)
        self.r.store(fo_B, _field_two, _result_two)

        self.assertEqual(len(self.r), 4)

    def test_add_empty_does_not_increment_len(self):
        _field = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        _results = list()
        self.r.store(self.fileobject, _field, _results)

        self.assertEqual(len(self.r), 0)

    def test_store_data_with_invalid_meowuri_raises_error(self):
        with self.assertRaises(AssertionError):
            self.r.store(self.fileobject, None, {'value': 'foo'})

        with self.assertRaises(AssertionError):
            self.r.store(self.fileobject, '', {'value': 'foo'})

    def test_stores_data_with_valid_meowuri(self):
        meowuris = [
            uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME),
            uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE),
            uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)
        ]
        for valid_uri in meowuris:
            self.r.store(self.fileobject, valid_uri, {'value': 'foo'})

    def test_valid_meowuri_returns_expected_data(self):
        valid_uri = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        self.r.store(self.fileobject, valid_uri, {'value': 'expected_data'})

        response = self.r.query(self.fileobject, valid_uri)
        self.assertEqual(response.value, 'expected_data')

    def test_none_meowuri_returns_query_response_failure(self):
        valid_uri = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        self.r.store(self.fileobject, valid_uri, {'value': 'foo'})

        response = self.r.query(self.fileobject, None)
        self.assertFalse(response)
        self.assertIsInstance(response, QueryResponseFailure)

    def test_valid_meowuris_returns_expected_data(self):
        uri_A = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME)
        uri_B = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_TITLE)
        self.r.store(self.fileobject, uri_A, {'value': 'foo'})
        self.r.store(self.fileobject, uri_B, {'value': 'bar'})

        response_A = self.r.query(self.fileobject, uri_A)
        self.assertEqual('foo', response_A.value)
        response_B = self.r.query(self.fileobject, uri_B)
        self.assertEqual('bar', response_B.value)


class TestRepositoryGenericToExplicitMeowURIMapping(TestCase):
    @classmethod
    def setUpClass(cls):
        from core.model.genericfields import GenericTitle
        cls.generic_title = GenericTitle

    def setUp(self):
        self.r = Repository()
        self.fo = uu.get_mock_fileobject(mime_type='text/plain')

    def test_storing_data_with_explicit_uri_is_returned_with_generic_query(self):
        data = {
            'value': 'MEow MEOW',
            'generic_field': self.generic_title(),
        }
        explicit_uri = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCTITLE)
        self.r.store(self.fo, explicit_uri, data)

        generic_uri = uu.as_meowuri(uuconst.MEOWURI_GEN_METADATA_TITLE)
        response = self.r.query(self.fo, generic_uri)
        self.assertEqual('MEow MEOW', response[0].value)

    def test_all_stored_data_with_explicit_uris_is_returned_with_generic_query(self):
        data_A = {
            'value': 'MEOW',
            'generic_field': self.generic_title(),
        }
        explicit_uri_A = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCTITLE)
        self.r.store(self.fo, explicit_uri_A, data_A)

        data_B = {
            'value': 'Gibson RULES ..meow',
            'generic_field': self.generic_title(),
        }
        explicit_uri_B = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_PDFTITLE)
        self.r.store(self.fo, explicit_uri_B, data_B)

        generic_uri = uu.as_meowuri(uuconst.MEOWURI_GEN_METADATA_TITLE)
        response = self.r.query(self.fo, generic_uri)
        response_values = [databundle.value for databundle in response]
        self.assertEqual(2, len(response_values))
        self.assertIn('MEOW', response_values)
        self.assertIn('Gibson RULES ..meow', response_values)


class TestRepositoryRetrievalWithGenericLeafAlias(TestCase):
    @classmethod
    def setUpClass(cls):
        from core.model.genericfields import GenericTitle
        cls.generic_title = GenericTitle

    def setUp(self):
        self.r = Repository()
        self.fo = uu.get_mock_fileobject(mime_type='text/plain')

    def test_stored_data_with_explicit_uri_retrieved_with_leaf_alias(self):
        data = {
            'value': 'meow',
            'generic_field': self.generic_title(),
        }
        explicit_uri = uu.as_meowuri('extractor.metadata.exiftool.XMP-dc:Title')
        self.r.store(self.fo, explicit_uri, data)

        leaf_alias_uri = uu.as_meowuri('extractor.metadata.exiftool.title')
        response = self.r.query(self.fo, leaf_alias_uri)
        self.assertEqual('meow', response[0].value)

    def test_all_stored_data_with_explicit_uris_retrieved_with_leaf_alias(self):
        data_A = {
            'value': 'meow',
            'generic_field': self.generic_title(),
        }
        explicit_uri_A = uu.as_meowuri('extractor.metadata.exiftool.XMP-dc:Title')
        self.r.store(self.fo, explicit_uri_A, data_A)

        data_B = {
            'value': 'gibson rules',
            'generic_field': self.generic_title(),
        }
        explicit_uri_B = uu.as_meowuri('extractor.metadata.exiftool.PDF:Title')
        self.r.store(self.fo, explicit_uri_B, data_B)

        leaf_alias_uri = uu.as_meowuri('extractor.metadata.exiftool.title')
        response = self.r.query(self.fo, leaf_alias_uri)
        response_values = [databundle.value for databundle in response]
        self.assertEqual(2, len(response_values))
        self.assertIn('meow', response_values)
        self.assertIn('gibson rules', response_values)


class TestDataBundle(TestCase):
    @classmethod
    def setUpClass(cls):
        from core.model import WeightedMapping
        from core.namebuilder import fields

        cls.fields_Author = fields.Author
        cls.fields_Creator = fields.Creator
        cls.fields_Publisher = fields.Publisher
        cls.fields_Title = fields.Title

        # analyzer.filename.publisher
        cls.d1 = DataBundle.from_dict({
            'mapped_fields': [
                WeightedMapping(cls.fields_Publisher, weight=1),
            ]
        })
        # extractor.metadata.exiftool.XMP:Creator
        cls.d2 = DataBundle.from_dict({
            'mapped_fields': [
                WeightedMapping(cls.fields_Author, weight=0.5),
                WeightedMapping(cls.fields_Creator, weight=1),
                WeightedMapping(cls.fields_Publisher, weight=0.02),
                WeightedMapping(cls.fields_Title, weight=0.01)
            ]
        })

    def test_field_mapping_weight_returns_default_value(self):
        self.assertEqual(0.0, self.d1.field_mapping_weight(None))
        self.assertEqual(0.0, self.d1.field_mapping_weight(False))
        self.assertEqual(0.0, self.d1.field_mapping_weight(list()))

    def test_field_mapping_weight_d1(self):
        for field in (self.fields_Author, self.fields_Creator,
                      self.fields_Title):
            with self.subTest(field=str(field)):
                actual = self.d1.field_mapping_weight(field)
                self.assertEqual(0.0, actual)

        self.assertEqual(
            1.0, self.d1.field_mapping_weight(self.fields_Publisher)
        )

    def test_field_mapping_weight_d2(self):
        self.assertEqual(
            0.5, self.d2.field_mapping_weight(self.fields_Author)
        )
        self.assertEqual(
            1, self.d2.field_mapping_weight(self.fields_Creator)
        )
        self.assertEqual(
            0.02, self.d2.field_mapping_weight(self.fields_Publisher)
        )
        self.assertEqual(
            0.01, self.d2.field_mapping_weight(self.fields_Title)
        )


class TestDataBundleComparison(TestCase):
    @classmethod
    def setUpClass(cls):
        mock_coercer = Mock()
        mock_source = Mock()
        mock_generic_field = Mock()
        mock_mapped_field = Mock()
        cls.databundle_dict = {
            'value': 'foo',
            'coercer': mock_coercer,
            'source': mock_source,
            'generic_field': mock_generic_field,
            'mapped_fields': [mock_mapped_field],
            'multivalued': False
        }

    def _databundle_from_dict(self, datadict):
        return DataBundle.from_dict(datadict)

    def test_comparison_with_databundle_created_from_same_source_dict(self):
        databundle_dict = dict(self.databundle_dict)
        a = self._databundle_from_dict(databundle_dict)
        b = self._databundle_from_dict(databundle_dict)
        self.assertEqual(a, b)

    def test_comparison_with_databundle_that_has_different_value(self):
        databundle_dict = dict(self.databundle_dict)
        a = self._databundle_from_dict(databundle_dict)

        databundle_dict['value'] = 'BAR'
        b = self._databundle_from_dict(databundle_dict)
        self.assertNotEqual(a, b)

    def test_membership(self):
        databundle_dict = dict(self.databundle_dict)

        container = set()
        a = self._databundle_from_dict(databundle_dict)
        container.add(a)
        self.assertEqual(1, len(container))

        b = self._databundle_from_dict(databundle_dict)
        container.add(b)
        self.assertEqual(1, len(container))

        databundle_dict['value'] = 'BAR'
        c = self._databundle_from_dict(databundle_dict)
        container.add(c)
        self.assertEqual(2, len(container))
