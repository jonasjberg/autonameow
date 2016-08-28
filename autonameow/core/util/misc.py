# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging
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
