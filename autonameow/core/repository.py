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
        self._query_string_source_map = {}
        self.resolvable_query_strings = set()

    def initialize(self):
        self._create_query_string_source_mapping()
        self.resolvable_query_strings = self._get_resolvable_query_strings()

    def _create_query_string_source_mapping(self):
        # Module attributes store all available non-core components in dicts,
        # with keys being the "query strings" that the components store data
        # under and the contained values are lists of classes.
        self._query_string_source_map['extractors'] = extractors.QueryStringExtractorClassMap
        self._query_string_source_map['analyzers'] = analyzers.QueryStringAnalyzerClassMap
        self._query_string_source_map['plugins'] = plugins.QueryStringPluginClassMap

    def _get_resolvable_query_strings(self):
        out = set()

        for key in ['extractors', 'analyzers', 'plugins']:
            for query_string, _ in self._query_string_source_map[key].items():
                out.add(query_string)

        return out

    def store(self, file_object, label, data):
        util.nested_dict_set(self.data, [file_object, label], data)

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

SessionRepository = Repository()
SessionRepository.initialize()
