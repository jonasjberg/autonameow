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

import logging
import os

from core import util
from core.util import sanity

from .io import (
    delete,
    exists,
    isdir,
    isfile,
    makedirs,
    rename_file,
    tempdir
)
from .pathstring import (
    basename_prefix,
    basename_suffix,
    split_basename
)
from .sanitize import sanitize_filename


log = logging.getLogger(__name__)


def file_basename(file_path):
    return util.syspath(os.path.basename(file_path))


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

    if basename_one == basename_two:
        return True
    else:
        return False


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
