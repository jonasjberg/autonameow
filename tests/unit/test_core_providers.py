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
from unittest.mock import Mock

from core.providers import (
    get_providers_for_meowuris,
    ProviderRegistry
)
import unit.utils as uu
import unit.constants as uuconst


class TestGetProvidersForMeowURIs(TestCase):
    @classmethod
    def setUpClass(cls):

        cls._meowuris_filetags = [
            uu.as_meowuri(uuconst.MEOWURI_AZR_FILETAGS_DATETIME),
            uu.as_meowuri(uuconst.MEOWURI_AZR_FILETAGS_DESCRIPTION),
            uu.as_meowuri(uuconst.MEOWURI_AZR_FILETAGS_FOLLOWS),
            uu.as_meowuri(uuconst.MEOWURI_AZR_FILETAGS_TAGS),
        ]
        cls._meowuris_filesystem = [
            uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT),
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
            uu.as_meowuri('plugin.guessit.date'),
            uu.as_meowuri('plugin.guessit.title'),
        ]
        cls._extractor_meowuris = (cls._meowuris_filesystem
                                   + cls._meowuris_exiftool)
        cls._analyzer_meowuris = cls._meowuris_filetags
        cls._plugin_meowuris = cls._meowuris_guessit
        cls._all_meowuris = (cls._meowuris_filetags + cls._meowuris_filesystem
                             + cls._meowuris_exiftool + cls._meowuris_guessit)

        uu.init_provider_registry()

    def _assert_maps(self, actual_sources, expected_sources):
        self.assertEqual(len(actual_sources), len(expected_sources))
        for s in actual_sources:
            self.assertTrue(uu.is_class(s))
            self.assertIn(s.__name__, expected_sources)

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
        self._assert_maps(actual, ['FiletagsAnalyzer'])

    def test_returns_expected_source_filesystem(self):
        actual = get_providers_for_meowuris(self._meowuris_filesystem)
        self._assert_maps(actual, ['CrossPlatformFileSystemExtractor'])

    def test_returns_expected_source_exiftool(self):
        actual = get_providers_for_meowuris(self._meowuris_exiftool)
        self._assert_maps(actual, ['ExiftoolMetadataExtractor'])

    def test_returns_expected_source_guessit(self):
        # TODO: This should not depend on actually having the (OPTIONAL) 'guessit' dependency installed!
        actual = get_providers_for_meowuris(self._meowuris_guessit)
        self._assert_maps(actual, ['GuessitPlugin'])

    def test_returns_expected_sources(self):
        # TODO: This should not depend on actually having the (OPTIONAL) 'guessit' dependency installed!
        actual = get_providers_for_meowuris(self._all_meowuris)
        self.assertEqual(4, len(actual))
        self._assert_maps(actual, ['CrossPlatformFileSystemExtractor',
                                   'ExiftoolMetadataExtractor',
                                   'FiletagsAnalyzer',
                                   'GuessitPlugin'])

    def test_returns_included_sources_analyzers(self):
        actual = get_providers_for_meowuris(
            self._all_meowuris, include_roots=['analyzer']
        )
        self._assert_maps(actual, ['FiletagsAnalyzer'])

    def test_returns_included_sources_extractorss(self):
        actual = get_providers_for_meowuris(
            self._all_meowuris, include_roots=['extractor']
        )
        self._assert_maps(actual, ['CrossPlatformFileSystemExtractor',
                                   'ExiftoolMetadataExtractor'])

    def test_returns_included_sources_plugins(self):
        # TODO: This should not depend on actually having the (OPTIONAL) 'guessit' dependency installed!
        actual = get_providers_for_meowuris(
            self._all_meowuris, include_roots=['plugin']
        )
        self._assert_maps(actual, ['GuessitPlugin'])


class TestMapMeowURItoSourceClass(TestCase):
    @classmethod
    def setUpClass(cls):
        ExpectedMapping = collections.namedtuple('ExpectedMapping',
                                                 ['MeowURIs', 'Extractors'])

        cls._analyzer_meowuris_sourcemap = [
            ExpectedMapping(
                MeowURIs=[
                    uu.as_meowuri(uuconst.MEOWURI_AZR_FILETAGS_DATETIME),
                    uu.as_meowuri(uuconst.MEOWURI_AZR_FILETAGS_DESCRIPTION),
                    uu.as_meowuri(uuconst.MEOWURI_AZR_FILETAGS_FOLLOWS),
                    uu.as_meowuri(uuconst.MEOWURI_AZR_FILETAGS_TAGS)
                ],
                Extractors=['FiletagsAnalyzer']
            ),
        ]
        cls._extractor_meowuris_sourcemap = [
            ExpectedMapping(
                MeowURIs=[
                    uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT),
                    uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL),
                    uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_BASENAME_PREFIX),
                    uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE),
                    uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL)
                ],
                Extractors=['CrossPlatformFileSystemExtractor']
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
                Extractors=['ExiftoolMetadataExtractor']
            )
        ]
        cls._all_meowuris_sourcemap = (cls._analyzer_meowuris_sourcemap
                                       + cls._extractor_meowuris_sourcemap)

        # NOTE: This depends on actual extractors, plugins, analyzers.
        from core import providers
        providers.initialize()
        cls.registry = providers.Registry

    def _check_returned_providers(self, actual_providers,
                                  expected_provider_names):
        # TODO: Not sure why this is assumed. Likely erroneous (?)
        actual_count = len(actual_providers)
        actual_provider_names = [k.__name__ for k in actual_providers]
        expect_count = len(expected_provider_names)
        self.assertEqual(expect_count, actual_count)
        self.assertEqual(sorted(expected_provider_names),
                         sorted(actual_provider_names))

    def test_maps_meowuris_to_expected_source(self):
        for meowuris, expected_sources in self._all_meowuris_sourcemap:
            for uri in meowuris:
                actual = self.registry.providers_for_meowuri(uri)
                self._check_returned_providers(actual, expected_sources)

    def test_maps_meowuris_to_expected_source_include_analyzers(self):
        for meowuris, expected_sources in self._analyzer_meowuris_sourcemap:
            for uri in meowuris:
                actual = self.registry.providers_for_meowuri(
                    uri, includes=['analyzer']
                )
                self._check_returned_providers(actual, expected_sources)

    def test_maps_none_given_extractor_meowuris_but_includes_analyzers(self):
        for meowuris, _ in self._extractor_meowuris_sourcemap:
            for uri in meowuris:
                actual = self.registry.providers_for_meowuri(
                    uri, includes=['analyzer']
                )
                self.assertEqual(0, len(actual))

    def test_maps_meowuris_to_expected_source_include_extractors(self):
        for meowuris, expected_sources in self._extractor_meowuris_sourcemap:
            for uri in meowuris:
                actual = self.registry.providers_for_meowuri(
                    uri, includes=['extractor']
                )
                self._check_returned_providers(actual, expected_sources)

    def test_maps_none_given_analyzer_meowuris_but_includes_extractors(self):
        for meowuris, _ in self._analyzer_meowuris_sourcemap:
            for uri in meowuris:
                actual = self.registry.providers_for_meowuri(
                    uri, includes=['extractor']
                )
                self.assertEqual(0, len(actual))

    def test_maps_meowuris_to_expected_source_include_plugins(self):
        for meowuris, _ in self._analyzer_meowuris_sourcemap:
            for uri in meowuris:
                actual = self.registry.providers_for_meowuri(
                    uri, includes=['plugin']
                )
                self.assertEqual(0, len(actual))

    def test_maps_none_given_extractor_meowuris_but_includes_plugins(self):
        for meowuris, _ in self._extractor_meowuris_sourcemap:
            for uri in meowuris:
                actual = self.registry.providers_for_meowuri(
                    uri, includes=['plugin']
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
                    'FiletagsAnalyzer',
                    'ExiftoolMetadataExtractor']
        self._check_returned_providers(actual, expected)

    def test_maps_generic_meowuri_mimetype_to_expected_providers(self):
        meowuri = uu.as_meowuri(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        actual = self.registry.providers_for_meowuri(
            meowuri,
        )
        expected = ['CrossPlatformFileSystemExtractor',
                    'FiletagsAnalyzer',
                    'ExiftoolMetadataExtractor']
        self._check_returned_providers(actual, expected)

    def test_maps_generic_meowuri_datecreated_to_expected_extractors(self):
        meowuri = uu.as_meowuri(uuconst.MEOWURI_GEN_METADATA_DATECREATED)
        actual = self.registry.providers_for_meowuri(
            meowuri, includes=['extractor']
        )
        expected = ['CrossPlatformFileSystemExtractor',
                    'ExiftoolMetadataExtractor']
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
    #                 'FiletagsAnalyzer']
    #     self._check_returned_providers(actual, expected)

    # def test_maps_generic_meowuri_datecreated_to_expected_plugins(self):
    #     meowuri = uu.as_meowuri(uuconst.MEOWURI_GEN_METADATA_DATECREATED)
    #     actual = self.registry.providers_for_meowuri(
    #         meowuri, includes=['plugin']
    #     )
    #     expected = ['GuessitPlugin']
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
    #                 'FiletagsAnalyzer',
    #                 'GuessitPlugin']
    #     self._check_returned_providers(actual, expected)


class TestProviderRegistryMethodResolvable(TestCase):
    @classmethod
    def setUpClass(cls):
        mock_provider = Mock()
        mock_provider.FIELD_LOOKUP = dict()
        dummy_source_map = {
            'analyzer': {
                'analyzer.filename': mock_provider
            },
            'plugin': {
                'plugin.guessit': mock_provider
            },
            'extractor': {
                'extractor.metadata.exiftool': mock_provider,
                'extractor.filesystem.xplat': mock_provider
            }
        }
        cls.p = ProviderRegistry(meowuri_source_map=dummy_source_map)

    def test_empty_meowuri_returns_false(self):
        self.assertFalse(self.p.resolvable(None))
        self.assertFalse(self.p.resolvable(''))

    def test_bad_meowuri_returns_false(self):
        def _aF(test_input):
            self.assertFalse(self.p.resolvable(test_input))

        _aF('')
        _aF(' ')
        _aF('foo')
        _aF('not.a.valid.source.surely')
        _aF('metadata.exiftool')
        _aF('metadata.exiftool.PDF:CreateDate')

    def test_good_meowuri_returns_true(self):
        def _aT(test_input):
            self.assertTrue(self.p.resolvable(test_input))

        _aT('extractor.metadata.exiftool')
        _aT(uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE)
        _aT(uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL)
        _aT(uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT)
        _aT(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)

    def test_with_meowuri_and_no_mapped_meowuirs(self):
        p = ProviderRegistry(meowuri_source_map=dict())

        # Patch the instance attribute.
        # p.mapped_meowuris = dict()

        meowuri = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE)
        self.assertFalse(p.resolvable(meowuri))

    def test_with_meowuri_and_single_mapped_meowuri(self):
        mock_provider = Mock()
        mock_provider.FIELD_LOOKUP = dict()
        dummy_source_map = {
            'plugin': {
                'plugin.guessit': mock_provider
            }
        }
        p = ProviderRegistry(meowuri_source_map=dummy_source_map)

        # Patch the instance attribute.
        # p.mapped_meowuris = {'plugin.guessit'}

        uri_guessit = uu.as_meowuri(uuconst.MEOWURI_PLU_GUESSIT_DATE)
        self.assertTrue(p.resolvable(uri_guessit))

        uri_exiftool = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCDATE)
        self.assertFalse(p.resolvable(uri_exiftool))

        uri_filesystem = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_MIMETYPE)
        self.assertFalse(p.resolvable(uri_filesystem))

    def test_with_meowuri_and_three_mapped_meowuris(self):
        meowuri_guessit_a = uu.as_meowuri(uuconst.MEOWURI_PLU_GUESSIT_DATE)
        meowuri_guessit_b = uu.as_meowuri(uuconst.MEOWURI_PLU_GUESSIT_TYPE)
        meowuri_guessit_c = uu.as_meowuri(uuconst.MEOWURI_PLU_GUESSIT_TITLE)
        self.assertTrue(self.p.resolvable(meowuri_guessit_a))
        self.assertTrue(self.p.resolvable(meowuri_guessit_b))
        self.assertTrue(self.p.resolvable(meowuri_guessit_c))

        meowuri_exiftool = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCDATE)
        self.assertTrue(self.p.resolvable(meowuri_exiftool))

        meowuri_fn = uu.as_meowuri(uuconst.MEOWURI_AZR_FILENAME_TAGS)
        self.assertTrue(self.p.resolvable(meowuri_fn))
