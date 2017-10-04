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

from core import constants as C
from core import (
    exceptions,
    repository
)
from core.repository import Repository

import unit_utils as uu
import unit_utils_constants as uuconst


class TestRepository(TestCase):
    def setUp(self):
        self.r = Repository()

    def test_setup(self):
        self.r.initialize()
        self.assertTrue(isinstance(self.r.meowuri_class_map, dict))


class TestRepositoryMethodStore(TestCase):
    def setUp(self):
        self.r = Repository()
        self.r.initialize()
        self.file_object = uu.get_mock_fileobject(mime_type='text/plain')

    def test_repository_init_in_expected_state(self):
        self.assertTrue(isinstance(self.r.data, dict))
        self.assertEqual(len(self.r), 0)

    def test_storing_data_increments_len(self):
        valid_label = uuconst.VALID_DATA_SOURCES[0]
        self.r.store(self.file_object, valid_label, 'data')
        self.assertEqual(len(self.r), 1)

    def test_storing_data_with_different_labels_increments_len(self):
        first_valid_label = uuconst.VALID_DATA_SOURCES[0]
        self.r.store(self.file_object, first_valid_label, 'data')
        self.assertEqual(len(self.r), 1)

        second_valid_label = uuconst.VALID_DATA_SOURCES[1]
        self.r.store(self.file_object, second_valid_label, 'data')
        self.assertEqual(len(self.r), 2)

    def test_adding_data_with_same_label_increments_len(self):
        first_valid_label = uuconst.VALID_DATA_SOURCES[0]
        self.r.store(self.file_object, first_valid_label, 'data')
        self.assertEqual(len(self.r), 1)

        second_valid_label = uuconst.VALID_DATA_SOURCES[0]
        self.r.store(self.file_object, second_valid_label, 'data')
        self.assertEqual(len(self.r), 2)

    def test_adding_one_result_increments_len_once(self):
        _field = C.ANALYSIS_RESULTS_FIELDS[0]
        _results = ['foo']
        self.r.store(self.file_object, _field, _results)

        self.assertEqual(len(self.r), 1)

    def test_adding_two_results_increments_len_twice(self):
        _field_one = C.ANALYSIS_RESULTS_FIELDS[0]
        _field_two = C.ANALYSIS_RESULTS_FIELDS[1]
        _result_one = ['foo']
        _result_two = ['bar']
        self.r.store(self.file_object, _field_one, _result_one)
        self.r.store(self.file_object, _field_two, _result_two)

        self.assertEqual(len(self.r), 2)

    def test_adding_list_of_two_results_increments_len_twice(self):
        _field_one = C.ANALYSIS_RESULTS_FIELDS[0]
        _result_one = ['foo', 'bar']
        self.r.store(self.file_object, _field_one, _result_one)

        self.assertEqual(len(self.r), 2)

    def test_adding_dict_of_two_results_increments_len_twice(self):
        _field_one = C.ANALYSIS_RESULTS_FIELDS[0]
        _result_one = {'baz': ['foo', 'bar']}
        self.r.store(self.file_object, _field_one, _result_one)

        self.assertEqual(len(self.r), 2)

    def test_add_empty_does_not_increment_len(self):
        _field = C.ANALYSIS_RESULTS_FIELDS[0]
        _results = []
        self.r.store(self.file_object, _field, _results)

        self.assertEqual(len(self.r), 0)

    def test_store_data_with_invalid_label_raises_error(self):
        with self.assertRaises(exceptions.InvalidDataSourceError):
            self.r.store(self.file_object, None, 'data')
        with self.assertRaises(exceptions.InvalidDataSourceError):
            self.r.store(self.file_object, '', 'data')

    def test_stores_data_with_valid_label(self):
        valid_labels = uuconst.VALID_DATA_SOURCES[:3]
        for valid_label in valid_labels:
            self.r.store(self.file_object, valid_label, 'data')

    def test_valid_label_returns_expected_data(self):
        valid_label = uuconst.VALID_DATA_SOURCES[0]
        self.r.store(self.file_object, valid_label, 'expected_data')

        response = self.r.query(self.file_object, valid_label)
        self.assertEqual(response, 'expected_data')

    def test_none_label_raises_exception(self):
        valid_label = uuconst.VALID_DATA_SOURCES[0]
        self.r.store(self.file_object, valid_label, 'expected_data')

        with self.assertRaises(exceptions.InvalidDataSourceError):
            self.r.query(self.file_object, None)

    def test_valid_label_returns_expected_data_multiple_entries(self):
        valid_label = uuconst.VALID_DATA_SOURCES[0]
        self.r.store(self.file_object, valid_label, 'expected_data_a')
        self.r.store(self.file_object, valid_label, 'expected_data_b')

        response = self.r.query(self.file_object, valid_label)
        self.assertIn('expected_data_a', response)
        self.assertIn('expected_data_b', response)


class TestRepositoryMethodResolvable(TestCase):
    def setUp(self):
        self.r = Repository()
        self.r.initialize()

    def test_empty_meowuri_returns_false(self):
        self.assertFalse(self.r.resolvable(None))
        self.assertFalse(self.r.resolvable(''))

    def test_bad_meowuri_returns_false(self):
        def _aF(test_input):
            self.assertFalse(self.r.resolvable(test_input))

        _aF('')
        _aF(' ')
        _aF('foo')
        _aF('not.a.valid.source.surely')
        _aF('metadata.exiftool')
        _aF('metadata.exiftool.PDF:CreateDate')

    def test_good_meowuri_returns_true(self):
        def _aT(test_input):
            self.assertTrue(self.r.resolvable(test_input))

        _aT('extractor.metadata.exiftool')
        _aT('extractor.metadata.exiftool.PDF:CreateDate')
        _aT('extractor.filesystem.xplat.basename.full')
        _aT('extractor.filesystem.xplat.basename.extension')
        _aT('extractor.filesystem.xplat.contents.mime_type')


class TestMapMeowURItoSourceClass(TestCase):
    meowURIsExtractors = collections.namedtuple('meowURIsExtractors',
                                                ['meowURIs', 'Extractors'])

    def setUp(self):
        self._analyzer_meowURI_sourcemap = [
            (['analyzer.filetags.datetime',
              'analyzer.filetags.description',
              'analyzer.filetags.follows_filetags_convention',
              'analyzer.filetags.tags'],
             'FiletagsAnalyzer'),
        ]
        self._extractor_meowURI_sourcemap = [
            (['extractor.filesystem.xplat.basename.extension',
              'extractor.filesystem.xplat.basename.full',
              'extractor.filesystem.xplat.basename.prefix',
              'extractor.filesystem.xplat.contents.mime_type',
              'extractor.filesystem.xplat.pathname.full'],
             'CrossPlatformFileSystemExtractor'),
            (['extractor.metadata.exiftool.EXIF:CreateDate',
              'extractor.metadata.exiftool.EXIF:DateTimeOriginal',
              'extractor.metadata.exiftool.PDF:CreateDate',
              'extractor.metadata.exiftool.XMP-dc:Creator',
              'extractor.metadata.exiftool.XMP-dc:CreatorFile-as',
              'extractor.metadata.exiftool.XMP-dc:Date',
              'extractor.metadata.exiftool.XMP-dc:Publisher',
              'extractor.metadata.exiftool.XMP-dc:Title'],
             'ExiftoolMetadataExtractor')
        ]
        self._all_meowURI_sourcemap = (self._analyzer_meowURI_sourcemap
                                       + self._extractor_meowURI_sourcemap)

    def test_maps_meowuris_to_expected_source(self):
        for meowuris, expected_source in self._all_meowURI_sourcemap:
            for uri in meowuris:
                actual = repository.map_meowuri_to_source_class(uri)
                self.assertEqual(len(actual), 1)

                actual = actual[0]
                self.assertEqual(actual.__name__, expected_source)
                self.assertTrue(uu.is_class(actual))

    def test_maps_meowuris_to_expected_source_include_analyzers(self):
        for meowuris, expected_source in self._analyzer_meowURI_sourcemap:
            for uri in meowuris:
                actual = repository.map_meowuri_to_source_class(
                    uri, includes='analyzers'
                )
                self.assertEqual(len(actual), 1)

                actual = actual[0]
                self.assertEqual(actual.__name__, expected_source)
                self.assertTrue(uu.is_class(actual))

        for meowuris, expected_source in self._extractor_meowURI_sourcemap:
            for uri in meowuris:
                actual = repository.map_meowuri_to_source_class(
                    uri, includes='analyzers'
                )
                self.assertEqual(len(actual), 0)

    def test_maps_meowuris_to_expected_source_include_extractors(self):
        for meowuris, expected_source in self._extractor_meowURI_sourcemap:
            for uri in meowuris:
                actual = repository.map_meowuri_to_source_class(
                    uri, includes='extractors'
                )
                self.assertEqual(len(actual), 1)

                actual = actual[0]
                self.assertEqual(actual.__name__, expected_source)
                self.assertTrue(uu.is_class(actual))

        for meowuris, expected_source in self._analyzer_meowURI_sourcemap:
            for uri in meowuris:
                actual = repository.map_meowuri_to_source_class(
                    uri, includes='extractors'
                )
                self.assertEqual(len(actual), 0)

    def test_maps_meowuris_to_expected_source_include_plugins(self):
        for meowuris, expected_source in self._analyzer_meowURI_sourcemap:
            for uri in meowuris:
                actual = repository.map_meowuri_to_source_class(
                    uri, includes='plugins'
                )
                self.assertEqual(len(actual), 0)

        for meowuris, expected_source in self._extractor_meowURI_sourcemap:
            for uri in meowuris:
                actual = repository.map_meowuri_to_source_class(
                    uri, includes='plugins'
                )
                self.assertEqual(len(actual), 0)


class TestGetSourcesForMeowURIs(TestCase):
    def setUp(self):
        self._meowuris_filetags = [
            'analyzer.filetags.datetime',
            'analyzer.filetags.description',
            'analyzer.filetags.follows_filetags_convention',
            'analyzer.filetags.tags',
        ]
        self._meowuris_filesystem = [
            'extractor.filesystem.xplat.basename.extension',
            'extractor.filesystem.xplat.basename.full',
            'extractor.filesystem.xplat.basename.prefix',
            'extractor.filesystem.xplat.contents.mime_type',
            'extractor.filesystem.xplat.pathname.full',
        ]
        self._meowuris_exiftool = [
            'extractor.metadata.exiftool.EXIF:CreateDate',
            'extractor.metadata.exiftool.EXIF:DateTimeOriginal',
            'extractor.metadata.exiftool.PDF:CreateDate',
            'extractor.metadata.exiftool.QuickTime:CreationDate',
            'extractor.metadata.exiftool.XMP-dc:Creator',
            'extractor.metadata.exiftool.XMP-dc:Date',
            'extractor.metadata.exiftool.XMP-dc:Publisher',
            'extractor.metadata.exiftool.XMP-dc:Title',
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
            actual = repository.get_sources_for_meowuris(meowuri_list)
            self.assertEqual(len(actual), 0)

        _assert_empty_mapping(None)
        _assert_empty_mapping([])
        _assert_empty_mapping([None])
        _assert_empty_mapping([None, None])
        _assert_empty_mapping(['xxxyyyzzz'])
        _assert_empty_mapping([None, 'xxxyyyzzz'])

    def test_returns_expected_source_filetags(self):
        actual = repository.get_sources_for_meowuris(self._meowuris_filetags)
        self._assert_maps(actual, 'FiletagsAnalyzer')

    def test_returns_expected_source_filesystem(self):
        actual = repository.get_sources_for_meowuris(self._meowuris_filesystem)
        self._assert_maps(actual, 'CrossPlatformFileSystemExtractor')

    def test_returns_expected_source_exiftool(self):
        actual = repository.get_sources_for_meowuris(self._meowuris_exiftool)
        self._assert_maps(actual, 'ExiftoolMetadataExtractor')

    def test_returns_expected_source_guessit(self):
        actual = repository.get_sources_for_meowuris(self._meowuris_guessit)
        self._assert_maps(actual, 'GuessitPlugin')

    def test_returns_expected_sources(self):
        actual = repository.get_sources_for_meowuris(self._all_meowuris)
        self.assertEqual(len(actual), 4)
        self._assert_maps(actual, ['CrossPlatformFileSystemExtractor',
                                   'ExiftoolMetadataExtractor',
                                   'FiletagsAnalyzer',
                                   'GuessitPlugin'])

    def test_returns_included_sources_analyzers(self):
        actual = repository.get_sources_for_meowuris(
            self._all_meowuris, include_roots=['analyzer']
        )
        self._assert_maps(actual, 'FiletagsAnalyzer')

    def test_returns_included_sources_extractorss(self):
        actual = repository.get_sources_for_meowuris(
            self._all_meowuris, include_roots=['extractor']
        )
        self._assert_maps(actual, ['CrossPlatformFileSystemExtractor',
                                   'ExiftoolMetadataExtractor'])

    def test_returns_included_sources_plugins(self):
        actual = repository.get_sources_for_meowuris(
            self._all_meowuris, include_roots=['plugin']
        )
        self._assert_maps(actual, 'GuessitPlugin')


class TestRepositoryGenericStorage(TestCase):
    def setUp(self):
        self.r = Repository()
        self.r.initialize()

    def test_todo(self):
        self.skipTest('TODO: Add tests for storing "generic fields" ..')
