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

from core import exceptions

# TODO: [TD0077] Implement a "repository" to handle "query string" queries.
# TODO: [TD0076] Have all non-core components register themselves at run-time.


class Repository(object):
    def __init__(self):
        self.data = {}
        self._resolvable_query_strings = set()

    def initialize(self):
        extractor_query_strings = extraction

    def resolve(self, query_string):
        if not query_string:
            raise exceptions.InvalidDataSourceError(
                'Unable to resolve empty query string'
            )

        # TODO: ..
        pass

    def resolvable(self, query_string):
        if not query_string:
            return False

        # TODO: ..
        pass
