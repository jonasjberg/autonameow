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

from core import constants
from core.exceptions import InvalidDataSourceError


class Extractor(object):
    """
    Top-level abstract base class for all extractor classes.

    Includes common functionality and interfaces that must be implemented
    by inheriting extractor classes.
    """

    def __init__(self, source):
        """
        Creates a extractor instance acting on the specified source data.

        Args:
            source: Source of data from which to extract information.
        """
        self.source = source

    def query(self, field=None):
        """
        Queries the extractor for extracted data.

        Argument "field" is optional. All data is returned by default.

        Args:
            field: Optional refinement of the query.
                Expect format and type is defined by the extractor class.

        Returns:
            All data gathered by the extractor if no field is specified.
            Else the data matching the specified field.
        """
        raise NotImplementedError('Must be implemented by inheriting classes.')

    def __str__(self):
        return self.__class__.__name__


class ExtractedData(object):
    """
    Container for data gathered by extractors.
    """
    def __init__(self):
        self._data = {}

    def add(self, label, data):
        if not data:
            return
        if not label or label not in constants.VALID_DATA_SOURCES:
            raise InvalidDataSourceError('Invalid source: "{}"'.format(label))
        else:
            # TODO: Necessary to handle multiple adds to the same label?
            if label in self._data:
                t = self._data[label]
                self._data[label] = [t] + [data]
            else:
                self._data[label] = data

    def get(self, label):
        """
        Returns extracted data matching the specified label.

        Args:
            One of the strings defined in "constants.VALID_DATA_SOURCES".
        Returns:
            Extracted data associated with the given label, or False if the
            data does not exist.
        Raises:
            InvalidDataSourceError: The label is not a valid data source.
        """
        if not label or label not in constants.VALID_DATA_SOURCES:
            raise InvalidDataSourceError('Invalid label: "{}"'.format(label))

        return self._data.get(label, False)

    def __len__(self):
        def count_dict_recursive(dictionary, count):
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    count_dict_recursive(value, count)
                elif value:
                    if isinstance(value, list):
                        for v in value:
                            if v:
                                count += 1
                    else:
                        count += 1

            return count

        return count_dict_recursive(self._data, 0)