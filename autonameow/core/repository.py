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

import analyzers
import extractors
import plugins
from core import (
    exceptions,
    util
)


class Repository(object):
    def __init__(self):
        self.data = {}
        self.query_string_class_map = {}
        self.resolvable_query_strings = set()

    def initialize(self):
        self.query_string_class_map = querystring_class_map_dict()
        self.resolvable_query_strings = resolvable_query_strings(
            self.query_string_class_map
        )

    def store(self, file_object, query_string, data):
        """
        Adds data related to a given 'file_object', at a storage location
        defined by the given 'query_string'.

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
        if not query_string:
            raise exceptions.InvalidDataSourceError(
                'Invalid source (missing label)'
            )

        if data is None:
            log.warning('Attempted to add None data with query string'
                        ' "{!s}"'.format(query_string))
            return

        try:
            any_existing = util.nested_dict_get(self.data,
                                                [file_object, query_string])
        except KeyError:
            pass
        else:
            if any_existing is not None:
                assert(not isinstance(data, list))
                data = [any_existing] + [data]

        util.nested_dict_set(self.data, [file_object, query_string], data)

    def resolve(self, file_object, query_string):
        if not query_string:
            raise exceptions.InvalidDataSourceError(
                'Unable to resolve empty query string'
            )

        try:
            d = util.nested_dict_get(self.data, [file_object, query_string])
        except KeyError as e:
            log.debug('Repository request raised KeyError: {!s}'.format(e))
            return None
        else:
            return d

    def resolvable(self, query_string):
        if not query_string:
            return False

        resolvable = list(self.resolvable_query_strings)
        if any([query_string.startswith(r) for r in resolvable]):
            return True
        return False

    def __len__(self):
        return util.count_dict_recursive(self.data)

    def __str__(self):
        out = {}

        for key, value in self.data.items():
            # TODO: [TD0066] Handle all encoding properly.
            if isinstance(value, bytes):
                out[key] = util.displayable_path(value)
            else:
                out[key] = value

        expanded = util.expand_query_string_data_dict(out)
        return util.dump(expanded)

    def __repr__(self):
        out = {}

        for key, value in self.data.items():
            # TODO: [TD0066] Handle all encoding properly.
            if isinstance(value, bytes):
                out[key] = util.displayable_path(value)
            else:
                out[key] = value

        return out


def querystring_class_map_dict():
    # The 'QueryStringClassMap' attributes in non-core modules keep
    # references to the available component class.
    # These are dicts with keys being the "query strings" that the data
    # stored by the respective component uses when storing data and the
    # contained values are lists of classes mapped to the "query string".
    _query_string_class_map = {
        'extractors': extractors.QueryStringClassMap,
        'analyzers': analyzers.QueryStringClassMap,
        'plugins': plugins.QueryStringClassMap
    }
    return _query_string_class_map


def resolvable_query_strings(query_string_class_map):
    out = set()

    # for key in ['extractors', 'analyzers', 'plugins']:
    for key in query_string_class_map.keys():
        for query_string, _ in query_string_class_map[key].items():
            out.add(query_string)

    return out


SessionRepository = Repository()
SessionRepository.initialize()
