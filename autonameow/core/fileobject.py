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
import magic

from core import (
    constants,
    exceptions,
    util
)
from .util import diskutils


class FileObject(object):
    def __init__(self, path):
        """
        Creates a new FileObject instance representing a single path/file.

        Args:
            path: The absolute normalized path to the file, as an
                  "internal filename bytestring", I.E. bytes.
        """
        assert(isinstance(path, bytes))
        validate_path_argument(path)
        self.abspath = path

        self.filename = util.bytestring_path(
            os.path.basename(util.syspath(path))
        )
        self.pathname = util.bytestring_path(
            os.path.dirname(util.syspath(path))
        )
        self.pathparent = util.bytestring_path(
            os.path.basename(os.path.dirname(util.syspath(path)))
        )

        self.mime_type = filetype_magic(self.abspath)

        # Extract parts of the file name.
        self.basename_prefix = diskutils.basename_prefix(self.abspath)
        self.basename_suffix = diskutils.basename_suffix(self.abspath)

        # Avoid round-tripping to the OS to decode strings.
        self.__cached_str = None
        self.__cached_repr = None

    def __str__(self):
        if self.__cached_str is None:
            self.__cached_str = util.displayable_path(self.filename)

        return self.__cached_str

    def __repr__(self):
        if self.__cached_repr is None:
            self.__cached_repr = '<{} {}>'.format(
                self.__class__.__name__, util.displayable_path(self.abspath)
            )

        return self.__cached_repr

    def __hash__(self):
        # NOTE(jonas): Might need to use a more robust method to avoid
        #              collisions. Use "proper" cryptographic checksum?
        return hash((self.abspath, self.mime_type))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        else:
            return (self.abspath, self.mime_type) == (other.abspath,
                                                      other.mime_type)

    def __ne__(self, other):
        return not (self == other)


MY_MAGIC = None


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


def filetype_magic(file_path):
    """
    Determine file type by reading "magic" header bytes.

    Should be equivalent to the 'file --mime-type' command in *NIX environments.
    This functions sets the global 'MY_MAGIC' the first time it is called.

    Args:
        file_path: The path to the file to get the MIME type of as a string.

    Returns:
        The MIME type of the file at the given path ('application/pdf') or
        'constants.MAGIC_TYPE_UNKNOWN' if the MIME type can not be determined.
    """
    if not file_path:
        return constants.MAGIC_TYPE_UNKNOWN

    global MY_MAGIC
    if MY_MAGIC is None:
        MY_MAGIC = _build_magic()

    try:
        found_type = MY_MAGIC.file(file_path)
    except (magic.MagicException, TypeError):
        found_type = constants.MAGIC_TYPE_UNKNOWN

    return found_type


def validate_path_argument(path):
    """
    Checks that a "raw" argument from an unknown/untrusted source is a
    valid path appropriate for instantiating a new 'FileObject' object.

    Args:
        path: Alleged path in the "internal filename bytestring" format.
              Unicode str paths seem to be handled equally well on MacOS,
              at least for simple testing with trivial inputs.
              But still; __assume 'path' is bytes__ and pass 'path' as bytes.

    Raises:
        InvalidFileArgumentError: The given 'path' is not considered valid.
    """
    def _raise(error_message):
        raise exceptions.InvalidFileArgumentError(error_message)

    if not isinstance(path, (str, bytes)):
        _type = str(type(path))
        _raise('Path is neither "str" or "bytes"; type: "{}"'.format(_type))
    elif not path.strip():
        _raise('Path is None/empty')

    _path = util.syspath(path)

    if not os.path.exists(_path):
        _raise('Path does not exist')
    if os.path.isdir(_path):
        # TODO: [TD0045] Implement handling/renaming directories.
        _raise('Safe handling of directories is not implemented yet')
    if os.path.islink(_path):
        # TODO: [TD0026] Implement handling of symlinks.
        _raise('Safe handling of symbolic links is not implemented yet')
    if not os.access(_path, os.R_OK):
        _raise('Not authorized to read path')
