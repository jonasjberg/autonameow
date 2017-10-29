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
import magic
import mimetypes

from core import constants as C
from core import types
from core.util import sanity


log = logging.getLogger(__name__)


# Any custom "extension to MIME-type"-mappings goes here.
mimetypes.add_type('application/epub+zip', '.epub')
mimetypes.add_type('application/gzip', 'gz')
mimetypes.add_type('application/x-lzma', 'lzma')
mimetypes.add_type('application/x-rar', 'rar')
mimetypes.add_type('text/rtf', 'rtf')
mimetypes.add_type('application/gzip', 'tar.gz')
mimetypes.add_type('application/x-lzma', 'tar.lzma')
mimetypes.add_type('text/x-shellscript', 'sh')
mimetypes.add_type('text/x-asm', 'asm')


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
    _unknown_mime_type = types.NullMIMEType()
    if not file_path:
        return _unknown_mime_type

    global MY_MAGIC
    if MY_MAGIC is None:
        MY_MAGIC = _build_magic()

    try:
        found_type = MY_MAGIC.file(file_path)
    except (AttributeError, magic.MagicException, TypeError):
        found_type = _unknown_mime_type

    return found_type


def eval_glob(mime_to_match, glob_list):
    """
    Tests if a given MIME type string matches any of the specified globs.

    The MIME types consist of a "type" and a "subtype", separated by '/'.
    For instance; "image/jpg" or "application/pdf".

    Globs can substitute either one or both of "type" and "subtype" with an
    asterisk to ignore that part. Examples:

        mime_to_match         glob_list                 evaluates
        'image/jpg'           ['image/jpg']             True
        'image/png'           ['image/*']               True
        'application/pdf'     ['*/*']                   True
        'application/pdf'     ['image/*', '*/jpg']      False

    This function performs extra argument validation due to the fact that it is
    likely to be used by third party developers. It is also exposed to possibly
    malformed configuration entries.

    Unknown MIME-types evaluate to True only for '*/*', otherwise always False.

    Args:
        mime_to_match: The MIME to match against the globs as a Unicode string.
        glob_list: A list of globs as Unicode strings.

    Returns:
        True if the MIME to match is valid and matches any of the globs.
        False if the MIME to match is valid but does not match any of the globs.
    Raises:
        TypeError: Got non-Unicode string arguments.
        ValueError: Argument "mime_to_match" is not on the form "foo/bar".
    """
    if not glob_list:
        return False

    # Unknown MIME-type evaluates True if a glob matches anything, else False.
    if mime_to_match == types.NULL_AW_MIMETYPE:
        if '*/*' in glob_list:
            return True
        else:
            return False

    if not mime_to_match:
        # Test again after the case above because NullMIMEType evaluates False.
        return False

    if not (isinstance(mime_to_match, str)):
        raise TypeError('Expected "mime_to_match" to be of type str')

    if '/' not in mime_to_match:
        raise ValueError('Expected "mime_to_match" to be on the form "foo/bar"')

    if not isinstance(glob_list, list):
        glob_list = [glob_list]

    log.debug(
        'Evaluating MIME. MimeToMatch: "{!s}" Globs: {!s}'.format(mime_to_match,
                                                                  glob_list)
    )
    mime_to_match_type, mime_to_match_subtype = mime_to_match.split('/')
    for glob in glob_list:
        sanity.check_internal_string(glob)

        if glob == mime_to_match:
            return True
        elif '*' in glob:
            try:
                glob_type, glob_subtype = glob.split('/')
            except ValueError:
                raise ValueError(
                    'Expected globs to be on the form "*/a", "a/*"'
                )
            if glob_type == '*' and glob_subtype == '*':
                # Matches everything.
                return True
            elif glob_type == '*' and glob_subtype == mime_to_match_subtype:
                # Matches any type. Tests subtype equality.
                return True
            elif glob_type == mime_to_match_type and glob_subtype == '*':
                # Checks type equality. Matches any subtype.
                return True
    return False


try:
    MIME_TYPE_LOOKUP = {
        ext.lstrip('.'): mime for ext, mime in mimetypes.types_map.items()
    }
except AttributeError:
    MIME_TYPE_LOOKUP = {}

# TODO: Improve robustness of interfacing with 'mimetypes'.
sanity.check(len(MIME_TYPE_LOOKUP) > 0,
             'MIME_TYPE_LOOKUP is empty')

# TODO: Inconsistent results 'application/gzip' and 'application/x-gzip'..?

MIME_TYPE_LOOKUP_INV = {
    mime: ext for ext, mime in MIME_TYPE_LOOKUP.items()
}

# Override "MIME-type to extension"-mappings here.
MIME_TYPE_LOOKUP_INV['image/jpeg'] = 'jpg'
MIME_TYPE_LOOKUP_INV['video/quicktime'] = 'mov'
MIME_TYPE_LOOKUP_INV['video/mp4'] = 'mp4'
MIME_TYPE_LOOKUP_INV['text/plain'] = 'txt'
MIME_TYPE_LOOKUP_INV['text/rtf'] = 'rtf'
MIME_TYPE_LOOKUP_INV['inode/x-empty'] = ''

KNOWN_EXTENSIONS = frozenset(MIME_TYPE_LOOKUP.keys())
KNOWN_MIME_TYPES = frozenset(
    list(MIME_TYPE_LOOKUP.values()) + ['inode/x-empty']
)
