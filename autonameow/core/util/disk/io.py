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

import os
import tempfile

from core import (
    exceptions,
    util
)


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


def exists(path):
    try:
        return os.path.exists(util.syspath(path))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)


def isdir(path):
    try:
        return os.path.isdir(util.syspath(path))
    except (OSError, TypeError, ValueError) as e:
        raise exceptions.FilesystemError(e)


def isfile(path):
    try:
        return os.path.isfile(util.syspath(path))
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
        return util.normpath(tempfile.mkdtemp())
    except OSError as e:
        raise exceptions.FilesystemError(e)


def makedirs(path):
    if not isinstance(path, bytes):
        raise TypeError('Expected "path" to be a bytestring path')
    if not path or not path.strip():
        raise ValueError('Got empty argument "path"')

    try:
        os.makedirs(util.syspath(path))
    except (OSError, ValueError, TypeError) as e:
        raise exceptions.FilesystemError(e)
