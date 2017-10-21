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
from core.util import textutils


log = logging.getLogger(__name__)


class ExtractedData(object):
    """
    Instances of this class wrap some extracted data with extra information.

    Extractors can specify which (if any) name template fields that the item
    should be associated with. For instance, date/time-information could be
    used to populate the 'datetime'/'date' name template fields.
    """
    def __init__(self, coercer, mapped_fields=None, generic_field=None,
                 multivalued=None):
        self.coercer = coercer

        if mapped_fields is not None:
            self.field_map = mapped_fields
        else:
            self.field_map = []

        self._value = None

        if generic_field is not None:
            self.generic_field = generic_field
        else:
            self.generic_field = None

        if multivalued is not None:
            self.multivalued = bool(multivalued)
        else:
            self.multivalued = False

    def __call__(self, raw_value):
        if self._value is not None:
            log.critical('"{!s}"._value is *NOT* None! Called with value:'
                         ' {!s}"'.format(self, raw_value))

        if not self.coercer:
            _sample_raw_value = None

            if isinstance(raw_value, (list, tuple)):
                try:
                    _sample_raw_value = raw_value[0]
                except IndexError:
                    pass
            elif isinstance(raw_value, dict):
                try:
                    _sample_raw_value = raw_value.get(raw_value.keys()[0])
                except (IndexError, KeyError):
                    pass
            else:
                _sample_raw_value = raw_value

            _candidate_coercer = types.coercer_for(_sample_raw_value)
            if _candidate_coercer:
                self.coercer = _candidate_coercer
            else:
                log.warning('Unknown coercer for value: "{!s}" ({!s})'.format(
                        _sample_raw_value, type(_sample_raw_value)
                ))

        # TODO: [TD0115] Clear up uncertainties about data multiplicities
        if self.coercer:
            if self.multivalued:
                _coerced_values = []
                _raw_values = raw_value
                for _value in _raw_values:
                    _coerced = self.coercer(_value)
                    if _coerced:
                        _coerced_values.append(_coerced)

                self._value = _coerced_values

            else:
                self._value = self.coercer(raw_value)
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
                self._value = raw_value
            else:
                self._value = coerced

        return self

    def as_string(self):
        if self.coercer:
            # TODO: [TD0115] Clear up uncertainties about data multiplicities
            if self.multivalued:
                _values = self.value
                _strings = []
                for _value in _values:
                    try:
                        s = self.coercer.format(_value)
                    except types.AWTypeError:
                        pass
                    else:
                        if s is not None:
                            _strings.append(s)

                if _strings:
                    return '["{}"]'.format('", "'.join(_strings))
            else:
                try:
                    s = self.coercer.format(self.value)
                except types.AWTypeError:
                    log.debug('"as_string()" failed for value: "{!s}"'.format(
                            self.value))
                else:
                    if s is not None:
                        return s
            log.warning('"as_string()" returning empty string')
            return ''
        else:
            log.warning('Coercer unknown! "as_string()" returning empty string')
            return ''

    @classmethod
    def from_raw(cls, instance, raw_value):
        """
        Use this when the same 'ExtractedData' instance is re-used ..
        """
        # TODO: [hack] This is needed because the design is flawed. FIX!
        _instance_copy = copy.deepcopy(instance)
        try:
            return _instance_copy(raw_value)
        except types.AWTypeError as e:
            log.debug(str(e))
            return None

    @property
    def value(self):
        return self._value

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
        _maybe_string = self.as_string()
        if _maybe_string is not None and isinstance(_maybe_string, str):
            return _maybe_string
        else:
            return '{!s}'.format(self.value)

        # 3) Use the format method of the coercer ..
        # return self.coercer.format(self.value)

    def __repr__(self):
        _contents = str(self)
        if _contents and isinstance(_contents, str):
            _contents = textutils.truncate_text(_contents, 50)

        r = '<{!s}({!s}, mapped_fields={!s}, generic_field={!s})({})>'.format(
            self.__class__.__name__, self.coercer, self.field_map,
            self.generic_field, _contents
        )
        return r

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if (self.coercer == other.coercer
                and self.field_map == other.field_map
                and self.value == other.value):
            return True
        return False
