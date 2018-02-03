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

import extractors
from core import (
    logs,
    repository
)
from core.exceptions import (
    AutonameowException,
    InvalidMeowURIError
)
from core.fileobject import FileObject
from core.model import MeowURI
from core.model.genericfields import get_field_class
from extractors import ExtractorError


log = logging.getLogger(__name__)


def store_results(fileobject, meowuri_prefix, data):
    """
    Collects extractor data, passes it the session repository.

    Args:
        fileobject: Instance of 'FileObject' that produced the data to add.
        meowuri_prefix: MeowURI parts excluding the "leaf", as a Unicode str.
        data: Data to add, as a dict containing the data and meta-information.
    """
    assert isinstance(data, dict), (
        'Expected data of type "dict" in "extraction.store_results()" '
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
    return [e for e in extractors.ProviderClasses if e.can_handle(fileobject)]


def _wrap_extracted_data(extracteddata, metainfo, source_klass):
    out = dict()

    for field, value in extracteddata.items():
        field_metainfo = dict(metainfo.get(field, {}))
        if not field_metainfo:
            log.warning('Missing metainfo for field "{!s}"'.format(field))

        field_metainfo['value'] = value
        # Do not store a reference to the class itself before actually needed..
        field_metainfo['source'] = str(source_klass)

        # TODO: [TD0146] Rework "generic fields". Possibly bundle in "records".
        # Map strings to generic field classes.
        _generic_field_string = field_metainfo.get('generic_field')
        if _generic_field_string:
            _generic_field_klass = get_field_class(_generic_field_string)
            if _generic_field_klass:
                field_metainfo['generic_field'] = _generic_field_klass
            else:
                field_metainfo.pop('generic_field')

        out[field] = field_metainfo

    return out


def filter_able_to_handle(extractor_klasses, fileobject):
    return {k for k in extractor_klasses if k.can_handle(fileobject)}


def filter_meowuri_prefix(extractor_klasses, match_string):
    assert isinstance(match_string, str)
    return {k for k in extractor_klasses
            if k.meowuri_prefix().startswith(match_string)}


def filter_not_slow(extractor_klasses):
    return {k for k in extractor_klasses if not k.is_slow}


class ExtractorRunner(object):
    def __init__(self, available_extractors=None, add_results_callback=None):
        if not available_extractors:
            self._available_extractors = set()
        else:
            self._available_extractors = set(available_extractors)

        if __debug__:
            for k in self._available_extractors:
                log.debug('Available: {!s}'.format(str(k.__name__)))

        # TODO: Separate repository from the runner ('extract.py' use-case)
        self.add_results_callback = add_results_callback
        self.exclude_slow = True

    def start(self, fileobject, request_extractors=None, request_all=None):
        log.debug(' Extractor Runner Started '.center(120, '='))
        assert isinstance(fileobject, FileObject), (
            'Expected type "FileObject". Got {!s}'.format(type(fileobject)))

        _request_all = bool(request_all)

        selected_klasses = set()
        if _request_all:
            # Add all available extractors.
            log.debug('Requested all available extractors')
            selected_klasses = self._available_extractors
        else:
            # Add requested extractors.
            if request_extractors:
                selected_klasses = set(request_extractors)

                if __debug__:
                    log.debug('Selected {} requested extractors'.format(
                        len(selected_klasses)
                    ))
                    for k in selected_klasses:
                        log.debug('Selected:  {!s}'.format(str(k.__name__)))

        log.debug('Selected {} of {} available extractors'.format(
            len(selected_klasses), len(self._available_extractors)))

        # Get only extractors suitable for the given file.
        selected_klasses = filter_able_to_handle(selected_klasses, fileobject)
        log.debug('Removed extractors that can not handle the current file. '
                  'Remaining: {}'.format(len(selected_klasses)))

        if self.exclude_slow:
            selected_klasses = filter_not_slow(selected_klasses)
            log.debug('Removed slow extractors. Remaining: {}'.format(
                len(selected_klasses)
            ))

        if __debug__:
            log.debug('Prepared {} extractors that can handle "{!s}"'.format(
                len(selected_klasses), fileobject
            ))
            for k in selected_klasses:
                log.debug('Prepared:  {!s}'.format(str(k.__name__)))

        if selected_klasses:
            # Run all prepared extractors.
            with logs.log_runtime(log, 'Extraction'):
                self._run_extractors(fileobject, selected_klasses)

    @staticmethod
    def _run_extractors(fileobject, all_klasses):
        for klass in all_klasses:
            _extractor_instance = klass()
            if not _extractor_instance:
                log.critical('Error instantiating "{!s}" (!!)'.format(klass))
                continue

            try:
                _metainfo = _extractor_instance.metainfo()
            except (ExtractorError, NotImplementedError) as e:
                log.error('Unable to get meta info! Aborting extractor "{!s}":'
                          ' {!s}'.format(_extractor_instance, e))
                continue

            try:
                _extracted_data = _extractor_instance.extract(fileobject)
            except (ExtractorError, NotImplementedError) as e:
                log.error('Unable to extract data! Aborting extractor "{!s}":'
                          ' {!s}'.format(_extractor_instance, e))
                continue

            if not _extracted_data:
                log.warning('Got empty data from extractor "{!s}"'.format(
                    _extractor_instance))
                continue

            # TODO: [TD0034] Filter out known bad data.
            # TODO: [TD0035] Use per-extractor, per-field, etc., blacklists?
            _results = _wrap_extracted_data(_extracted_data, _metainfo,
                                            _extractor_instance)
            _meowuri_prefix = klass.meowuri_prefix()
            store_results(fileobject, _meowuri_prefix, _results)


def run_extraction(fileobject, require_extractors, run_all_extractors=False):
    """
    Sets up and executes data extraction for the given file.

    Args:
        fileobject: The file object to extract data from.
        require_extractors: List of extractor classes that should be included.
        run_all_extractors: Whether all data extractors should be included.

    Raises:
        AutonameowException: An unrecoverable error occurred during extraction.
    """
    runner = ExtractorRunner(available_extractors=extractors.ProviderClasses)
    try:
        runner.start(fileobject,
                     request_extractors=require_extractors,
                     request_all=run_all_extractors)
    except AutonameowException as e:
        log.critical('Extraction FAILED: {!s}'.format(e))
        raise
