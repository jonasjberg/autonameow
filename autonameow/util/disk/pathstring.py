# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2019 Jonas Sjöberg <autonameow@jonasjberg.com>
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


COMPOUND_SUFFIX_TAILS = frozenset([
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
])

EMPTY_FILENAME_PART = b''


def split_basename(filepath):
    """
    Splits the basename of the specified path into two parts.

    Does almost the same thing as 'os.path.splitext', but handles
    "compound" file extensions, such as 'foo.tar.gz' differently.

      Input File Path:  'foo.tar'       Return Value:  ('foo', 'tar')
      Input File Path:  'foo.tar.gz'    Return Value:  ('foo', 'tar.gz')

    The "compound" extension is called the "suffix" and the remaining
    leftmost part (basename) is called the "prefix".

    Args:
        filepath (bytes): The path name to split as an "internal bytestring".

    Returns:
        The basename of the given path split into two parts, as a tuple of
        bytestrings. Empty parts are substituted with EMPTY_FILENAME_PART.
    """
    assert isinstance(filepath, bytes)

    prefix, suffix = os.path.splitext(os.path.basename(enc.syspath(filepath)))
    prefix = enc.bytestring_path(prefix)
    suffix = enc.bytestring_path(suffix)

    # Split "prefix" twice to make compound suffix out of the two extensions.
    if suffix.lower() in COMPOUND_SUFFIX_TAILS:
        suffix = os.path.splitext(prefix)[1] + suffix
        prefix = os.path.splitext(prefix)[0]

    suffix = suffix.lstrip(b'.').strip()
    if suffix:
        return prefix, suffix

    return prefix, EMPTY_FILENAME_PART


def basename_suffix(filepath, make_lowercase=True):
    """
    Returns the "suffix" or file extension of the basename, for a given file.

    The file path can be of any type, relative, absolute, etc.

    NOTE: On non-standard behaviour;
          Compound file extensions like 'foo.tar.gz' will return the full
          "suffix", 'tar.gz' and not just the conventional extension 'gz'.

    Args:
        filepath (bytes): Path from which to get the full "suffix", I.E.
                          the file extension part of the basename, with special
                          treatment of compound file extensions.

        make_lowercase (bool): Whether to convert the suffix to lower case
                               before returning it. Defaults to True.

    Returns:
        The "suffix" or compound file extension for the given path as a
        "internal bytestring" or EMPTY_FILENAME_PART if it is not present.
    """
    _, suffix = split_basename(filepath)
    if suffix and make_lowercase:
        suffix = suffix.lower()

    return suffix if suffix else EMPTY_FILENAME_PART


def basename_prefix(filepath):
    """
    Returns the basename _without_ any extension ("suffix"), for a given file.

    The file path can be of any type, relative, absolute, etc.
    Compound file extensions like ".tar.gz" are treated as a single "suffix"
    or extension, not to be included in the output.

    Args:
        filepath (bytes): Path to the file from which to get the "prefix",
                          I.E. the basename without the extension ("suffix").

    Returns:
        The basename of the specified path, without any extension ("suffix"),
        as a "internal bytestring" or EMPTY_FILENAME_PART if it is not present.
    """
    prefix, _ = split_basename(filepath)
    return prefix if prefix else EMPTY_FILENAME_PART


def compare_basenames(basename_one, basename_two):
    """
    Compares to file basenames in the "internal byte string" format.

    Args:
        basename_one (bytes): The first basename to compare.
        basename_two (bytes): The second basename to compare.

    Returns (bool):
        True if the basenames are equal, otherwise False.
    """
    assert all(x is not None and isinstance(x, bytes)
               for x in (basename_one, basename_two))
    return bool(basename_one == basename_two)
