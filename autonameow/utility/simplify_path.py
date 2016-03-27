#!/usr/bin/env python

import os

import sys


def enumerate_paths(path):
    """Returns the path to all the files in a directory recursively"""


    path_collection = []

    for root, dirs, files in os.walk(path):
        for file in files:
            full_path = os.path.join(root, file)
            path_collection.append(full_path)

    return path_collection


def simplify_path():
    test = enumerate_paths(sys.argv[1])

    for entry in test:
        print str(entry)


if __name__ == '__main__':
    simplify_path()
