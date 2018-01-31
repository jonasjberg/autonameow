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
    Handles top-level _DYNAMIC_ data retrieval and data extraction delegation.

    This is one of two main means of querying for data related to a file.
    Compared to the repository, which is a static storage that either contain
    the requested data or not, this is a "reactive" interface to the repository.

    If the requested data is in the repository, is it retrieved and returned.
    Otherwise, data providers (extractors/analyzers/plugins) that might be able
    to provide the requested data is executed. If the execution turns up the
    requested data, it is returned.
    This is intended to be a "dynamic" or "reactive" data retrieval interface
    for use by any part of the application.
    """
    def __init__(self, config):
        self.seen_fileobject_meowuris = defaultdict(dict)
        self.config = config

        self.debug_stats = defaultdict(dict)

    def query(self, fileobject, meowuri):
        """
        First attempt to get the data from the repository.
        If that fails, delegate the task of extracting the data to the
        "relevant" providers. Then try querying the repository again.
        """
        if meowuri not in self.debug_stats[fileobject]:
            self.debug_stats[fileobject][meowuri] = dict()
            self.debug_stats[fileobject][meowuri]['queries'] = 1
            self.debug_stats[fileobject][meowuri]['repository_queries'] = 0
            self.debug_stats[fileobject][meowuri]['delegated'] = 0
        else:
            self.debug_stats[fileobject][meowuri]['queries'] += 1

        self._print_debug_stats()

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
        return None

    def _query_repository(self, fileobject, meowuri):
        self.debug_stats[fileobject][meowuri]['repository_queries'] += 1

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
        log.debug('Delegating request to providers: [{:8.8}]->[{!s}]'.format(fileobject.hash_partial, meowuri))

        self.debug_stats[fileobject][meowuri]['delegated'] += 1
        _delegation_count = self.debug_stats[fileobject][meowuri]['delegated']
        if _delegation_count > 1:
            log.warning('Delegated {} times:  [{:8.8}]->[{!s}]'.format(_delegation_count, fileobject.hash_partial, meowuri))

        # TODO: [TD0142] Rework overall architecture to fetch data when needed.
        _possible_providers = providers.get_providers_for_meowuri(meowuri)
        log.debug('Got {} possible providers'.format(len(_possible_providers)))

        # TODO: [TD0142] Handle this properly ..
        # TODO: [TD0142] Check here if the provider can handle the file.
        # Run only what is suitable and necessary.
        # Currently, when requesting 'generic.contents.text' from a PDF
        # document, the extractor runner is started 4 times.
        # Only one of these are really appropriate; when requesting the
        # 'PdftotextTextExtractor'. Other extractor requests should be skipped.

        # TODO: [TD0161] Translate from specific to "generic" MeowURI?
        # Might be useful to be able to translate a specific MeowURI like
        # 'analyzer.ebook.title' to a "generic" like 'generic.metadata.title'.
        # Otherwise, user is almost never prompted with any possible candidates.
        if _possible_providers:
            for _provider in _possible_providers:
                log.debug('Delegating possible provider: {!s}'.format(_provider))
                if issubclass(_provider, BaseExtractor):
                    extraction.run_extraction(fileobject, [_provider])
                elif issubclass(_provider, BaseAnalyzer):
                    analysis.run_analysis(
                        fileobject,
                        self.config,
                        analyzers_to_run=None
                        #analyzers_to_run=[_provider]
                    )
                elif issubclass(_provider, plugins.BasePlugin):
                    plugin_handler.run_plugins(
                        fileobject,
                        require_plugins=_provider,
                    )

    def _print_debug_stats(self):
        if not __debug__:
            return

        stats_strings = list()
        for _fileobject, _meowuris in self.debug_stats.items():
            for _meowuri, _counters in _meowuris.items():
                _meowuri_stats = ['{}: {}'.format(stat, count)
                                  for stat, count in _counters.items()]
                stats_strings.append(
                    '[{:8.8}]->{!s:60.60} {!s}'.format(_fileobject.hash_partial,
                                                       _meowuri,
                                                       ' '.join(_meowuri_stats))
                )

        log.debug('{!s} debug stats:'.format(self.__class__.__name__))
        for stat_string in sorted(stats_strings):
            log.debug(stat_string)


_master_data_provider = None


def initialize(active_config):
    global _master_data_provider
    _master_data_provider = MasterDataProvider(active_config)


def query(fileobject, meowuri):
    sanity.check_isinstance_meowuri(
        meowuri, msg='TODO: [TD0133] Fix inconsistent use of MeowURIs'
    )
    return _master_data_provider.query(fileobject, meowuri)
