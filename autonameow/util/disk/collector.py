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

import fnmatch
import logging

from util import encoding as enc
from util import (
    disk,
    sanity
)


log = logging.getLogger(__name__)


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

    if not disk.isfile(search_path) and not disk.isdir(search_path):
        dp = enc.displayable_path(search_path)
        raise FileNotFoundError('File or path not found: "{!s}"'.format(dp))

    if disk.isfile(search_path):
        sanity.check_internal_bytestring(search_path)
        yield search_path
    elif disk.isdir(search_path):
        try:
            _dir_listing = disk.listdir(search_path)
        except PermissionError as e:
            log.warning(str(e))
        else:
            for entry in _dir_listing:
                entry_path = disk.joinpaths(search_path, entry)
                if not disk.exists(entry_path):
                    raise FileNotFoundError

                if disk.isfile(entry_path):
                    sanity.check_internal_bytestring(entry_path)
                    yield entry_path
                elif recurse and disk.isdir(entry_path):
                    for f in get_files_gen(entry_path, recurse=recurse):
                        sanity.check_internal_bytestring(f)
                        yield f


class PathCollector(object):
    def __init__(self, ignore_globs=None, recurse=False):
        if ignore_globs:
            if not isinstance(ignore_globs, (list, frozenset)):
                ignore_globs = [ignore_globs]

            # Convert globs to internal format.
            self.ignore_globs = [
                enc.bytestring_path(i) for i in ignore_globs
            ]
        else:
            self.ignore_globs = []

        self.recurse = bool(recurse)

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
            path = enc.normpath(path)
            try:
                files = list(get_files_gen(path, self.recurse))
            except FileNotFoundError:
                log.error('File(s) not found: "{}"'.format(
                    enc.displayable_path(path)))
                continue

            for f in self.filter_paths(files):
                file_list.add(f)

        return sorted(list(file_list))

    def filter_paths(self, path_list):
        if not self.ignore_globs:
            return path_list

        return [p for p in path_list
                if not path_matches_any_glob(p, self.ignore_globs)]


def path_matches_any_glob(path, globs):
    return any(fnmatch.fnmatch(path, glob) for glob in globs)


def normpaths_from_opts(path_list, ignore_globs, recurse):
    pc = PathCollector(ignore_globs, recurse)
    return pc.get_paths(path_list)
