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
import re

import magic

from core import (
    constants,
    util
)
from core.exceptions import InvalidFileArgumentError
from .util import diskutils

DATE_SEP = b'[:\-._ ]?'
TIME_SEP = b'[:\-._ T]?'
DATE_REGEX = b'[12]\d{3}' + DATE_SEP + b'[01]\d' + DATE_SEP + b'[0123]\d'
TIME_REGEX = (b'[012]\d' + TIME_SEP + b'[012345]\d' + TIME_SEP
              + b'[012345]\d(.[012345]\d)?')
FILENAMEPART_TS_REGEX = re.compile(DATE_REGEX + b'([T_ -]?' + TIME_REGEX + b')?')


class FileObject(object):
    def __init__(self, path, opts):
        """
        Creates a new FileObject instance representing a single path/file.

        Args:
            path: The absolute normalized path to the file, as a bytestring.
            opts: Configuration options as an instance of 'Configuration'.
        """

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
        self.fnbase = diskutils.file_base(self.abspath)
        self.suffix = diskutils.file_suffix(self.abspath)

        self.BETWEEN_TAG_SEPARATOR = util.bytestring_path(
            opts.options['FILETAGS_OPTIONS'].get('between_tag_separator')
        )
        self.FILENAME_TAG_SEPARATOR = util.bytestring_path(
            opts.options['FILETAGS_OPTIONS'].get('filename_tag_separator')
        )

        # Do "filename partitioning" -- split the file name into four parts:
        #
        #   * filenamepart_ts     Date-/timestamp.
        #   * filenamepart_base   Descriptive text.
        #   * filenamepart_ext    File extension/suffix.
        #   * filenamepart_tags   Tags created within the "filetags" workflow.
        #
        # Example basename '20160722 Descriptive name -- firsttag tagtwo.txt':
        #
        #                               .------------ FILENAME_TAG_SEPARATOR
        #                              ||         .-- BETWEEN_TAG_SEPARATOR
        #                              VV         V
        #    20160722 Descriptive name -- firsttag tagtwo.txt
        #    |______| |______________|    |_____________| |_|
        #       ts          base               tags       ext
        #
        # TODO: Move "filetags"-specific code to separate module. (?)
        self._filenamepart_ts = self._filenamepart_ts()
        self._filenamepart_base = self._filenamepart_base()
        self._filenamepart_ext = self._filenamepart_ext()
        self._filenamepart_tags = self._filenamepart_tags() or []

    @property
    def filenamepart_ts(self):
        if not self._filenamepart_ts:
            return None
        return util.decode_(self._filenamepart_ts)

    @property
    def filenamepart_base(self):
        if not self._filenamepart_base:
            return None
        return util.decode_(self._filenamepart_base)

    @property
    def filenamepart_ext(self):
        if not self._filenamepart_ext:
            return None
        return util.decode_(self._filenamepart_ext)

    @property
    def filenamepart_tags(self):
        if not self._filenamepart_tags:
            return []
        return [util.decode_(t) for t in self._filenamepart_tags]

    def _filenamepart_ts(self):
        ts = FILENAMEPART_TS_REGEX.match(self.fnbase)
        if ts:
            return ts.group(0)
        return None

    def _filenamepart_base(self):
        fnbase = self.fnbase
        if self._filenamepart_ts:
            fnbase = self.fnbase.lstrip(self._filenamepart_ts)

        if not re.findall(self.BETWEEN_TAG_SEPARATOR, fnbase):
            return fnbase

        # NOTE: Handle case with multiple "BETWEEN_TAG_SEPARATOR" better?
        r = re.split(self.FILENAME_TAG_SEPARATOR, fnbase, 1)
        return r[0].strip()

    def _filenamepart_ext(self):
        return self.suffix

    def _filenamepart_tags(self):
        if not re.findall(self.BETWEEN_TAG_SEPARATOR, self.fnbase):
            return None

        r = re.split(self.FILENAME_TAG_SEPARATOR, self.fnbase, 1)
        try:
            tags = r[1].split(self.BETWEEN_TAG_SEPARATOR)
            return tags
        except IndexError:
            return None

    # NOTE: Move "filetags"-specific code to separate module. (?)
    def filetags_format_filename(self):
        """
        Returns whether the file name is in the "filetags" format.

                                   .------------ FILENAME_TAG_SEPARATOR
                                  ||         .-- BETWEEN_TAG_SEPARATOR
                                  VV         V
        20160722 Descriptive name -- firsttag tagtwo.txt
        |______| |______________|    |_____________| |_|
           ts          base               tags       ext

        All filename parts; 'ts', 'base' and 'tags' must be present.

        Returns:
            True if the filename is in the "filetags" format.
            Otherwise False.
        """
        if (self._filenamepart_ts and self._filenamepart_base
                and self._filenamepart_tags):
            return True
        else:
            return False

    def __str__(self):
        # TODO: Handle file name encoding before returning.
        return str(self.filename)

    def __repr__(self):
        # TODO: Handle file name encoding before returning.
        return '<{} {}>'.format(self.__class__.__name__, str(self.abspath))


def filetype_magic(file_path):
    """
    Determine file type by reading "magic" header bytes.

    Should be equivalent to the 'file --mime-type' command in *NIX environments.

    Args:
        file_path: The path to the file to get the MIME type of as a string.

    Returns:
        The MIME type of the file at the given path ('application/pdf') or
        'constants.MAGIC_TYPE_UNKNOWN' if the MIME type can not be determined.
    """
    if not file_path:
        return constants.MAGIC_TYPE_UNKNOWN

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
            _my_magic = magic.open(magic.MAGIC_MIME_TYPE)
            _my_magic.load()
        except AttributeError:
            _my_magic = magic.Magic(mime=True)
            _my_magic.file = _my_magic.from_file
        return _my_magic

    magic_instance = _build_magic()
    try:
        found_type = magic_instance.file(file_path)
    except (magic.MagicException, TypeError):
        found_type = constants.MAGIC_TYPE_UNKNOWN

    return found_type


def validate_path_argument(path):
    """
    Validates a raw path option argument.

    Args:
        path: Path option argument as a string.

    Raises:
        InvalidFileArgumentError: The given path is not considered valid.
    """
    path = util.syspath(path)

    if not os.path.exists(path):
        raise InvalidFileArgumentError('Path does not exist')
    elif os.path.isdir(path):
        raise InvalidFileArgumentError('Safe handling of directories is '
                                       'not implemented yet')
    elif os.path.islink(path):
        raise InvalidFileArgumentError('Safe handling of symbolic links is '
                                       'not implemented yet')
    elif not os.access(path, os.R_OK):
        raise InvalidFileArgumentError('Not authorized to read path')


def eval_magic_glob(mime_to_match, glob_list):
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

    Args:
        mime_to_match: The MIME to match against the globs as a string.
        glob_list: A list of globs as strings.

    Returns:
        True if the given MIME type matches any of the specified globs.
    """
    if not mime_to_match or not glob_list:
        return False

    if not isinstance(glob_list, list):
        glob_list = [glob_list]

    mime_to_match_type, mime_to_match_subtype = mime_to_match.split('/')

    for glob in glob_list:
        if glob == mime_to_match:
            return True
        elif '*' in glob:
            try:
                glob_type, glob_subtype = glob.split('/')
            except ValueError:
                # NOTE(jonas): Raise exception? Use sophisticated glob parser?
                raise
            if glob_type == '*' and glob_subtype == '*':
                return True
            elif glob_type == '*' and glob_subtype == mime_to_match_subtype:
                return True
            elif glob_type == mime_to_match_type and glob_subtype == '*':
                return True
    return False
