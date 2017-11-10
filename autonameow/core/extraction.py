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
from core.exceptions import InvalidMeowURIError
from core.fileobject import FileObject
from core.model import (
    ExtractedData,
    MeowURI
)
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
            try:
                _meowuri = MeowURI(meowuri_prefix, _uri_leaf)
            except InvalidMeowURIError as e:
                log.critical(
                    'Got invalid MeowURI from extractor -- !{!s}"'.format(e)
                )
                continue
            repository.SessionRepository.store(fileobject, _meowuri, _data)
    else:
        try:
            _meowuri = MeowURI(meowuri_prefix)
        except InvalidMeowURIError as e:
            log.critical(
                'Got invalid MeowURI from extractor -- !{!s}"'.format(e)
            )
            return
        repository.SessionRepository.store(fileobject, _meowuri, data)


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
        if not klass.is_slow:
            out.append(klass)
        elif klass.is_slow:
            if klass in required_extractors:
                log.debug('Extractor "{!s}" is required ..'.format(klass))
                out.append(klass)
                log.debug('Included slow extractor "{!s}"'.format(klass))
            else:
                log.debug('Excluded slow extractor "{!s}"'.format(klass))

    return out


def start(fileobject,
          require_extractors=None,
          require_all_extractors=False):
    """
    Starts extracting data for a given 'fileobject'.
    """
    log.debug(' Extraction Started '.center(80, '='))

    assert isinstance(fileobject, FileObject), (
        'Expected type "FileObject". Got {!s}')

    if require_extractors:
        _required_extractors = require_extractors
    else:
        _required_extractors = []
    log.debug('Required extractors: {!s}'.format(_required_extractors))

    klasses = extractors.suitable_extractors_for(fileobject)
    log.debug('Extractors able to handle the file: {}'.format(len(klasses)))

    if not require_all_extractors:
        # Exclude "slow" extractors if they are not explicitly required.
        klasses = keep_slow_extractors_if_required(klasses,
                                                   _required_extractors)

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
            _metainfo = _extractor_instance.metainfo()
        except (ExtractorError, NotImplementedError) as e:
            log.error('Failed to get meta info! Halted extractor "{!s}":'
                      ' {!s}'.format(_extractor_instance, e))
            continue

        try:
            _extracted_data = _extractor_instance.extract(fileobject)
        except (ExtractorError, NotImplementedError) as e:
            log.error('Failed to extract data! Halted extractor "{!s}":'
                      ' {!s}'.format(_extractor_instance, e))
            continue

        _results = _to_extracteddata(_extracted_data, _metainfo,
                                     _extractor_instance)
        _meowuri_prefix = klass.meowuri_prefix()
        collect_results(fileobject, _meowuri_prefix, _results)

    log.debug(' Extraction Completed '.center(80, '='))


def _to_extracteddata(extracteddata, metainfo, source_klass):
    # TODO: [TD0119] Separate adding contextual information from coercion.
    out = {}
    for field, value in extracteddata.items():
        _field_info = metainfo.get(field)
        if not _field_info:
            continue

        try:
            coercer = _field_info.get('typewrap')
            mapped_fields = _field_info.get('mapped_fields', [])
            generic_fields = _field_info.get('generic_field')
            multivalued = _field_info.get('multiple')
        except AttributeError as e:
            log.critical(
                'TODO: Fix hack "_to_extracteddata()"! :: {!s}'.format(e)
            )
        else:
            out[field] = ExtractedData(
                coercer=coercer,
                mapped_fields=mapped_fields,
                generic_field=generic_fields,
                multivalued=multivalued,
                source=source_klass
            )(value)
    return out
