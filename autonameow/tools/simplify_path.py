#!/usr/bin/env python
# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import os
import re
import sys


class FilePath(object):
    def __init__(self, path):
        self.path = path
        self.words = self.split_into_words()

    def split_into_words(self):
        # This splits up a file name into a list.
        # http://stackoverflow.com/a/1059601
        words = re.split('\W+|_', self.path)
        return words


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


def simplify_path(list_of_paths):
    filepath_list = []

    for path in list_of_paths:
        for root, dirs, files in os.walk(path):
            for file in files:
                file_abs_path = os.path.join(root, file)
                filepath_list.append(FilePath(file_abs_path))

    path_list = []
    entry_count_min = 0
    set_of_words = set()

    # This splits up a file name into a list.
    # http://stackoverflow.com/a/1059601
    # These are then added to the set of parts, which handles duplicates.
    for filepath in filepath_list:
        for word in filepath.words:
            set_of_words.add(word)

    # print long_substr(file_list)
    for entry in path_list:
        print entry

    # print 'Entry count (low): {}'.format(entry_count_min)

def simplify_path_main(argv):
    if len(argv) == 0:
        print "Need root path as argument"
        return None

    arg_list = []

    # Fill up argument list.
    for arg in argv:
        if not os.path.isdir(arg):
            print 'Need root path as argument. Skipping "{}"'.format(arg)
            continue
        else:
            arg_list.append(arg)

    # Run main routine on the argument list if it is not empty.
    if arg_list and arg_list is not None:
        simplify_path(arg_list)
    else:
        print 'Got empty argument list. Exiting.'
        sys.exit()





if __name__ == '__main__':
    simplify_path_main(sys.argv[1:])
