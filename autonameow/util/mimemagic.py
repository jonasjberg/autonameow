# -*- coding: utf-8 -*-

#   Copyright(c) 2016-2018 Jonas Sjöberg
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
import mimetypes
import os

from core.exceptions import AutonameowException
from core.exceptions import DependencyError
from util import coercers
from util import sanity


log = logging.getLogger(__name__)


# File in this directory with mappings between MIME-types and extensions.
MIMEMAGIC_MAPPINGS_BASENAME = 'mimemagic.mappings'

# File in this directory with preferred extensions for MIME-types.
MIMEMAGIC_PREFERRED_BASENAME = 'mimemagic.preferred'


def _build_magic():
    """
    Workaround ambiguity about which magic library is actually used.

    Attempt to detect which of three 'magic' implementations that was
    imported and return a function that is roughly equivalent to running
    'file --mime-type' on POSIX systems.

    Based off of this:
    https://github.com/androguard/androguard/blob/2e1f04350bcb38a3acf796f8f8829d816b38fe21/androguard/core/bytecodes/apk.py#L380

    Documentation for the various magics:
    'filemagic'       https://pypi.python.org/pypi/filemagic
    'file-magic'      https://github.com/file/file/tree/master/python
    'python-magic'    https://github.com/ahupp/python-magic

    Notes on installing versions used on my (jonas) active development boxes:

        MacOS   Requires 'libmagic'. Install by running;
                $ brew install libmagic
                $ pip3 install file-magic

        Linux   Install 'python3-magic' from the repositories on Linux.
                For Debian-likes using apt:
                $ apt install python3-magic

    Returns:
        Callable the returns a MIME-type read from magic header bytes of the
        given file.

    Raises:
        SystemExit: Unable to import any 'magic' module.
        AutonameowException: Failed to get a callable from any 'magic' module.
    """
    try:
        import magic
    except ImportError:
        raise DependencyError(missing_modules='magic')
    # pylint: disable=unexpected-keyword-arg,no-value-for-parameter,no-member
    _magic = None
    try:
        # Test if loaded magic is the 'python-magic' package.
        getattr(magic, 'MagicException')
    except AttributeError:
        try:
            # Test if loaded magic is the 'filemagic' package.
            getattr(magic.Magic, 'id_buffer')
        except AttributeError:
            # Load the 'file-magic' package.
            # https://github.com/file/file/tree/master/python
            ms = magic.open(magic.MAGIC_MIME_TYPE)
            ms.load()
            _magic = ms.file
        else:
            # Now using the 'filemagic' package.
            # To identify with mime type, rather than a textual description,
            # pass the magic.MAGIC_MIME_TYPE flag when creating the magic.Magic
            # instance.
            # NOTE(jonas): This one is used on both MacOS and Linux devboxes.
            m = magic.Magic(flags=magic.MAGIC_MIME_TYPE)
            _magic = m.id_filename
    else:
        # Now using the 'python-magic' package.
        #
        # There is also a Magic class that provides more direct control,
        # including overriding the magic database file and turning on character
        # encoding detection. This is not recommended for general use.
        # In particular, it's not safe for sharing across multiple threads and
        # will fail throw if this is # attempted.
        # https://github.com/ahupp/python-magic
        #
        # NOTE(jonas): Might cause problems later on, if using threading!
        m = magic.Magic(mime=True, uncompress=False)
        _magic = m.from_file

    if _magic is None:
        raise AutonameowException(
            'Unable to retrieve a suitable magic callable in "mimemagic.py" ..'
        )
    return _magic


MY_MAGIC = None


def file_mimetype(file_path):
    """
    Determine file type by reading "magic" header bytes.

    Should be equivalent to the 'file --mime-type' command in *NIX environments.
    This functions sets the global 'MY_MAGIC' the first time it is called.

    Args:
        file_path: The path to the file to get the MIME type of as a string.

    Returns:
        The MIME type of the file at the given path ('application/pdf') or
        a "null" class instance if the MIME type can not be determined.
    """
    unknown_mime_type = coercers.NULL_AW_MIMETYPE
    if not file_path:
        return unknown_mime_type

    global MY_MAGIC
    if MY_MAGIC is None:
        MY_MAGIC = _build_magic()

    try:
        found_type = MY_MAGIC(file_path)
    except (AttributeError, TypeError):
        # TODO: Fix 'magic.MagicException' not available in both libraries.
        found_type = unknown_mime_type

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
    if mime_to_match == coercers.NULL_AW_MIMETYPE:
        if '*/*' in glob_list:
            return True
        return False

    if not mime_to_match:
        # Test again after the case above because 'NullMIMEType' evaluates False.
        return False

    if not isinstance(mime_to_match, str):
        raise TypeError('Expected "mime_to_match" to be of type str')

    if '/' not in mime_to_match:
        raise ValueError('Expected "mime_to_match" to be on the form "foo/bar"')

    if not isinstance(glob_list, list):
        glob_list = [glob_list]

    # log.debug('Evaluating MIME. MimeToMatch: "{!s}" Globs: {!s}'.format(
    #     mime_to_match, glob_list
    # ))
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


class MimeExtensionMapper(object):
    def __init__(self):
        self.unknown_mime_type = coercers.NULL_AW_MIMETYPE

        # Stores sets.
        self._mime_to_ext = dict()
        self._ext_to_mime = dict()

        # Stores single strings.
        self._mime_to_preferred_ext = dict()

    def add_mapping(self, mimetype, extension):
        if extension not in self._ext_to_mime:
            self._ext_to_mime[extension] = {mimetype}
        else:
            if mimetype not in self._ext_to_mime.get(extension, set()):
                self._ext_to_mime[extension].add(mimetype)

        if mimetype not in self._mime_to_ext:
            self._mime_to_ext[mimetype] = {extension}
        else:
            if extension not in self._mime_to_ext.get(mimetype, set()):
                self._mime_to_ext[mimetype].add(extension)

    def add_preferred_extension(self, mimetype, extension):
        """
        Adds a overriding mapping from a MIME-type to an extension.
        """
        self._mime_to_preferred_ext[mimetype] = extension
        self.add_mapping(mimetype, extension)

    def get_candidate_mimetypes(self, extension):
        """
        Returns a list of all MIME-types mapped to a given extension.

        MIME-types containing 'x-', as in "experimental" (?) are placed at
        the end of the list.

        Args:
            extension: Extension to get MIME-types for, as a Unicode string.

        Returns:
            All MIME-types mapped to the given extension, as a list of strings.
        """
        candidates = self._ext_to_mime.get(extension)
        if not candidates:
            return []

        # NOTE(jonas): Sorting criteria pretty much arbitrarily chosen.
        #              Gives more consistent results, which helps with testing.
        sorted_candidates = sorted(
            list(candidates),
            key=lambda x: ('x-' not in x, 'text' in x, len(x)),
            reverse=True
        )
        return sorted_candidates

    def get_mimetype(self, extension):
        """
        Returns a single MIME-type from the types mapped to a given extension.

        Args:
            extension: Extension to get a MIME-type for, as a Unicode string.

        Returns:
            A single MIME-type mapped to the given extension, as a Unicode
            string. See the "get_candidates"-method for info on prioritization.
            If no MIME-type is found, a "null" class instance is returned.
        """
        if isinstance(extension, str) and extension.strip():
            candidates = self.get_candidate_mimetypes(extension)
            if candidates:
                if len(candidates) > 1:
                    # If more than one candidate MIME-type, use any candidate
                    # found in the preferred extension mapping.
                    for candidate in candidates:
                        if candidate in self._mime_to_preferred_ext:
                            return candidate
                # Use the first of the (arbitrarily sorted) candidates.
                return candidates[0]

        return self.unknown_mime_type

    def get_candidate_extensions(self, mimetype):
        """
        Returns a list of all extensions mapped to a given MIME-type.
        """
        candidates = self._mime_to_ext.get(mimetype, [])
        if not candidates:
            return []

        # De-prioritize any composite extensions like "tar.gz".
        sorted_candidates = sorted(
            list(candidates),
            key=lambda x: '.' not in x,
            reverse=True
        )
        return sorted_candidates

    def get_extension(self, mimetype):
        """
        Returns a single extension for a given MIME-type.
        """
        preferred = self._mime_to_preferred_ext.get(mimetype)
        if preferred:
            return preferred

        candidates = self.get_candidate_extensions(mimetype)
        if candidates:
            return candidates[0]

        return None


# Shared global singleton.
MAPPER = MimeExtensionMapper()


def _load_mimetypes_module_mimemagic_mappings():
    try:
        mimetypes_types_map = {
            ext.lstrip('.'): mime for ext, mime in mimetypes.types_map.items()
        }
    except AttributeError:
        log.error('Unable to get MIME-type map from the "mimetypes" module.')
    else:
        for extension, mime_type in mimetypes_types_map.items():
            MAPPER.add_mapping(mime_type, extension)


def _read_mimetype_extension_mapping_file(mapfile_basename, callback):
    """
    Load MIME-type to extension mappings from external file.

    Each line should contain a MIME-type and a extension, separated by a colon.
    Any whitespace is ignored, as well as any initial period in the extension.
    Lines beginning with a hash ('#') are also ignored.

    Args:
        mapfile_basename: Basename of the file in this directory to read.
        callback: Called with the MIME-type and extension, once per line.

    Returns:
        All MIME-types mapped to the given extension, as a list of strings.
    """
    mapfile = os.path.realpath(os.path.join(
        os.path.dirname(__file__), mapfile_basename
    ))
    try:
        with open(mapfile, 'r') as fh:
            lines = fh.readlines()
    except OSError:
        return

    for n, line in enumerate(lines, start=1):
        line = line.strip()
        if not line or line.startswith('#'):
            continue
        try:
            mime_type, extension = line.strip().split(':')
        except ValueError:
            log.error('Error parsing "{!s}" line {}'.format(mapfile, n))
        else:
            str_mime_type = coercers.force_string(mime_type).strip()
            str_extension = coercers.force_string(extension).strip().lstrip('.')
            if not str_mime_type:
                continue

            callback(str_mime_type, str_extension)


def _load_mimemagic_mappings():
    """
    Load MIME-type to extension mappings from external file.
    """
    _read_mimetype_extension_mapping_file(MIMEMAGIC_MAPPINGS_BASENAME,
                                          MAPPER.add_mapping)


def _load_mimemagic_mapping_overrides():
    """
    Load MIME-type to extension mapping overrides from external file.
    These are the "preferred" extensions for any given MIME-type.
    """
    _read_mimetype_extension_mapping_file(MIMEMAGIC_PREFERRED_BASENAME,
                                          MAPPER.add_preferred_extension)


# Load MIME to extension mappings from the 'mimetypes' module.
# This is the baseline, extended by the following custom mappings.
_load_mimetypes_module_mimemagic_mappings()

# Load any custom "extension to MIME-type"-mappings.
_load_mimemagic_mappings()

# Load any custom overrides of the "extension to MIME-type"-mappings.
_load_mimemagic_mapping_overrides()


def get_mimetype(extension):
    return MAPPER.get_mimetype(extension)


def get_extension(mimetype):
    assert isinstance(mimetype, str)
    return MAPPER.get_extension(mimetype)
