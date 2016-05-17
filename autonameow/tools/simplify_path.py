#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import os
import re
import sys


def enumerate_paths(path):
    """Returns the path to all the files in a directory recursively"""


    path_collection = []

    for root, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            path_collection.append(full_path)

    return path_collection


def enumerate_files(path):
    """Returns all the files in a directory as a list"""

    file_collection = []

    for root, dirs, files in os.walk(path):
        for file in files:
            file_collection.append(file)

    return file_collection


def long_substr(data):
    substr = ''
    if len(data) > 1 and len(data[0]) > 0:
        for i in range(len(data[0])):
            for j in range(len(data[0])-i+1):
                if j > len(substr) and all(data[0][i:i+j] in x for x in data):
                    substr = data[0][i:i+j]
    return substr


def simplify_path(path):
    file_list = os.listdir(path)
    set_of_parts = set()

    path_list = []
    entry_count_min = 0

    # This splits up a file name into a list.
    # http://stackoverflow.com/a/1059601
    # These are then added to the set of parts, which handles duplicates.
    for file in file_list:
        parts = re.split("\W+|_", file)

        for part in parts:
            set_of_parts.add(part)

        path_list.append(parts)

        if len(parts) < entry_count_min:
            entry_count_min = len(parts)

    # print "Set of file name parts:"
    # print set_of_parts

    # print long_substr(file_list)
    for entry in path_list:
        print entry

    print 'Entry count (low): {}'.format(entry_count_min)





def simplify_path_main(argv):
    if len(argv) == 0:
        print "Need root path as argument"
        return None

    for path in argv:
        if not os.path.isdir(path):
            print 'Need root path as argument. Skipping "{}"'.format(path)
            continue

        simplify_path(path)





if __name__ == '__main__':
    simplify_path_main(sys.argv[1:])
