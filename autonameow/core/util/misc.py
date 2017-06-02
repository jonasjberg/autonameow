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

import itertools

import yaml


def dump(obj):
    """
    Returns a human-readable representation of "obj".

    Args:
        obj: The object to dump.

    Returns:
        A human-readable representation of "obj" in YAML-format.
    """
    return yaml.dump(obj, default_flow_style=False, width=80, indent=4)


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
