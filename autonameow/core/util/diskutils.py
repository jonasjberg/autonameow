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
import os
import re
import itertools
import logging
import tempfile

from core import util

log = logging.getLogger(__name__)

# Needed by 'sanitize_filename' for sanitizing filenames in restricted mode.
ACCENT_CHARS = dict(zip('ÂÃÄÀÁÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖŐØŒÙÚÛÜŰÝÞßàáâãäåæçèéêëìíîïðñòóôõöőøœùúûüűýþÿ',
                        itertools.chain('AAAAAA', ['AE'], 'CEEEEIIIIDNOOOOOOO', ['OE'], 'UUUUUYP', ['ss'],
                                        'aaaaaa', ['ae'], 'ceeeeiiiionooooooo', ['oe'], 'uuuuuypy')))


def sanitize_filename(s, restricted=False, is_id=False):
    """Sanitizes a string so it could be used as part of a filename.
    If restricted is set, use a stricter subset of allowed characters.
    Set is_id if this is not an arbitrary string, but an ID that should be kept
    if possible.

    NOTE:  This function was lifted as-is from the "youtube-dl" project.

           https://github.com/rg3/youtube-dl/blob/master/youtube_dl/utils.py
           Commit: b407d8533d3956a7c27ad42cbde9a877c36df72c
    """
    def replace_insane(char):
        if restricted and char in ACCENT_CHARS:
            return ACCENT_CHARS[char]
        if char == '?' or ord(char) < 32 or ord(char) == 127:
            return ''
        elif char == '"':
            return '' if restricted else '\''
        elif char == ':':
            return '_-' if restricted else ' -'
        elif char in '\\/|*<>':
            return '_'
        if restricted and (char in '!&\'()[]{}$;`^,#' or char.isspace()):
            return '_'
        if restricted and ord(char) > 127:
            return '_'
        return char

    # Handle timestamps
    s = re.sub(r'[0-9]+(?::[0-9]+)+', lambda m: m.group(0).replace(':', '_'), s)
    result = ''.join(map(replace_insane, s))
    if not is_id:
        while '__' in result:
            result = result.replace('__', '_')
        result = result.strip('_')
        # Common case of "Foreign band name - English song title"
        if restricted and result.startswith('-_'):
            result = result[2:]
        if result.startswith('-'):
            result = '_' + result[len('-'):]
        result = result.lstrip('.')
        if not result:
            result = '_'
    return result


def rename_file(source_path, new_basename):
    dest_base = util.syspath(new_basename)
    source = util.syspath(source_path)

    source = os.path.realpath(os.path.normpath(source))
    if not os.path.exists(source):
        raise FileNotFoundError('Source does not exist: "{!s}"'.format(
            util.displayable_path(source)
        ))

    dest_abspath = os.path.normpath(
        os.path.join(os.path.dirname(source), dest_base)
    )
    if os.path.exists(dest_abspath):
        raise FileExistsError('Destination exists: "{!s}"'.format(
            util.displayable_path(dest_abspath)
        ))

    log.debug('Renaming "{!s}" to "{!s}"'.format(
        util.displayable_path(source),
        util.displayable_path(dest_abspath))
    )
    try:
        os.rename(source, dest_abspath)
    except OSError:
        raise


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
    """
    assert(isinstance(file_path, bytes))

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


def file_basename(file_path):
    return util.syspath(os.path.basename(file_path))


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
    out = []

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
    out = []

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


def get_files(search_path, recurse=False):
    """
    Returns all files in the specified path as a list of strings.

    The specified search path is traversed non-recursively by default.
    If the keyword argument "recurse" is set to True, the search path is
    walked recursively.

        NOTE: Does not currently handle symlinks.

    Args:
        search_path: The path to collect files from as an "internal bytestring".
        recurse: Whether to traverse the path recursively or not.

    Returns:
        Absolute paths to files in the specified path, as a list of bytestrings.
    """
    # TODO: [TD0026] Follow symlinks? Add option for following symlinks?
    # NOTE(jonas): If one were to have "out" be a set instead of a list, some
    # information might get lost when unravelling symlinks. One might want to
    # rename a symbolic link and the file that this link points to in the same
    # run. Resolving the full ("real") paths of these two args might return two
    # identical paths, which would be merged into just one if stored in a set.

    if not search_path:
        raise FileNotFoundError
    if not os.path.isfile(search_path) and not os.path.isdir(search_path):
        raise FileNotFoundError

    out = []

    def traverse(path):
        assert(isinstance(path, bytes))

        if os.path.isfile(util.syspath(path)):
            out.append(path)

        elif os.path.isdir(util.syspath(path)):
            for entry in os.listdir(util.syspath(path)):
                entry_path = os.path.join(util.syspath(path),
                                          util.syspath(entry))
                entry_path = util.bytestring_path(entry_path)
                if os.path.isfile(util.syspath(entry_path)):
                    out.append(entry_path)
                elif recurse and os.path.isdir(util.syspath(entry_path)):
                    traverse(entry_path)

    traverse(search_path)

    return out


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
    if not search_path:
        raise FileNotFoundError
    if not os.path.isfile(search_path) and not os.path.isdir(search_path):
        raise FileNotFoundError

    if os.path.isfile(search_path):
        yield search_path
    elif os.path.isdir(search_path):
        for entry in os.listdir(search_path):
            entry_path = os.path.join(search_path, entry)

            if not os.path.isfile(entry_path) and not os.path.isdir(entry_path):
                raise FileNotFoundError
            elif os.path.isfile(entry_path):
                yield entry_path
            elif recurse and os.path.isdir(entry_path):
                for f in get_files_gen(entry_path, recurse=recurse):
                    yield f


def compare_basenames(basename_one, basename_two):
    """
    Compares to file basenames in the "internal byte string" format.

    Args:
        basename_one: The first basename to compare.
        basename_two: The second basename to compare.

    Returns:
        True if the basenames are equal, otherwise False.
    """
    if not basename_one or not basename_two:
        raise ValueError('Expected two non-empty arguments')
    if (not isinstance(basename_one, bytes) or
            not isinstance(basename_two, bytes)):
        raise TypeError('Expected arguments to be "internal" byte strings')

    if basename_one == basename_two:
        return True
    else:
        return False


def filter_paths(path_list, ignore_globs):
    if not ignore_globs:
        return path_list

    ignore_globs = [util.bytestring_path(i) for i in ignore_globs]

    remain = []
    for path in path_list:
        skip = False
        for pattern in ignore_globs:
            if fnmatch.fnmatch(path, pattern):
                skip = True
                log.info(
                    'Ignored path: "{!s}"'.format(util.displayable_path(path))
                )
                break
        if skip:
            continue

        remain.append(path)

    return remain


def normpaths_from_opts(path_list, ignore_globs, recurse):
    file_list = set()

    for path in path_list:
        if not path:
            continue

        # Path name encoding boundary. Convert to internal format.
        path = util.normpath(path)
        try:
            found_files = get_files(path, recurse)
        except FileNotFoundError:
            log.error('File(s) not found: "{}"'.format(
                util.displayable_path(path))
            )
        else:
            for f in filter_paths(found_files, ignore_globs):
                file_list.add(f)

    return list(file_list)

