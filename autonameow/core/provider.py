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

import logging
import pprint
from collections import defaultdict

import plugins
from analyzers import BaseAnalyzer
from core import (
    analysis,
    extraction,
    plugin_handler,
    providers,
    repository,
)
from extractors import BaseExtractor
from util import sanity


log = logging.getLogger(__name__)


# TODO: [TD0142] Rework overall architecture to fetch data when needed.


class MasterDataProvider(object):
    """
    Handles top-level data retrieval and data extraction delegation.

    Part of restructuring the overall architecture to fetch data lazily while
    evaluating rule conditions, etc.
    """
    def __init__(self, config):
        self.seen_fileobject_meowuris = defaultdict(dict)
        self.config = config

        self.debug_stats = defaultdict(dict)

    def query(self, fileobject, meowuri):
        if meowuri not in self.debug_stats[fileobject]:
            self.debug_stats[fileobject][meowuri] = dict()
            self.debug_stats[fileobject][meowuri]['seen'] = 1
            self.debug_stats[fileobject][meowuri]['queries'] = 0
            self.debug_stats[fileobject][meowuri]['delegated'] = 0
        else:
            self.debug_stats[fileobject][meowuri]['seen'] += 1

        _data = self._query_repository(fileobject, meowuri)
        if _data:
            return _data

        self._delegate_to_providers(fileobject, meowuri)

        # TODO: [TD0142] Handle this properly ..
        _data = self._query_repository(fileobject, meowuri)
        if _data:
            return _data

        # TODO: [TD0142] Handle this properly ..
        log.debug('Failed query, then delegation, then another query and returning None')
        self._print_debug_stats()
        return None

    def _query_repository(self, fileobject, meowuri):
        self.debug_stats[fileobject][meowuri]['queries'] += 1

        if fileobject in self.seen_fileobject_meowuris:
            _cached_data = self.seen_fileobject_meowuris[fileobject].get(meowuri)
            if _cached_data:
                return _cached_data

        _repo_data = repository.SessionRepository.query(fileobject, meowuri)
        if _repo_data:
            self.seen_fileobject_meowuris[fileobject][meowuri] = _repo_data
            return _repo_data

        return None

    def _delegate_to_providers(self, fileobject, meowuri):
        self.debug_stats[fileobject][meowuri]['delegated'] += 1

        _possible_providers = providers.get_providers_for_meowuri(meowuri)
        # TODO: [TD0142] Rework overall architecture to fetch data when needed.
        log.debug('Delegating request to providers: [{:8.8}]->[{!s}]'.format(fileobject.hash_partial, meowuri))
        log.debug('Possible Providers: {!s}'.format(_possible_providers))

        # TODO: [TD0142] Handle this properly ..
        if _possible_providers:
            for _provider in _possible_providers:
                if issubclass(_provider, BaseExtractor):
                    extraction.run_extraction(fileobject, [_provider])
                elif issubclass(_provider, BaseAnalyzer):
                    analysis.run_analysis(fileobject, self.config)
                elif issubclass(_provider, plugins.BasePlugin):
                    plugin_handler.run_plugins(
                        fileobject,
                        require_plugins=_provider,
                    )

    def _print_debug_stats(self):
        log.debug(pprint.pformat(self.debug_stats))


_master_data_provider = None


def initialize(active_config):
    global _master_data_provider
    _master_data_provider = MasterDataProvider(active_config)


def query(fileobject, meowuri):
    sanity.check_isinstance_meowuri(
        meowuri, msg='TODO: [TD0133] Fix inconsistent use of MeowURIs'
    )
    return _master_data_provider.query(fileobject, meowuri)
