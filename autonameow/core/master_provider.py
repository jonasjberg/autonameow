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

import logging
from collections import defaultdict

from core import event
from core import logs
from core.datastore import repository
from core.datastore.query import QueryResponseFailure
from core.exceptions import AutonameowException
from core.model import genericfields
from util import sanity


log = logging.getLogger(__name__)


def _map_generic_sources(meowuri_class_map):
    """
    Returns a dict keyed by provider classes storing sets of "generic"
    fields as Unicode strings.
    """
    klass_generic_meowuris_map = defaultdict(set)
    for _, klass in meowuri_class_map.items():
        # TODO: [TD0151] Fix inconsistent use of classes/instances.
        # TODO: [TD0157] Look into analyzers 'FIELD_LOOKUP' attributes.
        for _, field_metainfo in klass.metainfo().items():
            generic_field_string = field_metainfo.get('generic_field')
            if not generic_field_string:
                continue

            assert isinstance(generic_field_string, str)
            generic_field_klass = genericfields.get_field_for_uri_leaf(generic_field_string)
            if not generic_field_klass:
                continue

            assert issubclass(generic_field_klass, genericfields.GenericField)
            generic_meowuri = generic_field_klass.uri()
            if not generic_meowuri:
                continue

            klass_generic_meowuris_map[klass].add(generic_meowuri)

    return klass_generic_meowuris_map


def _get_meowuri_source_map():
    """
    Returns a dict mapping "MeowURIs" to provider classes.

    Example return value: {
        'extractor.filesystem.xplat': CrossPlatformFilesystemExtractor,
        'extractor.metadata.exiftool': ExiftoolMetadataExtractor,
    }

    Returns: Dictionary keyed by instances of the 'MeowURI' class,
             storing provider classes.
    """
    import analyzers
    import extractors

    mapping = dict()
    for module_name in (analyzers, extractors):
        module_registry = getattr(module_name, 'registry')
        klass_list = module_registry.all_providers

        for klass in klass_list:
            uri = klass.meowuri_prefix()
            assert uri, 'Got empty "meowuri_prefix" from {!s}'.format(klass)
            assert uri not in mapping, 'URI "{!s}" already mapped'.format(uri)
            mapping[uri] = klass

    return mapping


def _get_excluded_sources():
    """
    Returns a set of provider classes excluded due to unmet dependencies.
    """
    import extractors
    import analyzers

    all_excluded = set()
    for module_name in (analyzers, extractors):
        module_registry = getattr(module_name, 'registry')
        all_excluded.update(module_registry.excluded_providers)
    return all_excluded


class ProviderRegistry(object):
    def __init__(self, meowuri_source_map, excluded_providers):
        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )

        self.meowuri_sources = dict(meowuri_source_map)
        self._debug_log_mapped_meowuri_sources()
        self._excluded_providers = excluded_providers

        # Set of all MeowURIs "registered" by extractors or analyzers.
        self.mapped_meowuris = self.unique_map_meowuris(self.meowuri_sources)

        # Providers declaring generic MeowURIs through 'metainfo()'.
        self.generic_meowuri_sources = _map_generic_sources(self.meowuri_sources)
        self._debug_log_mapped_generic_meowuri_sources()

    @property
    def excluded_providers(self):
        # Sort here so that callers won't have to work around the possibility
        # of excluded providers not having a common base class and thus being
        # unorderable.
        return sorted(self._excluded_providers, key=lambda x: x.__name__)

    def _debug_log_mapped_meowuri_sources(self):
        if not logs.DEBUG:
            return

        for uri, klass in sorted(self.meowuri_sources.items()):
            self.log.debug('Mapped MeowURI "%s" to %s', uri, klass.name())

    def _debug_log_mapped_generic_meowuri_sources(self):
        if not logs.DEBUG:
            return

        for klass, uris in self.generic_meowuri_sources.items():
            klass_name = klass.name()
            for uri in sorted(uris):
                self.log.debug('Mapped generic MeowURI "%s" to %s', uri, klass_name)

    def might_be_resolvable(self, uri):
        if not uri:
            return False

        sanity.check_isinstance_meowuri(uri)
        resolvable = list(self.mapped_meowuris)
        uri_without_leaf = uri.stripleaf()
        return any(m.matches_start(uri_without_leaf) for m in resolvable)

    def providers_for_meowuri(self, requested_meowuri):
        """
        Returns a set of classes that might store data under a given "MeowURI".

        Note that the provider "MeowURI" is matched as a substring of the
        requested "MeowURI".

        Args:
            requested_meowuri: The "MeowURI" of interest.

        Returns:
            A set of classes that "could" produce and store data under a
            "MeowURI" that is a substring of the given "MeowURI".
        """
        found = set()
        if not requested_meowuri:
            self.log.error('"providers_for_meowuri()" got empty MeowURI!')
            return found

        if requested_meowuri.is_generic:
            found = self._providers_for_generic_meowuri(requested_meowuri)
        else:
            found = self._source_providers_for_meowuri(requested_meowuri)

        self.log.debug('%s returning %d providers for MeowURI %s',
                       self.__class__.__name__, len(found), requested_meowuri)
        return found

    def _providers_for_generic_meowuri(self, requested_meowuri):
        found = set()
        for klass, meowuris in self.generic_meowuri_sources.items():
            if requested_meowuri in meowuris:
                found.add(klass)
        return found

    def _source_providers_for_meowuri(self, requested_meowuri):
        # Argument 'requested_meowuri' is a full "source-specific" MeowURI,
        # like 'extractor.metadata.exiftool.EXIF:CreateDate'
        requested_meowuri_without_leaf = requested_meowuri.stripleaf()

        found = set()
        for uri in self.meowuri_sources.keys():
            # 'uri' is a "MeowURI root" ('extractor.metadata.epub')
            if uri.matches_start(requested_meowuri_without_leaf):
                found.add(self.meowuri_sources[uri])
        return found

    @staticmethod
    def unique_map_meowuris(meowuri_class_map):
        unique_meowuris = set()
        for uri in meowuri_class_map.keys():
            unique_meowuris.add(uri)
        return unique_meowuris


class ProviderRunner(object):
    def __init__(self, config, extractor_runner, run_analysis_func):
        self.config = config
        self._extractor_runner = extractor_runner

        assert callable(run_analysis_func), (
            'Expected dependency-injected "run_analysis" to be callable'
        )
        self._run_analysis = run_analysis_func

        self._provider_delegation_history = defaultdict(set)
        self._delegate_every_possible_meowuri_history = set()

    def delegate_to_providers(self, fileobject, uri):
        possible_providers = set(Registry.providers_for_meowuri(uri))
        if not possible_providers:
            log.debug('Got no possible providers for delegation %s', uri)
            return

        # TODO: [TD0161] Translate from specific to "generic" MeowURI?
        # Might be useful to be able to translate a specific MeowURI like
        # 'analyzer.ebook.title' to a "generic" like 'generic.metadata.title'.
        # Otherwise, user is almost never prompted with any possible candidates.

        prepared_analyzers = set()
        prepared_extractors = set()
        num_possible_providers = len(possible_providers)
        for n, provider in enumerate(possible_providers, start=1):
            log.debug('Looking at possible provider (%d/%d): %s',
                      n, num_possible_providers, provider)

            if self._previously_delegated_provider(fileobject, provider):
                log.debug('Skipping previously delegated provider %s', provider)
                continue

            self._remember_provider_delegation(fileobject, provider)

            if _provider_is_extractor(provider):
                prepared_extractors.add(provider)
            elif _provider_is_analyzer(provider):
                prepared_analyzers.add(provider)

        if prepared_extractors:
            log.debug('Delegating %s to extractors: %s', uri, prepared_extractors)
            self._delegate_to_extractors(fileobject, prepared_extractors)
        if prepared_analyzers:
            log.debug('Delegating %s to analyzers: %s', uri, prepared_analyzers)
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
            log.critical('Extraction FAILED: %s', e)
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
            log.critical('Extraction FAILED: %s', e)
            raise

        # Run all analyzers
        self._run_analysis(fileobject, self.config)


def _provider_is_extractor(provider):
    # TODO: [hack] Fix circular import problems when running new unit test runner.
    #       $ PYTHONPATH=autonameow:tests python3 -m unit --skip-slow
    from extractors.metadata.base import BaseMetadataExtractor
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
    def __init__(self, config, run_analysis_func):
        self.config = config

        assert repository.SessionRepository is not None, (
            'Expected Repository to be initialized at this point'
        )
        from core.extraction import ExtractorRunner
        extractor_runner = ExtractorRunner(
            add_results_callback=repository.SessionRepository.store
        )
        assert hasattr(extractor_runner, 'start'), (
            'Expected "ExtractorRunner" to have an attribute "start"'
        )

        self.provider_runner = ProviderRunner(
            self.config,
            extractor_runner,
            run_analysis_func
        )

    def delegate_every_possible_meowuri(self, fileobject):
        log.debug('Running all available providers for %r', fileobject)
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
        log.debug('Got request %r->[%s]', fileobject, uri)

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
        log.debug('Delegating request to providers: %r->[%s]', fileobject, uri)
        self.provider_runner.delegate_to_providers(fileobject, uri)

    def _query_repository(self, fileobject, uri):
        return repository.SessionRepository.query(fileobject, uri)


_MASTER_DATA_PROVIDER = None


def _initialize_master_data_provider(*_, **kwargs):
    active_config = kwargs.get('config')

    from core import analysis
    run_analysis_func = analysis.run_analysis

    # Keep one global 'MasterDataProvider' singleton per 'Autonameow' instance.
    global _MASTER_DATA_PROVIDER
    _MASTER_DATA_PROVIDER = MasterDataProvider(active_config, run_analysis_func)


def _shutdown_master_data_provider(*_, **__):
    # TODO: [TD0202] Handle signals and graceful shutdown properly!
    global _MASTER_DATA_PROVIDER
    _MASTER_DATA_PROVIDER = None


Registry = None


def _initialize_provider_registry(*_, **__):
    # Keep one global 'ProviderRegistry' singleton per 'Autonameow' instance.
    global Registry
    if not Registry:
        Registry = ProviderRegistry(
            meowuri_source_map=_get_meowuri_source_map(),
            excluded_providers=_get_excluded_sources()
        )


def _shutdown_provider_registry(*_, **__):
    # TODO: [TD0202] Handle signals and graceful shutdown properly!
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
