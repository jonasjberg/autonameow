# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
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

import analyzers
from core import logs
from core import master_provider
from core.config.configuration import Configuration
from core.datastore import repository
from core.exceptions import AutonameowException
from core.model import force_meowuri
from util import sanity


log = logging.getLogger(__name__)


"""
Performs high-level handling of an analysis.

A run queue is populated based on which analyzers are suited for the
current file.
"""


# TODO: [TD0040] Add assigning tags to GPS coordinates.


def _execute_run_queue(analyzer_queue):
    """
    Executes analyzers in the analyzer run queue.
    """
    for i, analyzer_instance in enumerate(analyzer_queue):
        log.debug('Executing queue item %d/%d: %s',
                  i + 1, len(analyzer_queue), analyzer_instance)

        log.debug('Running Analyzer "%s"', analyzer_instance)
        try:
            with logs.log_runtime(log, str(analyzer_instance)):
                results = analyzer_instance.run()
        except analyzers.AnalyzerError as e:

            log.error('Halted analyzer "%s": %s', analyzer_instance, e)
            continue

        # TODO: [TD0126] Clean up boundaries/interface to the 'analyzers' package.
        fileobject = analyzer_instance.fileobject
        for uri, wrapped_data in results.items():
            store_results(fileobject, uri, wrapped_data)

        log.debug('Finished running "%s"', analyzer_instance)


def request_global_data(fileobject, uri_string):
    # NOTE(jonas): String to MeowURI conversion boundary.
    sanity.check_internal_string(uri_string)

    uri = force_meowuri(uri_string)
    if not uri:
        log.error('Bad MeowURI in analyzer request: "%s"', uri_string)
        return None

    # Pass a "tie-breaker" to resolve cases where we only want one item?
    # TODO: [TD0175] Handle requesting exactly one or multiple alternatives.
    # TODO: [TD0185] Rework access to 'master_provider' functionality.
    response = master_provider.request(fileobject, uri)
    if response:
        if isinstance(response, list):
            # TODO: [cleanup] This method is currently only used once?
            # TODO: Currently only called by 'request_any_textual_content()'
            return [r.value for r in response]
        return response.value
    return None


def store_results(fileobject, meowuri_prefix, data):
    """
    Collects analyzer results to store in the session repository.

    Args:
        fileobject: Instance of 'FileObject' that produced the data to add.
        meowuri_prefix: MeowURI parts excluding the "leaf", as a Unicode str.
        data: The data to add as dicts (or lists of dicts..)
    """
    uri = force_meowuri(meowuri_prefix)
    if not uri:
        log.error('Unable to create MeowURI from analyzer prefix string "%s"',
                  meowuri_prefix)
        return

    # TODO: [TD0102] Fix inconsistencies in results passed back by analyzers.
    if isinstance(data, list):
        for d in data:
            assert isinstance(d, dict), (
                '[TD0102] Expected list elements passed to "store_results()"'
                ' to be type dict. Got: ({!s}) "{!s}"'.format(type(d), d)
            )
            repository.SessionRepository.store(fileobject, uri, d)
    else:
        assert isinstance(data, dict), (
            '[TD0102] Got non-dict data in "analysis.store_results()" :: '
            '({!s}) "{!s}"'.format(type(data), data)
        )
        repository.SessionRepository.store(fileobject, uri, data)


def _instantiate_analyzers(fileobject, klass_list, config):
    """
    Get a list of class instances from a given list of classes.

    Args:
        fileobject: The file to analyze.
        klass_list: The classes to instantiate as a list of type 'class'.

    Returns:
        One instance of each of the given classes as a list of objects.
    """
    return [
        analyzer(
            fileobject, config,
            request_data_callback=request_global_data
        ) for analyzer in klass_list
    ]


def filter_able_to_handle(analyzer_klasses, fileobject):
    return {a for a in analyzer_klasses if a.can_handle(fileobject)}


def _start(fileobject, config, analyzers_to_run=None):
    """
    Starts analyzing 'fileobject' using all analyzers deemed "suitable".
    """
    log.debug(logs.center_pad_log_entry('Analysis Preparation Started'))

    # TODO: [TD0126] Remove assertions once "boundaries" are cleaned up.
    sanity.check_isinstance_fileobject(fileobject)
    sanity.check_isinstance(config, Configuration)

    all_available_analyzers = analyzers.registry.all_providers

    if analyzers_to_run:
        assert isinstance(analyzers_to_run, (list, set))
        chosen_analyzers = [a for a in all_available_analyzers
                            if a in analyzers_to_run]
    else:
        chosen_analyzers = all_available_analyzers

    klasses = filter_able_to_handle(chosen_analyzers, fileobject)
    if not klasses:
        log.debug('None of the analyzers can handle the current file')
        return

    analyzer_queue = list()
    for a in _instantiate_analyzers(fileobject, klasses, config):
        if a not in analyzer_queue:
            analyzer_queue.insert(0, a)
        else:
            log.error('Attempted to enqueue queued analyzer: "%s"', a)

    if logs.DEBUG:
        def _prettyprint(list_):
            out = list()
            for pos, item in enumerate(list_):
                out.append('{:02d}: {!s}'.format(pos, item))
            return ', '.join(out)

        log.debug('Enqueued analyzers: %s', _prettyprint(analyzer_queue))

    # Sort queue by analyzer priority.
    sorted(analyzer_queue, key=lambda x: x.RUN_QUEUE_PRIORITY or 0.1)

    # Run all analyzers in the queue.
    with logs.log_runtime(log, 'Analysis'):
        _execute_run_queue(analyzer_queue)


def run_analysis(fileobject, active_config, analyzers_to_run=None):
    """
    Sets up and executes "analysis" of the given file.

    Args:
        fileobject: The file object to analyze.
        active_config: An instance of the 'Configuration' class.
        analyzers_to_run: Optional list of analyzers to run. All if omitted.

    Raises:
        AutonameowException: An unrecoverable error occurred during analysis.
    """
    try:
        _start(fileobject, active_config, analyzers_to_run)
    except AutonameowException as e:
        # TODO: [TD0164] Tidy up throwing/catching of exceptions.
        log.critical('Analysis FAILED: %s', e)
        raise
