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
            for j in range(len(data[0]) - i + 1):
                if j > len(substr) and all(data[0][i:i + j] in x for x in data):
                    substr = data[0][i:i + j]
    return substr


class FilePath(object):
    def __init__(self, path):
        self.path = os.path.abspath(path)
        self.basename = os.path.basename(self.path)
        self.basename_words = re.split('\W+|_', self.basename)
        self.new_path = None

    # def split_path_into_words(self):
    #     # This splits up a file name into a list.
    #     # http://stackoverflow.com/a/1059601
    #     words = re.split('\W+|_', self.path)
    #     return words


def simplify_path(list_of_paths):
    filepath_list = []
    longest_entry = None

    # Walk path, create list of FilePath objects from found files.
    for path in list_of_paths:
        for root, dirs, files in os.walk(path):
            for f in files:
                path = os.path.join(root, f)
                filepath_list.append(FilePath(path))

    filepath_list = sorted(filepath_list)

    set_of_words = set()
    for filepath in filepath_list:
        # Store the entry with the highest number of words
        if longest_entry is None:
            longest_entry = filepath
        else:
            if len(filepath.basename_words) > len(longest_entry.basename_words):
                longest_entry = filepath

        # Populate the set of unique words
        for word in filepath.basename_words:
            set_of_words.add(word)

    # Debug printing ..
    for filepath in filepath_list:
        if not filepath:
            continue

        print('')
        print('BASENAME : {}'.format(filepath.basename))
        print('WORDS    : {}'.format(filepath.basename_words))

    print('\nSet of words: ')
    print(set_of_words)

    for filepath in filepath_list:
        for i in range(0, len(filepath.basename_words)):
            if filepath.basename_words[i] == longest_entry.basename_words[i]:
                pass


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
        print('Running simplify_path ..')
        simplify_path(arg_list)
    else:
        print 'Got empty argument list. Exiting.'
        sys.exit()


if __name__ == '__main__':
    simplify_path_main(sys.argv[1:])
