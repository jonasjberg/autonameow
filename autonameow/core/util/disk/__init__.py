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


log = logging.getLogger(__name__)


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
