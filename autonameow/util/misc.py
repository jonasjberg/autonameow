# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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
import logging
import os
import shutil
import subprocess

from core import constants as C

__all__ = [
    'count_dict_recursive',
    'flatten_sequence_type',
    'git_commit_hash',
    'is_executable',
    'nested_dict_get',
    'nested_dict_set',
    'process_id',
]


log = logging.getLogger(__name__)


__counter_generator_function = itertools.count(0)


def flatten_sequence_type(container):
    """
    Flattens arbitrarily nested lists or tuples of tuples and/or lists.

    Args:
        container: List or tuple of lists and/or tuples.
                   Other types are returned as-is.

    Returns:
        A flat sequence of the same type as the given outermost container.
        If the given value is not a list or tuple, it is returned as-is.
    """
    if not isinstance(container, (list, tuple)):
        return container

    container_type = type(container)

    def _generate_flattened(_container):
        for element in _container:
            if isinstance(element, (list, tuple)):
                for subelement in _generate_flattened(element):
                    yield subelement
            else:
                yield element

    return container_type(_generate_flattened(container))


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

    for value in dictionary.values():
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

    The list of keys can not contain any None or whitespace-only items.

    Note that the dictionary is modified IN PLACE.

    Based on this post:  https://stackoverflow.com/a/37704379/7802196

    Args:
        dictionary: The dictionary from which to retrieve a value.
        list_of_keys: List of keys to the value to set, as any hashable type.
        value: The new value that will be set in the given dictionary.
    Raises:
        TypeError: Arg 'list_of_keys' evaluates None or isn't a list.
        ValueError: Arg 'list_of_keys' contains None or whitespace-only string.
        KeyError: Existing value would have been clobbered.
    """
    if not list_of_keys or not isinstance(list_of_keys, list):
        raise TypeError('Expected "list_of_keys" to be a list of strings')

    if (None in list_of_keys or
            any(k.strip() == '' for k in list_of_keys if isinstance(k, str))):
        raise ValueError(
            'Expected "list_of_keys" to not contain any None/"empty" items'
        )

    for key in list_of_keys[:-1]:
        dictionary = dictionary.setdefault(key, {})

    try:
        dictionary[list_of_keys[-1]] = value
    except TypeError:
        # TODO: Add keyword-argument to allow overwriting any existing.
        # This happens when the dictionary contains a non-dict item where one
        # of the keys would go. For example;
        #
        #    example_dict = {'a': 2,
        #                    'b': {'c': 4,
        #                          'foo': 6}})
        #
        # Calling "nested_dict_set(example_dict, ['a', 'foo'], 1])" would
        # fail because 'a' stores the integer "2" where we would like to
        # create the new dict;  "{'foo': 6}"
        raise KeyError('Caught TypeError (would have clobbered existing value)')


def is_executable(command):
    """
    Checks if the given command would be executable.

    Args:
        command: The command to test.

    Returns:
        True if the command would be executable, otherwise False.
    """
    return shutil.which(command) is not None


def process_id():
    return os.getpid()


def git_commit_hash():
    if not is_executable('git'):
        return None

    _old_pwd = os.path.curdir
    try:
        os.chdir(C.AUTONAMEOW_SRCROOT_DIR)
        process = subprocess.Popen(
            ['git', 'rev-parse', '--short', 'HEAD'],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, _ = process.communicate()
    except (OSError, ValueError, TypeError, subprocess.SubprocessError):
        return None
    else:
        # NOTE(jonas): git returns 128 for the "fatal: Not a git repository.."
        # error. Substring matching is redundant but probably won't hurt either.
        if process.returncode == 0:
            from util import coercers
            str_stdout = coercers.force_string(stdout).strip()
            if str_stdout and 'fatal: Not a git repository' not in str_stdout:
                return str_stdout
        return None
    finally:
        os.chdir(_old_pwd)
