# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2020 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import extractors
from core import event
from core import logs
from core.model import force_meowuri
from core.persistence import PersistenceError
from core.providers import wrap_provider_results
from extractors import ExtractorError
from util import sanity


log = logging.getLogger(__name__)


def filter_able_to_handle(extractor_klasses, fileobject):
    """
    Returns extractor classes that can handle the given file object.

    Args:
        extractor_klasses: List or set of extractor classes to filter.
        fileobject: The 'FileObject' that extractors should be able to handle.

    Returns:
        The set of extractor classes that can extract data from the given file.
    """
    return {k for k in extractor_klasses if k.can_handle(fileobject)}


def filter_not_slow(extractor_klasses, required):
    return {k for k in extractor_klasses if not k.IS_SLOW or k in required}


class ExtractorRunner(object):
    def __init__(self, add_results_callback=None):
        """
        Instantiates a new extractor runner.

        Results are passed to the callback when running the extractors.
        The callback should accept three arguments;

            fileobject (FileObject), meowuri (MeowURI), data (dict)

        It will be called for each extracted "item" returned by each of the
        selected extractors. Results are simply discarded if the callback is
        left unspecified, rendering the run basically a expensive "no-op".

        If 'exclude_slow' is true, "slow" extractors that are not explicitly
        requested are excluded. Alternatively, if all extractors are requested
        slow extractors will be included as well.

        Args:
            add_results_callback: Callable that accepts three arguments.
        """
        if add_results_callback:
            assert callable(add_results_callback)
            self._add_results_callback = add_results_callback
        else:
            # Throw away the results. For testing, etc.
            self._add_results_callback = lambda *_: None

        self._instance_pool = dict()
        self._available_extractors = set()
        self.exclude_slow = True

        self.register(extractors.registry.all_providers)
        event.dispatcher.on_shutdown.add(self.shutdown_pooled_extractors)

    def register(self, extractor_klasses):
        self._available_extractors.update(extractor_klasses)

        if logs.DEBUG:
            log.debug('Initialized %s with %d available extractors',
                      self.__class__.__name__, len(self._available_extractors))
            for k in self._available_extractors:
                # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
                log.debug('Available: %s', k.name())

    def start(self, fileobject, request_extractors=None, request_all=None):
        """
        Starts extraction data from the given file using specified extractors.

        Which extractors that are included is controlled by either passing a
        list of extractor classes to 'request_extractors' or setting
        'request_all' to True.
        If 'exclude_slow' is true, "slow" extractors that are not explicitly
        requested are excluded.
        Note that extractors that are unable to handle the given 'fileobject'
        are always excluded.

        Args:
            fileobject: The file object to extract data from.
            request_extractors: List of extractor classes that must be included.
            request_all: Whether all data extractors should be included.
        """
        log.debug(logs.center_pad_log_entry('Extractor Runner Started'))
        sanity.check_isinstance_fileobject(fileobject)

        _request_all = bool(request_all)

        # Get only extractors suitable for the given file.
        extractors_for_file = filter_able_to_handle(
            self._available_extractors, fileobject
        )
        log.debug('Removed extractors that can not handle the current file. '
                  'Remaining: %d', len(extractors_for_file))

        selected = set()
        if _request_all:
            # Add all available extractors.
            log.debug('Requested all available extractors')
            selected = extractors_for_file
        elif request_extractors:
            # Add requested extractors.
            requested_klasses = set(request_extractors)
            selected = self._select_from_available(extractors_for_file, requested_klasses)

        if logs.DEBUG:
            log.debug('Selected %d of %d available extractors',
                      len(selected), len(self._available_extractors))
            for k in selected:
                # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
                log.debug('Selected extractor:  %s', k.name())

        if selected:
            # Run all prepared extractors.
            with logs.log_runtime(log, 'Extraction'):
                self._run_extractors(fileobject, selected)

    def _select_from_available(self, available, requested_klasses):
        selected = {
            k for k in requested_klasses if k in available
        }

        if logs.DEBUG:
            def _format_string(_extractors):
                # TODO: [TD0151] Fix inconsistent use of classes vs. class instances.
                return ', '.join(k.name() for k in _extractors)

            if not requested_klasses.issubset(available):
                na = requested_klasses.difference(available)
                log.debug('Requested %d unavailable extractors: %s',
                          len(na), _format_string(na))

            log.debug('Selected %d requested extractors: %s',
                      len(selected), _format_string(selected))

        if self.exclude_slow:
            selected = filter_not_slow(selected, requested_klasses)
            if logs.DEBUG:
                log.debug('Removed slow extractors. Remaining: %d',
                          len(selected))
        return selected

    def _run_extractors(self, fileobject, extractors_to_run):
        for klass in extractors_to_run:
            extractor_instance = self._get_pooled_extractor_instance(klass)
            if not extractor_instance:
                log.critical('Unable to get an instance of "%s"', klass)
                continue

            try:
                metainfo = extractor_instance.metainfo()
            except (ExtractorError, PersistenceError, NotImplementedError) as e:
                log.error('Unable to get meta info! Aborting extractor "%s": %s',
                          extractor_instance, e)
                # TODO: Remove extractor from instance pool?
                continue

            try:
                with logs.log_runtime(log, str(extractor_instance)):
                    extracted_data = extractor_instance.extract(fileobject)
            except (ExtractorError, NotImplementedError) as e:
                # TODO: Remove extractor from instance pool?
                log.error('Unable to extract data! Aborting extractor "%s": %s',
                          extractor_instance, e)
                continue

            if not extracted_data:
                log.warning('Got no data from extractor "%s"', extractor_instance)
                continue

            # TODO: [TD0034] Filter out known bad data.
            # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
            wrapped_results = wrap_provider_results(extracted_data, metainfo, klass)
            self.store_results(fileobject, klass.meowuri_prefix(), wrapped_results)

    def _get_pooled_extractor_instance(self, klass):
        instance = self._instance_pool.get(klass)
        if not instance:
            instance = klass()
            self._instance_pool[klass] = instance
        return instance

    def store_results(self, fileobject, meowuri_prefix, data):
        """
        Constructs a full MeowURI and calls the callback with the results.

        Args:
            fileobject: Instance of 'FileObject' that produced the data to add.
            meowuri_prefix: MeowURI parts excluding the "leaf", as a Unicode str.
            data: Data to add, as a dict containing the data and meta-information.
        """
        assert isinstance(data, dict)
        for _uri_leaf, _data in data.items():
            uri = force_meowuri(meowuri_prefix, _uri_leaf)
            if not uri:
                log.error('Unable to construct full extractor result MeowURI '
                          'from prefix "%s" and leaf "%s"', meowuri_prefix, _uri_leaf)
                continue

            self._add_results_callback(fileobject, uri, _data)

    def shutdown_pooled_extractors(self, *_, **__):
        # TODO: [TD0202] Handle signals and graceful shutdown properly!
        log.debug('Shutting down %s', self.__class__.__name__)
        for instance in self._instance_pool.values():
            if not hasattr(instance, 'shutdown'):
                continue

            assert callable(getattr(instance, 'shutdown')), (
                'Expected callable extractor attribute "shutdown"'
            )
            log.debug('Shutting down extractor "%s" ..', instance)
            instance.shutdown()
