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
from core.model import MeowURI
from core.model.genericfields import get_field_class
from extractors import ExtractorError
from util import sanity


log = logging.getLogger(__name__)


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


def construct_full_meowuri(meowuri_prefix, meowuri_leaf):
    try:
        return MeowURI(meowuri_prefix, meowuri_leaf)
    except InvalidMeowURIError as e:
        log.error(e)
        return None


def filter_able_to_handle(extractor_klasses, fileobject):
    return {k for k in extractor_klasses if k.can_handle(fileobject)}


def filter_not_slow(extractor_klasses, required):
    return {k for k in extractor_klasses if not k.is_slow or k in required}


class ExtractorRunner(object):
    def __init__(self, add_results_callback=None):
        """
        Instantiates a new extractor runner. Results are passed to the callback.

        The callback should accept three arguments;

            fileobject (FileObject), meowuri (MeowURI), data (dict)

        It will be called for each extracted "item" returned by each of the
        selected extractors. Results are discarded if left unspecified.

        If 'exclude_slow' is true, "slow" extractors that are not explicitly
        requested are excluded.

        Args:
            add_results_callback: Callable that accepts three arguments.
        """
        if add_results_callback:
            assert callable(add_results_callback)
            self._add_results_callback = add_results_callback
        else:
            self._add_results_callback = lambda *_: None

        self._available_extractors = set(extractors.ProviderClasses)
        if __debug__:
            for k in self._available_extractors:
                log.debug('Available: {!s}'.format(str(k.__name__)))

        self.exclude_slow = True

    def start(self, fileobject, request_extractors=None, request_all=None):
        log.debug(' Extractor Runner Started '.center(120, '='))
        sanity.check_isinstance_fileobject(fileobject)

        _request_all = bool(request_all)

        # Get only extractors suitable for the given file.
        available = filter_able_to_handle(self._available_extractors,
                                          fileobject)
        log.debug('Removed extractors that can not handle the current file. '
                  'Remaining: {}'.format(len(available)))

        selected = set()
        if _request_all:
            # Add all available extractors.
            log.debug('Requested all available extractors')
            selected = available
        elif request_extractors:
            # Add requested extractors.
            requested_klasses = set(request_extractors)
            selected = self._select_from_available(available, requested_klasses)

        log.debug('Selected {} of {} available extractors'.format(
            len(selected), len(self._available_extractors)))

        if __debug__:
            log.debug('Prepared {} extractors that can handle "{!s}"'.format(
                len(selected), fileobject
            ))
            for k in selected:
                log.debug('Prepared:  {!s}'.format(str(k.__name__)))

        if selected:
            # Run all prepared extractors.
            with logs.log_runtime(log, 'Extraction'):
                self._run_extractors(fileobject, selected)

    def _select_from_available(self, available, requested_klasses):
        selected = {
            k for k in requested_klasses if k in available
        }
        if not requested_klasses.issubset(available):
            na = requested_klasses.difference(available)
            log.warning('Requested {} unavailable extractors'.format(len(na)))
            for k in na:
                log.warning('Unavailable:  {!s}'.format(str(k.__name__)))

        if __debug__:
            log.debug('Selected {} requested extractors'.format(len(selected)))
            for k in selected:
                log.debug('Selected:  {!s}'.format(str(k.__name__)))

        if self.exclude_slow:
            selected = filter_not_slow(selected, requested_klasses)
            log.debug('Removed slow extractors. Remaining: {}'.format(
                len(selected)
            ))

        return selected

    def _run_extractors(self, fileobject, extractors_to_run):
        for klass in extractors_to_run:
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
            self.store_results(fileobject, _meowuri_prefix, _results)

    def store_results(self, fileobject, meowuri_prefix, data):
        """
        Constructs a full MeowURI and calls the callback with the results.

        Args:
            fileobject: Instance of 'FileObject' that produced the data to add.
            meowuri_prefix: MeowURI parts excluding the "leaf", as a Unicode str.
            data: Data to add, as a dict containing the data and meta-information.
        """
        sanity.check_isinstance(data, dict)
        for _uri_leaf, _data in data.items():
            _meowuri = construct_full_meowuri(meowuri_prefix, _uri_leaf)
            if not _meowuri:
                log.debug('Unable to construct full MeowURI from prefix "{!s}" '
                          'and leaf "{!s}"'.format(meowuri_prefix, _uri_leaf))
                continue

            self._add_results_callback(fileobject, _meowuri, _data)


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
    runner = ExtractorRunner(
        add_results_callback=repository.SessionRepository.store
    )
    try:
        runner.start(fileobject,
                     request_extractors=require_extractors,
                     request_all=run_all_extractors)
    except AutonameowException as e:
        log.critical('Extraction FAILED: {!s}'.format(e))
        raise
