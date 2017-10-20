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

import fnmatch
import logging
import os

from core import (
    exceptions,
    util
)
from core.util import sanity


log = logging.getLogger(__name__)


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

    base, ext = os.path.splitext(os.path.basename(util.syspath(file_path)))
    base = util.bytestring_path(base)
    ext = util.bytestring_path(ext)

    # Split "base" twice to make compound suffix out of the two extensions.
    if ext.lower() in [b'.bz2', b'.gz', b'.lz', b'.lzma', b'.lzo', b'.xz',
                       b'.z']:
        ext = os.path.splitext(base)[1] + ext
        base = os.path.splitext(base)[0]

    ext = ext.lstrip(b'.')
    if ext and ext.strip():
        return base, ext
    else:
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


def get_files_gen(search_path, recurse=False):
    """
    Returns all files in the specified path as a list of strings.

    The specified search path is traversed non-recursively by default.
    If the keyword argument "recurse" is set to True, the search path is
    walked recursively.

        NOTE: Does not currently handle symlinks.

    Args:
        search_path: The path from which to collect files.
        recurse: Whether to traverse the path recursively or not.

    Returns:
        Absolute paths to files in the specified path, as a generator object.
    """
    # TODO: [TD0026] Follow symlinks? Add option for following symlinks?
    # NOTE(jonas): If one were to have "out" be a set instead of a list, some
    # information might get lost when unravelling symlinks. One might want to
    # rename a symbolic link and the file that this link points to in the same
    # run. Resolving the full ("real") paths of these two args might return two
    # identical paths, which would be merged into just one if stored in a set.

    if not search_path:
        raise FileNotFoundError
    if not search_path.strip():
        raise FileNotFoundError

    sanity.check_internal_bytestring(search_path)

    if not (os.path.isfile(util.syspath(search_path))
            or os.path.isdir(util.syspath(search_path))):
        raise FileNotFoundError

    if os.path.isfile(util.syspath(search_path)):
        sanity.check_internal_bytestring(search_path)
        yield search_path
    elif os.path.isdir(util.syspath(search_path)):
        try:
            _dir_listing = os.listdir(util.syspath(search_path))
        except PermissionError as e:
            log.warning(str(e))
            pass
        else:
            for entry in _dir_listing:
                entry_path = os.path.join(util.syspath(search_path),
                                          util.syspath(entry))
                if not os.path.exists(util.syspath(entry_path)):
                    raise FileNotFoundError

                if os.path.isfile(entry_path):
                    sanity.check_internal_bytestring(entry_path)
                    yield entry_path
                elif recurse and os.path.isdir(entry_path):
                    for f in get_files_gen(entry_path, recurse=recurse):
                        sanity.check_internal_bytestring(f)
                        yield f


def normpaths_from_opts(path_list, ignore_globs, recurse):
    pc = PathCollector(ignore_globs, recurse)
    return pc.get_paths(path_list)


class PathCollector(object):
    def __init__(self, ignore_globs=None, recurse=False):
        if ignore_globs:
            if not isinstance(ignore_globs, (list, frozenset)):
                ignore_globs = [ignore_globs]

            # Convert globs to internal format.
            self.ignore_globs = [util.bytestring_path(i) for i in ignore_globs]
        else:
            self.ignore_globs = []

        self.recurse = recurse

    def get_paths(self, path_list):
        if not path_list:
            return []
        if not isinstance(path_list, list):
            path_list = [path_list]

        file_list = set()

        for path in path_list:
            if not path or not path.strip():
                continue

            # Path name encoding boundary. Convert to internal format.
            path = util.normpath(path)
            try:
                _files = get_files_gen(path, self.recurse)
            except FileNotFoundError:
                log.error('File(s) not found: "{}"'.format(
                    util.displayable_path(path))
                )
            else:
                for f in self.filter_paths(_files):
                    file_list.add(f)

        return list(file_list)

    def filter_paths(self, path_list):
        if not self.ignore_globs:
            return path_list

        def _no_match(path, globs):
            for pattern in globs:
                if fnmatch.fnmatch(path, pattern):
                    log.info('Ignored path: "{!s}" (Glob: "{!s}")'.format(
                        util.displayable_path(path), pattern)
                    )
                    return None
            return path

        try:
            return [p for p in path_list if _no_match(p, self.ignore_globs)]
        except FileNotFoundError:
            return []


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
        path: The path to the file to test.
        permissions: The required permissions as a Unicode string
                             containing any of characters 'r', 'w' and 'x'.

    Returns:
        True if the given path has the given permissions, else False.
    """
    if not isinstance(permissions, str):
        raise TypeError('Expected "permissions" to be a Unicode string')
    if not isinstance(path, bytes):
        raise TypeError('Expected "path" to be a bytestring path')

    if not permissions.strip():
        return True

    perms = permissions.lower()
    for char in CHAR_PERMISSION_LOOKUP.keys():
        if char in perms:
            try:
                ok = os.access(util.syspath(path), CHAR_PERMISSION_LOOKUP[char])
            except OSError:
                return False
            else:
                if not ok:
                    return False

    return True


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
        FilesystemError: The path could not be removed, or the path does not
                         exist and "ignore_missing" is False.
        ValueError: Argument "path" is empty or only whitespace.
    """
    sanity.check_internal_bytestring(path)
    if not path or not path.strip():
        raise ValueError('Argument "path" is empty or only whitespace')

    p = util.syspath(path)
    if ignore_missing and not os.path.exists(p):
        return

    try:
        os.remove(util.syspath(p))
    except OSError as e:
        raise exceptions.FilesystemError(e)


def exists(path):
    try:
        return os.path.exists(util.syspath(path))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)
