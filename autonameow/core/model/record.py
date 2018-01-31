# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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

    def __contains__(self, item):
        if not item:
            return False
        return bool(item in self.fields)

    def __len__(self):
        return len(self.fields)


class RecordComparator(object):
    def weigh(self, record1, record2):
        # Prefer record with most number of non-empty fields.
        _record1_len = len([f for f in record1.fields if f])
        _record2_len = len([f for f in record2.fields if f])
        if _record1_len > _record2_len:
            return record1
        elif _record2_len > _record1_len:
            return record2

        # Prefer record with highest total field-length.
        _record1_field_sum = sum(len(f) for f in record1.fields if f)
        _record2_field_sum = sum(len(f) for f in record2.fields if f)
        if _record1_field_sum > _record2_field_sum:
            return record1
        elif _record2_field_sum > _record1_field_sum:
            return record2
