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

import util
from core import exceptions
from core.ui.cli import ColumnFormatter
from core.model import MeowURI
from util import encoding as enc
from util import textutils
from util.text import truncate_text


log = logging.getLogger(__name__)


class Repository(object):
    """
    The repository class is the central internal storage used by all parts
    of the program. The repository stores data per file, cataloguing the
    individual data elements using "MeowURIs".

    The internal storage structure is laid out like this:

            STORAGE = {
                'fileobject_A': {
                    'meowuri_a': 1
                    'meowuri_b': 'foo'
                    'meowuri_c': (...)
                }
                'fileobject_B': {
                    'meowuri_a': ['bar']
                    'meowuri_b': [2, 1]
                }
            }

    The first level of the nested structure uses instances of 'fileobject' as
    keys into containing structures that use "MeowURIs" (Unicode strings) keys.
    """
    def __init__(self):
        self.data = {}
        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )

    def shutdown(self):
        # TODO: Any shutdown tasks goes here ..
        pass

    def store(self, fileobject, meowuri, data):
        """
        Primary global publicly available interface for data storage.

        Adds data related to a given 'fileobject', at a storage location
        defined by the given 'meowuri'.
        """
        if not meowuri or not isinstance(meowuri, MeowURI):
            raise exceptions.InvalidMeowURIError

        if not data:
            log.warning('Attempted to add empty data with meowURI'
                        ' "{!s}"'.format(meowuri))
            return

        if isinstance(data, list):
            data_sample = data[0]
        else:
            data_sample = data
        assert isinstance(data_sample, dict), (
            'Expected "data" to be of type dict. Got "{!s}"'.format(type(data))
        )

        self._store(fileobject, meowuri, data)
        self._store_generic(fileobject, data)

    def _store_generic(self, fileobject, data):
        def __store(data):
            if data.get('generic_field') is not None:
                try:
                    _gen_uri = data['generic_field'].uri()
                except AttributeError:
                    self.log.critical('TODO: Fix missing "field.uri()" for some'
                                      ' GenericField classes!')
                else:
                    self._store(fileobject, _gen_uri, data)

        if isinstance(data, list):
            for d in data:
                __store(d)
        else:
            __store(data)

    def _store(self, fileobject, meowuri, data):
        if meowuri.matchglobs(['generic.contents.text', 'extractor.text.*']):
            _debugmsg_data = dict(data)
            _truncated_value = truncate_text(_debugmsg_data['value'])
            _debugmsg_data['value'] = _truncated_value
        else:
            _debugmsg_data = data

        log.debug('{} storing: [{:8.8}]->[{!s}] :: "{!s}"'.format(
            self.__class__.__name__, fileobject.hash_partial, meowuri,
            _debugmsg_data.get('value')
        ))
        try:
            any_existing = self.__get_data(fileobject, meowuri)
        except KeyError:
            pass
        else:
            if any_existing is not None:
                if not isinstance(any_existing, list):
                    any_existing = [any_existing]
                if not isinstance(data, list):
                    data = [data]

                data = any_existing + data

        self.__store_data(fileobject, meowuri, data)

    def query_mapped(self, fileobject, field):
        out = []

        _data = self.data.get(fileobject)
        for meowuri, data in _data.items():
            if isinstance(data, list):
                for d in data:
                    if maps_field(d, field):
                        out.append(d)
            else:
                if maps_field(data, field):
                    out.append(data)

        return out

    def query(self, fileobject, meowuri):
        if not meowuri:
            raise exceptions.InvalidMeowURIError(
                'Unable to resolve empty meowURI'
            )

        log.debug('Got request [{:8.8}]->[{!s}]'.format(
            fileobject.hash_partial, meowuri))

        try:
            data = self.__get_data(fileobject, meowuri)
        except KeyError as e:
            log.debug('Repository request raised KeyError: {!s}'.format(e))
            return None
        else:
            return data

    def __get_data(self, file, meowuri):
        return util.nested_dict_get(self.data, [file, meowuri])

    def __store_data(self, file, meowuri, data):
        util.nested_dict_set(self.data, [file, meowuri], data)

    def human_readable_contents(self):
        out = []
        for fileobject, data in self.data.items():
            out.append('FileObject basename: "{!s}"'.format(fileobject))

            _abspath = enc.displayable_path(fileobject.abspath)
            out.append('FileObject absolute path: "{!s}"'.format(_abspath))

            out.append('')
            # out.extend(self._human_readable_contents(data))
            out.append(self._machine_readable_contents(data))
            out.append('\n')

        return '\n'.join(out)

    @staticmethod
    def _machine_readable_contents(data):
        # First pass -- handle encoding and truncating extracted text.
        temp = {}
        for meowuri, data in sorted(data.items()):
            if isinstance(data, list):
                log.debug('TODO: Improve robustness of handling this case')
                temp_list = []
                for d in data:
                    v = d.get('value')
                    if isinstance(v, bytes):
                        temp_list.append(enc.displayable_path(v))
                    elif meowuri.matchglobs(['generic.contents.text',
                                             'extractor.text.*']):
                        # Often *a lot* of text, trim to arbitrary size..
                        _truncated = truncate_text(v)
                        temp_list.append(_truncated)
                    else:
                        temp_list.append(str(v))

                temp[meowuri] = temp_list

            else:
                v = data.get('value')
                if isinstance(v, bytes):
                    temp[meowuri] = enc.displayable_path(v)

                elif meowuri.matchglobs(['generic.contents.text',
                                         'extractor.text.*']):
                    # Often *a lot* of text, trim to arbitrary size..
                    temp[meowuri] = truncate_text(v)
                else:
                    temp[meowuri] = str(v)

        cf = ColumnFormatter()
        COLUMN_DELIMITER = '::'
        MAX_VALUE_WIDTH = 80
        def _add_row(str_meowuri, value):
            str_value = str(value)
            if len(str_value) > MAX_VALUE_WIDTH:
                str_value = str_value[:MAX_VALUE_WIDTH]
            cf.addrow(str_meowuri, COLUMN_DELIMITER, str_value)

        for meowuri, data in sorted(temp.items()):
            _meowuri_str = str(meowuri)
            if isinstance(data, list):
                for v in data:
                    _add_row(_meowuri_str, v)
                continue

            if meowuri.matchglobs(['generic.contents.text',
                                   'extractor.text.*']):
                _text = textutils.extract_lines(data, firstline=1, lastline=1)
                _text = _text.rstrip('\n')
                data = _text
            _add_row(_meowuri_str, data)

        return str(cf)

    def __len__(self):
        # TODO:  FIX THIS! Unverified after removing the 'ExtractedData' class.
        # return util.count_dict_recursive(self.data)
        return sum(len(v) for k, v in self.data.items())

    def __str__(self):
        return self.human_readable_contents()

    # def __repr__(self):
    #     # TODO: Implement this properly.
    #     pass


def _create_repository():
    repository = Repository()
    return repository


class RepositoryPool(object):
    DEFAULT_SESSION_ID = 'SINGLETON_SESSION'

    def __init__(self):
        self._repositories = {}

    def get(self, id_=None):
        if id_ is None:
            id_ = self.DEFAULT_SESSION_ID

        if id_ not in self._repositories:
            raise KeyError('{} does not contain ID "{!s}'.format(self, id_))

        return self._repositories.get(id_)

    def add(self, repository=None, id_=None):
        if id_ is None:
            id_ = self.DEFAULT_SESSION_ID

        if id_ in self._repositories:
            raise KeyError('{} already contains ID "{!s}'.format(self, id_))

        if repository is None:
            _repo = _create_repository()
        else:
            _repo = repository

        self._repositories[id_] = _repo

    def __len__(self):
        return len(self._repositories)


def initialize(id_=None):
    # Keep one global 'SessionRepository' per 'Autonameow' instance.
    global Pool
    Pool = RepositoryPool()
    Pool.add(id_=id_)

    global SessionRepository
    SessionRepository = Pool.get(id_=id_)


def shutdown(id_=None):
    global Pool
    if not Pool:
        return

    try:
        r = Pool.get(id_=id_)
    except KeyError as e:
        log.error(
            'Unable to retrieve repository with ID "{!s}"; {!s}'.format(id_, e)
        )
    else:
        r.shutdown()


def maps_field(datadict, field):
    for mapping in datadict.get('field_map', {}):
        if field == mapping.field:
            return True
    return False


Pool = None
SessionRepository = None
