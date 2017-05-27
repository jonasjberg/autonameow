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


def dump(obj, nested_level=0, output=sys.stdout):
    # http://stackoverflow.com/a/21049038
    spacing = '   '
    if type(obj) == dict:
        print(('%s{' % ((nested_level) * spacing)))
        for k, v in list(obj.items()):
            if hasattr(v, '__iter__'):
                print(('%s%s:' % ((nested_level + 1) * spacing, k)))
                dump(v, nested_level + 1, output)
            else:
                print(('%s%s: %s' % ((nested_level + 1) * spacing, k, v)))
        print(('%s}' % (nested_level * spacing)))
    elif type(obj) == list:
        print(('%s[' % ((nested_level) * spacing)))
        for v in obj:
            if hasattr(v, '__iter__'):
                dump(v, nested_level + 1, output)
            else:
                print(('%s%s' % ((nested_level + 1) * spacing, v)))
        print(('%s]' % ((nested_level) * spacing)))
    else:
        print(('%s%s' % (nested_level * spacing, obj)))


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


def unique_identifier():
    """
    Generates a unique identifier string.
    The identifier consists of 8 random digits prefixed with "UUID".

        NOTE:  This is not a proper UUID as per RFC 4122.

    Returns:
        A identifier text on the form "UUID00000000" as a string.
    """
    def uuid_generator():
        # Max 24-bit value: 16777215
        seed = random.getrandbits(24)

        while True:
            yield 'UUID{:08d}'.format(seed)
            seed += 1

    unique_sequence = uuid_generator()
    return next(unique_sequence)