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

import filecmp
import magic
import os

from core import constants as C
from core import (
    exceptions,
    util
)
from core.util import (
    diskutils,
    sanity
)


UNKNOWN_BYTESIZE = 0


class FileObject(object):
    def __init__(self, path):
        """
        Creates a new FileObject instance representing a single path/file.

        Args:
            path: The absolute normalized path to the file, as an
                  "internal filename bytestring", I.E. bytes.
        """
        sanity.check_internal_bytestring(path)
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

        # Set only when needed.
        self._bytesize = None
        self._hash_partial = None

    @property
    def bytesize(self):
        if self._bytesize is None:
            self._bytesize = self._get_bytesize()
        return self._bytesize

    @property
    def hash_partial(self):
        if self._hash_partial is None:
            self._hash_partial = self._get_hash_partial()
        return self._hash_partial

    def __check_equality_fast(self, other):
        return filecmp.cmp(self.abspath, other.abspath, shallow=True)

    def _get_bytesize(self):
        try:
            statinfo = os.stat(util.syspath(self.abspath))
            if statinfo:
                return statinfo.st_size
        except OSError:
            pass

        return UNKNOWN_BYTESIZE

    def _get_hash_partial(self):
        # Raises FilesystemError for any "real" errors.
        return util.partial_sha256digest(self.abspath)

    def __str__(self):
        if self.__cached_str is None:
            self.__cached_str = util.displayable_path(self.filename)

        return self.__cached_str

    def __repr__(self):
        if self.__cached_repr is None:
            self.__cached_repr = '<{!s}("{!s}")>'.format(
                self.__class__.__name__, util.displayable_path(self.abspath)
            )

        return self.__cached_repr

    def __hash__(self):
        # NOTE(jonas): Theoretical risk of hash collisions due to the "partial"
        #              hashes.. Might add conditionally hashing the entire file?
        return hash(
            (self.abspath, self.mime_type, self.bytesize, self.hash_partial)
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        else:
            return self.__check_equality_fast(other)

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
        'C.MAGIC_TYPE_UNKNOWN' if the MIME type can not be determined.
    """
    if not file_path:
        return C.MAGIC_TYPE_UNKNOWN

    global MY_MAGIC
    if MY_MAGIC is None:
        MY_MAGIC = _build_magic()

    try:
        found_type = MY_MAGIC.file(file_path)
    except (magic.MagicException, TypeError):
        found_type = C.MAGIC_TYPE_UNKNOWN

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

    # Check assumptions about implementation. Might detect future bugs.
    if not os.path.isabs(_path):
        _raise('Not an absolute path (?) This should not happen!')
