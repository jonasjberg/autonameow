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

import logging


# Undefined or invalid "source" --- extractor/analyzer/plugin class that
# produced the data.
UNKNOWN_SOURCE = '(unknown source)'


log = logging.getLogger(__name__)


# TODO: [TD0119] Separate adding contextual information from coercion.
class MetaInfo(object):
    """
    Instances of this class provides extra information to fields produced
    by data sources.

    Sources can specify which (if any) name template fields that an item
    should be associated with.  For instance, date/time-information could be
    used to populate the 'datetime'/'date' name template fields.
    """
    def __init__(self, multivalued=None, mapped_fields=None,
                 generic_field=None, source=None):
        """
        Args:
            multivalued: Whether a file could produce many instances of this
                         data. Note that the data itself could also be
                         multivalued, which would result in lists of lists.
            mapped_fields: List of "WeightedMappings" to namebuilder fields.
            generic_field: Optional subclass of 'GenericField'.
            source: Optional class instance that produced the value.
        """
        self._source = UNKNOWN_SOURCE
        self._multivalued = None

        if mapped_fields is not None:
            self.field_map = mapped_fields
        else:
            self.field_map = []

        if generic_field is not None:
            self.generic_field = generic_field
        else:
            self.generic_field = None

        self.source = source
        self.multivalued = multivalued

    @property
    def multivalued(self):
        return self._multivalued

    @multivalued.setter
    def multivalued(self, multivalued):
        if multivalued is not None:
            self._multivalued = bool(multivalued)
        else:
            self._multivalued = False

    @property
    def source(self):
        return self._source or UNKNOWN_SOURCE

    @source.setter
    def source(self, new_source):
        if new_source is not None:
            self._source = new_source
        else:
            self._source = UNKNOWN_SOURCE

    def maps_field(self, field):
        for mapping in self.field_map:
            if field == mapping.field:
                return True
        return False

    def __str__(self):
        return self.__class__.__name__

    def __repr__(self):
        s = '<{!s}(source={!s}, mapped_fields={!s}, generic_field={!s})>'.format(
            self.__class__.__name__, self.source, self.field_map,
            self.generic_field,
        )
        return s

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False

        return bool(
            self.field_map == other.field_map and
            self.source == other.source and
            self.generic_field == other.generic_field
        )
