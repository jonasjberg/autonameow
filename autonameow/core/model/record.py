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


class Record(object):
    """
    Instances of the Record class represent a collection of fields,
    I.E. a bundle of data fields. One example might be ISBN metadata.
    """
    def __init__(self, *fields):
        self.fields = list(fields)

        self._weight = None

    # def _calculate_weight(self):
    #     if not self.fields:
    #         return 0.0
    #
    #     _field_weights = sum(f.weight for f in self.fields)
    #    return _field_weights / len(self.fields)

    def __contains__(self, item):
        if not item:
            return False
        return bool(item in self.fields)

    def __len__(self):
        return len(self.fields)


class RecordComparator(object):
    pass
