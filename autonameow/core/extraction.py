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

import extractors
from core import (
    util,
    repository
)
from extractors import ExtractorError


log = logging.getLogger(__name__)


def collect_results(file_object, label, data):
    """
    Collects extractor data, passes it the the session repository.

    Args:
        file_object: File that produced the data to add.
        label: Label that uniquely identifies the data.
        data: The data to add.
    """
    repository.SessionRepository.store(file_object, label, data)


def _execute_run_queue(extractor_queue, file_object):
    """
    Executes all enqueued extractors and collects the results.
    """
    for i, e in enumerate(extractor_queue):
        item_number = i + 1
        total_items = len(extractor_queue)

        log.debug('Executing queue item {}/{}: '
                  '{!s}'.format(item_number, total_items, e))

        try:
            collect_results(file_object, e.meowuri_root, e.execute())
        except ExtractorError as e:
            log.warning(
                'Execution of queue item {}/{} raised ExtractorError; '
                '{!s}'.format(item_number, total_items, e)
            )
            continue


def _instantiate_extractors(file_object, klass_list):
    """
    Get a list of class instances from a given list of classes.

    Args:
        file_object: The file to extract data from.
        klass_list: The classes to instantiate as a list of type 'class'.

    Returns:
        One instance of each of the given classes as a list of objects.
    """
    instances = []

    for klass in klass_list:
        if klass.__name__ == 'CommonFileSystemExtractor':
            # Special case where the source should be a 'FileObject'.
            _instance = klass(file_object)
        else:
            _instance = klass(file_object.abspath)

        instances.append(_instance)

    return instances


def keep_slow_extractors_if_required(extractor_klasses, required_extractors):
    """
    Filters out "slow" extractor classes if they are not explicitly required.

    If the extractor class variable 'is_slow' is True, the extractor is
    excluded if the same class is not specified in 'required_extractors'.

    Args:
        extractor_klasses: List of extractor classes to filter.
        required_extractors: List of required extractor classes.

    Returns:
        A list of extractor classes, including "slow" classes only if required.
    """
    out = []

    for klass in extractor_klasses:
        if klass.is_slow is True:
            if klass in required_extractors:
                out.append(klass)
                log.debug(
                    'Included required slow extractor "{!s}"'.format(klass)
                )
            else:
                log.debug(
                    'Excluded slow extractor "{!s}"'.format(klass)
                )
        else:
            out.append(klass)

    return out


def start(file_object,
          require_extractors=None,
          require_all_extractors=False):
    """
    Starts extracting data for a given 'file_object'.
    """
    log.debug('Started data extraction')

    if require_extractors:
        required_extractors = require_extractors
    else:
        required_extractors = []
    log.debug('Required extractors: {!s}'.format(required_extractors))

    classes = extractors.suitable_data_extractors_for(file_object)
    log.debug('Extractors able to handle the file: {}'.format(len(classes)))

    if not require_all_extractors:
        # Exclude "slow" extractors if they are not explicitly required.
        classes = keep_slow_extractors_if_required(classes,
                                                   required_extractors)

    log.debug('Will instantiate and enqueue {} extractors'.format(len(classes)))
    extractor_queue = util.GenericQueue()
    for instance in _instantiate_extractors(file_object, classes):
        extractor_queue.enqueue(instance)
    log.debug('Enqueued extractors: {!s}'.format(extractor_queue))

    # Execute all suitable extractors and collect results.
    _execute_run_queue(extractor_queue, file_object)
