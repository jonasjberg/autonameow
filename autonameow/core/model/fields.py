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

from core.metadata.normalize import normalize_full_human_name
from core.metadata.normalize import normalize_full_title


# Benefits of encapsulating a field/value tuple in a 'Field' class
# ================================================================
# Cases where there are fields that should have a single value,
# I.E. not 'multivalued'.
# Storing metadata in dicts keyed by fields does not handle this well;
#
#     metadata = {
#         'XMP:ModifyDate': [1942, 2018]
#     }
#
# Passing this to 'coerce_field_value' would result in either skipping the
# value because the field meta specifies that a single value is expected
# *OR* coercing the list into a single value, maybe by only using the first
# (1942) or maybe joining them into a single string ('1942 2018') ..
#
# Either way is not what we want. Would probably rather store two separate
# instances, __which isn't possible__ when storing in dicts keyed by the field!
#
# Workarounds like this will NOT work for obvious reasons..
#
#     metadata = {
#         'XMP:ModifyDate_A': 1942,
#         'XMP:ModifyDate_B': 2018
#     }
#
# HOWEVER, this could be worked around by encapsulating the field name and
# value in an instance of a 'Field' class that uses both the field name and value
# to calculate the hash used by dicts;
#
#     metadata = [
#         Field('XMP:ModifyDate', 1942),
#         Field('XMP:ModifyDate', 2018)
#     ]
#
# And to avoid having to iterate over lists to check for membership, etc.,
# a collection of fields could be bundled with instances of a 'Record' class;
#
#     metadata = Record(
#         Field('XMP:ModifyDate', 1942),
#         Field('XMP:ModifyDate', 2018)
#     )
#
# Alternatively, to indicate these are mutually exclusive *possible* values;
#
#     metadata = [
#         Record(
#             Field('XMP:ModifyDate', 1942),
#         ),
#         Record(
#             Field('XMP:ModifyDate', 2018)
#         )
#     ]


class BaseField(object):
    def __init__(self, value):
        self.value = value
        self.record = None

        self._normvalue = None
        self.normalize = lambda x: x

    @property
    def normvalue(self):
        if self._normvalue is None:
            self._normvalue = self.normalize(self.value)
        return self._normvalue

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.value == other.value:
            return True
        if self.normvalue == other.normvalue:
            return True

        return False

    def __bool__(self):
        return bool(self.normvalue)

    def __len__(self):
        return len(self.normvalue) or 0


class Author(BaseField):
    def __init__(self, value):
        super().__init__(value)
        self.normalize = normalize_full_human_name


class Title(BaseField):
    def __init__(self, value):
        super().__init__(value)
        self.normalize = normalize_full_title
