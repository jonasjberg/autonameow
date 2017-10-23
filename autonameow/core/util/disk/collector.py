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

from core import util
from core.util import sanity


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

    if not (os.path.isfile(util.enc.syspath(search_path))
            or os.path.isdir(util.enc.syspath(search_path))):
        raise FileNotFoundError

    if os.path.isfile(util.enc.syspath(search_path)):
        sanity.check_internal_bytestring(search_path)
        yield search_path
    elif os.path.isdir(util.enc.syspath(search_path)):
        try:
            _dir_listing = os.listdir(util.enc.syspath(search_path))
        except PermissionError as e:
            log.warning(str(e))
            pass
        else:
            for entry in _dir_listing:
                entry_path = os.path.join(util.enc.syspath(search_path),
                                          util.enc.syspath(entry))
                if not os.path.exists(util.enc.syspath(entry_path)):
                    raise FileNotFoundError

                if os.path.isfile(entry_path):
                    sanity.check_internal_bytestring(entry_path)
                    yield entry_path
                elif recurse and os.path.isdir(entry_path):
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
                util.enc.bytestring_path(i) for i in ignore_globs
            ]
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
            path = util.enc.normpath(path)
            try:
                _files = get_files_gen(path, self.recurse)
            except FileNotFoundError:
                log.error('File(s) not found: "{}"'.format(
                    util.enc.displayable_path(path))
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
                        util.enc.displayable_path(path), pattern)
                    )
                    return None
            return path

        try:
            return [p for p in path_list if _no_match(p, self.ignore_globs)]
        except FileNotFoundError:
            return []


def normpaths_from_opts(path_list, ignore_globs, recurse):
    pc = PathCollector(ignore_globs, recurse)
    return pc.get_paths(path_list)
