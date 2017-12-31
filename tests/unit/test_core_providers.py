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
            uuconst.MEOWURI_AZR_FILETAGS_DATETIME,
            uuconst.MEOWURI_AZR_FILETAGS_DESCRIPTION,
            uuconst.MEOWURI_AZR_FILETAGS_FOLLOWS,
            uuconst.MEOWURI_AZR_FILETAGS_TAGS,
        ]
        cls._meowuris_filesystem = [
            uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT,
            uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL,
            uuconst.MEOWURI_FS_XPLAT_BASENAME_PREFIX,
            uuconst.MEOWURI_FS_XPLAT_MIMETYPE,
            uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL,
        ]
        cls._meowuris_exiftool = [
            uuconst.MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE,
            uuconst.MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL,
            uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE,
            uuconst.MEOWURI_EXT_EXIFTOOL_QTCREATIONDATE,
            uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCCREATOR,
            uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCDATE,
            uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCPUBLISHER,
            uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCTITLE,
        ]
        cls._meowuris_guessit = [
            'plugin.guessit.date',
            'plugin.guessit.title',
        ]
        cls._extractor_meowuris = (cls._meowuris_filesystem
                                   + cls._meowuris_exiftool)
        cls._analyzer_meowuris = cls._meowuris_filetags
        cls._plugin_meowuris = cls._meowuris_guessit
        cls._all_meowuris = (cls._meowuris_filetags + cls._meowuris_filesystem
                             + cls._meowuris_exiftool + cls._meowuris_guessit)

        uu.init_provider_registry()

    def _assert_maps(self, actual_sources, expected_source):
        self.assertEqual(len(actual_sources), len(expected_source))
        for s in actual_sources:
            self.assertTrue(uu.is_class(s))
            self.assertIn(s.__name__, expected_source)

    def test_returns_no_sources_for_invalid_meowuris(self):
        def _assert_empty_mapping(meowuri_list):
            actual = get_providers_for_meowuris(meowuri_list)
            self.assertEqual(0, len(actual))

        _assert_empty_mapping(None)
        _assert_empty_mapping([])
        _assert_empty_mapping([None])
        _assert_empty_mapping([None, None])
        _assert_empty_mapping(['xxxyyyzzz'])
        _assert_empty_mapping([None, 'xxxyyyzzz'])

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
        actual = get_providers_for_meowuris(self._meowuris_guessit)
        self._assert_maps(actual, ['GuessitPlugin'])

    def test_returns_expected_sources(self):
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
        actual = get_providers_for_meowuris(
            self._all_meowuris, include_roots=['plugin']
        )
        self._assert_maps(actual, ['GuessitPlugin'])


class TestMapMeowURItoSourceClass(TestCase):
    # TODO: Use or remove ..
    meowURIsExtractors = collections.namedtuple('meowURIsExtractors',
                                                ['meowURIs', 'Extractors'])

    @classmethod
    def setUpClass(cls):
        cls._analyzer_meowURI_sourcemap = [
            ([uuconst.MEOWURI_AZR_FILETAGS_DATETIME,
              uuconst.MEOWURI_AZR_FILETAGS_DESCRIPTION,
              uuconst.MEOWURI_AZR_FILETAGS_FOLLOWS,
              uuconst.MEOWURI_AZR_FILETAGS_TAGS],
             'FiletagsAnalyzer'),
        ]
        cls._extractor_meowURI_sourcemap = [
            ([uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT,
              uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL,
              uuconst.MEOWURI_FS_XPLAT_BASENAME_PREFIX,
              uuconst.MEOWURI_FS_XPLAT_MIMETYPE,
              uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL],
             'CrossPlatformFileSystemExtractor'),
            ([uuconst.MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE,
              uuconst.MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL,
              uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE,
              uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCCREATOR,
              uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCCREATORFILEAS,
              uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCDATE,
              uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCPUBLISHER,
              uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCTITLE],
             'ExiftoolMetadataExtractor')
        ]
        cls._all_meowURI_sourcemap = (cls._analyzer_meowURI_sourcemap
                                      + cls._extractor_meowURI_sourcemap)

        # NOTE: This depends on actual extractors, plugins, analyzers.
        from core import providers
        providers.initialize()
        cls.registry = providers.Registry

    def test_maps_meowuris_to_expected_source(self):
        expect_num = 1
        for meowuris, expected_source in self._all_meowURI_sourcemap:
            for uri in meowuris:
                actual = self.registry.provider_for_meowuri(uri)
                self.assertEqual(
                    expect_num, len(actual),
                    'Got {} sources but expected {} for "{!s}"'.format(
                        len(actual), expect_num, uri
                    )
                )

                actual = actual[0]
                self.assertEqual(expected_source, actual.__name__)
                self.assertTrue(uu.is_class(actual))

    def test_maps_meowuris_to_expected_source_include_analyzers(self):
        for meowuris, expected_source in self._analyzer_meowURI_sourcemap:
            for uri in meowuris:
                actual = self.registry.provider_for_meowuri(
                    uri, includes='analyzer'
                )
                self.assertEqual(1, len(actual))

                actual = actual[0]
                self.assertEqual(expected_source, actual.__name__)
                self.assertTrue(uu.is_class(actual))

        for meowuris, expected_source in self._extractor_meowURI_sourcemap:
            for uri in meowuris:
                actual = self.registry.provider_for_meowuri(
                    uri, includes='analyzer'
                )
                self.assertEqual(0, len(actual))

    def test_maps_meowuris_to_expected_source_include_extractors(self):
        for meowuris, expected_source in self._extractor_meowURI_sourcemap:
            for uri in meowuris:
                actual = self.registry.provider_for_meowuri(
                    uri, includes='extractor'
                )
                self.assertEqual(1, len(actual))

                actual = actual[0]
                self.assertEqual(expected_source, actual.__name__)
                self.assertTrue(uu.is_class(actual))

        for meowuris, expected_source in self._analyzer_meowURI_sourcemap:
            for uri in meowuris:
                actual = self.registry.provider_for_meowuri(
                    uri, includes='extractors'
                )
                self.assertEqual(0, len(actual))

    def test_maps_meowuris_to_expected_source_include_plugins(self):
        for meowuris, expected_source in self._analyzer_meowURI_sourcemap:
            for uri in meowuris:
                actual = self.registry.provider_for_meowuri(
                    uri, includes='plugins'
                )
                self.assertEqual(0, len(actual))

        for meowuris, expected_source in self._extractor_meowURI_sourcemap:
            for uri in meowuris:
                actual = self.registry.provider_for_meowuri(
                    uri, includes='plugins'
                )
                self.assertEqual(0, len(actual))


class TestProviderRegistryMethodResolvable(TestCase):
    @classmethod
    def setUpClass(cls):
        dummy_source_map = {
            'analyzer': {
                'analyzer.filename': Mock()
            },
            'plugin': {
                'plugin.guessit': Mock()
            },
            'extractor': {
                'extractor.metadata.exiftool': Mock(),
                'extractor.filesystem.xplat': Mock(),
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
        # p.mapped_meowuris = {}

        meowuri = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE)
        self.assertFalse(p.resolvable(meowuri))

    def test_with_meowuri_and_single_mapped_meowuri(self):
        dummy_source_map = {
            'plugin': {
                'plugin.guessit': Mock()
            }
        }
        p = ProviderRegistry(meowuri_source_map=dummy_source_map)

        # Patch the instance attribute.
        # p.mapped_meowuris = {'plugin.guessit'}

        meowuri_guessit = uu.as_meowuri(uuconst.MEOWURI_PLU_GUESSIT_DATE)
        self.assertTrue(p.resolvable(meowuri_guessit))

        meowuri_exiftool = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCDATE)
        self.assertFalse(p.resolvable(meowuri_exiftool))

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
