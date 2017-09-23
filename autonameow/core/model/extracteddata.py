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

import copy
import logging

from core import types


log = logging.getLogger(__name__)


class ExtractedData(object):
    """
    Instances of this class wrap some extracted data with extra information.

    Extractors can specify which (if any) name template fields that the item
    is compatible with. For instance, date/time-information is could be used
    to populate the 'datetime' name template field.
    """
    def __init__(self, coercer, mapped_fields=None, generic_field=None):
        self.coercer = coercer

        if mapped_fields is not None:
            self.field_map = mapped_fields
        else:
            self.field_map = []

        self._data = None

        if generic_field is not None:
            self.generic_field = generic_field
        else:
            self.generic_field = None

    def __call__(self, raw_value):
        if self._data is not None:
            log.critical('"{!s}"._data is *NOT* None! Called with value:'
                         ' {!s}"'.format(self, raw_value))

        if not self.coercer:
            _candidate_coercer = types.coercer_for(raw_value)
            if _candidate_coercer:
                self.coercer = _candidate_coercer

        if self.coercer:
            self._data = self.coercer(raw_value)
        else:
            log.warning('Unknown coercer in ExtractedData: "{!s}"'.format(self))
            # Fall back to automatic type detection.
            # Note that this will coerce some types in unintended ways.
            # Bytestring paths (bytes) is coerced to "str" --- NOT GOOD!
            # Paths/filenames should be coerced with 'AW_PATH*' ..

            # TODO: [TD0088] The "resolver" needs 'coerce.format' ..
            coerced = types.try_coerce(raw_value)
            if coerced is None:
                log.critical('Unhandled coercion of raw value "{!s}" '
                             '({!s})'.format(raw_value, type(raw_value)))
                self._data = raw_value
            else:
                self._data = coerced

        return self

    @classmethod
    def from_raw(cls, instance, raw_value):
        _instance_copy = copy.deepcopy(instance)
        try:
            return _instance_copy(raw_value)
        except types.AWTypeError as e:
            log.debug(str(e))
            return None

    @property
    def value(self):
        return self._data

    def maps_field(self, field):
        for mapping in self.field_map:
            if field == mapping.field:
                return True
        return False

    def __str__(self):
        # 1) Detailed information, not suitable when listing to user ..
        # return '{!s}("{!s}")  FieldMap: {!s}"'.format(
        #     self.coercer, self.value, self.field_map
        # )

        # 2) Simple default string representation of the data ..
        return '{!s}'.format(self.value)

        # 3) Use the format method of the coercer ..
        # return self.coercer.format(self.value)

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if (self.coercer == other.coercer
                and self.field_map == other.field_map
                and self.value == other.value):
            return True
        return False
