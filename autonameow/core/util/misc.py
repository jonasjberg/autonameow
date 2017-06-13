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

import itertools

import collections
import yaml

import logging as log

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
        return yaml.dump(obj, default_flow_style=False, width=80, indent=4)
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


def indent(text, amount=4, ch=' '):
    """
    Indents (multi-line) text a specified amount.

    Shift text right by the given "amount" (default 4) using the character
    "ch", which default to a space if left unspecified.

    Based on this post; https://stackoverflow.com/a/8348914/7802196

    Args:
        text: The text to indent. Single or multi-line.
        amount: Optional number of columns of indentation. Default: 4
        ch: Optional character to insert. Default: ' '

    Returns:
        An indented version of the given text.
    """
    padding = amount * ch
    return ''.join(padding + line for line in text.splitlines(True))


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

    Returns: A list suited for traversing nested dicts.
    """
    if not isinstance(query_string, str):
        raise InvalidQueryStringError('Query string must be of type "str"')
    else:
        query_string = query_string.strip()
    if not query_string:
        raise InvalidQueryStringError('Got empty query string')

    if '.' not in query_string:
        raise InvalidQueryStringError('Query string is too shallow (missing .)')
    else:
        stripped_period = str(query_string).replace('.', '')
        if not stripped_period.strip():
            raise InvalidQueryStringError('Invalid query string')

    # TODO: Implement tests and function!

    parts = query_string.split('.')
    return parts

    # TODO: Detect invalid parts


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
