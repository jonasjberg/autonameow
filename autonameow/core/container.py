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

from core import util


class DataContainerBase(object):
    def __init__(self):
        self._data = {}

    def add(self, query_string, data):
        """
        Adds data for later retrieval through "query string".
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def get(self, query_string=None):
        """
        Returns all contained data, or data matching a specified "query string".
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def __iter__(self):
        for k, v in self._data.items():
            yield (k, v)

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
