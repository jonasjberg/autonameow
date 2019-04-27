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

import collections
from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

import unit.constants as uuconst
import unit.utils as uu
from core.master_provider import MasterDataProvider
from core.master_provider import ProviderRegistry
from core.master_provider import ProviderRunner


def _get_provider_registry(**kwargs):
    meowuri_source_map = kwargs.get('meowuri_source_map', dict())
    excluded_providers = kwargs.get('excluded_providers', set())
    return ProviderRegistry(meowuri_source_map, excluded_providers)


class TestProviderRegistryMightBeResolvable(TestCase):
    @classmethod
    def setUpClass(cls):
        mock_provider = uu.get_mock_provider()
        dummy_source_map = {
            uu.as_meowuri('analyzer.filename'): mock_provider,
            uu.as_meowuri('extractor.metadata.exiftool'): mock_provider,
            uu.as_meowuri('extractor.filesystem.xplat'): mock_provider,
            uu.as_meowuri('extractor.filesystem.guessit'): mock_provider,
        }
        cls.p = _get_provider_registry(meowuri_source_map=dummy_source_map)

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
        p = _get_provider_registry(meowuri_source_map=dict())

        # Patch the instance attribute.
        # p.mapped_meowuris = dict()

        meowuri = uu.as_meowuri(uuconst.MEOWURI_EXT_EXIFTOOL_PDFCREATEDATE)
        self.assertFalse(p.might_be_resolvable(meowuri))

    def test_with_meowuri_and_single_mapped_meowuri(self):
        mock_provider = uu.get_mock_provider()
        dummy_source_map = {
            uu.as_meowuri('extractor.filesystem.guessit'): mock_provider
        }
        p = _get_provider_registry(meowuri_source_map=dummy_source_map)

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


class TestProvidersForMeowURI(TestCase):
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
        from core import master_provider
        with patch('core.datastore.repository.SessionRepository', MagicMock()):
            master_provider._initialize_master_data_provider(_get_mock_config())
            cls.registry = master_provider.Registry

    def _check_returned_providers(self, actual_providers,
                                  expected_provider_names):
        # TODO: Not sure why this is assumed. Likely erroneous (?)
        actual_count = len(actual_providers)
        # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
        actual_provider_names = [k.name() for k in actual_providers]
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

    def test_maps_generic_meowuri_mimetype_to_expected_providers(self):
        meowuri = uu.as_meowuri(uuconst.MEOWURI_GEN_CONTENTS_MIMETYPE)
        actual = self.registry.providers_for_meowuri(
            meowuri,
        )
        expected = ['CrossPlatformFileSystemExtractor',
                    'ExiftoolMetadataExtractor']
        self._check_returned_providers(actual, expected)


class TestProviderRunner(TestCase):
    @staticmethod
    def _get_provider_runner(*args, **kwargs):
        test_config = kwargs.get('config')
        test_extractor_runner = kwargs.get('extractor_runner')
        test_run_analysis_func = kwargs.get('run_analysis_func', lambda x: True)
        kwargs.update({
            'config': test_config,
            'extractor_runner': test_extractor_runner,
            'run_analysis_func': test_run_analysis_func
        })
        return ProviderRunner(*args, **kwargs)

    @patch('core.datastore.repository.SessionRepository', MagicMock())
    def test_instantiated_provider_runner_is_not_none(
            self
    ):
        provider_runner = self._get_provider_runner()
        self.assertIsNotNone(provider_runner)

    # TODO: [cleanup] This much mocking indicates poor design choices ..
    @patch('core.master_provider.Registry.providers_for_meowuri')
    @patch('core.datastore.repository.SessionRepository', MagicMock())
    @patch('core.master_provider.ProviderRunner._delegate_to_extractors')
    @patch('core.master_provider.ProviderRunner._delegate_to_analyzers')
    def test_does_not_delegate_when_no_providers_are_available_for_meowuri(
            self, mock__delegate_to_analyzers,
            mock__delegate_to_extractors, mock_providers_for_meowuri
    ):
        mock_providers_for_meowuri.return_value = set()
        provider_runner = self._get_provider_runner()

        fo = uu.get_mock_fileobject(mime_type='text/plain')
        uri = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

        provider_runner.delegate_to_providers(fo, uri)
        mock__delegate_to_analyzers.assert_not_called()
        mock__delegate_to_extractors.assert_not_called()

    # # TODO: [cleanup] This much mocking indicates poor design choices ..
    @patch('core.master_provider.Registry.providers_for_meowuri')
    @patch('core.datastore.repository.SessionRepository', MagicMock())
    @patch('core.master_provider.ProviderRunner._delegate_to_extractors')
    @patch('core.master_provider.ProviderRunner._delegate_to_analyzers')
    def test_delegates_once_to_expected_provider_filesystem_extractor(
            self, mock__delegate_to_analyzers,
            mock__delegate_to_extractors, mock_providers_for_meowuri
    ):
        provider_runner = self._get_provider_runner()

        from extractors.filesystem import CrossPlatformFileSystemExtractor
        provider_For_meowuri = set([CrossPlatformFileSystemExtractor])
        mock_providers_for_meowuri.return_value = provider_For_meowuri

        fo = uu.get_mock_fileobject(mime_type='text/plain')
        uri = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

        provider_runner.delegate_to_providers(fo, uri)
        mock__delegate_to_analyzers.assert_not_called()
        mock__delegate_to_extractors.assert_called_once_with(fo, provider_For_meowuri)

        provider_runner.delegate_to_providers(fo, uri)
        mock__delegate_to_analyzers.assert_not_called()
        mock__delegate_to_extractors.assert_called_once_with(fo, provider_For_meowuri)

    # # TODO: [cleanup] This much mocking indicates poor design choices ..
    @patch('core.master_provider.Registry.providers_for_meowuri')
    @patch('core.datastore.repository.SessionRepository', MagicMock())
    @patch('core.master_provider.ProviderRunner._delegate_to_extractors')
    @patch('core.master_provider.ProviderRunner._delegate_to_analyzers')
    def test_delegates_once_to_expected_provider_ebook_analyzer(
            self, mock__delegate_to_analyzers,
            mock__delegate_to_extractors, mock_providers_for_meowuri
    ):
        provider_runner = self._get_provider_runner()

        from analyzers.analyze_ebook import EbookAnalyzer
        provider_For_meowuri = set([EbookAnalyzer])
        mock_providers_for_meowuri.return_value = provider_For_meowuri

        fo = uu.get_mock_fileobject(mime_type='text/plain')
        uri = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

        provider_runner.delegate_to_providers(fo, uri)
        mock__delegate_to_analyzers.assert_called_once_with(fo, provider_For_meowuri)
        mock__delegate_to_extractors.assert_not_called()

        provider_runner.delegate_to_providers(fo, uri)
        mock__delegate_to_analyzers.assert_called_once_with(fo, provider_For_meowuri)
        mock__delegate_to_extractors.assert_not_called()

    @patch('core.datastore.repository.SessionRepository', MagicMock())
    def test_delegation_history_methods(self):
        fo1 = MagicMock()
        fo2 = MagicMock()
        provider1 = MagicMock()
        provider2 = MagicMock()

        provider_runner = self._get_provider_runner()
        self.assertFalse(provider_runner._previously_delegated_provider(fo1, provider1))
        self.assertFalse(provider_runner._previously_delegated_provider(fo2, provider1))
        self.assertFalse(provider_runner._previously_delegated_provider(fo1, provider2))
        self.assertFalse(provider_runner._previously_delegated_provider(fo2, provider2))

        provider_runner._remember_provider_delegation(fo1, provider1)
        self.assertTrue(provider_runner._previously_delegated_provider(fo1, provider1))
        self.assertFalse(provider_runner._previously_delegated_provider(fo2, provider1))
        self.assertFalse(provider_runner._previously_delegated_provider(fo1, provider2))
        self.assertFalse(provider_runner._previously_delegated_provider(fo2, provider2))

        provider_runner._remember_provider_delegation(fo2, provider1)
        self.assertTrue(provider_runner._previously_delegated_provider(fo1, provider1))
        self.assertTrue(provider_runner._previously_delegated_provider(fo2, provider1))
        self.assertFalse(provider_runner._previously_delegated_provider(fo1, provider2))
        self.assertFalse(provider_runner._previously_delegated_provider(fo2, provider2))

        provider_runner._remember_provider_delegation(fo1, provider2)
        provider_runner._remember_provider_delegation(fo2, provider2)
        self.assertTrue(provider_runner._previously_delegated_provider(fo1, provider1))
        self.assertTrue(provider_runner._previously_delegated_provider(fo2, provider1))
        self.assertTrue(provider_runner._previously_delegated_provider(fo1, provider2))
        self.assertTrue(provider_runner._previously_delegated_provider(fo2, provider2))

    def test_delegation_history_includes_delegation_of_every_possible_uri(self):
        fo1 = MagicMock()
        fo2 = MagicMock()
        provider1 = MagicMock()
        provider2 = MagicMock()

        mock_extractor_runner = MagicMock()
        mock_run_analysis = MagicMock()
        provider_runner = self._get_provider_runner(
            extractor_runner=mock_extractor_runner,
            run_analysis_func=mock_run_analysis
        )
        provider_runner._extractor_runner.start = mock_extractor_runner
        self.assertFalse(provider_runner._previously_delegated_provider(fo1, provider1))
        self.assertFalse(provider_runner._previously_delegated_provider(fo2, provider1))
        self.assertFalse(provider_runner._previously_delegated_provider(fo1, provider2))
        self.assertFalse(provider_runner._previously_delegated_provider(fo2, provider2))

        mock_run_analysis.assert_not_called()
        mock_extractor_runner.start.assert_not_called()

        provider_runner.delegate_every_possible_meowuri(fo1)
        self.assertEqual(1, mock_run_analysis.call_count)
        self.assertEqual(1, mock_extractor_runner.start.call_count)

        self.assertTrue(provider_runner._previously_delegated_provider(fo1, provider1))
        self.assertFalse(provider_runner._previously_delegated_provider(fo2, provider1))
        self.assertTrue(provider_runner._previously_delegated_provider(fo1, provider2))
        self.assertFalse(provider_runner._previously_delegated_provider(fo2, provider2))

        provider_runner.delegate_every_possible_meowuri(fo2)
        self.assertEqual(2, mock_run_analysis.call_count)
        self.assertEqual(2, mock_extractor_runner.start.call_count)

        self.assertTrue(provider_runner._previously_delegated_provider(fo1, provider1))
        self.assertTrue(provider_runner._previously_delegated_provider(fo2, provider1))
        self.assertTrue(provider_runner._previously_delegated_provider(fo1, provider2))
        self.assertTrue(provider_runner._previously_delegated_provider(fo2, provider2))


def _get_mock_config():
    return Mock()


def _get_master_data_provider():
    return MasterDataProvider(config=_get_mock_config(), run_analysis_func=lambda x: True)


class TestMasterDataProvider(TestCase):
    @patch('core.datastore.repository.SessionRepository', MagicMock())
    def test_instantiated_master_data_provider_is_not_none(self):
        p = _get_master_data_provider()
        self.assertIsNotNone(p)

    @patch('core.datastore.repository.SessionRepository', MagicMock())
    @patch('core.master_provider.ProviderRunner.delegate_every_possible_meowuri')
    def test_delegate_every_possible_meowuri(self, mock_delegate_every_possible_meowuri):
        p = _get_master_data_provider()

        mock_fileobject = Mock()
        p.delegate_every_possible_meowuri(mock_fileobject)
        mock_delegate_every_possible_meowuri.assert_called_with(mock_fileobject)

    @patch('core.datastore.repository.SessionRepository')
    @patch('core.master_provider.MasterDataProvider._delegate_to_providers')
    def test_request_when_data_is_already_stored_in_the_repository(
            self, mock__delegate_to_providers, mock_session_repository
    ):
        mock_session_repository.query.return_value = True  # Data already in repository
        mock_fileobject = Mock()
        mock_meowuri = Mock()

        p = _get_master_data_provider()
        response = p.request(mock_fileobject, mock_meowuri)

        self.assertTrue(response)
        mock_session_repository.query.assert_called_once_with(mock_fileobject, mock_meowuri)
        mock__delegate_to_providers.assert_not_called()

    @patch('core.datastore.repository.SessionRepository')
    @patch('core.master_provider.MasterDataProvider._delegate_to_providers')
    def test_request_delegates_to_providers_when_data_is_not_stored_in_the_repository(
            self, mock__delegate_to_providers, mock_session_repository
    ):
        mock_session_repository.query.return_value = False  # Data not in repository
        mock_fileobject = Mock()
        mock_meowuri = Mock()

        p = _get_master_data_provider()
        response = p.request(mock_fileobject, mock_meowuri)

        self.assertFalse(response)  # Mock returns False every time ..
        mock_session_repository.query.assert_called_with(mock_fileobject, mock_meowuri)
        self.assertEqual(2, mock_session_repository.query.call_count)
        mock__delegate_to_providers.assert_called_with(mock_fileobject, mock_meowuri)
