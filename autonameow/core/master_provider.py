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

from core import constants as C
from core import event
from core import logs
from core import repository
from core.exceptions import AutonameowException
from core.model import genericfields
from core.repository import QueryResponseFailure
from util import sanity


log = logging.getLogger(__name__)


def _map_generic_sources(meowuri_class_map):
    """
    Returns a dict keyed by provider classes storing sets of "generic"
    fields as Unicode strings.
    """
    out = dict()

    # for root in ['extractors', 'analyzer'] ..
    for root in sorted(list(C.MEOWURI_ROOTS_SOURCES)):
        if root not in meowuri_class_map:
            continue

        out[root] = dict()
        for _, klass in meowuri_class_map[root].items():
            out[root][klass] = set()

            # TODO: [TD0151] Fix inconsistent use of classes/instances.
            # TODO: [TD0157] Look into analyzers 'FIELD_LOOKUP' attributes.
            for _, field_metainfo in klass.metainfo().items():
                _generic_field_string = field_metainfo.get('generic_field')
                if not _generic_field_string:
                    continue

                sanity.check_internal_string(_generic_field_string)
                _generic_field_klass = genericfields.get_field_for_uri_leaf(_generic_field_string)
                if not _generic_field_klass:
                    continue

                assert issubclass(_generic_field_klass, genericfields.GenericField)
                _generic_meowuri = _generic_field_klass.uri()
                if not _generic_meowuri:
                    continue

                out[root][klass].add(_generic_meowuri)
    return out


def _get_meowuri_source_map():
    def __get_meowuri_roots_for_providers(module_name):
        """
        Returns a dict mapping "MeowURIs" to provider classes.

        Example return value: {
            'extractor.filesystem.xplat': CrossPlatformFilesystemExtractor,
            'extractor.metadata.exiftool': ExiftoolMetadataExtractor,
        }

        Returns: Dictionary keyed by instances of the 'MeowURI' class,
                 storing provider classes.
        """
        module_registry = getattr(module_name, 'registry')
        klass_list = module_registry.all_providers

        mapping = dict()
        for klass in klass_list:
            uri = klass.meowuri_prefix()
            if not uri:
                # TODO: [TD0151] Fix inconsistent use of classes/instances.
                log.critical('Got empty from '
                             '"{!s}.meowuri_prefix()"'.format(klass.name()))
                continue

            assert uri not in mapping, (
                'Provider MeowURI "{!s}" is already mapped'.format(uri)
            )
            mapping[uri] = klass
        return mapping

    import analyzers
    import extractors
    return {
        'extractor': __get_meowuri_roots_for_providers(extractors),
        'analyzer': __get_meowuri_roots_for_providers(analyzers),
    }


def _get_excluded_sources():
    """
    Returns a dict of provider classes excluded due to unmet dependencies.
    """
    def __get_excluded_providers(module_name):
        module_registry = getattr(module_name, 'registry')
        return module_registry.excluded_providers

    import extractors
    import analyzers
    return {
        'extractor': __get_excluded_providers(extractors),
        'analyzer': __get_excluded_providers(analyzers),
    }


class ProviderRegistry(object):
    def __init__(self, meowuri_source_map, excluded_providers):
        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )

        self.meowuri_sources = dict(meowuri_source_map)
        self._debug_log_mapped_meowuri_sources()

        self.excluded_providers = excluded_providers

        # Set of all MeowURIs "registered" by extractors or analyzers.
        self.mapped_meowuris = self.unique_map_meowuris(self.meowuri_sources)

        # Providers declaring generic MeowURIs through 'metainfo()'.
        self.generic_meowuri_sources = _map_generic_sources(
            self.meowuri_sources
        )

        # VALID_SOURCE_ROOTS = set(C.MEOWURI_ROOTS_SOURCES)
        # assert all(r in self.generic_meowuri_sources
        #            for r in VALID_SOURCE_ROOTS)

    def _debug_log_mapped_meowuri_sources(self):
        if not logs.DEBUG:
            return

        for key in self.meowuri_sources.keys():
            for meowuri, klass in self.meowuri_sources[key].items():
                self.log.debug('Mapped MeowURI "{!s}" to "{!s}" ({!s})'.format(
                    meowuri, klass, key))

    def might_be_resolvable(self, uri):
        if not uri:
            return False

        sanity.check_isinstance_meowuri(uri)
        resolvable = list(self.mapped_meowuris)
        uri_without_leaf = uri.stripleaf()
        return any(m.matches_start(uri_without_leaf) for m in resolvable)

    def providers_for_meowuri(self, requested_meowuri, includes=None):
        """
        Returns a set of classes that might store data under a given "MeowURI".

        Note that the provider "MeowURI" is matched as a substring of the
        requested "MeowURI".

        Args:
            requested_meowuri: The "MeowURI" of interest.
            includes: Optional list of provider roots to include.
                      Must be one of 'C.MEOWURI_ROOTS_SOURCES'.
                      Default is to include all.

        Returns:
            A set of classes that "could" produce and store data under a
            "MeowURI" that is a substring of the given "MeowURI".
        """
        found = set()
        if not requested_meowuri:
            log.error('"providers_for_meowuri()" got empty MeowURI!')
            return found

        if requested_meowuri.is_generic:
            found = self._providers_for_generic_meowuri(requested_meowuri,
                                                        includes)
        else:
            found = self._source_providers_for_meowuri(requested_meowuri,
                                                       includes)

        log.debug('{} returning {} providers for MeowURI {!s}'.format(
            self.__class__.__name__, len(found), requested_meowuri))
        return found

    @staticmethod
    def _yield_included_roots(includes=None):
        VALID_INCLUDES = set(C.MEOWURI_ROOTS_SOURCES)
        if not includes:
            # No includes specified -- search all ("valid includes") providers.
            includes = VALID_INCLUDES
        else:
            # Search only specified providers.
            # Sanity-check 'includes' argument.
            for include in includes:
                assert include in VALID_INCLUDES, (
                    '"{!s}" is not one of {!s}'.format(include, VALID_INCLUDES)
                )

        # Sort for more consistent behaviour.
        for root in sorted(list(includes)):
            yield root

    def _providers_for_generic_meowuri(self, requested_meowuri, includes=None):
        found = set()
        for root in self._yield_included_roots(includes):
            for klass, meowuris in self.generic_meowuri_sources[root].items():
                if requested_meowuri in meowuris:
                    found.add(klass)
        return found

    def _source_providers_for_meowuri(self, requested_meowuri, includes=None):
        # 'uri' is shorter "root";
        #     'extractor.metadata.epub'
        # 'requested_meowuri' is full "source-specific";
        #     'extractor.metadata.exiftool.EXIF:CreateDate'
        found = set()
        requested_meowuri_without_leaf = requested_meowuri.stripleaf()
        for root in self._yield_included_roots(includes):
            for uri in self.meowuri_sources[root].keys():
                if uri.matches_start(requested_meowuri_without_leaf):
                    found.add(self.meowuri_sources[root][uri])
        return found

    @staticmethod
    def unique_map_meowuris(meowuri_class_map):
        out = set()
        # for root in ['extractors', 'analyzer'] ..
        for root in meowuri_class_map.keys():
            for uri in meowuri_class_map[root].keys():
                out.add(uri)
        return out


class ProviderRunner(object):
    def __init__(self, config, extractor_runner, run_analysis_func):
        self.config = config
        self._extractor_runner = extractor_runner
        self._run_analysis = run_analysis_func

        self.debug_stats = defaultdict(dict)
        self._provider_delegation_history = defaultdict(set)
        self._delegate_every_possible_meowuri_history = set()

    def delegate_to_providers(self, fileobject, uri):
        possible_providers = set(Registry.providers_for_meowuri(uri))
        if not possible_providers:
            log.debug('Got no possible providers for delegation {!s}'.format(uri))
            return

        # TODO: [TD0161] Translate from specific to "generic" MeowURI?
        # Might be useful to be able to translate a specific MeowURI like
        # 'analyzer.ebook.title' to a "generic" like 'generic.metadata.title'.
        # Otherwise, user is almost never prompted with any possible candidates.

        prepared_analyzers = set()
        prepared_extractors = set()
        num_possible_providers = len(possible_providers)
        for n, provider in enumerate(possible_providers, start=1):
            log.debug('Looking at possible provider ({}/{}): {!s}'.format(
                n, num_possible_providers, provider
            ))

            if self._previously_delegated_provider(fileobject, provider):
                log.debug('Skipping previously delegated provider {!s}'.format(provider))
                continue

            self._remember_provider_delegation(fileobject, provider)

            if _provider_is_extractor(provider):
                prepared_extractors.add(provider)
            elif _provider_is_analyzer(provider):
                prepared_analyzers.add(provider)

        if prepared_extractors:
            log.debug('Delegating {!s} to extractors: {!s}'.format(uri, prepared_extractors))
            self._delegate_to_extractors(fileobject, prepared_extractors)
        if prepared_analyzers:
            log.debug('Delegating {!s} to analyzers: {!s}'.format(uri, prepared_analyzers))
            self._delegate_to_analyzers(fileobject, prepared_analyzers)

    def _previously_delegated_provider(self, fileobject, provider):
        if fileobject in self._delegate_every_possible_meowuri_history:
            return True

        return bool(
            fileobject in self._provider_delegation_history
            and provider in self._provider_delegation_history[fileobject]
        )

    def _remember_provider_delegation(self, fileobject, provider):
        self._provider_delegation_history[fileobject].add(provider)

    def _delegate_to_extractors(self, fileobject, extractors_to_run):
        try:
            self._extractor_runner.start(fileobject, extractors_to_run)
        except AutonameowException as e:
            # TODO: [TD0164] Tidy up throwing/catching of exceptions.
            log.critical('Extraction FAILED: {!s}'.format(e))
            raise

    def _delegate_to_analyzers(self, fileobject, analyzers_to_run):
        self._run_analysis(
            fileobject,
            self.config,
            analyzers_to_run=analyzers_to_run
        )

    def delegate_every_possible_meowuri(self, fileobject):
        self._delegate_every_possible_meowuri_history.add(fileobject)

        # Run all extractors
        try:
            self._extractor_runner.start(fileobject, request_all=True)
        except AutonameowException as e:
            # TODO: [TD0164] Tidy up throwing/catching of exceptions.
            log.critical('Extraction FAILED: {!s}'.format(e))
            raise

        # Run all analyzers
        self._run_analysis(fileobject, self.config)


def _provider_is_extractor(provider):
    # TODO: [hack] Fix circular import problems when running new unit test runner.
    #       $ PYTHONPATH=autonameow:tests python3 -m unit --skip-slow
    from extractors.common import BaseMetadataExtractor
    return issubclass(provider, BaseMetadataExtractor)


def _provider_is_analyzer(provider):
    # TODO: [hack] Fix circular import problems when running new unit test runner.
    #       $ PYTHONPATH=autonameow:tests python3 -m unit --skip-slow
    from analyzers import BaseAnalyzer
    return issubclass(provider, BaseAnalyzer)


class MasterDataProvider(object):
    """
    Handles top-level _DYNAMIC_ data retrieval and data extraction delegation.

    This is one of two main means of querying for data related to a file.
    Compared to the repository, which is a static storage that either contain
    the requested data or not, this is a "reactive" interface to the repository.

    If the requested data is in the repository, is it retrieved and returned.
    Otherwise, data providers (extractors/analyzers) that might be able
    to provide the requested data is executed. If the execution turns up the
    requested data, it is returned.
    This is intended to be a "dynamic" or "reactive" data retrieval interface
    for use by any part of the application.
    """
    def __init__(self, config):
        self.config = config

        # Import class instance and function to be DI'd into 'ProviderRunner'.
        from core import analysis
        run_analysis_func = analysis.run_analysis
        assert callable(run_analysis_func), (
            'Expected dependency injected "run_analysis" to be callable'
        )

        from core.extraction import ExtractorRunner
        extractor_runner = ExtractorRunner(
            add_results_callback=repository.SessionRepository.store
        )
        assert hasattr(extractor_runner, 'start'), (
            'Expected attribute "start" in dependency injected ExtractorRunner'
        )

        self.provider_runner = ProviderRunner(
            self.config,
            extractor_runner,
            run_analysis_func
        )

        self.debug_stats = defaultdict(dict)

    def delegate_every_possible_meowuri(self, fileobject):
        log.debug('Running all available providers for {!r}'.format(fileobject))
        self.provider_runner.delegate_every_possible_meowuri(fileobject)

    def request(self, fileobject, uri):
        """
        Highest-level retrieval mechanism for data related to a file.

        First the repository is queried with the MeowURI and if the query
        returns data, it is returned. If the data is not in the repository,
        the task of gathering the data is delegated to the "relevant" providers.
        Then the repository is queried again.
        If the delegation "succeeded" and the sought after data could be
        gathered, it would now be stored in the repository and passed back
        as the return value.
        None is returned if nothing turns up.
        """
        if uri not in self.debug_stats[fileobject]:
            self.debug_stats[fileobject][uri] = dict()
            self.debug_stats[fileobject][uri]['queries'] = 1
            self.debug_stats[fileobject][uri]['repository_queries'] = 0
            self.debug_stats[fileobject][uri]['delegated'] = 0
        else:
            self.debug_stats[fileobject][uri]['queries'] += 1

        # TODO: Provide means of toggling on/off or remove.
        # self._print_debug_stats()

        log.debug('Got request {!r}->[{!s}]'.format(fileobject, uri))

        # First try the repository for previously gathered data
        response = self._query_repository(fileobject, uri)
        if response:
            return response

        # Have relevant providers gather the data
        self._delegate_to_providers(fileobject, uri)

        # Try the repository again
        response = self._query_repository(fileobject, uri)
        if response:
            return response

        log.debug('Failed query, then delegation, then another query and returning None')
        return QueryResponseFailure(
            fileobject=fileobject, uri=uri,
            msg='Repository query -> Delegation -> Repository query'
        )

    def request_one(self, fileobject, uri):
        # TODO: [TD0175] Handle requesting exactly one or multiple alternatives.
        response = self.request(fileobject, uri)
        if isinstance(response, list):
            if len(response) == 1:
                return response[0]

            return QueryResponseFailure(
                fileobject=fileobject, uri=uri,
                msg='Requested one but response contains {}'.format(len(response))
            )

        return response

    def _delegate_to_providers(self, fileobject, uri):
        log.debug('Delegating request to providers: {!r}->[{!s}]'.format(fileobject, uri))
        self.debug_stats[fileobject][uri]['delegated'] += 1
        self.provider_runner.delegate_to_providers(fileobject, uri)

    def _query_repository(self, fileobject, uri):
        self.debug_stats[fileobject][uri]['repository_queries'] += 1
        return repository.SessionRepository.query(fileobject, uri)

    def _print_debug_stats(self):
        if not logs.DEBUG:
            return

        stats_strings = list()
        for fileobject, uris in self.debug_stats.items():
            for uri, _counters in uris.items():
                uri_stats = [
                    '{}: {}'.format(stat, count) for stat, count in _counters.items()
                ]
                stats = '{!r}->{!s:60.60} {!s}'.format(fileobject, uri, ' '.join(uri_stats))
                stats_strings.append(stats)

        log.debug('{!s} debug stats:'.format(self.__class__.__name__))
        for stat_string in sorted(stats_strings):
            log.debug(stat_string)


_MASTER_DATA_PROVIDER = None
Registry = None


def _initialize_master_data_provider(*_, **kwargs):
    # assert 'config' in kwargs
    active_config = kwargs.get('config')

    # Keep one global 'MasterDataProvider' singleton per 'Autonameow' instance.
    global _MASTER_DATA_PROVIDER
    _MASTER_DATA_PROVIDER = MasterDataProvider(active_config)


def _shutdown_master_data_provider(*_, **__):
    global _MASTER_DATA_PROVIDER
    _MASTER_DATA_PROVIDER = None


def _initialize_provider_registry(*_, **__):
    # Keep one global 'ProviderRegistry' singleton per 'Autonameow' instance.
    global Registry
    if not Registry:
        Registry = ProviderRegistry(
            meowuri_source_map=_get_meowuri_source_map(),
            excluded_providers=_get_excluded_sources()
        )


def _shutdown_provider_registry(*_, **__):
    global Registry
    Registry = None


event.dispatcher.on_config_changed.add(_initialize_master_data_provider)
event.dispatcher.on_startup.add(_initialize_provider_registry)
event.dispatcher.on_shutdown.add(_shutdown_provider_registry)
event.dispatcher.on_shutdown.add(_shutdown_master_data_provider)


def request(fileobject, uri):
    sanity.check_isinstance_meowuri(uri)
    return _MASTER_DATA_PROVIDER.request(fileobject, uri)


def request_one(fileobject, uri):
    sanity.check_isinstance_meowuri(uri)
    return _MASTER_DATA_PROVIDER.request_one(fileobject, uri)


def delegate_every_possible_meowuri(fileobject):
    _MASTER_DATA_PROVIDER.delegate_every_possible_meowuri(fileobject)
