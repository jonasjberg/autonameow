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

import logging as log

from core import (
    util,
    constants
)
from core.exceptions import InvalidDataSourceError


class DataContainerBase(object):
    # TODO: [TD0073] Fix or remove the 'SessionDataPool' class.
    def __init__(self):
        self._data = {}

    def add(self, file_object, query_string, data):
        """
        Adds data related to a given 'file_object', at a storage location
        defined by the given 'query string'.

            STORAGE = {
                'file_object_A': {
                    'query_string_a': [1, 2]
                    'query_string_b': ['foo']
                }
                'file_object_B': {
                    'query_string_a': ['bar']
                    'query_string_b': [2, 1]
                }
            }
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def get(self, file_object=None, query_string=None):
        """
        Returns all contained data if neither optional argument is given.
        If 'file_object' is specified, return only data related to that object.
        If 'query_string' is specified, data matching the query is returned.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    # TODO: Now encapsulated by outer dict keyed by 'FileObject' instances.
    # def __iter__(self):
    #     for k, v in self._data.items():
    #         yield (k, v)

    def __len__(self):
        return util.count_dict_recursive(self._data)

    def __str__(self):
        out = {}

        for key, value in self._data.items():
            # TODO: [TD0066] Handle all encoding properly.
            if isinstance(value, bytes):
                out[key] = util.displayable_path(value)
            else:
                out[key] = value

        expanded = util.expand_query_string_data_dict(out)
        return util.dump(expanded)

    def __repr__(self):
        out = {}

        for key, value in self._data.items():
            # TODO: [TD0066] Handle all encoding properly.
            if isinstance(value, bytes):
                out[key] = util.displayable_path(value)
            else:
                out[key] = value

        return out


class SessionDataPool(DataContainerBase):
    # TODO: [TD0073] Fix or remove the 'SessionDataPool' class.
    def __init__(self):
        super(SessionDataPool, self).__init__()

    def add(self, file_object, query_string, data):
        if not query_string:
            raise InvalidDataSourceError('Invalid source (missing label)')

        if data is None:
            log.warning('Attempted to add None data with query string'
                        ' "{!s}"'.format(query_string))
            return

        if file_object not in self._data:
            self._data[file_object] = {}

        if query_string in self._data[file_object]:
            t = self._data[file_object][query_string]
            self._data[file_object][query_string] = [t] + [data]
        else:
            self._data[file_object][query_string] = data

    def get(self, query_string=None):
        """
        Returns all contained data, or data matching a specified "query string".

        Args:
            query_string: Any string defined in "constants.VALID_DATA_SOURCES".
        Returns:
            Data associated with the given query string, or False if the data
            does not exist.
            If no query string is specified, all data is returned.
        Raises:
            InvalidDataSourceError: The query string is not a valid data source.
        """
        if query_string is not None:
            if query_string not in constants.VALID_DATA_SOURCES:
                log.critical('Attempted to retrieve data using "invalid"'
                             'query_string: "{}"'.format(query_string))
            return self._data.get(query_string, False)
        else:
            return self._data
