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

"""
Miscellaneous utility functions.
"""

import collections
import itertools
import logging as log

import yaml

from core.exceptions import InvalidQueryStringError


def dump(obj):
    """
    Returns a human-readable representation of "obj".

    Args:
        obj: The object to dump.

    Returns:
        A human-readable representation of "obj" in YAML-format.
    """
    try:
        return yaml.dump(obj, default_flow_style=False, width=120, indent=4)
    except TypeError as e:
        log.critical('Dump FAILED: ' + str(e))
        raise


def dump_to_list(obj, nested_level=0, output=None):
    spacing = '   '
    if not output:
        out = []
    else:
        out = output

    if type(obj) == dict:
        out.append(('%s{' % ((nested_level) * spacing)))
        for k, v in list(obj.items()):
            if hasattr(v, '__iter__'):
                out.append(('%s%s:' % ((nested_level + 1) * spacing, k)))
                dump_to_list(v, nested_level + 1, out)
            else:
                out.append(('%s%s: %s' % ((nested_level + 1) * spacing, k, v)))
        out.append(('%s}' % (nested_level * spacing)))
    elif type(obj) == list:
        out.append(('%s[' % ((nested_level) * spacing)))
        for v in obj:
            if hasattr(v, '__iter__'):
                dump_to_list(v, nested_level + 1, out)
            else:
                out.append(('%s%s' % ((nested_level + 1) * spacing, v)))
        out.append(('%s]' % ((nested_level) * spacing)))
    else:
        out.append(('%s%s' % (nested_level * spacing, obj)))

    return out


__counter_generator_function = itertools.count(0)


def unique_identifier():
    """
    Returns a (practically unique) identifier string.

    The numeric part of the identifier is incremented at each function call.

    Numbers are unique even after as much as 10^6 function calls, which I doubt
    will be used up during a single program invocation.

    Returns:
        A (pretty much unique) identifier text string.
    """
    n = next(__counter_generator_function)
    if n % 3 == 0:
        _prefix = 'M3'
    else:
        _prefix = 'ME'
    if n % 2 == 0:
        _postfix = 'OW'
    else:
        _postfix = '0W'
    return '{}{:03d}{}'.format(_prefix, n, _postfix)


def multiset_count(list_data):
    """
    Counts duplicate entries in a list and returns a dictionary of frequencies.

    keyed by entries,
    with the entry count as value.

    Args:
        list_data: A list of data to count.

    Returns:
        A dictionary with unique list entries as keys and the corresponding
        value is the frequency of that entry in the given "list_data".
    """
    if list_data is None:
        return None
    elif not list_data:
        return {}

    out = {}

    for entry in list_data:
        if entry in out:
            out[entry] += 1
        else:
            out[entry] = 1

    return out


def query_string_list(query_string):
    """
    Converts a "query string" to a list suited for traversing nested dicts.

    Example query string:  "metadata.exiftool.datetimeoriginal"
    Resulting output:      ['metadata', 'exiftool', 'datetimeoriginal']

    Args:
        query_string: The "query string" to convert.

    Returns: The components of the given "query string" as a list.
    """
    if not isinstance(query_string, str):
        raise InvalidQueryStringError('Query string must be of type "str"')
    else:
        query_string = query_string.strip()
    if not query_string:
        raise InvalidQueryStringError('Got empty query string')

    if '.' in query_string:
        # Remove any leading/trailing periods.
        if query_string.startswith('.'):
            query_string = query_string.lstrip('.')
        if query_string.endswith('.'):
            query_string = query_string.rstrip('.')

        # Collapse any repeating periods.
        while '..' in query_string:
            query_string = query_string.replace('..', '.')

        # Check if input is all periods.
        stripped_period = str(query_string).replace('.', '')
        if not stripped_period.strip():
            raise InvalidQueryStringError('Invalid query string')

    parts = query_string.split('.')
    return [p for p in parts if p is not None]


def flatten_dict(d, parent_key='', sep='.'):
    """
    Flattens a possibly nested dictionary by joining nested keys.

    Based on this post:  https://stackoverflow.com/a/6027615/7802196
    Example:
              INPUT = {
                  'contents': {
                      'mime_type': None,
                      'textual': {
                          'raw_text': None,
                      }
                  }
              }
              OUTPUT = {
                  'contents.mime_type': None,
                  'contents.textual.raw_text': None,
              }

    Note that if the low-level values are empty dictionaries or lists,
    they will be omitted from the output.

    Args:
        d: The dictionary to flatten.
        parent_key: Not used, required for recursion.
        sep: String or character to use as separator.

    Returns:
        A flattened dictionary with nested keys are joined by "sep".
    """
    if not isinstance(d, (dict, list)):
        raise TypeError

    items = []

    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k

        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep=sep).items())
        else:
            items.append((new_key, v))

    return dict(items)


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

    for key, value in dictionary.items():
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


def expand_query_string_data_dict(query_string_dict):
    """
    Performs the reverse operation of that of 'flatten_dict'.

    A dictionary with "query strings" as keys storing data in each value is
    expanded by splitting the query strings by periods and creating a
    nested dictionary.

    Args:
        query_string_dict: Dictionary keyed by "query strings".

    Returns:
        An "expanded" or "unflattened" version of the given dictionary.
    """
    if not query_string_dict or not isinstance(query_string_dict, dict):
        raise TypeError

    out = {}
    for key, value in query_string_dict.items():
        key_parts = key.split('.')
        nested_dict_set(out, key_parts, value)

    return out


def dict_lookup(dictionary, key, *list_of_keys):
    """
    Gets a value from the given dictionary by either a single key or a list
    of keys for retrieval from multiple nested dictionaries.

    Based on this post:  https://stackoverflow.com/a/11701539/7802196

    Args:
        dictionary: The dictionary from which to retrieve a value.
        key: Key to the value.
        *list_of_keys: Any number of keys for nested dictionaries.

    Returns:
        The dictionary value if present, otherwise None.
    """
    if list_of_keys:
        return dict_lookup(dictionary.get(key, {}), *list_of_keys)

    return dictionary.get(key)


def nested_dict_get(dictionary, list_of_keys):
    """
    Retrieves a value from a given nested dictionary structure.

    The structure is traversed by accessing each key in the given list of keys
    in order.

    Based on this post:  https://stackoverflow.com/a/37704379/7802196

    Args:
        dictionary: The dictionary structure to traverse.
        list_of_keys: List of keys to use during the traversal.

    Returns:
        The value in the nested structure, if successful.

    Raises:
        KeyError: Failed to retrieve any value with the given list of keys.
    """
    if not list_of_keys or not isinstance(list_of_keys, list):
        raise TypeError('Expected "list_of_keys" to be a list of strings')

    for k in list_of_keys:
        try:
            dictionary = dictionary[k]
        except TypeError:
            raise KeyError('Thing is not subscriptable (traversed too deep?)')
    return dictionary


def nested_dict_set(dictionary, list_of_keys, value):
    """
    Sets a value in a nested dictionary structure.

    The structure is traversed using the given list of keys and the destination
    dictionary is set to the given value, unless the traversal fails by
    attempting to overwrite an already existing value with a new dictionary
    entry.

    Note that the dictionary is modified IN PLACE.

    Based on this post:  https://stackoverflow.com/a/37704379/7802196

    Args:
        dictionary: The dictionary from which to retrieve a value.
        list_of_keys: List of keys to the value to set.
        value: The new value that will be set.
    """
    if not list_of_keys or not isinstance(list_of_keys, list):
        raise TypeError('Expected "list_of_keys" to be a list of strings')
    elif all(not k for k in list_of_keys):
        raise ValueError('Expected "list_of_keys" not to be all None/empty')

    for key in list_of_keys[:-1]:
        dictionary = dictionary.setdefault(key, {})

    try:
        dictionary[list_of_keys[-1]] = value
    except TypeError:
        raise KeyError('Caught TypeError (would have clobbered existing value)')
