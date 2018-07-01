# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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

import os

from util import encoding as enc
from util import sanity


COMPOUND_SUFFIX_LAST_PARTS = [
    b'.7z',
    b'.bz2',
    b'.gz',
    b'.lz',
    b'.lzma',
    b'.lzo',
    b'.sig',
    b'.tbz',
    b'.tbz2',
    b'.tgz',
    b'.xz',
    b'.z',
    b'.zip',
    b'.zipx',
]


def split_basename(file_path):
    """
    Splits the basename of the specified path into two parts.

    Does almost the same thing as 'os.path.splitext', but handles
    "compound" file extensions, such as 'foo.tar.gz' differently.

      Input File Path:  'foo.tar'       Return Value:  ('foo', 'tar')
      Input File Path:  'foo.tar.gz'    Return Value:  ('foo', 'tar.gz')

    The "compound" extension is called the "suffix" and the remaining
    leftmost part (basename) is called the "prefix".

    Args:
        file_path (bytes): The path name to split as an "internal bytestring".

    Returns:
        The basename of the given path split into two parts,
        as a tuple of bytestrings.

    Raises:
        EncodingBoundaryViolation: Given arguments are not bytestrings.
    """
    sanity.check_internal_bytestring(file_path)

    prefix, suffix = os.path.splitext(os.path.basename(enc.syspath(file_path)))
    prefix = enc.bytestring_path(prefix)
    suffix = enc.bytestring_path(suffix)

    # Split "prefix" twice to make compound suffix out of the two extensions.
    if suffix.lower() in COMPOUND_SUFFIX_LAST_PARTS:
        suffix = os.path.splitext(prefix)[1] + suffix
        prefix = os.path.splitext(prefix)[0]

    suffix = suffix.lstrip(b'.')
    if suffix and suffix.strip():
        return prefix, suffix
    return prefix, None


def basename_suffix(file_path, make_lowercase=True):
    """
    Returns the "suffix" or file extension of the basename, for a given file.

    The file path can be of any type, relative, absolute, etc.

    NOTE: On non-standard behaviour;
          Compound file extensions like 'foo.tar.gz' will return the full
          "suffix", 'tar.gz' and not just the conventional extension 'gz'.

    Args:
        file_path (bytes): Path from which to get the full "suffix", I.E.
                           the file extension part of the basename, with special
                           treatment of compound file extensions.

        make_lowercase (bool): Whether to convert the suffix to lower case
                               before returning it. Defaults to True.

    Returns:
        The "suffix" or compound file extension for the given path as a
        "internal bytestring".  None is returned if it is not present.
    """
    _, suffix = split_basename(file_path)
    if suffix and make_lowercase:
        suffix = suffix.lower()

    return suffix if suffix else None


def basename_prefix(file_path):
    """
    Returns the basename _without_ any extension ("suffix"), for a given file.

    The file path can be of any type, relative, absolute, etc.
    Compound file extensions like ".tar.gz" are treated as a single "suffix"
    or extension, not to be included in the output.

    Args:
        file_path (bytes): Path to the file from which to get the "prefix",
                           I.E. the basename without the extension ("suffix").

    Returns:
        The basename of the specified path, without any extension ("suffix"),
        as a "internal bytestring".  None is returned if it is not present.
    """
    prefix, _ = split_basename(file_path)
    return prefix if prefix else None


def compare_basenames(basename_one, basename_two):
    """
    Compares to file basenames in the "internal byte string" format.

    Args:
        basename_one (bytes): The first basename to compare.
        basename_two (bytes): The second basename to compare.

    Returns (bool):
        True if the basenames are equal, otherwise False.

    Raises:
        ValueError: Any of the arguments is None.
        EncodingBoundaryViolation: Any argument is not of type bytes.
    """
    if None in (basename_one, basename_two):
        raise ValueError('Expected two non-None bytestrings')

    sanity.check_internal_bytestring(basename_one)
    sanity.check_internal_bytestring(basename_two)
    return bool(basename_one == basename_two)


def path_ancestry(path):
    """
    Return a list consisting of path's parent directory, its grandparent,
    and so on. For instance:

       >>> path_ancestry('/a/b/c')
       ['/', '/a', '/a/b']

    NOTE:  This function is based on code from the "beets" project.
           Source repo: https://github.com/beetbox/beets
           Source file: 'beets/util/__init__.py'
           Commit hash: b38f34b2c06255f1c51e8714c8af6962e297a3c5
    """
    out = list()

    last_path = None
    while path:
        path = os.path.dirname(path)

        if path == last_path:
            break
        last_path = path

        if path:
            out.insert(0, path)

    return out


def path_components(path):
    """
    Return a list of the path components for a given path. For instance:

       >>> path_components('/a/b/c')
       ['a', 'b', 'c']

    NOTE:  This function is based on code from the "beets" project.
           Source repo: https://github.com/beetbox/beets
           Source file: 'beets/util/__init__.py'
           Commit hash: b38f34b2c06255f1c51e8714c8af6962e297a3c5
    """
    out = list()

    ancestors = path_ancestry(path)
    for anc in ancestors:
        comp = os.path.basename(anc)
        if comp:
            out.append(comp)
        else:  # root
            out.append(anc)

    last = os.path.basename(path)
    if last:
        out.append(last)

    return out
