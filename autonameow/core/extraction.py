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
from core.model import MeowURI
from extractors import ExtractorError


log = logging.getLogger(__name__)


def collect_results(fileobject, meowuri_prefix, data):
    """
    Collects extractor data, passes it the the session repository.

    Args:
        fileobject: Instance of 'FileObject' that produced the data to add.
        meowuri_prefix: MeowURI parts excluding the "leaf", as a Unicode str.
        data: Data to add, as a dict containing the data and meta-information.
    """
    assert isinstance(data, dict), (
        'Expected data of type "dict" in "extraction.collect_results()" '
        ':: ({!s}) {!s}'.format(type(data), data)
    )

    for _uri_leaf, _data in data.items():
        try:
            _meowuri = MeowURI(meowuri_prefix, _uri_leaf)
        except InvalidMeowURIError as e:
            log.critical(
                'Got invalid MeowURI from extractor -- !{!s}"'.format(e)
            )
            continue
        repository.SessionRepository.store(fileobject, _meowuri, _data)


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


def suitable_extractors_for(fileobject):
    """
    Returns extractor classes that can handle the given file object.

    Args:
        fileobject: File to get extractors for as an instance of 'FileObject'.

    Returns:
        A list of extractor classes that can extract data from the given file.
    """
    return [e for e in extractors.ExtractorClasses if e.can_handle(fileobject)]


def start(fileobject,
          require_extractors=None,
          require_all_extractors=False):
    """
    Starts extracting data for a given 'fileobject'.
    """
    log.debug(' Extraction Started '.center(80, '='))

    assert isinstance(fileobject, FileObject), (
        'Expected type "FileObject". Got {!s}'.format(type(fileobject)))

    if require_extractors:
        assert isinstance(require_extractors, list), (
            'Expected "require_extractors" to be a list. Got {!s}'.format(
                type(require_extractors))
        )
        _required_extractors = list(require_extractors)
    else:
        _required_extractors = []
    log.debug('Required extractors: {!s}'.format(_required_extractors))

    klasses = suitable_extractors_for(fileobject)
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

        if not _extracted_data:
            continue

        _results = _wrap_extracted_data(_extracted_data, _metainfo,
                                        _extractor_instance)
        _meowuri_prefix = klass.meowuri_prefix()
        collect_results(fileobject, _meowuri_prefix, _results)

    log.debug(' Extraction Completed '.center(80, '='))


def _wrap_extracted_data(extracteddata, metainfo, source_klass):
    out = {}

    for field, value in extracteddata.items():
        field_metainfo = dict(metainfo.get(field, {}))
        if not field_metainfo:
            log.warning('Missing metainfo for field "{!s}"'.format(field))

        field_metainfo['value'] = value
        field_metainfo['source'] = source_klass
        out[field] = field_metainfo

    return out
