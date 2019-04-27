# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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

from core import event
from core import logs
from core.datastore.query import QueryResponseFailure
from core.model import meowuri_mapper
from util import encoding as enc
from util import sanity


log = logging.getLogger(__name__)


# TODO: [TD0198] Separate repositories for "raw" vs. "processed" data.


def _get_column_formatter():
    from core.view.cli import ColumnFormatter
    return ColumnFormatter()


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

    def field_mapping_weight(self, field):
        unknown_mapping_weight = 0.0

        if not self.mapped_fields or not field:
            return unknown_mapping_weight

        for mapping in self.mapped_fields:
            if field == mapping.field:
                return float(mapping.weight)

        return unknown_mapping_weight

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

    def shutdown(self):
        self._data = dict()

    def store(self, fileobject, meowuri, data):
        """
        Primary global publicly available interface for data storage.

        Adds data related to a given 'fileobject', at a storage location
        defined by the given 'meowuri'.
        """
        sanity.check_isinstance_meowuri(meowuri)
        assert not meowuri.is_generic

        if not data:
            log.warning('Attempt to add empty data with MeowURI "%s"', meowuri)
            return

        assert isinstance(data, dict)
        self._store(fileobject, meowuri, data)
        self._map_generic_field_if_present_in_data(meowuri, data)

    def _map_generic_field_if_present_in_data(self, uri, data):
        # TODO: [TD0146] Rework "generic fields". Possibly bundle in "records".
        data_generic_field = data.get('generic_field')
        if data_generic_field:
            assert (hasattr(data_generic_field, 'uri')
                    and callable(data_generic_field.uri)), (
                'Expected generic field to have a callable attribute "uri"'
            )
            data_generic_field_uri = data_generic_field.uri()

            # Store mapping between full "explicit" and "generic" URIs.
            meowuri_mapper.generic.map(uri, data_generic_field_uri)

            # Store mapping between this full "explicit" URI and a version of
            # the full URI with its leaf replaced by the leaf of the generic
            # field URI.  This is utilized in the 'query()' method.
            meowuri_mapper.leaves.map(uri, data_generic_field_uri)

    def _store(self, fileobject, meowuri, data):
        if logs.DEBUG:
            _data_value = data.get('value')
            log.debug('Storing %r->[%s] :: %s %s',
                      fileobject, meowuri, type(_data_value), _data_value)

        any_existing = self.__get_data(fileobject, meowuri)
        assert not any_existing, (
            'Would have clobbered value for URI {!s}'.format(meowuri)
        )

        self.__store_data(fileobject, meowuri, data)

    def query_mapped(self, fileobject, wanted_field):
        out = list()

        fileobject_data = self._data.get(fileobject)
        for meowuri, datadict in fileobject_data.items():
            assert isinstance(datadict, dict)
            mapped_fields = datadict.get('mapped_fields')
            if not mapped_fields:
                continue

            # TODO: [TD0167] MeowURIs in databundles only needed by resolver!
            for mapping in mapped_fields:
                if mapping.field == wanted_field:
                    out.append(
                        (mapping.weight, meowuri, DataBundle.from_dict(datadict))
                    )

        return out

    def query(self, fileobject, meowuri):
        if not meowuri:
            return QueryResponseFailure(msg='did not include a MeowURI')

        log.debug('Got query %r->[%s]', fileobject, meowuri)

        mapped_uri = None
        meowuri_is_generic = meowuri.is_generic
        if meowuri_is_generic:
            data = self._query_generic(fileobject, meowuri)
        else:
            mapped_uri = meowuri_mapper.leaves.fetch(meowuri)
            if mapped_uri:
                data = self._query_explicit_mapped(fileobject, mapped_uri)
            else:
                data = self._query_explicit(fileobject, meowuri)

        if data is None:
            return QueryResponseFailure()

        if meowuri_is_generic or mapped_uri:
            assert isinstance(data, list), (
                'Generic and "mapped" URIs should return one or more results'
            )
            return [DataBundle.from_dict(d) for d in data]

        assert isinstance(data, dict), (
            'Full "explicit" URIs should return a single result.'
        )
        return DataBundle.from_dict(data)

    def _query_explicit(self, fileobject, uri):
        return self.__get_data(fileobject, uri)

    def _query_generic(self, fileobject, uri):
        explicit_uris = meowuri_mapper.generic.fetch(uri)
        if not explicit_uris:
            return None

        data_list = list()
        for explicit_uri in explicit_uris:
            d = self.__get_data(fileobject, explicit_uri)
            if d:
                data_list.append(d)

        return data_list or None

    def _query_explicit_mapped(self, fileobject, uris):
        data_list = list()
        for uri in uris:
            d = self.__get_data(fileobject, uri)
            if d:
                data_list.append(d)

        return data_list or None

    def remove(self, fileobject):
        # TODO: [TD0131] Limit repository size! Do not remove everything!
        # TODO: [TD0131] Keep all but very bulky data like extracted text.
        if fileobject in self._data:
            self._data.pop(fileobject)

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
            out.append(self._human_readable_generic_to_explicit_uri_map())
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
                    assert isinstance(d, dict)
                    str_v = _stringify_datadict_value(d.get('value'))
                    temp_list.append(str_v)

                first_pass[meowuri] = temp_list

            else:
                assert isinstance(datadict, dict)
                str_v = _stringify_datadict_value(datadict.get('value'))
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

    def _human_readable_generic_to_explicit_uri_map(self):
        cf = _get_column_formatter()
        COLUMN_DELIMITER = '->'

        mapped = meowuri_mapper.generic._generic_to_explicit_uri_map.items()
        for generic_uri, explicit_uris in sorted(mapped):
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


SessionRepository = None


def _initialize(*_, **kwargs):
    instance = kwargs.get('autonameow_instance', '(UNKNOWN)')
    log.debug('Repository initializing (autonameow instance %s)', instance)

    global SessionRepository
    SessionRepository = Repository()


def _shutdown(*_, **kwargs):
    # TODO: [TD0202] Handle signals and graceful shutdown properly!
    instance = kwargs.get('autonameow_instance', '(UNKNOWN)')

    global SessionRepository
    if SessionRepository:
        log.debug('Repository shutting down (autonameow instance %s)', instance)
        SessionRepository.shutdown()
        SessionRepository = None


event.dispatcher.on_startup.add(_initialize)
event.dispatcher.on_shutdown.add(_shutdown)
