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

try:
    import magic
except ImportError:
    raise SystemExit(
        'Missing required module "magic".  Make sure "magic" (file-magic) '
        'is available before running this program.'
    )

from core import types
from util import sanity


log = logging.getLogger(__name__)


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

    TODO: Seems like this is the version currently in use? (on MacOS)
          https://pypi.python.org/pypi/file-magic/0.3.0
          https://github.com/file/file

          Requires 'libmagic'! Install by running;
          $ brew install libmagic
          $ pip3 install file-magic

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
        an instance of 'NullMIMEType' if the MIME type can not be determined.
    """
    _unknown_mime_type = types.NullMIMEType()
    if not file_path:
        return _unknown_mime_type

    global MY_MAGIC
    if MY_MAGIC is None:
        MY_MAGIC = _build_magic()

    try:
        found_type = MY_MAGIC.file(file_path)
    except (AttributeError, TypeError):
        # TODO: Fix 'magic.MagicException' not available in both libraries.
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
        _candidates = self._ext_to_mime.get(extension)
        if not _candidates:
            return []

        # NOTE(jonas): Sorting criteria pretty much arbitrarily chosen.
        #              Gives more consistent results, which helps with testing.
        _sorted_candidates = sorted(
            list(_candidates),
            key=lambda x: ('x-' not in x, 'text' in x, len(x)),
            reverse=True
        )
        return _sorted_candidates

    def get_mimetype(self, extension):
        """
        Returns a single MIME-type from the types mapped to a given extension.

        Args:
            extension: Extension to get a MIME-type for, as a Unicode string.

        Returns:
            A single MIME-type mapped to the given extension, as a Unicode
            string. See the "get_candidates"-method for info on prioritization.
            An instance of 'NullMIMEType' is returned if no MIME-type is found.
        """
        if extension and extension.strip():
            _candidates = self.get_candidate_mimetypes(extension)
            if _candidates:
                return _candidates[0]

        return types.NullMIMEType()

    def get_candidate_extensions(self, mimetype):
        """
        Returns a list of all extensions mapped to a given MIME-type.
        """
        _candidates = self._mime_to_ext.get(mimetype, [])
        if not _candidates:
            return []

        # De-prioritize any composite extensions like "tar.gz".
        _sorted_candidates = sorted(
            list(_candidates),
            key=lambda x: '.' not in x,
            reverse=True
        )
        return _sorted_candidates

    def get_extension(self, mimetype):
        """
        Returns a single extension for a given MIME-type.
        """
        _preferred = self._mime_to_preferred_ext.get(mimetype)
        if _preferred:
            return _preferred

        _candidates = self.get_candidate_extensions(mimetype)
        if _candidates:
            return _candidates[0]

        return None


# Shared global singleton.
MAPPER = MimeExtensionMapper()

# Add MIME to extension mappings from the 'mimetypes' module.
try:
    _mimetypes_map = {
        ext.lstrip('.'): mime for ext, mime in mimetypes.types_map.items()
    }
except AttributeError:
    log.error('Unable to get MIME-type map from the "mimetypes" module.')
else:
    for _ext, _mime in _mimetypes_map.items():
        MAPPER.add_mapping(_mime, _ext)


# Any custom "extension to MIME-type"-mappings goes here.
MAPPER.add_mapping('application/epub+zip', 'epub')
MAPPER.add_mapping('application/gzip', 'gz')
MAPPER.add_mapping('application/gzip', 'tar.gz')
MAPPER.add_mapping('application/octet-stream', 'bin')
MAPPER.add_mapping('application/rar', 'rar')
MAPPER.add_mapping('application/rtf', 'rtf')
MAPPER.add_mapping('application/vnd.oasis.opendocument.presentation', 'odp')
MAPPER.add_mapping('application/vnd.oasis.opendocument.text', 'odt')
MAPPER.add_mapping('application/vnd.openxmlformats-officedocument.wordprocessingml.document', 'docx')
MAPPER.add_mapping('application/x-7z-compressed', '7z')
MAPPER.add_mapping('application/x-bzip2', 'bz2')
MAPPER.add_mapping('application/x-gzip', 'gz')
MAPPER.add_mapping('application/x-gzip', 'tgz')
MAPPER.add_mapping('application/x-gzip', 'tar.gz')
MAPPER.add_mapping('application/x-lzma', 'lzma')
MAPPER.add_mapping('application/x-lzma', 'tar.lzma')
MAPPER.add_mapping('application/x-rar', 'rar')
MAPPER.add_mapping('application/x-tex', 'tex')
MAPPER.add_mapping('audio/midi', 'mid')
MAPPER.add_mapping('audio/x-flac', 'flac')
MAPPER.add_mapping('image/vnd.djvu', 'djvu')
MAPPER.add_mapping('inode/x-empty', '')
MAPPER.add_mapping('text/rtf', 'rtf')
MAPPER.add_mapping('text/x-asm', 'asm')
MAPPER.add_mapping('text/x-c', 'c')
MAPPER.add_mapping('text/x-c++', 'cpp')
MAPPER.add_mapping('text/x-sh', 'sh')
MAPPER.add_mapping('text/x-shellscript', 'sh')
MAPPER.add_mapping('text/x-shellscript', 'bash')
MAPPER.add_mapping('text/x-tex', 'tex')
MAPPER.add_mapping('video/x-matroska', 'mkv')

# Any custom overrides of the "extension to MIME-type"-mapping goes here.
MAPPER.add_preferred_extension('image/jpeg', 'jpg')
MAPPER.add_preferred_extension('application/gzip', 'gz')
MAPPER.add_preferred_extension('audio/midi', 'mid')
MAPPER.add_preferred_extension('video/quicktime', 'mov')
MAPPER.add_preferred_extension('video/mp4', 'mp4')
MAPPER.add_preferred_extension('text/plain', 'txt')
MAPPER.add_preferred_extension('text/rtf', 'rtf')
MAPPER.add_preferred_extension('text/x-sh', 'sh')
MAPPER.add_preferred_extension('text/x-shellscript', 'sh')
MAPPER.add_preferred_extension('inode/x-empty', '')


def get_mimetype(extension):
    return MAPPER.get_mimetype(extension)


def get_extension(mimetype):
    return MAPPER.get_extension(mimetype)
