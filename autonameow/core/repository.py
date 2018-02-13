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

import util
from core import exceptions
from core.ui.cli import ColumnFormatter
from util import encoding as enc
from util import sanity
from util import textutils
from util.text import truncate_text


log = logging.getLogger(__name__)


class QueryResponseFailure(object):
    def __init__(self, fileobject=None, uri=None, msg=None):
        self.fileobject = fileobject
        self.uri = uri or 'unspecified MeowURI'
        self.msg = msg or ''

    def __str__(self):
        if self.fileobject:
            fileobject_str = self.fileobject.hash_partial
        else:
            fileobject_str = 'unknown FileObject'

        if self.msg:
            _msg = ' :: {!s}'.format(self.msg)
        else:
            _msg = ''

        return 'Failed query [{:8.8}]->[{!s}]{!s}'.format(
            fileobject_str, self.uri, _msg)

    def __bool__(self):
        return False


class DataBundle(object):
    def __init__(self, value, coercer, source, generic_field, mapped_fields,
                 multivalued):
        self.value = value
        self.coercer = coercer
        self.source = source
        self.generic_field = generic_field
        self.mapped_fields = mapped_fields
        self.multivalued = multivalued

    @classmethod
    def from_dict(cls, data):
        return DataBundle(
            value=data.get('value'),
            coercer=data.get('coercer'),
            source=data.get('source'),
            generic_field=data.get('generic_field'),
            mapped_fields=data.get('mapped_fields'),
            multivalued=data.get('multivalued')
        )

    def maps_field(self, field):
        # TODO: Duplicates functionality of function with the same name!
        # This might return a None, using a default dict value will not work.
        if not self.mapped_fields or not field:
            return False

        for mapping in self.mapped_fields:
            if field == mapping.field:
                return True
        return False

    def field_mapping_probability(self, field):
        if not self.maps_field(field):
            return 0.0

        for mapping in self.mapped_fields:
            if field == mapping.field:
                return float(mapping.probability)

        return 0.0


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
        self.data = dict()
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
        sanity.check_isinstance_meowuri(meowuri)

        if not data:
            log.warning('Attempted to add empty data with meowURI'
                        ' "{!s}"'.format(meowuri))
            return

        # if meowuri == 'extractor.filesystem.xplat.basename.full':
        #     assert 'extractor.filesystem.xplat.basename.full' not in self.data[fileobject]

        if isinstance(data, list):
            data_sample = data[0]
        else:
            data_sample = data
        sanity.check_isinstance(data_sample, dict)

        self._store(fileobject, meowuri, data)
        self._store_generic(fileobject, data)

    def _store_generic(self, fileobject, data):
        # TODO: [TD0146] Rework "generic fields". Possibly bundle in "records".
        def __store(_data):
            _generic_field = _data.get('generic_field')
            if _generic_field:
                assert not isinstance(_generic_field, str), str(_data)
                _gen_uri = _data['generic_field'].uri()
                self._store(fileobject, _gen_uri, _data)

        if isinstance(data, list):
            for d in data:
                __store(d)
        else:
            __store(data)

    def _store(self, fileobject, meowuri, data):
        if __debug__:
            if meowuri.matchglobs(['generic.contents.text', 'extractor.text.*']):
                _debugmsg_data = dict(data)
                _truncated_value = truncate_text(_debugmsg_data['value'])
                _debugmsg_data['value'] = _truncated_value
            else:
                _debugmsg_data = data

            log.debug('Storing [{:8.8}]->[{!s}] :: ({}) {!s}'.format(
                fileobject.hash_partial,
                meowuri,
                type(_debugmsg_data.get('value')),
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
        # TODO: [TD0165] Should also return 'DataBundle' for consistency.
        out = []

        _data = self.data.get(fileobject)
        for meowuri, data in _data.items():
            if isinstance(data, list):
                for d in data:
                    if maps_field(d, field):
                        # TODO: [TD0167] Why is this update here?
                        d.update(meowuri=meowuri)
                        out.append(d)
            else:
                if maps_field(data, field):
                    # TODO: [TD0167] Why is this update here?
                    data.update(meowuri=meowuri)
                    out.append(data)

        return out

    def query(self, fileobject, meowuri):
        if not meowuri:
            raise exceptions.InvalidMeowURIError(
                'Got query with "empty" or missing MeowURI'
            )

        if __debug__:
            log.debug('Got query [{:8.8}]->[{!s}]'.format(
                fileobject.hash_partial, meowuri
            ))
        try:
            data = self.__get_data(fileobject, meowuri)
        except KeyError as e:
            log.debug('Query raised KeyError: {!s}'.format(e))
            return QueryResponseFailure()
        else:
            # TODO: Store and query "generic" data separately?
            #       Alternatively store "generic" only as "references"?
            if isinstance(data, list):
                return [DataBundle.from_dict(d) for d in data]
            else:
                return DataBundle.from_dict(data)

    def __get_data(self, fileobject, meowuri):
        # TODO: [TD0167] Is it necessary to be able to handle nested keys?
        return util.nested_dict_get(self.data, [fileobject, meowuri])

    def __store_data(self, fileobject, meowuri, data):
        # TODO: [TD0167] Is it necessary to be able to handle nested keys?
        util.nested_dict_set(self.data, [fileobject, meowuri], data)

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
        temp = dict()
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
                    # TODO: Clean up converting ANY value to Unicode strings ..
                    temp[meowuri] = enc.displayable_path(v)

                elif meowuri.matchglobs(['generic.contents.text',
                                         'extractor.text.*']):
                    # Often *a lot* of text, trim to arbitrary size..
                    temp[meowuri] = truncate_text(v)
                else:
                    # TODO: Clean up converting ANY value to Unicode strings ..
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
        self._repositories = dict()

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
    # This might return a None, using a default dict value will not work.
    mapped_fields = datadict.get('mapped_fields')
    if not mapped_fields:
        return False

    for mapping in mapped_fields:
        if field == mapping.field:
            return True
    return False


Pool = None
SessionRepository = None
