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

import magic

from core import constants as C


def _build_magic():
    """
    Workaround ambiguity about which magic library is actually used.

    https://github.com/ahupp/python-magic
      "There are, sadly, two libraries which use the module name magic.
       Both have been around for quite a while.If you are using this
       module and get an error using a method like open, your code is
       expecting the other one."

    http://www.zak.co.il/tddpirate/2013/03/03/the-python-module-for-file-type-identification-called-magic-is-not-standardized/
      "The following code allows the rest of the script to work the same
       way with either version of 'magic'"

    Returns:
        An instance of 'magic' as type 'Magic'.
    """
    try:
        _magic = magic.open(magic.MAGIC_MIME_TYPE)
        _magic.load()
    except AttributeError:
        _magic = magic.Magic(mime=True)
        _magic.file = _magic.from_file

    return _magic


MY_MAGIC = None


def filetype(file_path):
    """
    Determine file type by reading "magic" header bytes.

    Should be equivalent to the 'file --mime-type' command in *NIX environments.
    This functions sets the global 'MY_MAGIC' the first time it is called.

    Args:
        file_path: The path to the file to get the MIME type of as a string.

    Returns:
        The MIME type of the file at the given path ('application/pdf') or
        'C.MAGIC_TYPE_UNKNOWN' if the MIME type can not be determined.
    """
    if not file_path:
        return C.MAGIC_TYPE_UNKNOWN

    global MY_MAGIC
    if MY_MAGIC is None:
        MY_MAGIC = _build_magic()

    try:
        found_type = MY_MAGIC.file(file_path)
    except (AttributeError, magic.MagicException, TypeError):
        found_type = C.MAGIC_TYPE_UNKNOWN

    return found_type
