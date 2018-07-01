# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg <autonameow@jonasjberg.com>
#   Source repository: https://github.com/jonasjberg/autonameow
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
import os

from core import constants as C
from core import exceptions
from util import disk
from util import encoding as enc
from util import mimemagic
from util import sanity


class FileObject(object):
    __slots__ = ('abspath', 'filename', 'pathname', 'pathparent', 'mime_type',
                 'basename_prefix', 'basename_suffix', '__cached_str',
                 '_bytesize', '_hash_partial')

    def __init__(self, path):
        """
        Creates a new FileObject instance representing a single path/file.

        Args:
            path: The absolute normalized path to the file, as an
                  "internal filename bytestring", I.E. bytes.
        """
        sanity.check_internal_bytestring(path)
        _validate_path_argument(path)
        self.abspath = path

        self.filename = enc.bytestring_path(
            os.path.basename(enc.syspath(path))
        )
        self.pathname = enc.bytestring_path(
            os.path.dirname(enc.syspath(path))
        )
        self.pathparent = enc.bytestring_path(
            os.path.basename(os.path.dirname(enc.syspath(path)))
        )

        self.mime_type = mimemagic.file_mimetype(self.abspath)

        # Extract parts of the file name.
        self.basename_prefix = disk.basename_prefix(self.abspath) or b''
        self.basename_suffix = disk.basename_suffix(self.abspath) or b''

        # Avoid round-tripping to the OS to decode strings.
        self.__cached_str = None

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
            statinfo = os.stat(enc.syspath(self.abspath))
            if statinfo:
                return statinfo.st_size
        except OSError:
            pass

        return C.UNKNOWN_BYTESIZE

    def _get_hash_partial(self):
        # Raises FilesystemError for any "real" errors.
        from util import partial_sha256digest
        return partial_sha256digest(self.abspath)

    def __str__(self):
        if self.__cached_str is None:
            self.__cached_str = enc.displayable_path(self.filename)
        return self.__cached_str

    def __repr__(self):
        return '{!s}({:8.8})'.format(self.__class__.__name__, self.hash_partial)

    def __hash__(self):
        # NOTE(jonas): Theoretical risk of hash collisions due to the "partial"
        #              hashes.. Might add conditionally hashing the entire file?
        return hash(
            (self.abspath, self.mime_type, self.bytesize, self.hash_partial)
        )

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        return self.__check_equality_fast(other)

    def __ne__(self, other):
        # Infinite recursion with 'return self != other'
        return not self == other

    def __lt__(self, other):
        if isinstance(other, self.__class__):
            return self.abspath < other.abspath

        # NOTE(jonas): Objects of other types are always "less".
        return False

    def __gt__(self, other):
        return not self < other


def _validate_path_argument(path):
    """
    Checks that a "raw" argument from an unknown/untrusted source is a
    valid path appropriate for instantiating a new 'FileObject' object.

    Args:
        path: Alleged path in the "internal filename bytestring" format.
              Unicode str paths seem to be handled equally well on MacOS,
              at least for simple testing with trivial inputs.
              But still; __assume 'path' is bytes__.

    Raises:
        InvalidFileArgumentError: The given 'path' is not considered valid.
    """
    def _raise(error_message):
        raise exceptions.InvalidFileArgumentError(error_message)

    if not isinstance(path, bytes):
        _raise('Expected path of type "bytes". Got: "{!s}"'.format(type(path)))
    elif not path.strip():
        _raise('Path is empty or only whitespace')

    if not disk.exists(path):
        _raise('Path does not exist')
    if disk.isdir(path):
        # TODO: [TD0045] Implement handling/renaming directories.
        _raise('Safe handling of directories is not implemented yet')
    if disk.islink(path):
        # TODO: [TD0026] Implement handling of symlinks.
        _raise('Safe handling of symbolic links is not implemented yet')
    if not disk.has_permissions(path, 'r'):
        _raise('Not authorized to read path')

    # Check assumptions about implementation. Might detect future bugs.
    if not disk.isabs(path):
        _raise('Not an absolute path (?) This should not happen!')
