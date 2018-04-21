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

import os

from util import sanity
from util import encoding as enc


def split_basename(file_path):
    """
    Splits the basename of the specified path in two parts.

    Does almost the same thing as 'os.path.splitext', but handles "compound"
    file extensions, such as 'foo.tar.gz' differently.

      Input File Path:  'foo.tar'       Return Value:  ('foo', 'tar')
      Input File Path:  'foo.tar.gz'    Return Value:  ('foo', 'tar.gz')

    Args:
        file_path: The path name to split as an "internal bytestring".

    Returns:
        The basename of the given path split into two parts,
            as a tuple of bytestrings.
    Raises:
        EncodingBoundaryViolation: Got arguments of unexpected types.
    """
    sanity.check_internal_bytestring(file_path)

    base, ext = os.path.splitext(os.path.basename(enc.syspath(file_path)))
    base = enc.bytestring_path(base)
    ext = enc.bytestring_path(ext)

    # Split "base" twice to make compound suffix out of the two extensions.
    if ext.lower() in [b'.bz2', b'.gz', b'.lz', b'.lzma', b'.lzo', b'.xz',
                       b'.z', b'.sig']:
        ext = os.path.splitext(base)[1] + ext
        base = os.path.splitext(base)[0]

    ext = ext.lstrip(b'.')
    if ext and ext.strip():
        return base, ext
    return base, None


def basename_suffix(file_path, make_lowercase=True):
    """
    Returns the "suffix" or file extension of the basename, for a given file.

    The file path can be of any type, relative, absolute, etc.

    NOTE: On non-standard behaviour;
    Compound file extensions like 'foo.tar.gz' will return the (full "suffix")
    'tar.gz' and not just the conventional file extension 'gz'.

    Args:
        file_path: Path from which to get the full "suffix", I.E. the file
            extension part of the basename, with special treatment of
            compound file extensions, like 'repo_backup.git.tar.lzma'.

        make_lowercase: Whether to convert the suffix to lower case before
            returning it. Defaults to True.

    Returns:
        The "suffix" or compound file extension for the given path as a
        "internal bytestring".  None is returned if it is not present.
    """
    _, ext = split_basename(file_path)

    if ext and make_lowercase:
        ext = ext.lower()

    return ext


def basename_prefix(file_path):
    """
    Returns the basename _without_ any extension ("suffix"), for a given file.

    The file path can be of any type, relative, absolute, etc.
    Compound file extensions like ".tar.gz" are treated as a single "suffix"
    or extension, not to be included in the output.

    Args:
        file_path: Path to the file from which to get the "prefix", I.E.
            the basename without the extension ("suffix").

    Returns:
        The basename of the specified path, without any extension ("suffix"),
        as a "internal bytestring".  None is returned if it is not present.
    """
    base, _ = split_basename(file_path)
    return base if base else None


def compare_basenames(basename_one, basename_two):
    """
    Compares to file basenames in the "internal byte string" format.

    Args:
        basename_one: The first basename to compare as a bytestring.
        basename_two: The second basename to compare as a bytestring.

    Returns:
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
