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

import analyzers
import extractors
import plugins
from core import (
    exceptions,
    util,
)
from core.model import (
    ExtractedData,
    MeowURI
)
from core.util import (
    sanity,
    textutils
)


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
                    'meowuri_c': ExtractedData(...)
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
        self.meowuri_class_map = {}
        self.mapped_meowuris = set()
        self.log = logging.getLogger(
            '{!s}.{!s}'.format(__name__, self.__module__)
        )
        # self.log.setLevel(logging.DEBUG)

    def initialize(self):
        self.meowuri_class_map = meowuri_class_map_dict()
        self._log_string_class_map()

        # Set of all MeowURIs "registered" by extractors, analyzers or plugins.
        self.mapped_meowuris = unique_map_meowuris(self.meowuri_class_map)

    def _log_string_class_map(self):
        for key in self.meowuri_class_map.keys():
            for meowuri, klass in self.meowuri_class_map[key].items():
                self.log.debug(
                    'Mapped meowURI "{!s}" to "{!s}" ({!s})'.format(meowuri,
                                                                    klass, key)
                )

    def store(self, fileobject, meowuri, data):
        """
        Primary global publicly available interface for data storage.

        Adds data related to a given 'fileobject', at a storage location
        defined by the given 'meowuri'.
        """
        def __meowuri_error(bad_meowuri):
            raise exceptions.InvalidDataSourceError(
                'Invalid MeowURI: "{!s}" ({})'.format(bad_meowuri,
                                                      type(bad_meowuri))
            )

        if not meowuri or not isinstance(meowuri, str):
            __meowuri_error(meowuri)
        if not meowuri.strip():
            __meowuri_error(meowuri)

        if data is None:
            log.warning('Attempted to add None data with meowURI'
                        ' "{!s}"'.format(meowuri))
            return

        self._store(fileobject, meowuri, data)
        self._store_generic(fileobject, data)

    def _store_generic(self, fileobject, data):
        # TODO: [TD0082] Integrate the 'ExtractedData' class.
        if not isinstance(data, ExtractedData):
            return

        if data.generic_field is not None:
            try:
                _gen_uri = data.generic_field.uri()
            except AttributeError:
                # TODO: [TD0082] Integrate the 'ExtractedData' class.
                self.log.critical('TODO: Fix missing "field.uri()" for some'
                                  ' GenericField classes!')
            else:
                self._store(fileobject, _gen_uri, data)

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
                    if isinstance(d, ExtractedData):
                        if d.maps_field(field):
                            out.append(d)
            else:
                if isinstance(data, ExtractedData):
                    if data.maps_field(field):
                        out.append(data)

        return out

    def query(self, fileobject, meowuri, mapped_to_field=None):
        if not meowuri:
            raise exceptions.InvalidDataSourceError(
                'Unable to resolve empty meowURI'
            )

        log.debug('Got request [{:8.8}]->[{!s}] Mapped to Field: "{!s}"'.format(
            fileobject.hash_partial, meowuri, mapped_to_field))

        try:
            data = self.__get_data(fileobject, meowuri)
        except KeyError as e:
            log.debug('Repository request raised KeyError: {!s}'.format(e))
            return None
        else:
            # TODO: [TD0082] Integrate the 'ExtractedData' class.
            if isinstance(data, ExtractedData):
                if mapped_to_field is not None:
                    if data.maps_field(mapped_to_field):
                        return data
                    else:
                        log.debug(
                            'Repository request failed requirement; [{:8.8}]->'
                            '[{!s}] Mapped to Field: "{!s}"'.format(
                                fileobject.hash_partial, meowuri,
                                mapped_to_field
                            )
                        )
                        return None
                else:
                    return data

            else:
                return data

    def __get_data(self, file, meowuri):
        return util.nested_dict_get(self.data, [file, meowuri])

    def __store_data(self, file, meowuri, data):
        util.nested_dict_set(self.data, [file, meowuri], data)

    def resolvable(self, meowuri):
        if not meowuri:
            return False

        resolvable = list(self.mapped_meowuris)
        if any(r in meowuri for r in resolvable):
            return True
        return False

    def human_readable_contents(self):
        out = []
        for fileobject, data in self.data.items():
            out.append('FileObject basename: "{!s}"'.format(fileobject))

            _abspath = util.displayable_path(fileobject.abspath)
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
                return '{: <{}}: * {!s}'.format(_key, width, _value)

        def _fmt_text_line(width, _value, _key=None):
            if _key is None:
                return '{: <{}}  > {!s}'.format('', width, _value)
            else:
                return '{: <{}}: > {!s}'.format(_key, width, _value)

        def _fmt_entry(_key, width, _value):
            return '{: <{}}: {!s}'.format(_key, width, _value)

        # TODO: [TD0066] Handle all encoding properly.
        temp = {}
        _max_len_meowuri = 20
        for uri, data in data.items():
            _max_len_meowuri = max(_max_len_meowuri, len(uri))

            if isinstance(data, list):
                log.debug('TODO: Improve robustness of handling this case')
                temp_list = []
                for element in data:
                    # TODO: [TD0082] Integrate the 'ExtractedData' class.
                    if isinstance(element, ExtractedData):
                        v = element.value
                    else:
                        v = element

                    if isinstance(v, bytes):
                        temp_list.append(util.displayable_path(v))

                    # TODO: [TD0105] Integrate the 'MeowURI' class.
                    elif MeowURI(uri).matchglobs(['generic.contents.text',
                                                  'extractor.text.*']):
                        # Often *a lot* of text, trim to arbitrary size..
                        _truncated = textutils.truncate_text(v)
                        temp_list.append(_truncated)
                    else:
                        temp_list.append(str(v))

                temp[uri] = temp_list

            else:
                # TODO: [TD0082] Integrate the 'ExtractedData' class.
                if isinstance(data, ExtractedData):
                    v = data.value
                else:
                    v = data

                if isinstance(v, bytes):
                    temp[uri] = util.displayable_path(v)

                # Often *a lot* of text, trim to arbitrary size..
                # TODO: [TD0105] Integrate the 'MeowURI' class.
                elif MeowURI(uri).matchglobs(['generic.contents.text',
                                              'extractor.text.*']):
                    temp[uri] = textutils.truncate_text(v)
                else:
                    temp[uri] = str(v)

        out = []
        for uri, data in temp.items():
            if isinstance(data, list):
                if data:
                    out.append(_fmt_list_entry(_max_len_meowuri, data[0], uri))
                    for v in data[1:]:
                        out.append(_fmt_list_entry(_max_len_meowuri, v))

            else:
                # TODO: [TD0105] Integrate the 'MeowURI' class.
                if MeowURI(uri).matchglobs(['generic.contents.text',
                                            'extractor.text.*']):
                    _text = textutils.extract_lines(
                        data, firstline=0, lastline=1
                    )
                    _text = _text.rstrip('\n')
                    out.append(_fmt_text_line(_max_len_meowuri, _text, uri))
                    _lines = textutils.extract_lines(
                        data, firstline=1, lastline=len(data.splitlines())
                    )
                    for _line in _lines.splitlines():
                        out.append(_fmt_text_line(_max_len_meowuri, _line))
                else:
                    out.append(_fmt_entry(uri, _max_len_meowuri, data))

        return out

    def __len__(self):
        return util.count_dict_recursive(self.data)

    def __str__(self):
        return self.human_readable_contents()

    # def __repr__(self):
    #     # TODO: Implement this properly.
    #     pass


MEOWURI_CLASS_MAP_DICT = {}


def meowuri_class_map_dict():
    # The 'MeowURIClassMap' attributes in non-core modules keep
    # references to the available component classes.
    # These are dicts with keys being the "meowURIs" that the respective
    # component uses when storing data and the contained values are lists of
    # classes mapped to the "meowURI".
    global MEOWURI_CLASS_MAP_DICT
    if not MEOWURI_CLASS_MAP_DICT:
        MEOWURI_CLASS_MAP_DICT = {
            'extractor': extractors.MeowURIClassMap,
            'analyzer': analyzers.MeowURIClassMap,
            'plugin': plugins.MeowURIClassMap
        }
    return MEOWURI_CLASS_MAP_DICT


def unique_map_meowuris(meowuri_class_map):
    out = set()

    # for key in ['extractors', 'analyzer', 'plugin'] ..
    for key in meowuri_class_map.keys():
        for _meowuri in meowuri_class_map[key].keys():
            sanity.check(not isinstance(_meowuri, list),
                         'Unexpectedly got "meowuri" of type list')
            out.add(_meowuri)

    return out


def all_meowuris():
    # TODO: [TD0099] FIX THIS! Temporary hack for 'prompt_toolkit' experiments.
    meowuri_class_map = meowuri_class_map_dict()
    return unique_map_meowuris(meowuri_class_map)


def map_meowuri_to_source_class(meowuri, includes=None):
    """
    Returns a list of classes that could store data using the given "MeowURI".

    Args:
        meowuri: The "MeowURI" of interest.
        includes: Optional list of sources to include. Default: include all

    Returns:
        A list of classes that "could" produce and store data with a MeowURI
        that matches the given MeowURI.
    """
    meowuri_class_map = meowuri_class_map_dict()

    def _search_source_type(key):
        for k, v in meowuri_class_map[key].items():
            if k in meowuri:
                return meowuri_class_map[key][k]
        return None

    if not meowuri:
        log.error('Got empty meowuri in "map_meowuri_to_source_class"')
        return []

    if includes is None:
        return (_search_source_type('extractor')
                or _search_source_type('analyzer')
                or _search_source_type('plugin')
                or [])
    else:
        if not isinstance(includes, list):
            includes = [includes]
        for include in includes:
            if include not in ('analyzer', 'extractor', 'plugin'):
                continue

            result = _search_source_type(include)
            if result is not None:
                return result

        return []


def get_sources_for_meowuris(meowuri_list, include_roots=None):
    if not meowuri_list:
        return []

    out = set()
    for uri in meowuri_list:
        source_classes = map_meowuri_to_source_class(uri, include_roots)

        # TODO: Improve robustness of linking "MeowURIs" to data source classes.
        if source_classes:
            for source_class in source_classes:
                out.add(source_class)

    return list(out)


def _create_repository():
    repository = Repository()
    repository.initialize()
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


def initialize(id_=None):
    # Keep one global 'SessionRepository' per 'Autonameow' instance.
    global Pool
    Pool = RepositoryPool()
    Pool.add(id_=id_)

    global SessionRepository
    SessionRepository = Pool.get(id_=id_)


Pool = None
SessionRepository = None
