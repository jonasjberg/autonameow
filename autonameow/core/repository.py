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
from collections import defaultdict

from core import event
from core import logs
from util import encoding as enc
from util import sanity
from util.text import truncate_text


log = logging.getLogger(__name__)


def _get_column_formatter():
    from core.view.cli import ColumnFormatter
    return ColumnFormatter()


class QueryResponseFailure(object):
    def __init__(self, fileobject=None, uri=None, msg=None):
        self.fileobject = fileobject
        self.uri = uri or 'unspecified MeowURI'
        self.msg = msg or ''

    def __repr__(self):
        if self.fileobject:
            str_fileobject = repr(self.fileobject)
        else:
            str_fileobject = '(Unknown FileObject)'

        if self.msg:
            _msg = ' :: {!s}'.format(self.msg)
        else:
            _msg = ''

        return '{}->[{!s}]{!s}'.format(str_fileobject, self.uri, _msg)

    def __str__(self):
        return 'Failed query ' + repr(self)

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

    def field_mapping_weight(self, field):
        if not self.maps_field(field):
            return 0.0

        for mapping in self.mapped_fields:
            if field == mapping.field:
                return float(mapping.weight)

        return 0.0

    def __str__(self):
        return '<{!s}({!s})>'.format(self.__class__.__name__, self.value)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return bool(
            self.value == other.value
            and self.coercer == other.coercer
            and self.source == other.source
            and self.generic_field == other.generic_field
            and self.mapped_fields == other.mapped_fields
            and self.multivalued == other.multivalued
        )

    def __hash__(self):
        hash_mapped_fields = sum(hash(f) for f in self.mapped_fields)

        if isinstance(self.value, list):
            hash_value = sum(hash(v) for v in self.value)
        else:
            hash_value = hash(self.value)

        return hash(
            (hash_value, self.coercer, self.source, self.generic_field,
             hash_mapped_fields, self.multivalued)
        )


class Repository(object):
    """
    The repository class is the central internal storage used by all parts
    of the program. The repository stores data per file, cataloguing the
    individual data elements using "MeowURIs".

    The first level of the nested structure uses instances of 'FileObject'
    as keys into containing structures keyed by instances of 'MeowURI'.
    Actual data "values" are stored in these dictionary structures,
    along with additional "metainfo" about the data "value".

    The internal storage structure is laid out like this:

            STORAGE = {
                'fileObject_A': {
                    'MeowURI_A': datadict()
                    'MeowURI_B': datadict()
                }
                'fileObject_B': {
                    'MeowURI_A': datadict()
                }
            }

    And the inner 'datadict' dictionaries are laid out like this:

            datadict = {
                'coercer': <subclass of BaseCoercer>,
                'generic_field': <subclass of GenericField>,
                'mapped_fields: [
                     <WeightedMapping>,
                     <WeightedMapping>,
                     ...
                ],
                'multivalued': False,
                'source': source provider class name as a string,
                'value': Actual data value, as a primitive type or 'datetime'
            }

    NOTE: Data is passed in as dicts but returned as instances of 'DataBundle'!
    """
    def __init__(self):
        self._data = dict()

        # Stores references from "generic" to "explicit" URIs.
        # Outer dict is keyed by instances of 'FileObject', storing
        # defaultdicts keyed by "generic" URIs that in turn store sets
        # of "explicit" URIs.
        self._generic_to_explicit_uri_map = dict()

    def shutdown(self):
        self._data = dict()
        self._generic_to_explicit_uri_map = dict()

    def store(self, fileobject, meowuri, data):
        """
        Primary global publicly available interface for data storage.

        Adds data related to a given 'fileobject', at a storage location
        defined by the given 'meowuri'.
        """
        sanity.check_isinstance_meowuri(meowuri)
        assert not meowuri.is_generic

        if not data:
            log.warning('Attempted to add empty data with meowURI'
                        ' "{!s}"'.format(meowuri))
            return

        sanity.check_isinstance(data, dict)
        self._store(fileobject, meowuri, data)
        self._store_generic(fileobject, meowuri, data)

    def _store_generic(self, fileobject, uri, data):
        # TODO: [TD0146] Rework "generic fields". Possibly bundle in "records".
        data_generic_field = data.get('generic_field')
        if data_generic_field:
            assert hasattr(data_generic_field, 'uri')
            assert callable(data_generic_field.uri)
            generic_field_uri = data_generic_field.uri()
            self._map_generic_to_explicit_uri(fileobject, generic_field_uri, uri)

    def _store(self, fileobject, meowuri, data):
        if logs.DEBUG:
            _data_value = data.get('value')
            if _is_full_text_meowuri(meowuri):
                assert isinstance(_data_value, str), (
                    'Expect data stored with this MeowURI to be type "str"'
                )
                _data_value = _truncate_text(_data_value)

            log.debug('Storing {!r}->[{!s}] :: {} {!s}'.format(
                fileobject, meowuri, type(_data_value), _data_value
            ))

        any_existing = self.__get_data(fileobject, meowuri)
        assert not any_existing, (
            'Would have clobbered value for URI {!s}'.format(meowuri)
        )

        self.__store_data(fileobject, meowuri, data)

    def _map_generic_to_explicit_uri(self, fileobject, generic_uri, explicit_uri):
        if fileobject not in self._generic_to_explicit_uri_map:
            self._generic_to_explicit_uri_map[fileobject] = defaultdict(set)

        if logs.DEBUG:
            log.debug('Mapping {!r} generic MeowURI {!s} -> {!s}'.format(
                fileobject, generic_uri, explicit_uri
            ))
        self._generic_to_explicit_uri_map[fileobject][generic_uri].add(explicit_uri)

    def _get_explicit_uris_from_generic_uri(self, fileobject, generic_uri):
        if fileobject not in self._generic_to_explicit_uri_map:
            return set()

        return self._generic_to_explicit_uri_map[fileobject].get(generic_uri)

    def query_mapped(self, fileobject, field):
        out = list()

        fileobject_data = self._data.get(fileobject)
        for meowuri, datadict in fileobject_data.items():
            assert isinstance(datadict, dict)
            if maps_field(datadict, field):
                # TODO: [TD0167] MeowURIs in databundles only needed by resolver!
                out.append(
                    (meowuri, DataBundle.from_dict(datadict))
                )

        return out

    def query(self, fileobject, meowuri):
        if not meowuri:
            return QueryResponseFailure(msg='did not include a MeowURI')

        log.debug('Got query {!r}->[{!s}]'.format(fileobject, meowuri))

        meowuri_is_generic = meowuri.is_generic
        if meowuri_is_generic:
            data = self._query_generic(fileobject, meowuri)
        else:
            data = self._query_explicit(fileobject, meowuri)

        if data is None:
            return QueryResponseFailure()

        if meowuri_is_generic:
            assert isinstance(data, list)
            return [DataBundle.from_dict(d) for d in data]

        assert isinstance(data, dict)
        return DataBundle.from_dict(data)

    def _query_explicit(self, fileobject, uri):
        return self.__get_data(fileobject, uri)

    def _query_generic(self, fileobject, uri):
        explicit_uris = self._get_explicit_uris_from_generic_uri(fileobject, uri)
        if not explicit_uris:
            return None

        data_list = list()
        for explicit_uri in explicit_uris:
            d = self.__get_data(fileobject, explicit_uri)
            if d:
                data_list.append(d)

        return data_list or None

    def remove(self, fileobject):
        # TODO: [TD0131] Limit repository size! Do not remove everything!
        # TODO: [TD0131] Keep all but very bulky data like extracted text.
        if fileobject in self._data:
            self._data.pop(fileobject)
        if fileobject in self._generic_to_explicit_uri_map:
            self._generic_to_explicit_uri_map.pop(fileobject)

    def __get_data(self, fileobject, meowuri):
        if fileobject in self._data:
            return self._data[fileobject].get(meowuri)
        return None

    def __store_data(self, fileobject, meowuri, data):
        if fileobject not in self._data:
            self._data[fileobject] = dict()
        self._data[fileobject][meowuri] = data

    def human_readable_contents(self):
        out = list()
        for fileobject, fileobject_data in self._data.items():
            out.append('FileObject basename: "{!s}"'.format(fileobject))

            _abspath = enc.displayable_path(fileobject.abspath)
            out.append('FileObject absolute path: "{!s}"'.format(_abspath))

            out.append('')
            out.append(self._prettyprint_fileobject_data(fileobject_data))
            out.append('')
            out.append(self._prettyprint_fileobject_generic_to_explicit_uri_map(fileobject))
            out.append('\n')

        return '\n'.join(out)

    @staticmethod
    def _prettyprint_fileobject_data(data):
        # First pass --- handle encoding and truncate extracted text.
        first_pass = dict()
        for meowuri, datadict in sorted(data.items()):
            if isinstance(datadict, list):
                temp_list = list()
                for d in datadict:
                    sanity.check_isinstance(d, dict)
                    str_v = _stringify_datadict_value(d.get('value'))
                    if _is_full_text_meowuri(meowuri):
                        # Often *a lot* of text, trim to arbitrary size..
                        temp_list.append(_truncate_text(str_v))
                    else:
                        temp_list.append(str_v)

                first_pass[meowuri] = temp_list

            else:
                sanity.check_isinstance(datadict, dict)
                str_v = _stringify_datadict_value(datadict.get('value'))
                if _is_full_text_meowuri(meowuri):
                    # Often *a lot* of text, trim to arbitrary size..
                    first_pass[meowuri] = _truncate_text(str_v)
                else:
                    first_pass[meowuri] = str_v

        # Second pass --- align in columns and add numbers to generic URIs.
        cf = _get_column_formatter()
        COLUMN_DELIMITER = '::'
        MAX_VALUE_WIDTH = 80

        def _add_row(_str_meowuri, _value):
            _str_value = str(_value)
            if len(_str_value) > MAX_VALUE_WIDTH:
                _str_value = _str_value[:MAX_VALUE_WIDTH]
            cf.addrow(_str_meowuri, COLUMN_DELIMITER, _str_value)

        for meowuri, str_value in sorted(first_pass.items()):
            str_meowuri = str(meowuri)

            if isinstance(str_value, list):
                str_values = str_value
                for n, v in enumerate(str_values, start=1):
                    numbered_meowuri = '{} ({})'.format(str_meowuri, n)
                    _add_row(numbered_meowuri, v)

                continue

            _add_row(str_meowuri, str_value)

        return str(cf)

    def _prettyprint_fileobject_generic_to_explicit_uri_map(self, fileobject):
        cf = _get_column_formatter()
        COLUMN_DELIMITER = '->'

        for generic_uri, explicit_uris in sorted(self._generic_to_explicit_uri_map[fileobject].items()):
            for n, explicit_uri in enumerate(sorted(explicit_uris), start=1):
                str_number = '({})'.format(n)
                str_generic_uri = str(generic_uri)
                str_explicit_uri = str(explicit_uri)
                cf.addrow(str_generic_uri, str_number, COLUMN_DELIMITER, str_explicit_uri)

        return str(cf)

    def __len__(self):
        """
        Returns: Total number of (MeowURI, databundle) entries for all files.
        """
        return sum(len(v) for k, v in self._data.items())

    def __str__(self):
        return self.human_readable_contents()


def _is_full_text_meowuri(uri):
    return uri.matchglobs(['generic.contents.text', 'extractor.text.*'])


def _truncate_text(text):
    t = truncate_text(text, maxlen=20, append_info=True)
    t = t.replace('\n', ' ')
    return t


def _stringify_datadict_value(datadict_value):
    def __stringify_value(_value):
        assert not isinstance(_value, (list, dict))

        if isinstance(_value, bytes):
            return enc.displayable_path(_value)
        else:
            return str(_value)

    if isinstance(datadict_value, list):
        values = datadict_value

        str_values = list()
        for value in values:
            str_value = __stringify_value(value)
            assert isinstance(str_value, str)
            str_values.append(str_value)

        return str(str_values)

    str_value = __stringify_value(datadict_value)
    assert isinstance(str_value, str)
    return str_value


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


def maps_field(datadict, field):
    # This might return a None, using a default dict value will not work.
    mapped_fields = datadict.get('mapped_fields')
    if not mapped_fields:
        return False

    for mapping in mapped_fields:
        if field == mapping.field:
            return True
    return False


def _initialize(*_, **kwargs):
    # Keep one global 'SessionRepository' per 'Autonameow' instance.
    # assert 'autonameow_instance' in kwargs
    autonameow_instance = kwargs.get('autonameow_instance', None)

    global Pool
    Pool = RepositoryPool()
    Pool.add(id_=autonameow_instance)

    global SessionRepository
    SessionRepository = Pool.get(autonameow_instance)


def _shutdown(*_, **kwargs):
    global Pool
    if not Pool:
        return

    assert 'autonameow_instance' in kwargs
    autonameow_instance = kwargs.get('autonameow_instance', None)
    try:
        r = Pool.get(autonameow_instance)
    except KeyError as e:
        log.critical('Unable to retrieve repository :: {!s}'.format(e))
    else:
        r.shutdown()


Pool = None
SessionRepository = None

event.dispatcher.on_startup.add(_initialize)
event.dispatcher.on_shutdown.add(_shutdown)
