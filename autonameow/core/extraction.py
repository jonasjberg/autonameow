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
from core import repository
from extractors import ExtractorError


log = logging.getLogger(__name__)


def collect_results(fileobject, meowuri_prefix, data):
    """
    Collects extractor data, passes it the the session repository.

    Args:
        fileobject: Instance of 'FileObject' that produced the data to add.
        meowuri_prefix: MeowURI parts excluding the "leaf", as a Unicode str.
        data: The data to add, as any type or container.
    """
    # TODO: [TD0106] Fix inconsistencies in results passed back by extractors.
    if not isinstance(data, dict):
        log.debug('[TD0106] Got non-dict data "extraction.collect_results()"')
        log.debug('[TD0106] Data type: {!s}'.format(type(data)))
        log.debug('[TD0106] Data contents: {!s}'.format(data))

    if isinstance(data, dict):
        for _uri_leaf, _data in data.items():
            # TODO: [TD0105] Integrate the `MeowURI` class.
            _uri = '{}.{!s}'.format(meowuri_prefix, _uri_leaf)
            repository.SessionRepository.store(fileobject, _uri, _data)
    else:
        repository.SessionRepository.store(fileobject, meowuri_prefix, data)


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


def start(fileobject,
          require_extractors=None,
          require_all_extractors=False):
    """
    Starts extracting data for a given 'fileobject'.
    """
    log.debug('Started data extraction')

    if require_extractors:
        required_extractors = require_extractors
    else:
        required_extractors = []
    log.debug('Required extractors: {!s}'.format(required_extractors))

    klasses = extractors.suitable_extractors_for(fileobject)
    log.debug('Extractors able to handle the file: {}'.format(len(klasses)))

    if not require_all_extractors:
        # Exclude "slow" extractors if they are not explicitly required.
        klasses = keep_slow_extractors_if_required(klasses,
                                                   required_extractors)

    # TODO: Use sets for required/actual klasses to easily display differences.
    # Which required extractors were not "suitable" for the file and therefore
    # not included?

    log.debug('Running {} extractors'.format(len(klasses)))
    for klass in klasses:
        _extractor_instance = klass()
        if not _extractor_instance:
            log.critical('Error instantiating extractor "{!s}"!'.format(klass))
            continue

        try:
            _results = _extractor_instance(fileobject)
        except ExtractorError as e:
            log.error('Halted extractor "{!s}": {!s}'.format(
                _extractor_instance, e
            ))
            continue
        else:
            _meowuri_prefix = klass.meowuri_prefix()
            collect_results(fileobject, _meowuri_prefix, _results)
