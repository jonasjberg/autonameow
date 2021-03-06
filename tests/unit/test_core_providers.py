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

from unittest import TestCase

import unit.utils as uu
from core.providers import get_coercer_for_metainfo_string
from core.providers import translate_metainfo_mappings
from core.providers import wrap_provider_results


class TestWrapProviderResults(TestCase):
    # TODO: [cleanup][temporary] Remove after refactoring!
    # TODO: [cleanup][hack] Use mocks!
    @classmethod
    def setUpClass(cls):
        from util import coercers
        cls.coercers_AW_BOOLEAN = coercers.AW_BOOLEAN
        cls.coercers_AW_FLOAT = coercers.AW_FLOAT
        cls.coercers_AW_MIMETYPE = coercers.AW_MIMETYPE
        cls.coercers_AW_PATHCOMPONENT = coercers.AW_PATHCOMPONENT
        cls.coercers_AW_PATH = coercers.AW_PATH
        cls.coercers_AW_STRING = coercers.AW_STRING
        cls.coercers_AW_TIMEDATE = coercers.AW_TIMEDATE
        cls.coercers_MULTIPLETYPES = coercers.MultipleTypes

        import datetime
        cls.EXAMPLE_FIELD_LOOKUP = {
            'abspath_full': {
                'coercer': 'aw_path',
                'multivalued': 'false'
            },
            'basename_full': {
                'coercer': 'aw_pathcomponent',
                'multivalued': 'false'
            },
            'extension': {
                'coercer': 'aw_pathcomponent',
                'multivalued': 'false',
                'mapped_fields': [
                    {'WeightedMapping': {'field': 'Extension', 'weight': '1'}},
                ],
            },
            'basename_suffix': {
                'coercer': 'aw_pathcomponent',
                'multivalued': 'false',
                'mapped_fields': [
                    {'WeightedMapping': {'field': 'Extension', 'weight': '1'}},
                ]
            },
            'basename_prefix': {
                'coercer': 'aw_pathcomponent',
                'multivalued': 'false',
            },
            'pathname_full': {'coercer': 'aw_path', 'multivalued': 'false'},
            'pathname_parent': {'coercer': 'aw_path', 'multivalued': 'false'},
            'mime_type': {
                'coercer': 'aw_mimetype',
                'multivalued': 'false',
                'mapped_fields': [
                    {'WeightedMapping': {'field': 'Extension', 'weight': '1'}},
                ],
                'generic_field': 'mime_type'
            },
            'date_created': {
                'coercer': 'aw_timedate',
                'multivalued': 'false',
                'mapped_fields': [
                    {'WeightedMapping': {'field': 'Date', 'weight': '1'}},
                    {'WeightedMapping': {'field': 'DateTime', 'weight': '1'}},
                ],
                'generic_field': 'date_created'
            },
            'date_modified': {
                'coercer': 'aw_timedate',
                'multivalued': 'false',
                'mapped_fields': [
                    {'WeightedMapping': {'field': 'Date', 'weight': '0.25'}},
                    {'WeightedMapping': {'field': 'DateTime', 'weight': '0.25'}},
                ],
                'generic_field': 'date_modified'
            },
            'tags': {
                'coercer': 'aw_string',
                'multivalued': 'true',
            },
        }
        cls.EXAMPLE_DATADICT = {
            'extension': b'pdf', 'mime_type': 'application/pdf',
            'date_created': datetime.datetime(2017, 12, 26, 23, 15, 40),
            'basename_suffix': b'pdf',
            'abspath_full': b'/tank/temp/to-be-sorted/aw/foo.bar.pdf',
            'pathname_parent': b'aw',
            'basename_prefix': b'foo.bar',
            'pathname_full': b'/tank/temp/to-be-sorted/aw',
            'basename_full': b'foo.bar.pdf',
            'date_modified': datetime.datetime(2017, 11, 5, 15, 33, 50),
            'tags': ['tag_foo', 'tag_bar']
        }

        from core.model import WeightedMapping
        from core.model.genericfields import GenericDateCreated, GenericDateModified, GenericMimeType
        from core.namebuilder import fields
        cls.EXPECTED_WRAPPED = {
            'date_created': {
                'coercer': cls.coercers_AW_TIMEDATE,
                'mapped_fields': [
                    WeightedMapping(field=fields.Date, weight=1.0),
                    WeightedMapping(field=fields.DateTime, weight=1.0)
                ],
                'multivalued': False,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': datetime.datetime(2017, 12, 26, 23, 15, 40),
                'generic_field': GenericDateCreated
            },
            'extension': {
                'coercer': cls.coercers_AW_PATHCOMPONENT,
                'source': 'CrossPlatformFileSystemExtractor',
                'mapped_fields': [
                    WeightedMapping(field=fields.Extension, weight=1.0)
                ],
                'multivalued': False,
                'value': b'pdf'
            },
            'basename_prefix': {
                'coercer': cls.coercers_AW_PATHCOMPONENT,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': b'foo.bar',
                'multivalued': False
            },
            'date_modified': {
                'coercer': cls.coercers_AW_TIMEDATE,
                'mapped_fields': [
                    WeightedMapping(field=fields.Date, weight=0.25),
                    WeightedMapping(field=fields.DateTime, weight=0.25)
                ],
                'multivalued': False,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': datetime.datetime(2017, 11, 5, 15, 33, 50),
                'generic_field': GenericDateModified
            },
            'basename_full': {
                'coercer': cls.coercers_AW_PATHCOMPONENT,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': b'foo.bar.pdf',
                'multivalued': False
            },
            'pathname_parent': {
                'coercer': cls.coercers_AW_PATH,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': b'aw',
                'multivalued': False
            },
            'basename_suffix': {
                'coercer': cls.coercers_AW_PATHCOMPONENT,
                'source': 'CrossPlatformFileSystemExtractor',
                'mapped_fields': [
                    WeightedMapping(field=fields.Extension, weight=1.0)
                ],
                'multivalued': False,
                'value': b'pdf'
            },
            'pathname_full': {
                'coercer': cls.coercers_AW_PATH,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': b'/tank/temp/to-be-sorted/aw',
                'multivalued': False
            },
            'abspath_full': {
                'coercer': cls.coercers_AW_PATH,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': b'/tank/temp/to-be-sorted/aw/foo.bar.pdf',
                'multivalued': False
            },
            'mime_type': {
                'coercer': cls.coercers_AW_MIMETYPE,
                'mapped_fields': [
                    WeightedMapping(field=fields.Extension, weight=1.0)
                ],
                'multivalued': False,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': 'application/pdf',
                'generic_field': GenericMimeType
            },
            'tags': {
                'coercer': cls.coercers_AW_STRING,
                'multivalued': True,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': ['tag_foo', 'tag_bar']
            },
        }

    def test_wraps_actual_crossplatform_filesystem_extractor_results(self):
        # TODO: [cleanup][temporary] Remove after refactoring!
        # TODO: [cleanup][hack] Use mocks!
        from extractors.metadata import CrossPlatformFileSystemExtractor
        example_provider_instance = CrossPlatformFileSystemExtractor()
        actual = wrap_provider_results(
            datadict=self.EXAMPLE_DATADICT,
            metainfo=self.EXAMPLE_FIELD_LOOKUP,
            source_klass=example_provider_instance
        )
        for key in self.EXPECTED_WRAPPED.keys():
            self.assertIn(key, actual)

        self.assertEqual(self.EXPECTED_WRAPPED, actual)

    def test_translates_arbitrary_datadict_metainfo_and_source_class(self):
        from core.model import WeightedMapping
        from core.namebuilder import fields
        actual = wrap_provider_results(
            datadict={
                'extension': b'pdf',
            },
            metainfo={
                'extension': {
                    'coercer': 'aw_pathcomponent',
                    'multivalued': 'false',
                    'mapped_fields': [
                        {'WeightedMapping': {'field': 'Extension', 'weight': '1'}},
                    ],
                },
            },
            source_klass=uu.get_mock_provider()
        )
        expect = {
            'extension': {
                'value': b'pdf',
                'coercer': self.coercers_AW_PATHCOMPONENT,
                'multivalued': False,
                'mapped_fields': [
                    WeightedMapping(fields.Extension, weight=1.0),
                ],
                'source': 'MockProvider'
            }
        }
        self.assertEqual(expect, actual)

    def test_translates_coercer_string_to_coercer_class(self):
        actual = wrap_provider_results(
            datadict={
                'extension': b'pdf',
            },
            metainfo={
                'extension': {
                    'coercer': 'aw_pathcomponent',
                    'multivalued': 'false',
                },
            },
            source_klass=uu.get_mock_provider()
        )
        self.assertIn('extension', actual)
        self.assertIn('coercer', actual['extension'])
        self.assertEqual(self.coercers_AW_PATHCOMPONENT, actual['extension']['coercer'])

    def test_translates_multivalued_string_to_boolean(self):
        actual = wrap_provider_results(
            datadict={
                'foo': 'a',
                'bar': 'b',
            },
            metainfo={
                'foo': {
                    'coercer': 'aw_string',
                    'multivalued': 'false',
                },
                'bar': {
                    'coercer': 'aw_string',
                    'multivalued': 'true',
                },
            },
            source_klass=uu.get_mock_provider()
        )
        self.assertIn('foo', actual)
        self.assertIn('multivalued', actual['foo'])
        self.assertFalse(actual['foo']['multivalued'])
        self.assertIn('bar', actual)
        self.assertIn('multivalued', actual['bar'])
        self.assertTrue(actual['bar']['multivalued'])

    def test_wraps_example_results(self):
        actual = wrap_provider_results(
            datadict={
                'health': 0.5,
                'is_jpeg': False,
            },
            metainfo={
                'health': {
                    'coercer': 'aw_float',
                    'multivalued': 'false',
                    'mapped_fields': None,
                },
                'is_jpeg': {
                    'coercer': 'aw_boolean',
                    'multivalued': 'false',
                    'mapped_fields': None,
                    'generic_field': None
                }
            },
            source_klass=uu.get_mock_provider()
        )
        expect = {
            'health': {
                'value': 0.5,
                'coercer': self.coercers_AW_FLOAT,
                'multivalued': False,
                'source': 'MockProvider'
            },
            'is_jpeg': {
                'value': False,
                'coercer': self.coercers_AW_BOOLEAN,
                'multivalued': False,
                'source': 'MockProvider'
            }
        }
        self.assertEqual(expect, actual)

    def test_wraps_example_results_with_multivalued_true(self):
        actual = wrap_provider_results(
            datadict={
                'is_jpeg': False,
            },
            metainfo={
                'is_jpeg': {
                    'coercer': 'aw_boolean',
                    'multivalued': 'true',
                    'mapped_fields': None,
                    'generic_field': None
                }
            },
            source_klass=uu.get_mock_provider()
        )
        expect = {
            'is_jpeg': {
                'value': False,
                'coercer': self.coercers_AW_BOOLEAN,
                'multivalued': True,
                'source': 'MockProvider'
            }
        }
        self.assertEqual(expect, actual)


class TestGotCoercerForMetainfoString(TestCase):
    def _get_coercer_for_metainfo_string(self, given):
        return get_coercer_for_metainfo_string(given)

    def test_does_not_return_none_given_string_representation_of_existing_coercer(self):
        self.assertIsNotNone(self._get_coercer_for_metainfo_string('aw_path'))

    def test_returns_none_given_string_that_does_not_map_to_existing_coercer(self):
        self.assertIsNone(self._get_coercer_for_metainfo_string('foo'))

    def test_returns_none_given_none(self):
        self.assertIsNone(self._get_coercer_for_metainfo_string(None))


class TestTranslateMetainfoMappings(TestCase):
    @classmethod
    def setUpClass(cls):
        from core.model import WeightedMapping
        from core.namebuilder import fields
        cls.WeightedMapping = WeightedMapping
        cls.fields_DateTime = fields.DateTime
        cls.fields_Date = fields.Date
        cls.fields_Title = fields.Title

    def test_returns_empty_list_given_empty_or_none_argument(self):
        for given in [None, list(), list(dict())]:
            actual = translate_metainfo_mappings(given)
            self.assertEqual(list(), actual)

    def test_translates_two_weighted_mappings(self):
        expected = [
            self.WeightedMapping(self.fields_DateTime, weight=1.0),
            self.WeightedMapping(self.fields_Date, weight=1.0)
        ]
        actual = translate_metainfo_mappings([
            {'WeightedMapping': {'field': 'DateTime', 'weight': '1'}},
            {'WeightedMapping': {'field': 'Date', 'weight': '1.0'}},
        ])
        self.assertEqual(expected, actual)

    def test_translates_one_weighted_mapping(self):
        expected = [
            self.WeightedMapping(self.fields_Title, weight=1.0),
        ]
        actual = translate_metainfo_mappings([
            {'WeightedMapping': {'field': 'Title', 'weight': '1'}},
        ])
        self.assertEqual(expected, actual)
