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

from unittest import TestCase
from unittest.mock import MagicMock, Mock, patch

import unit.utils as uu
import unit.constants as uuconst
from core.master_provider import (
    MasterDataProvider,
    ProviderRunner
)


class TestProviderRunner(TestCase):
    @patch('core.repository.SessionRepository', MagicMock())
    def test_instantiated_provider_runner_is_not_none(
            self
    ):
        provider_runner = ProviderRunner(config=None)
        self.assertIsNotNone(provider_runner)

    # TODO: [cleanup] This much mocking indicates poor design choices ..
    @patch('core.providers.get_providers_for_meowuri')
    @patch('core.repository.SessionRepository', MagicMock())
    @patch('core.master_provider.ProviderRunner._delegate_to_extractors')
    @patch('core.master_provider.ProviderRunner._delegate_to_analyzers')
    def test_does_not_delegate_when_no_providers_are_available_for_meowuri(
            self, mock__delegate_to_analyzers,
            mock__delegate_to_extractors, mock_get_providers_for_meowuri
    ):
        mock_get_providers_for_meowuri.return_value = set()
        provider_runner = ProviderRunner(config=None)

        fo = uu.get_mock_fileobject(mime_type='text/plain')
        uri = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

        provider_runner.delegate_to_providers(fo, uri)
        mock__delegate_to_analyzers.assert_not_called()
        mock__delegate_to_extractors.assert_not_called()

    # # TODO: [cleanup] This much mocking indicates poor design choices ..
    @patch('core.providers.get_providers_for_meowuri')
    @patch('core.repository.SessionRepository', MagicMock())
    @patch('core.master_provider.ProviderRunner._delegate_to_extractors')
    @patch('core.master_provider.ProviderRunner._delegate_to_analyzers')
    def test_delegates_once_to_expected_provider_filesystem_extractor(
            self, mock__delegate_to_analyzers,
            mock__delegate_to_extractors, mock_get_providers_for_meowuri
    ):
        provider_runner = ProviderRunner(config=None)

        from extractors.filesystem import CrossPlatformFileSystemExtractor
        provider_For_meowuri = set([CrossPlatformFileSystemExtractor])
        mock_get_providers_for_meowuri.return_value = provider_For_meowuri

        fo = uu.get_mock_fileobject(mime_type='text/plain')
        uri = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

        provider_runner.delegate_to_providers(fo, uri)
        mock__delegate_to_analyzers.assert_not_called()
        mock__delegate_to_extractors.assert_called_once_with(fo, provider_For_meowuri)

        provider_runner.delegate_to_providers(fo, uri)
        mock__delegate_to_analyzers.assert_not_called()
        mock__delegate_to_extractors.assert_called_once_with(fo, provider_For_meowuri)

    # # TODO: [cleanup] This much mocking indicates poor design choices ..
    @patch('core.providers.get_providers_for_meowuri')
    @patch('core.repository.SessionRepository', MagicMock())
    @patch('core.master_provider.ProviderRunner._delegate_to_extractors')
    @patch('core.master_provider.ProviderRunner._delegate_to_analyzers')
    def test_delegates_once_to_expected_provider_ebook_analyzer(
            self, mock__delegate_to_analyzers,
            mock__delegate_to_extractors, mock_get_providers_for_meowuri
    ):
        provider_runner = ProviderRunner(config=None)

        from analyzers.analyze_ebook import EbookAnalyzer
        provider_For_meowuri = set([EbookAnalyzer])
        mock_get_providers_for_meowuri.return_value = provider_For_meowuri

        fo = uu.get_mock_fileobject(mime_type='text/plain')
        uri = uu.as_meowuri(uuconst.MEOWURI_FS_XPLAT_ABSPATH_FULL)

        provider_runner.delegate_to_providers(fo, uri)
        mock__delegate_to_analyzers.assert_called_once_with(fo, provider_For_meowuri)
        mock__delegate_to_extractors.assert_not_called()

        provider_runner.delegate_to_providers(fo, uri)
        mock__delegate_to_analyzers.assert_called_once_with(fo, provider_For_meowuri)
        mock__delegate_to_extractors.assert_not_called()

    @patch('core.repository.SessionRepository', MagicMock())
    def test_delegation_history_methods(
            self
    ):
        fo1 = MagicMock()
        uri1 = MagicMock()
        provider1 = MagicMock()

        fo2 = MagicMock()
        uri2 = MagicMock()
        provider2 = MagicMock()

        provider_runner = ProviderRunner(config=None)
        self.assertFalse(provider_runner._previously_delegated(fo1, uri1, provider1))
        self.assertFalse(provider_runner._previously_delegated(fo1, uri2, provider1))
        self.assertFalse(provider_runner._previously_delegated(fo2, uri1, provider1))
        self.assertFalse(provider_runner._previously_delegated(fo1, uri2, provider2))
        self.assertFalse(provider_runner._previously_delegated(fo1, uri1, provider2))
        self.assertFalse(provider_runner._previously_delegated(fo2, uri1, provider2))
        self.assertFalse(provider_runner._previously_delegated(fo2, uri2, provider2))

        provider_runner._remember_delegation(fo1, uri1, provider1)
        self.assertTrue(provider_runner._previously_delegated(fo1, uri1, provider1))
        self.assertFalse(provider_runner._previously_delegated(fo1, uri2, provider1))
        self.assertFalse(provider_runner._previously_delegated(fo2, uri1, provider1))
        self.assertFalse(provider_runner._previously_delegated(fo1, uri2, provider2))
        self.assertFalse(provider_runner._previously_delegated(fo1, uri1, provider2))
        self.assertFalse(provider_runner._previously_delegated(fo2, uri1, provider2))
        self.assertFalse(provider_runner._previously_delegated(fo2, uri2, provider2))

        provider_runner._remember_delegation(fo2, uri1, provider1)
        self.assertTrue(provider_runner._previously_delegated(fo1, uri1, provider1))
        self.assertFalse(provider_runner._previously_delegated(fo1, uri2, provider1))
        self.assertTrue(provider_runner._previously_delegated(fo2, uri1, provider1))
        self.assertFalse(provider_runner._previously_delegated(fo1, uri2, provider2))
        self.assertFalse(provider_runner._previously_delegated(fo1, uri1, provider2))
        self.assertFalse(provider_runner._previously_delegated(fo2, uri1, provider2))
        self.assertFalse(provider_runner._previously_delegated(fo2, uri2, provider2))

        provider_runner._remember_delegation(fo1, uri2, provider1)
        provider_runner._remember_delegation(fo1, uri1, provider2)
        provider_runner._remember_delegation(fo2, uri1, provider2)
        self.assertTrue(provider_runner._previously_delegated(fo1, uri1, provider1))
        self.assertTrue(provider_runner._previously_delegated(fo1, uri2, provider1))
        self.assertTrue(provider_runner._previously_delegated(fo2, uri1, provider1))
        self.assertFalse(provider_runner._previously_delegated(fo1, uri2, provider2))
        self.assertTrue(provider_runner._previously_delegated(fo1, uri1, provider2))
        self.assertTrue(provider_runner._previously_delegated(fo2, uri1, provider2))
        self.assertFalse(provider_runner._previously_delegated(fo2, uri2, provider2))


def _get_mock_config():
    return Mock()


class TestMasterDataProvider(TestCase):
    @patch('core.repository.SessionRepository', MagicMock())
    def test_instantiated_master_data_provider_is_not_none(self):
        p = MasterDataProvider(config=_get_mock_config())
        self.assertIsNotNone(p)

    @patch('core.repository.SessionRepository', MagicMock())
    @patch('core.master_provider.ProviderRunner.delegate_every_possible_meowuri')
    def test_delegate_every_possible_meowuri(self, mock_delegate_every_possible_meowuri):
        p = MasterDataProvider(config=_get_mock_config())

        mock_fileobject = Mock()
        p.delegate_every_possible_meowuri(mock_fileobject)
        mock_delegate_every_possible_meowuri.assert_called_with(mock_fileobject)

    @patch('core.repository.SessionRepository')
    @patch('core.master_provider.MasterDataProvider._delegate_to_providers')
    def test_request_when_data_is_already_stored_in_the_repository(
            self, mock__delegate_to_providers, mock_session_repository
    ):
        mock_session_repository.query.return_value = True  # Data already in repository
        mock_fileobject = Mock()
        mock_meowuri = Mock()

        p = MasterDataProvider(config=_get_mock_config())
        response = p.request(mock_fileobject, mock_meowuri)

        self.assertTrue(response)
        mock_session_repository.query.assert_called_once_with(mock_fileobject, mock_meowuri)
        mock__delegate_to_providers.assert_not_called()

    @patch('core.repository.SessionRepository')
    @patch('core.master_provider.MasterDataProvider._delegate_to_providers')
    def test_request_delegates_to_providers_when_data_is_not_stored_in_the_repository(
            self, mock__delegate_to_providers, mock_session_repository
    ):
        mock_session_repository.query.return_value = False  # Data not in repository
        mock_fileobject = Mock()
        mock_meowuri = Mock()

        p = MasterDataProvider(config=_get_mock_config())
        response = p.request(mock_fileobject, mock_meowuri)

        self.assertFalse(response)  # Mock returns False every time ..
        mock_session_repository.query.assert_called_with(mock_fileobject, mock_meowuri)
        self.assertEqual(2, mock_session_repository.query.call_count)
        mock__delegate_to_providers.assert_called_with(mock_fileobject, mock_meowuri)
