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

from core import (
    disk,
    exceptions,
    util
)
from core.model import MeowURI
from core.util import textutils


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
        # self.log.setLevel(logging.DEBUG)

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

        if data is None:
            log.warning('Attempted to add None data with meowURI'
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
        log.debug('Repository storing: [{:8.8}]->[{!s}] :: "{!r}"'.format(
            fileobject.hash_partial, meowuri, data
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

            _abspath = util.enc.displayable_path(fileobject.abspath)
            out.append('FileObject absolute path: "{!s}"'.format(_abspath))

            out.append('')
            out.extend(self._human_readable_contents(data))
            out.append('\n')

        return '\n'.join(out)

    def _human_readable_contents(self, data):
        def _fmt_list_entry(width, _value, _key=None):
            if _key is None:
                return '{: <{}}  * {!s}'.format('', width, _value)
            else:
                return '{: <{}}: * {!s}'.format(str(_key), width, _value)

        def _fmt_text_line(width, _value, _key=None):
            if _key is None:
                return '{: <{}}  > {!s}'.format('', width, _value)
            else:
                return '{: <{}}: > {!s}'.format(str(_key), width, _value)

        def _fmt_entry(_key, width, _value):
            return '{: <{}}: {!s}'.format(str(_key), width, _value)

        # TODO: [TD0066] Handle all encoding properly.
        temp = {}
        _max_len_meowuri = 20
        for meowuri, data in sorted(data.items()):
            _max_len_meowuri = max(_max_len_meowuri, len(str(meowuri)))

            if isinstance(data, list):
                log.debug('TODO: Improve robustness of handling this case')
                temp_list = []
                for d in data:
                    v = d.get('value')
                    try:
                        if isinstance(v, bytes):
                            temp_list.append(util.enc.displayable_path(v))
                        elif meowuri.matchglobs(['generic.contents.text',
                                                 'extractor.text.*']):
                            # Often *a lot* of text, trim to arbitrary size..
                            _truncated = textutils.truncate_text(v)
                            temp_list.append(_truncated)
                        else:
                            temp_list.append(str(v))
                    except AttributeError:
                        pass

                temp[meowuri] = temp_list

            else:
                v = data.get('value')
                if isinstance(v, bytes):
                    temp[meowuri] = util.enc.displayable_path(v)

                elif meowuri.matchglobs(['generic.contents.text',
                                         'extractor.text.*']):
                    # Often *a lot* of text, trim to arbitrary size..
                    temp[meowuri] = textutils.truncate_text(v)
                else:
                    temp[meowuri] = str(v)

        out = []
        for meowuri, data in temp.items():
            if not data:
                continue

            if isinstance(data, list):
                out.append(
                    _fmt_list_entry(_max_len_meowuri, data[0], meowuri)
                )
                for v in data[1:]:
                    out.append(_fmt_list_entry(_max_len_meowuri, v))
            else:
                # datavalue = data.get('value')
                datavalue = data
                if meowuri.matchglobs(['generic.contents.text',
                                       'extractor.text.*']):
                    _text = textutils.extract_lines(
                        datavalue, firstline=0, lastline=1
                    )
                    _text = _text.rstrip('\n')
                    out.append(
                        _fmt_text_line(_max_len_meowuri, _text, meowuri)
                    )
                    _lines = textutils.extract_lines(
                        datavalue, firstline=1,
                        lastline=len(datavalue.splitlines())
                    )
                    for _line in _lines.splitlines():
                        out.append(_fmt_text_line(_max_len_meowuri, _line))
                else:
                    out.append(_fmt_entry(meowuri, _max_len_meowuri, datavalue))

        return out

    def __len__(self):
        return util.count_dict_recursive(self.data)

    def __str__(self):
        return self.human_readable_contents()

    def to_filedump(self, file_path):
        # NOTE: Debugging/testing experiment --- TO BE REMOVED!
        if not isinstance(file_path, (str, bytes)):
            return
        if not file_path.strip():
            return

        if disk.exists(file_path):
            return

        try:
            import cPickle as pickle
        except ImportError:
            import pickle

        with open(util.enc.syspath(file_path), 'wb') as fh:
            pickle.dump(self.data, fh, pickle.HIGHEST_PROTOCOL)

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
