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

from core.providers import (
    get_sources_for_meowuris,
    map_meowuri_to_source_class,
    ProviderRegistry
)
import unit_utils as uu
import unit_utils_constants as uuconst


class TestGetSourcesForMeowURIs(TestCase):
    def setUp(self):
        self._meowuris_filetags = [
            uuconst.MEOWURI_AZR_FILETAGS_DATETIME,
            uuconst.MEOWURI_AZR_FILETAGS_DESCRIPTION,
            uuconst.MEOWURI_AZR_FILETAGS_FOLLOWS,
            uuconst.MEOWURI_AZR_FILETAGS_TAGS,
        ]
        self._meowuris_filesystem = [
            uuconst.MEOWURI_FS_XPLAT_BASENAME_EXT,
            uuconst.MEOWURI_FS_XPLAT_BASENAME_FULL,
            uuconst.MEOWURI_FS_XPLAT_BASENAME_PREFIX,
            uuconst.MEOWURI_FS_XPLAT_MIMETYPE,
            uuconst.MEOWURI_FS_XPLAT_PATHNAME_FULL,
        ]
        self._meowuris_exiftool = [
            uuconst.MEOWURI_EXT_EXIFTOOL_EXIFCREATEDATE,
            uuconst.MEOWURI_EXT_EXIFTOOL_EXIFDATETIMEORIGINAL,
            uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE,
            uuconst.MEOWURI_EXT_EXIFTOOL_QTCREATIONDATE,
            uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCCREATOR,
            uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCDATE,
            uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCPUBLISHER,
            uuconst.MEOWURI_EXT_EXIFTOOL_XMPDCTITLE,
        ]
        self._meowuris_guessit = [
            'plugin.guessit.date',
            'plugin.guessit.title',
        ]
        self._extractor_meowuris = (self._meowuris_filesystem
                                    + self._meowuris_exiftool)
        self._analyzer_meowuris = self._meowuris_filetags
        self._plugin_meowuris = self._meowuris_guessit
        self._all_meowuris = (self._meowuris_filetags
                              + self._meowuris_filesystem
                              + self._meowuris_exiftool
                              + self._meowuris_guessit)

    def _assert_maps(self, actual, expected_source):
        if isinstance(expected_source, list):
            self.assertEqual(len(actual), len(expected_source))
            for a in actual:
                self.assertTrue(uu.is_class(a))
                self.assertIn(a.__name__, expected_source)
        else:
            self.assertEqual(len(actual), 1)
            a = actual[0]
            self.assertTrue(uu.is_class(a))
            self.assertEqual(a.__name__, expected_source)

    def test_returns_no_sources_for_invalid_meowuris(self):
        def _assert_empty_mapping(meowuri_list):
            actual = get_sources_for_meowuris(meowuri_list)
            self.assertEqual(len(actual), 0)

        _assert_empty_mapping(None)
        _assert_empty_mapping([])
        _assert_empty_mapping([None])
        _assert_empty_mapping([None, None])
        _assert_empty_mapping(['xxxyyyzzz'])
        _assert_empty_mapping([None, 'xxxyyyzzz'])

    def test_returns_expected_source_filetags(self):
        actual = get_sources_for_meowuris(self._meowuris_filetags)
        self._assert_maps(actual, 'FiletagsAnalyzer')

    def test_returns_expected_source_filesystem(self):
        actual = get_sources_for_meowuris(self._meowuris_filesystem)
        self._assert_maps(actual, 'CrossPlatformFileSystemExtractor')

    def test_returns_expected_source_exiftool(self):
        actual = get_sources_for_meowuris(self._meowuris_exiftool)
        self._assert_maps(actual, 'ExiftoolMetadataExtractor')

    def test_returns_expected_source_guessit(self):
        actual = get_sources_for_meowuris(self._meowuris_guessit)
        self._assert_maps(actual, 'GuessitPlugin')

    def test_returns_expected_sources(self):
        actual = get_sources_for_meowuris(self._all_meowuris)
        self.assertEqual(len(actual), 4)
        self._assert_maps(actual, ['CrossPlatformFileSystemExtractor',
                                   'ExiftoolMetadataExtractor',
                                   'FiletagsAnalyzer',
                                   'GuessitPlugin'])

    def test_returns_included_sources_analyzers(self):
        actual = get_sources_for_meowuris(
            self._all_meowuris, include_roots=['analyzer']
        )
        self._assert_maps(actual, 'FiletagsAnalyzer')

    def test_returns_included_sources_extractorss(self):
        actual = get_sources_for_meowuris(
            self._all_meowuris, include_roots=['extractor']
        )
        self._assert_maps(actual, ['CrossPlatformFileSystemExtractor',
                                   'ExiftoolMetadataExtractor'])

    def test_returns_included_sources_plugins(self):
        actual = get_sources_for_meowuris(
            self._all_meowuris, include_roots=['plugin']
        )
        self._assert_maps(actual, 'GuessitPlugin')


class TestMapMeowURItoSourceClass(TestCase):
    meowURIsExtractors = collections.namedtuple('meowURIsExtractors',
                                                ['meowURIs', 'Extractors'])

    def setUp(self):
        self._analyzer_meowURI_sourcemap = [
            ([uuconst.MEOWURI_AZR_FILETAGS_DATETIME,
              uuconst.MEOWURI_AZR_FILETAGS_DESCRIPTION,
              uuconst.MEOWURI_AZR_FILETAGS_FOLLOWS,
              uuconst.MEOWURI_AZR_FILETAGS_TAGS],
             'FiletagsAnalyzer'),
        ]
        self._extractor_meowURI_sourcemap = [
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
        self._all_meowURI_sourcemap = (self._analyzer_meowURI_sourcemap
                                       + self._extractor_meowURI_sourcemap)

    def test_maps_meowuris_to_expected_source(self):
        expect_num = 1
        for meowuris, expected_source in self._all_meowURI_sourcemap:
            for uri in meowuris:
                actual = map_meowuri_to_source_class(uri)
                self.assertEqual(
                    len(actual), expect_num,
                    'Got {} sources but expected {} for "{!s}"'.format(
                        len(actual), expect_num, uri
                    )
                )

                actual = actual[0]
                self.assertEqual(actual.__name__, expected_source)
                self.assertTrue(uu.is_class(actual))

    def test_maps_meowuris_to_expected_source_include_analyzers(self):
        for meowuris, expected_source in self._analyzer_meowURI_sourcemap:
            for uri in meowuris:
                actual = map_meowuri_to_source_class(
                    uri, includes='analyzer'
                )
                self.assertEqual(len(actual), 1)

                actual = actual[0]
                self.assertEqual(actual.__name__, expected_source)
                self.assertTrue(uu.is_class(actual))

        for meowuris, expected_source in self._extractor_meowURI_sourcemap:
            for uri in meowuris:
                actual = map_meowuri_to_source_class(
                    uri, includes='analyzer'
                )
                self.assertEqual(len(actual), 0)

    def test_maps_meowuris_to_expected_source_include_extractors(self):
        for meowuris, expected_source in self._extractor_meowURI_sourcemap:
            for uri in meowuris:
                actual = map_meowuri_to_source_class(
                    uri, includes='extractor'
                )
                self.assertEqual(len(actual), 1)

                actual = actual[0]
                self.assertEqual(actual.__name__, expected_source)
                self.assertTrue(uu.is_class(actual))

        for meowuris, expected_source in self._analyzer_meowURI_sourcemap:
            for uri in meowuris:
                actual = map_meowuri_to_source_class(
                    uri, includes='extractors'
                )
                self.assertEqual(len(actual), 0)

    def test_maps_meowuris_to_expected_source_include_plugins(self):
        for meowuris, expected_source in self._analyzer_meowURI_sourcemap:
            for uri in meowuris:
                actual = map_meowuri_to_source_class(
                    uri, includes='plugins'
                )
                self.assertEqual(len(actual), 0)

        for meowuris, expected_source in self._extractor_meowURI_sourcemap:
            for uri in meowuris:
                actual = map_meowuri_to_source_class(
                    uri, includes='plugins'
                )
                self.assertEqual(len(actual), 0)


class TestProviderRegistryMethodResolvable(TestCase):
    def setUp(self):
        self.p = ProviderRegistry()

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


