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
import random
import sys

import itertools

import yaml


# def dump(obj, nested_level=0, output=sys.stdout):
#     # http://stackoverflow.com/a/21049038
#     spacing = '   '
#     if type(obj) == dict:
#         print(('%s{' % ((nested_level) * spacing)))
#         for k, v in list(obj.items()):
#             if hasattr(v, '__iter__'):
#                 print(('%s%s:' % ((nested_level + 1) * spacing, k)))
#                 dump(v, nested_level + 1, output)
#             else:
#                 print(('%s%s: %s' % ((nested_level + 1) * spacing, k, v)))
#         print(('%s}' % (nested_level * spacing)))
#     elif type(obj) == list:
#         print(('%s[' % ((nested_level) * spacing)))
#         for v in obj:
#             if hasattr(v, '__iter__'):
#                 dump(v, nested_level + 1, output)
#             else:
#                 print(('%s%s' % ((nested_level + 1) * spacing, v)))
#         print(('%s]' % ((nested_level) * spacing)))
#     else:
#         print(('%s%s' % (nested_level * spacing, obj)))


def dump(obj):
    return yaml.dump(obj, default_flow_style=False)


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



def unpack_dict(dt_list):
    # TODO: Finish/verify this. Not sure it is finished/correct or even needed.
    if type(dt_list) is dict:
        return dt_list
    elif type(dt_list) is not list:
        logging.debug('Got unexpected type: {}'.format(type(dt_list)))

    results = {}
    for entry in dt_list:
        if type(entry) is dict:
            if entry not in results:
                results[entry] = entry
        else:
            for content in entry:
                if type(content) is dict:
                    results.append(entry)

    return results


_counter_generator_function = itertools.count(0)


def unique_identifier():
    """
    Returns a (practically unique) identifier string.

    The numeric part of the identifier is incremented at each function call.

    Numbers are unique even after as much as 10^6 function calls, which I doubt
    will be used up during a single program invocation.

    Returns:
        A (pretty much unique) identifier text string.
    """
    n = next(_counter_generator_function)
    if n % 3 == 0:
        _prefix = 'M3'
    else:
        _prefix = 'ME'
    if n % 2 == 0:
        _postfix = 'OW'
    else:
        _postfix = '0W'
    return '{}{:03d}{}'.format(_prefix, n, _postfix)

