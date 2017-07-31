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

    def add(self, destination, data):
        """
        Adds data for later retrieval through "destination".
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def get(self, query=None):
        """
        Returns all contained data, or data matching a specified query.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def __iter__(self):
        for k, v in self._data.items():
            yield (k, v)

    def __len__(self):
        return util.count_dict_recursive(self._data)
