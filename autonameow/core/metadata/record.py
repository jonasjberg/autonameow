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


class Record(object):
    def __init__(self, fields=dict()):
        assert isinstance(fields, dict)
        self._fields = fields

    def __getattr__(self, item):
        return self._fields.get(item)


def bundle(fields_dict):
    """
    Constructs a 'Record' instance from a dictionary.

    Intended as the primary "Public" method of creating records.
    """
    assert isinstance(fields_dict, dict)
    return Record(fields_dict)
