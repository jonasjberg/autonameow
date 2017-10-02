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

import collections
import itertools
import logging
import os
import shutil
import subprocess

try:
    import yaml
except ImportError:
    raise SystemExit(
        'Missing required module "yaml". '
        'Make sure "pyyaml" is available before running this program.'
    )

from core import constants as C
from core import types
from core.exceptions import InvalidMeowURIError
from core.util import sanity


log = logging.getLogger(__name__)


def dump(obj):
    """
    Returns a human-readable representation of "obj".

    Args:
        obj: The object to dump.

    Returns:
        A human-readable representation of "obj" in YAML-format.
    """
    try:
        return yaml.dump(obj, default_flow_style=False, width=120, indent=4)
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
        out.append('{}{{'.format(nested_level * spacing))
        for k, v in list(obj.items()):
            if hasattr(v, '__iter__'):
                out.append('{}{}:'.format((nested_level + 1) * spacing, k))
                dump_to_list(v, nested_level + 1, out)
            else:
                out.append('{}{}: {}'.format((nested_level + 1) * spacing, k, v))
        out.append('{}}}'.format(nested_level * spacing))
    elif type(obj) == list:
        out.append('{}['.format(nested_level * spacing))
        for v in obj:
            if hasattr(v, '__iter__'):
                dump_to_list(v, nested_level + 1, out)
            else:
                out.append('{}{}'.format((nested_level + 1) * spacing, v))
        out.append('{}]'.format(nested_level * spacing))
    else:
        out.append('{}{}'.format(nested_level * spacing, obj))

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


def meowuri_list(meowuri):
    """
    Converts a "meowURI" to a list suited for traversing nested dicts.

    Example meowURI:    'extractor.metadata.exiftool.createdate'
    Resulting output:   ['extractor', 'metadata', 'exiftool', 'createdate']

    Args:
        meowuri: The "meowURI" to convert.

    Returns: The components of the given "meowURI" as a list.
    """
    if not isinstance(meowuri, str):
        raise InvalidMeowURIError('meowURI must be of type "str"')
    else:
        meowuri = meowuri.strip()
    if not meowuri:
        raise InvalidMeowURIError('Got empty meowURI')

    if '.' in meowuri:
        # Remove any leading/trailing periods.
        if meowuri.startswith('.'):
            meowuri = meowuri.lstrip('.')
        if meowuri.endswith('.'):
            meowuri = meowuri.rstrip('.')

        # Collapse any repeating periods.
        while '..' in meowuri:
            meowuri = meowuri.replace('..', '.')

        # Check if input is all periods.
        stripped_period = str(meowuri).replace('.', '')
        if not stripped_period.strip():
            raise InvalidMeowURIError('Invalid meowURI')

    parts = meowuri.split('.')
    return [p for p in parts if p is not None]


def flatten_dict(d, parent_key='', sep='.'):
    """
    Flattens a possibly nested dictionary by joining nested keys.

    Based on this post:  https://stackoverflow.com/a/6027615/7802196
    Example:
              INPUT = {
                  'contents': {
                      'mime_type': None,
                      'textual': {
                          'text': {
                              'full: None,
                          }
                      }
                  }
              }
              OUTPUT = {
                  'contents.mime_type': None,
                  'contents.textual.text.full': None,
              }

    Note that if the low-level values are empty dictionaries or lists,
    they will be omitted from the output.

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

    for key, value in dictionary.items():
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


def expand_meowuri_data_dict(meowuri_dict):
    """
    Performs the reverse operation of that of 'flatten_dict'.

    A dictionary with "meowURIs" as keys storing data in each value is
    expanded by splitting the meowURIs by periods and creating a
    nested dictionary.

    Args:
        meowuri_dict: Dictionary keyed by "meowURIs".

    Returns:
        An "expanded" or "unflattened" version of the given dictionary.
    """
    if not meowuri_dict or not isinstance(meowuri_dict, dict):
        raise TypeError

    out = {}
    for key, value in meowuri_dict.items():
        key_parts = key.split('.')
        try:
            nested_dict_set(out, key_parts, value)
        except KeyError:
            log.error('Duplicate "meowURIs" would have clobbered existing!'
                      ' Key: "{!s}"  Value: {!s}'.format(key, value))

    return out


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


def eval_magic_glob(mime_to_match, glob_list):
    """
    Tests if a given MIME type string matches any of the specified globs.

    The MIME types consist of a "type" and a "subtype", separated by '/'.
    For instance; "image/jpg" or "application/pdf".

    Globs can substitute either one or both of "type" and "subtype" with an
    asterisk to ignore that part. Examples:

        mime_to_match         glob_list                 evaluates
        'image/jpg'           ['image/jpg']             True
        'image/png'           ['image/*']               True
        'application/pdf'     ['*/*']                   True
        'application/pdf'     ['image/*', '*/jpg']      False

    This function performs extra argument validation due to the fact that it is
    likely to be used by third party developers. It is also exposed to possibly
    malformed configuration entries.

    Args:
        mime_to_match: The MIME to match against the globs as a Unicode string.
        glob_list: A list of globs as Unicode strings.

    Returns:
        True if the MIME to match is valid and matches any of the globs.
        False if the MIME to match is valid but does not match any of the globs.
    Raises:
        TypeError: Got non-Unicode string arguments.
        ValueError: Argument "mime_to_match" is not on the form "foo/bar".
    """
    if not mime_to_match or not glob_list:
        return False
    if mime_to_match == C.MAGIC_TYPE_UNKNOWN:
        return False

    if not (isinstance(mime_to_match, str)):
        raise TypeError('Expected "mime_to_match" to be of type str')
    if '/' not in mime_to_match:
        raise ValueError('Expected "mime_to_match" to be on the form "foo/bar"')

    if not isinstance(glob_list, list):
        glob_list = [glob_list]

    log.debug(
        'Evaluating MIME. MimeToMatch: "{!s}" Globs: {!s}'.format(mime_to_match,
                                                                  glob_list)
    )
    mime_to_match_type, mime_to_match_subtype = mime_to_match.split('/')
    for glob in glob_list:
        sanity.check_internal_string(glob)

        if glob == mime_to_match:
            return True
        elif '*' in glob:
            try:
                glob_type, glob_subtype = glob.split('/')
            except ValueError:
                raise ValueError(
                    'Expected globs to be on the form "*/a", "a/*"'
                )
            if glob_type == '*' and glob_subtype == '*':
                # Matches everything.
                return True
            elif glob_type == '*' and glob_subtype == mime_to_match_subtype:
                # Matches any type. Tests subtype equality.
                return True
            elif glob_type == mime_to_match_type and glob_subtype == '*':
                # Checks type equality. Matches any subtype.
                return True
    return False


def is_executable(command):
    """
    Checks if the given command would be executable.

    Args:
        command: The command to test.

    Returns:
        True if the command would be executable, otherwise False.
    """
    return shutil.which(command) is not None


def contains_none(iterable):
    """
    Returns True if the given iterable is empty or contains a None item.
    """
    return not iterable or None in iterable


def filter_none(iterable):
    """
    Removes any None values from the given iterable and returns the result.
    """
    return [item for item in iterable if item is not None]


def process_id():
    return os.getpid()


def git_commit_hash():
    if not is_executable('git'):
        return None

    try:
        process = subprocess.Popen(
            ['git', 'rev-parse', '--short', 'HEAD'],
            shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
        )
        stdout, stderr = process.communicate()
    except (OSError, ValueError, TypeError, subprocess.SubprocessError):
        return None
    else:
        string = types.force_string(stdout).strip()
        return string if string else None
