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

"""
Miscellaneous utility functions.
"""

__all__ = [
    'count_dict_recursive',
    'flatten_sequence_type',
]


def flatten_sequence_type(container):
    """
    Flattens arbitrarily nested lists or tuples of tuples and/or lists.

    Args:
        container: List or tuple of lists and/or tuples.
                   Other types are returned as-is.

    Returns:
        A flat sequence of the same type as the given outermost container.
        If the given value is not a list or tuple, it is returned as-is.
    """
    if not isinstance(container, (list, tuple)):
        return container

    container_type = type(container)

    def _generate_flattened(_container):
        for element in _container:
            if isinstance(element, (list, tuple)):
                for subelement in _generate_flattened(element):
                    yield subelement
            else:
                yield element

    return container_type(_generate_flattened(container))


def count_dict_recursive(dictionary, count=0):
    """
    Counts non-"empty" items in a nested dictionary structure.

    The dictionaries are traversed recursively and items not None, empty
    or False are summed and returned.

    Args:
        dictionary: The dictionary structure in which to count items.
        count: Required to keep track of the count during recursion.

    Returns:
        The number of non-"empty" items contained in the given dictionary.
    """
    if not dictionary:
        return 0
    if not isinstance(dictionary, dict):
        raise TypeError('Argument "dictionary" must be of type dict')

    for value in dictionary.values():
        if isinstance(value, dict):
            count += count_dict_recursive(value, count)
        elif value:
            if isinstance(value, list):
                for v in value:
                    if v:
                        count += 1
            else:
                count += 1

    return count
