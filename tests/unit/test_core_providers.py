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

import collections
from unittest import TestCase
from unittest.mock import MagicMock, Mock

from core.providers import (
    get_providers_for_meowuris,
    ProviderRegistry,
    translate_metainfo_mappings,
    wrap_provider_results,
)
import unit.utils as uu
import unit.constants as uuconst


class TestWrapProviderResults(TestCase):
    # TODO: [cleanup][temporary] Remove after refactoring!
    # TODO: [cleanup][hack] Use mocks!
    @classmethod
    def setUpClass(cls):
        import datetime
        from core import types
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
                    {'WeightedMapping': {'field': 'Extension', 'probability': 1}},
                ],
            },
            'basename_suffix': {
                'coercer': 'aw_pathcomponent',
                'multivalued': 'false',
                'mapped_fields': [
                    {'WeightedMapping': {'field': 'Extension', 'probability': 1}},
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
                    {'WeightedMapping': {'field': 'Extension', 'probability': 1}},
                ],
                'generic_field': 'mime_type'
            },
            'date_created': {
                'coercer': 'aw_timedate',
                'multivalued': 'false',
                'mapped_fields': [
                    {'WeightedMapping': {'field': 'Date', 'probability': 1}},
                    {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
                ],
                'generic_field': 'date_created'
            },
            'date_modified': {
                'coercer': 'aw_timedate',
                'multivalued': 'false',
                'mapped_fields': [
                    {'WeightedMapping': {'field': 'Date', 'probability': 0.25}},
                    {'WeightedMapping': {'field': 'DateTime', 'probability': 0.25}},
                ],
                'generic_field': 'date_modified'
            }
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
            'date_modified': datetime.datetime(2017, 11, 5, 15, 33, 50)
        }

        from core.model import WeightedMapping
        from core.model.genericfields import GenericDateCreated, GenericDateModified, GenericMimeType
        from core.namebuilder import fields
        cls.EXPECTED_WRAPPED = {
            'date_created': {
                'coercer': types.AW_TIMEDATE,
                'mapped_fields': [
                    WeightedMapping(field=fields.Date, probability=1),
                    WeightedMapping(field=fields.DateTime, probability=1)
                ],
                'multivalued': False,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': datetime.datetime(2017, 12, 26, 23, 15, 40),
                'generic_field': GenericDateCreated
            },
            'extension': {
                'coercer': types.AW_PATHCOMPONENT,
                'source': 'CrossPlatformFileSystemExtractor',
                'mapped_fields': [
                    WeightedMapping(field=fields.Extension, probability=1)
                ],
                'multivalued': False,
                'value': b'pdf'
            },
            'basename_prefix': {
                'coercer': types.AW_PATHCOMPONENT,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': b'foo.bar',
                'multivalued': False
            },
            'date_modified': {
                'coercer': types.AW_TIMEDATE,
                'mapped_fields': [
                    WeightedMapping(field=fields.Date, probability=0.25),
                    WeightedMapping(field=fields.DateTime, probability=0.25)
                ],
                'multivalued': False,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': datetime.datetime(2017, 11, 5, 15, 33, 50),
                'generic_field': GenericDateModified
            },
            'basename_full': {
                'coercer': types.AW_PATHCOMPONENT,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': b'foo.bar.pdf',
                'multivalued': False
            },
            'pathname_parent': {
                'coercer': types.AW_PATH,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': b'aw',
                'multivalued': False
            },
            'basename_suffix': {
                'coercer': types.AW_PATHCOMPONENT,
                'source': 'CrossPlatformFileSystemExtractor',
                'mapped_fields': [
                    WeightedMapping(field=fields.Extension, probability=1)
                ],
                'multivalued': False,
                'value': b'pdf'
            },
            'pathname_full': {
                'coercer': types.AW_PATH,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': b'/tank/temp/to-be-sorted/aw',
                'multivalued': False
            },
            'abspath_full': {
                'coercer': types.AW_PATH,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': b'/tank/temp/to-be-sorted/aw/foo.bar.pdf',
                'multivalued': False
            },
            'mime_type': {
                'coercer': types.AW_MIMETYPE,
                'mapped_fields': [
                    WeightedMapping(field=fields.Extension, probability=1)
                ],
                'multivalued': False,
                'source': 'CrossPlatformFileSystemExtractor',
                'value': 'application/pdf',
                'generic_field': GenericMimeType
            }
        }

    def test_wraps_actual_crossplatform_filesystem_extractor_results(self):
        # TODO: [cleanup][temporary] Remove after refactoring!
        # TODO: [cleanup][hack] Use mocks!
        from extractors.filesystem import CrossPlatformFileSystemExtractor
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
        from core import types
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
                        {'WeightedMapping': {'field': 'Extension', 'probability': 1}},
                    ],
                },
            },
            source_klass='foo_klass'
        )
        expect = {
            'extension': {
                'value': b'pdf',
                'coercer': types.AW_PATHCOMPONENT,
                'multivalued': False,
                'mapped_fields': [
                    WeightedMapping(fields.Extension, probability=1.0),
                ],
                'source': 'foo_klass'
            }
        }
        self.assertEqual(expect, actual)

    def test_translates_coercer_string_to_coercer_class(self):
        from core import types
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
            source_klass='foo_klass'
        )
        self.assertIn('extension', actual)
        self.assertIn('coercer', actual['extension'])
        self.assertEqual(types.AW_PATHCOMPONENT, actual['extension']['coercer'])

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
            source_klass='foo_klass'
        )
        self.assertIn('foo', actual)
        self.assertIn('multivalued', actual['foo'])
        self.assertFalse(actual['foo']['multivalued'])
        self.assertIn('bar', actual)
        self.assertIn('multivalued', actual['bar'])
        self.assertTrue(actual['bar']['multivalued'])

    def test_wraps_example_results(self):
        from core import types
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
            source_klass='foo_klass'
        )
        expect = {
            'health': {
                'value': 0.5,
                'coercer': types.AW_FLOAT,
                'multivalued': False,
                'source': 'foo_klass'
            },
            'is_jpeg': {
                'value': False,
                'coercer': types.AW_BOOLEAN,
                'multivalued': False,
                'source': 'foo_klass'
            }
        }
        self.assertEqual(expect, actual)


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
            self.WeightedMapping(self.fields_DateTime, probability=1.0),
            self.WeightedMapping(self.fields_Date, probability=1.0)
        ]
        actual = translate_metainfo_mappings([
            {'WeightedMapping': {'field': 'DateTime', 'probability': 1}},
            {'WeightedMapping': {'field': 'Date', 'probability': 1.0}},
        ])
        self.assertEqual(expected, actual)

    def test_translates_one_weighted_mapping(self):
        expected = [
            self.WeightedMapping(self.fields_Title, probability=1.0),
        ]
        actual = translate_metainfo_mappings([
            {'WeightedMapping': {'field': 'Title', 'probability': 1}},
        ])
        self.assertEqual(expected, actual)


class TestGetProvidersForMeowURIs(TestCase):
    @classmethod
    def setUpClass(cls):

        cls._meowuris_filetags = [
            uu.as_meowuri(uuconst.MEOWURI_FS_FILETAGS_DATETIME),
            uu.as_meowuri(uuconst.MEOWURI_FS_FILETAGS_DESCRIPTION),
            uu.as_meowuri(uuconst.MEOWURI_FS_FILETAGS_FOLLOWS),
            uu.as_meowuri(uuconst.MEOWURI_FS_FILETAGS_TAGS),
        ]
        cls._meowuris_filesystem = [
            uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_EXTENSION),
            uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL),
            uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_BASENAME_PREFIX),
            uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE),
            uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL),
        ]
        cls._meowuris_exiftool = [
            uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE),
            uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL),
            uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE),
            uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_QTCREATIONDATE),
            uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCCREATOR),
            uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCDATE),
            uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCPUBLISHER),
            uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCTITLE),
        ]
        cls._meowuris_guessit = [
            uu.as_meowuri(uuconst.MEOWURI_EXT_GUESSIT_DATE),
            uu.as_meowuri(uuconst.MEOWURI_EXT_GUESSIT_TITLE),
        ]
        cls._all_meowuris = (cls._meowuris_filetags + cls._meowuris_filesystem
                             + cls._meowuris_exiftool + cls._meowuris_guessit)
        uu.init_provider_registry()

    def _assert_maps(self, actual_sources, expected_providers):
        self.assertEqual(len(expected_providers), len(actual_sources))
        for s in actual_sources:
            self.assertTrue(uu.is_class(s))
            self.assertIn(s.__name__, expected_providers)

    def test_raises_exception_for_invalid_meowuris(self):
        def _assert_raises(meowuri_list):
            with self.assertRaises(AssertionError):
                _ = get_providers_for_meowuris(meowuri_list)

        _assert_raises([None])
        _assert_raises([None, None])
        _assert_raises(['xxxyyyzzz'])
        _assert_raises([None, 'xxxyyyzzz'])

    def test_returns_no_sources_for_invalid_meowuris(self):
        def _assert_empty_mapping(meowuri_list):
            actual = get_providers_for_meowuris(meowuri_list)
            self.assertEqual(0, len(actual))

        _assert_empty_mapping(None)
        _assert_empty_mapping([])

    def test_returns_expected_source_filetags(self):
        actual = get_providers_for_meowuris(self._meowuris_filetags)
        self._assert_maps(actual, ['FiletagsExtractor'])

    def test_returns_expected_source_filesystem(self):
        actual = get_providers_for_meowuris(self._meowuris_filesystem)
        self._assert_maps(actual, ['CrossPlatformFileSystemExtractor'])

    def test_returns_expected_source_exiftool(self):
        actual = get_providers_for_meowuris(self._meowuris_exiftool)
        self._assert_maps(actual, ['ExiftoolMetadataExtractor'])

    def test_returns_expected_source_guessit(self):
        # TODO: This should not depend on actually having the (OPTIONAL) 'guessit' dependency installed!
        actual = get_providers_for_meowuris(self._meowuris_guessit)
        self._assert_maps(actual, ['GuessitExtractor'])

    def test_returns_expected_providers(self):
        # TODO: This should not depend on actually having the (OPTIONAL) 'guessit' dependency installed!
        actual = get_providers_for_meowuris(self._all_meowuris)
        self.assertEqual(4, len(actual))
        self._assert_maps(actual, ['CrossPlatformFileSystemExtractor',
                                   'ExiftoolMetadataExtractor',
                                   'FiletagsExtractor',
                                   'GuessitExtractor'])

    def test_returns_included_sources_analyzers(self):
        actual = get_providers_for_meowuris(
            self._all_meowuris, include_roots=['analyzer']
        )
        self._assert_maps(actual, [])

    def test_returns_included_sources_extractors(self):
        actual = get_providers_for_meowuris(
            self._all_meowuris, include_roots=['extractor']
        )
        self._assert_maps(actual, ['CrossPlatformFileSystemExtractor',
                                   'ExiftoolMetadataExtractor',
                                   'GuessitExtractor',
                                   'FiletagsExtractor'])


class TestMapMeowURItoSourceClass(TestCase):
    @classmethod
    def setUpClass(cls):
        ExpectedMapping = collections.namedtuple('ExpectedMapping',
                                                 ['MeowURIs', 'Providers'])

        cls._mapping_meowuris_analyzers = [
            ExpectedMapping(
                MeowURIs=[
                    uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_DATETIME),
                    uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_PUBLISHER),
                    uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_TAGS),
                    uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_TITLE)
                ],
                Providers=['FilenameAnalyzer']
            ),
        ]
        cls._mapping_meowuris_extractors = [
            ExpectedMapping(
                MeowURIs=[
                    # uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_EXTENSION),
                    # uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL),
                    # uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_BASENAME_PREFIX),
                    uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE),
                    # uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL)
                ],
                Providers=['CrossPlatformFileSystemExtractor']
            ),
            ExpectedMapping(
                MeowURIs=[
                    uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE),
                    uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL),
                    uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE),
                    uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCCREATOR),
                    uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCCREATORFILEAS),
                    uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCDATE),
                    uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCPUBLISHER),
                    uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCTITLE)
                ],
                Providers=['ExiftoolMetadataExtractor']
            )
        ]
        cls._mapping_meowuris_all_providers = (cls._mapping_meowuris_analyzers +
                                               cls._mapping_meowuris_extractors)

        # NOTE: This depends on actual extractors, analyzers.
        from core import providers
        providers.initialize()
        cls.registry = providers.Registry

    def _check_returned_providers(self, actual_providers,
                                  expected_provider_names):
        # TODO: Not sure why this is assumed. Likely erroneous (?)
        actual_count = len(actual_providers)
        actual_provider_names = [k.__name__ for k in actual_providers]
        expect_count = len(expected_provider_names)
        fail_msg = 'Expected: {!s}\nActual: {!s}'.format(
            expected_provider_names, actual_provider_names)
        self.assertEqual(expect_count, actual_count, fail_msg)
        self.assertEqual(sorted(expected_provider_names),
                         sorted(actual_provider_names), fail_msg)

    def test_maps_meowuris_to_expected_provider(self):
        for meowuris, expected_providers in self._mapping_meowuris_all_providers:
            for uri in meowuris:
                actual = self.registry.providers_for_meowuri(uri)
                self._check_returned_providers(actual, expected_providers)

    def test_maps_meowuris_to_expected_provider_include_analyzers(self):
        for meowuris, expected_providers in self._mapping_meowuris_analyzers:
            for uri in meowuris:
                actual = self.registry.providers_for_meowuri(
                    uri, includes=['analyzer']
                )
                self._check_returned_providers(actual, expected_providers)

    def test_maps_none_given_extractor_meowuris_but_includes_analyzers(self):
        for meowuris, _ in self._mapping_meowuris_extractors:
            for uri in meowuris:
                actual = self.registry.providers_for_meowuri(
                    uri, includes=['analyzer']
                )
                self.assertEqual(0, len(actual))

    def test_maps_meowuris_to_expected_provider_include_extractors(self):
        for meowuris, expected_providers in self._mapping_meowuris_extractors:
            for uri in meowuris:
                actual = self.registry.providers_for_meowuri(
                    uri, includes=['extractor']
                )
                self._check_returned_providers(actual, expected_providers)

    def test_maps_none_given_analyzer_meowuris_but_includes_extractors(self):
        for meowuris, _ in self._mapping_meowuris_analyzers:
            for uri in meowuris:
                actual = self.registry.providers_for_meowuri(
                    uri, includes=['extractor']
                )
                self.assertEqual(0, len(actual))

    def test_maps_generic_meowuri_mimetype_to_expected_extractors(self):
        meowuri = uu.as_meowuri(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        actual = self.registry.providers_for_meowuri(
            meowuri, includes=['extractor']
        )
        self._check_returned_providers(
            actual,
            expected_provider_names=[
                'CrossPlatformFileSystemExtractor',
                'ExiftoolMetadataExtractor'
            ]
        )

    def test_maps_generic_meowuri_mimetype_to_extractors_analyzers(self):
        meowuri = uu.as_meowuri(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        actual = self.registry.providers_for_meowuri(
            meowuri, includes=['extractor', 'analyzer']
        )
        expected = ['CrossPlatformFileSystemExtractor',
                    'ExiftoolMetadataExtractor']
        self._check_returned_providers(actual, expected)

    def test_maps_generic_meowuri_mimetype_to_expected_providers(self):
        meowuri = uu.as_meowuri(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        actual = self.registry.providers_for_meowuri(
            meowuri,
        )
        expected = ['CrossPlatformFileSystemExtractor',
                    'ExiftoolMetadataExtractor']
        self._check_returned_providers(actual, expected)

    def test_maps_generic_meowuri_datecreated_to_expected_extractors(self):
        meowuri = uu.as_meowuri(uuconst.MEOWURI_GEN_METADATA_DATECREATED)
        actual = self.registry.providers_for_meowuri(
            meowuri, includes=['extractor']
        )
        expected = [
            'CrossPlatformFileSystemExtractor',
            'FiletagsExtractor',
            'GuessitExtractor',
            'ExiftoolMetadataExtractor',
            'PandocMetadataExtractor'
        ]
        self._check_returned_providers(actual, expected)

    # TODO: [TD0157] Look into analyzers not implementing 'FIELD_LOOKUP'.
    # TODO: [TD0157] Only the FilenameAnalyzer has a 'FIELD_LOOKUP' attribute.
    # def test_maps_generic_meowuri_datecreated_to_expected_analyzers(self):
    #     meowuri = uu.as_meowuri(uuconst.MEOWURI_GEN_METADATA_DATECREATED)
    #     actual = self.registry.providers_for_meowuri(
    #         meowuri, includes=['analyzer']
    #     )
    #     expected = ['DocumentAnalyzer',
    #                 'EbookAnalyzer',
    #                 'FilenameAnalyzer',
    #                 'FiletagsExtractor']
    #     self._check_returned_providers(actual, expected)

    # def test_maps_generic_meowuri_datecreated_to_expected_providers(self):
    #     meowuri = uu.as_meowuri(uuconst.MEOWURI_GEN_METADATA_DATECREATED)
    #     actual = self.registry.providers_for_meowuri(
    #         meowuri
    #     )
    #     expected = ['CrossPlatformFileSystemExtractor',
    #                 'DocumentAnalyzer',
    #                 'ExiftoolMetadataExtractor',
    #                 'EbookAnalyzer',
    #                 'FilenameAnalyzer',
    #                 'FiletagsExtractor',
    #                 'GuessitExtractor']
    #     self._check_returned_providers(actual, expected)


def _get_mock_provider():
    mock_provider = Mock()
    mock_provider.metainfo = MagicMock(return_value=dict())
    return mock_provider


class TestProviderRegistryMightBeResolvable(TestCase):
    @classmethod
    def setUpClass(cls):
        mock_provider = _get_mock_provider()
        dummy_source_map = {
            'analyzer': {
                uu.as_meowuri('analyzer.filename'): mock_provider
            },
            'extractor': {
                uu.as_meowuri('extractor.metadata.exiftool'): mock_provider,
                uu.as_meowuri('extractor.filesystem.xplat'): mock_provider,
                uu.as_meowuri('extractor.filesystem.guessit'): mock_provider,
            }
        }
        cls.p = ProviderRegistry(meowuri_source_map=dummy_source_map)

    def test_empty_meowuri_returns_false(self):
        self.assertFalse(self.p.might_be_resolvable(None))
        self.assertFalse(self.p.might_be_resolvable(''))

    def test_returns_false_given_non_meowuri_arguments(self):
        def _aF(test_input):
            with self.assertRaises(AssertionError):
                _ = self.p.might_be_resolvable(test_input)

        _aF(' ')
        _aF('foo')
        _aF('not.a.valid.source.surely')
        _aF('metadata.exiftool')
        _aF('metadata.exiftool.PDF:CreateDate')

    def test_returns_false_given_empty_or_none_arguments(self):
        def _aF(test_input):
            self.assertFalse(self.p.might_be_resolvable(test_input))

        _aF('')
        _aF(None)

    def test_good_meowuri_returns_true(self):
        def _aT(test_input):
            given_meowuri = uu.as_meowuri(test_input)
            self.assertTrue(self.p.might_be_resolvable(given_meowuri))

        _aT('extractor.metadata.exiftool')
        _aT(uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE)
        _aT(uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL)
        _aT(uuconst.MEOWURI_FS_XPLAT_EXTENSION)
        _aT(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)

    def test_with_meowuri_and_no_mapped_meowuris(self):
        p = ProviderRegistry(meowuri_source_map=dict())

        # Patch the instance attribute.
        # p.mapped_meowuris = dict()

        meowuri = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE)
        self.assertFalse(p.might_be_resolvable(meowuri))

    def test_with_meowuri_and_single_mapped_meowuri(self):
        mock_provider = _get_mock_provider()
        dummy_source_map = {
            'extractor': {
                uu.as_meowuri('extractor.filesystem.guessit'): mock_provider
            }
        }
        p = ProviderRegistry(meowuri_source_map=dummy_source_map)

        uri_guessit = uu.as_meowuri(uuconst.MEOWURI_EXT_GUESSIT_DATE)
        self.assertTrue(p.might_be_resolvable(uri_guessit))

        uri_exiftool = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCDATE)
        self.assertFalse(p.might_be_resolvable(uri_exiftool))

        uri_filesystem = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        self.assertFalse(p.might_be_resolvable(uri_filesystem))

    def test_with_meowuri_and_three_mapped_meowuris(self):
        meowuri_guessit_a = uu.as_meowuri(uuconst.MEOWURI_EXT_GUESSIT_DATE)
        meowuri_guessit_b = uu.as_meowuri(uuconst.MEOWURI_EXT_GUESSIT_TYPE)
        meowuri_guessit_c = uu.as_meowuri(uuconst.MEOWURI_EXT_GUESSIT_TITLE)
        self.assertTrue(self.p.might_be_resolvable(meowuri_guessit_a))
        self.assertTrue(self.p.might_be_resolvable(meowuri_guessit_b))
        self.assertTrue(self.p.might_be_resolvable(meowuri_guessit_c))

        meowuri_exiftool = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCDATE)
        self.assertTrue(self.p.might_be_resolvable(meowuri_exiftool))

        meowuri_fn = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_TAGS)
        self.assertTrue(self.p.might_be_resolvable(meowuri_fn))
