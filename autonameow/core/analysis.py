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

import logging

import analyzers
from core import (
    exceptions,
    logs,
    repository
)
from core.config.configuration import Configuration
from core.exceptions import InvalidMeowURIError
from core.fileobject import FileObject
from core.model import MeowURI


log = logging.getLogger(__name__)


"""
Performs high-level handling of an analysis.

A run queue is populated based on which analyzers are suited for the
current file.
"""


def _execute_run_queue(analyzer_queue):
    """
    Executes analyzers in the analyzer run queue.
    """
    for i, a in enumerate(analyzer_queue):
        log.debug('Executing queue item {}/{}: '
                  '{!s}'.format(i + 1, len(analyzer_queue), a))

        log.debug('Running Analyzer "{!s}"'.format(a))
        try:
            results = a.run()
        except analyzers.AnalyzerError as e:

            log.error('Halted analyzer "{!s}": {!s}'.format(a, e))
            continue

        fileobject = a.fileobject
        for _uri, _data in results.items():
            collect_results(fileobject, _uri, _data)

        log.debug('Finished running "{!s}"'.format(a))


def request_global_data(fileobject, meowuri):
    response = repository.SessionRepository.query(fileobject, meowuri)
    return response


def collect_results(fileobject, meowuri_prefix, data):
    """
    Collects analyzer results to store in the session repository.

    If argument "data" is a dictionary, it is "flattened" here.
    Example:

      Incoming arguments:
        MeowURI: 'extractor.metadata.exiftool'     DATA: {'a': 'b', 'c': 'd'}

      Would be "flattened" to:
        MeowURI: 'extractor.metadata.exiftool.a'   DATA: 'b'
        MeowURI: 'extractor.metadata.exiftool.c'   DATA: 'd'

    Args:
        fileobject: Instance of 'FileObject' that produced the data to add.
        meowuri_prefix: MeowURI parts excluding the "leaf", as a Unicode str.
        data: The data to add, as any type or container.
    """
    # TODO: [TD0102] Fix inconsistencies in results passed back by analyzers.
    if isinstance(data, list):
        for d in data:
            assert isinstance(d, dict), (
                '[TD0102] Expected list elements passed to "collect_results()"'
                ' to be type dict. Got: ({!s}) "{!s}"'.format(type(d), d)
            )
            try:
                _meowuri = MeowURI(meowuri_prefix)
            except InvalidMeowURIError as e:
                log.critical(
                    'Got invalid MeowURI from analyzer -- !{!s}"'.format(e)
                )
                return
            repository.SessionRepository.store(fileobject, _meowuri, d)
    else:
        assert isinstance(data, dict), (
            '[TD0102] Got non-dict data in "analysis.collect_results()" :: '
            '({!s}) "{!s}"'.format(type(data), data)
        )

        try:
            _meowuri = MeowURI(meowuri_prefix)
        except InvalidMeowURIError as e:
            log.critical(
                'Got invalid MeowURI from analyzer -- !{!s}"'.format(e)
            )
            return
        repository.SessionRepository.store(fileobject, _meowuri, data)


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


def suitable_analyzers_for(fileobject):
    """
    Returns analyzer classes that can handle the given file object.

    Args:
        fileobject: File to get analyzers for as an instance of 'FileObject'.

    Returns:
        A list of analyzer classes that can analyze the given file.
    """
    return [a for a in analyzers.AnalyzerClasses if a.can_handle(fileobject)]


def start(fileobject, config):
    """
    Starts analyzing 'fileobject' using all analyzers deemed "suitable".
    """
    log.debug(' Analysis Preparation Started '.center(120, '='))

    # TODO: [TD0126] Remove assertions once "boundaries" are cleaned up.
    assert isinstance(fileobject, FileObject), (
           'Expected type "FileObject". Got {!s}')
    assert isinstance(config, Configuration), (
           'Expected type "Configuration". Got {!s}'.format(type(config)))

    klasses = suitable_analyzers_for(fileobject)
    if not klasses:
        raise exceptions.AutonameowException(
            'None of the analyzers applies (!)'
        )

    analyzer_queue = []
    for a in _instantiate_analyzers(fileobject, klasses, config):
        if a not in analyzer_queue:
            analyzer_queue.insert(0, a)
        else:
            log.error('Attempted to enqueue queued analyzer: "{!s}"'.format(a))

    def _prettyprint(list_):
        out = []
        for pos, item in enumerate(list_):
            out.append('{:02d}: {!s}'.format(pos, item))
        return ', '.join(out)
    log.debug('Enqueued analyzers: {}'.format(_prettyprint(analyzer_queue)))

    # Sort queue by analyzer priority.
    sorted(analyzer_queue, key=lambda x: x.RUN_QUEUE_PRIORITY or 0.1)

    # Run all analyzers in the queue.
    with logs.log_runtime(log, 'Analysis'):
        _execute_run_queue(analyzer_queue)
