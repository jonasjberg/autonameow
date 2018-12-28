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

#   -------------------------------------------------------------------------
#   This code is based on the "beets" project.
#   File:    beets/util/__init__.py
#   Commit:  b38f34b2c06255f1c51e8714c8af6962e297a3c5
#   -------------------------------------------------------------------------


# This file is part of beets.
# Copyright 2016, Adrian Sampson.
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.

import locale
import os
import sys

from core import constants as C
from util import sanity
from vendor import chardet


__all__ = [
    'arg_encoding',
    'autodetect_decode',
    'autodetect_encoding',
    'bytestring_path',
    'convert_command_args',
    'decode_',
    'displayable_path',
    'encode_',
    'normpath',
    'syspath'
]


WINDOWS_MAGIC_PREFIX = u'\\\\?\\'


def convert_command_args(args):
    """
    Convert command arguments to bytestrings on Python 2 and
    surrogate-escaped strings on Python 3.
    """
    assert isinstance(args, list)

    def convert(arg):
        if isinstance(arg, bytes):
            arg = arg.decode(arg_encoding(), 'surrogateescape')
        return arg

    return [convert(a) for a in args]


def normpath(path):
    """
    Provide the canonical form of a given path.

    This function should be used as the primary means of converting paths of
    unknown origins to the "internal bytestring" format.

    Any "~" is expanded to the user home directory, and symbolic links are
    untangled. The full full absolute, normalized path is returned.

    Args:
        path: The path to expand, normalize and encode to the internal format.
    Returns:
        A normalized version of the given path encoded to the "internal" format.
    """
    if not path:
        raise ValueError('path must not be empty')

    path = syspath(path, prefix=False)
    path = os.path.normpath(os.path.abspath(os.path.expanduser(path)))
    return bytestring_path(path)


def arg_encoding():
    """
    Gets the encoding for command-line arguments (and other OS
    locale-sensitive strings).
    """
    try:
        return locale.getdefaultlocale()[1] or C.DEFAULT_ENCODING
    except ValueError:
        # Invalid locale environment variable setting. To avoid
        # failing entirely, use default fallback encoding.
        return C.DEFAULT_ENCODING


def _fsencoding():
    """
    Gets the filesystem encoding of the system.
    On Windows, this is always UTF-8 (not MBCS).
    """
    encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
    if encoding == 'mbcs':
        # On Windows, a broken encoding known to Python as "MBCS" is
        # used for the filesystem. However, we only use the Unicode API
        # for Windows paths, so the encoding is actually immaterial so
        # we can avoid dealing with this nastiness. We arbitrarily
        # choose the default fallback encoding (UTF-8).
        encoding = C.DEFAULT_ENCODING
    return encoding


def bytestring_path(path):
    """
    Given a path, which is either a bytes or unicode string, returns a str path
    (ensuring that we never deal with Unicode pathnames).

    Incoming paths should be passed through this to convert to the
    "internal bytestring" format.

    Args:
        path: The path coming in through the "encoding boundary", to be
            converted to the internal format.

    Returns:
        The given path, encoded in the "internal bytestring" format.
    """
    # Pass through bytestrings.
    if isinstance(path, bytes):
        return path

    # On Windows, remove the magic prefix added by `syspath`. This makes
    # ``bytestring_path(syspath(X)) == X``, i.e., we can safely
    # round-trip through `syspath`.
    if os.path.__name__ == 'ntpath' and path.startswith(WINDOWS_MAGIC_PREFIX):
        path = path[len(WINDOWS_MAGIC_PREFIX):]

    # Try to encode with default encodings, fall back to default (utf-8).
    try:
        return path.encode(_fsencoding())
    except (UnicodeError, LookupError):
        return path.encode(C.DEFAULT_ENCODING)


def displayable_path(bpath):
    """
    Attempts to decode a bytestring path to a unicode object for the purpose
    of displaying it to the user.

    Used to format error messages and log output. It does its best to decode
    the path to human-readable Unicode text, and it’s not allowed to fail --
    but it’s lossy. The result is only good for human consumption, not for
    returning back to the OS.

    Hence the name, which is intentionally not unicode_path.

    Args:
        bpath: The path of unknown encoding to be converted.

    Returns:
        The given path(s) in a format suitable for displaying to the user.
    """
    if isinstance(bpath, str):
        return bpath
    elif not isinstance(bpath, bytes):
        # A non-string object: just get its unicode representation.
        return str(bpath)

    try:
        return bpath.decode(_fsencoding(), 'ignore')
    except (UnicodeError, LookupError):
        return bpath.decode(C.DEFAULT_ENCODING, 'ignore')


def syspath(path, prefix=True):
    """
    Convert a path for use by the operating system.

    In particular, paths on Windows must receive a magic prefix and must be
    converted to Unicode before they are sent to the OS.

    To disable the magic prefix on Windows, set `prefix` to False
    -- but only do this if you *really* know what you're doing.

      Every argument to an OS function like open or listdir must pass through
      the third utility: syspath. Think of this as converting from the
      internal representation to the OS’s own representation. On Unix, this is
      a no-op: the representations are the same. On Windows, this converts a
      bytestring path back to Unicode and then adds the ridiculous '\\?\' prefix,
      which avoids problems with long names.

    Source: http://beets.io/blog/paths.html

    Args:
        path:
        prefix:

    Returns:

    """
    # Don't do anything if we're not on windows
    if os.path.__name__ != 'ntpath':
        return path

    if not isinstance(path, str):
        # Beets currently represents Windows paths internally with UTF-8
        # arbitrarily. But earlier versions used MBCS because it is
        # reported as the FS encoding by Windows. Try both.
        try:
            path = path.decode('utf-8')
        except UnicodeError:
            # The encoding should always be MBCS, Windows' broken
            # Unicode representation.
            encoding = sys.getfilesystemencoding() or sys.getdefaultencoding()
            path = path.decode(encoding, 'replace')

    # Add the magic prefix if it isn't already there.
    # http://msdn.microsoft.com/en-us/library/windows/desktop/aa365247.aspx
    if prefix and not path.startswith(WINDOWS_MAGIC_PREFIX):
        if path.startswith(u'\\\\'):
            # UNC path. Final path should look like \\?\UNC\...
            path = u'UNC' + path[1:]
        path = WINDOWS_MAGIC_PREFIX + path

    return path


def encode_(strng):
    if isinstance(strng, bytes):
        return strng

    # Try to decode with the default system encoding, then try some default.
    try:
        return strng.encode(_fsencoding())
    except (UnicodeError, LookupError):
        return strng.encode(C.DEFAULT_ENCODING)


def decode_(strng):
    if isinstance(strng, str):
        return strng

    # Try to decode with the default system encoding, then try some default.
    try:
        return strng.decode(_fsencoding())
    except (UnicodeError, LookupError):
        try:
            return strng.decode(C.DEFAULT_ENCODING)
        except (UnicodeError, LookupError):
            return strng.decode(C.DEFAULT_ENCODING, errors='replace')


def autodetect_decode(strng):
    """
    Tries to decode a string with an unknown encoding to a Unicode string.

    Unicode strings and empty bytestrings are passed through as-is.

    Args:
        strng: The string to decode as a Unicode str or a bytestring.

    Returns:
        The given string decoded to an ("internal") Unicode string.

    Raises:
        ValueError: Autodetection and/or decoding was unsuccessful because
                    the given string is None or not a string type.
    """
    if isinstance(strng, str):
        return strng

    if not isinstance(strng, bytes):
        raise TypeError('Module "chardet" expects bytestrings')

    if strng == b'':
        return ''

    detected_encoding = chardet.detect(strng)
    if detected_encoding and 'encoding' in detected_encoding:
        try:
            strng = strng.decode(detected_encoding['encoding'])
        except ValueError:
            raise ValueError('Unable to autodetect encoding and decode string')

    sanity.check_internal_string(strng)
    return strng


def autodetect_encoding(filepath):
    try:
        with open(filepath, 'rb') as fh:
            detected_encoding = chardet.detect(fh.read())
    except (OSError, TypeError):
        return None
    else:
        return detected_encoding.get('encoding', None)
