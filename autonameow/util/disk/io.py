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

import logging
import os
import tempfile

from core import exceptions
from util import sanity
from util import encoding as enc

__all__ = [
    'delete',
    'dirname',
    'exists',
    'file_basename',
    'file_bytesize',
    'has_permissions',
    'isabs',
    'isdir',
    'isfile',
    'islink',
    'listdir',
    'joinpaths',
    'makedirs',
    'rename_file',
    'rmdir',
    'tempdir'
]


log = logging.getLogger(__name__)


def rename_file(source_path, new_basename):
    sanity.check_internal_bytestring(source_path)
    sanity.check_internal_bytestring(new_basename)
    assert isabs(source_path), (
        'Expected source path to be a full absolute path. '
        'Got "{!s}"'.format(enc.displayable_path(source_path))
    )

    _dp_source = enc.displayable_path(source_path)
    if not exists(source_path):
        raise FileNotFoundError(
            'Source path does not exist: "{!s}"'.format(_dp_source)
        )

    dest_path = joinpaths(dirname(source_path), new_basename)
    _dp_dest = enc.displayable_path(dest_path)
    if exists(dest_path):
        raise FileExistsError(
            'Destination exists: "{!s}"'.format(_dp_dest)
        )

    log.debug('Renaming "{!s}" to "{!s}"'.format(_dp_source, _dp_dest))
    try:
        os.rename(enc.syspath(source_path), enc.syspath(dest_path))
    except OSError:
        raise


def dirname(path):
    try:
        return os.path.dirname(enc.syspath(path))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)


def exists(path):
    try:
        return os.path.exists(enc.syspath(path))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)


def isabs(path):
    try:
        return os.path.isabs(enc.syspath(path))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)


def isdir(path):
    try:
        return os.path.isdir(enc.syspath(path))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)


def isfile(path):
    try:
        return os.path.isfile(enc.syspath(path))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)


def islink(path):
    try:
        return os.path.islink(enc.syspath(path))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)


def joinpaths(*paths):
    syspath_encoded_paths = [enc.syspath(p) for p in paths if p]
    try:
        return os.path.normpath(os.path.join(*syspath_encoded_paths))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)


def listdir(path):
    try:
        return os.listdir(enc.syspath(path))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)


def tempdir():
    """
    Creates and returns a temporary directory.

    Returns:
        The path to a new temporary directory, as an "internal" bytestring.
    Raises:
        FilesystemError: The directory could not be created.
    """
    try:
        return enc.normpath(tempfile.mkdtemp())
    except OSError as e:
        raise exceptions.FilesystemError(e)


def makedirs(path):
    if not isinstance(path, bytes):
        raise TypeError('Expected "path" to be a bytestring path')
    if not path or not path.strip():
        raise ValueError('Got empty argument "path"')

    try:
        os.makedirs(enc.syspath(path))
    except (OSError, ValueError, TypeError) as e:
        raise exceptions.FilesystemError(e)


def delete(path, ignore_missing=False):
    """
    Deletes the file at "path".

    Args:
        path: The path to delete as an "internal bytestring".
        ignore_missing: Controls whether to ignore non-existent paths.
                        False: Non-existent paths raises 'FilesystemError'.
                        True: Non-existent paths are silently ignored.

    Raises:
        EncodingBoundaryViolation: Argument "path" is not of type 'bytes'.
        FilesystemError: The path could not be removed; the path does not
                         exist and "ignore_missing" is False or the path
                         is a directory.
        ValueError: Argument "path" is empty or only whitespace.
    """
    sanity.check_internal_bytestring(path)
    if not path or not path.strip():
        raise ValueError('Argument "path" is empty or only whitespace')

    if ignore_missing and not exists(path):
        return

    try:
        os.remove(enc.syspath(path))
    except OSError as e:
        raise exceptions.FilesystemError(e)


def rmdir(path, ignore_missing=False):
    """
    Deletes the directory at "path".

    Args:
        path: The path to delete as an "internal bytestring".
        ignore_missing: Controls whether to ignore non-existent paths.
                        False: Non-existent paths raises 'FilesystemError'.
                        True: Non-existent paths are silently ignored.

    Raises:
        EncodingBoundaryViolation: Argument "path" is not of type 'bytes'.
        FilesystemError: The path could not be removed, or the path does not
                         exist and "ignore_missing" is False.
    """
    sanity.check_internal_bytestring(path)

    if ignore_missing and not exists(path):
        return

    try:
        os.rmdir(enc.syspath(path))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)


def file_basename(file_path):
    _basename = os.path.basename(enc.syspath(file_path))
    return enc.bytestring_path(_basename)


CHAR_PERMISSION_LOOKUP = {
    'r': os.R_OK,
    'w': os.W_OK,
    'x': os.X_OK
}


def has_permissions(path, permissions):
    """
    Tests if a path has the specified permissions.

    The required permissions should be given as a single Unicode string.
    Examples:
                      Required      Required Permissions
                     Permissions    READ  WRITE  EXECUTE

                         'r'         X      -       -
                         'w'         -      X       -
                         'x'         -      -       X
                         'RW'        X      X       -
                         'WwxX'      -      X       X

    Args:
        path: Path to the file to test as a Unicode string or bytes.
        permissions: The required permissions as a Unicode string
                             containing any of characters 'r', 'w' and 'x'.

    Returns:
        True if the given path has the given permissions, else False.
    """
    if not isinstance(permissions, str):
        raise TypeError('Expected "permissions" to be a Unicode string')
    if not isinstance(path, (bytes, str)):
        raise TypeError('Expected "path" to be a string type')

    if not permissions.strip():
        return True

    perms = permissions.lower()
    for char in CHAR_PERMISSION_LOOKUP.keys():
        if char in perms:
            try:
                ok = os.access(enc.syspath(path),
                               CHAR_PERMISSION_LOOKUP[char])
            except OSError:
                return False
            else:
                if not ok:
                    return False

    return True


def file_bytesize(path):
    """
    Returns the size of the file at "path" in bytes.

    Args:
        path: The path to the file of interest.

    Returns:
        The size of the file at the given path in bytes, as an integer.

    Raises:
        FilesystemError: The file size could not be ascertained for any reason.
    """
    try:
        return os.path.getsize(enc.syspath(path))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)
