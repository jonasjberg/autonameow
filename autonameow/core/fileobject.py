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
import re

import magic

from core.config.constants import (
    MAGIC_TYPE_LOOKUP,
    FILETAGS_DEFAULT_BETWEEN_TAG_SEPARATOR,
    FILETAGS_DEFAULT_FILENAME_TAG_SEPARATOR
)
from core.exceptions import InvalidFileArgumentError
from .util import diskutils

DATE_SEP = '[:\-._ ]?'
TIME_SEP = '[:\-._ T]?'
DATE_REGEX = '[12]\d{3}' + DATE_SEP + '[01]\d' + DATE_SEP + '[0123]\d'
TIME_REGEX = '[012]\d' + TIME_SEP + '[012345]\d' + TIME_SEP + '[012345]\d(.[012345]\d)?'
FILENAMEPART_TS_REGEX = re.compile(DATE_REGEX + '([T_ -]?' + TIME_REGEX + ')?')


class FileObject(object):
    def __init__(self, path, opts):
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

        self.abspath = os.path.abspath(path)
        logging.debug('FileObject path: {}'.format(self.abspath))
        self.filename = os.path.basename(self.abspath)

        self.mime_type = filetype_magic(self.abspath)

        # Extract parts of the file name.
        self.fnbase = diskutils.file_base(self.abspath)
        self.suffix = diskutils.file_suffix(self.abspath)

        self.BETWEEN_TAG_SEPARATOR = opts.options['FILETAGS_OPTIONS'].get('between_tag_separator')
        self.FILENAME_TAG_SEPARATOR = opts.options['FILETAGS_OPTIONS'].get('filename_tag_separator')


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
        self.filenamepart_ts = self._filenamepart_ts()
        self.filenamepart_base = self._filenamepart_base()
        self.filenamepart_ext = self._filenamepart_ext()
        self.filenamepart_tags = self._filenamepart_tags() or []

    def _filenamepart_ts(self):
        ts = FILENAMEPART_TS_REGEX.match(self.fnbase)
        if ts:
            return ts.group(0)
        return None

    def _filenamepart_base(self):
        fnbase = self.fnbase
        if self.filenamepart_ts:
            fnbase = self.fnbase.lstrip(self.filenamepart_ts)

        if not re.findall(self.BETWEEN_TAG_SEPARATOR, fnbase):
            return fnbase

        # NOTE: Handle case with multiple "BETWEEN_TAG_SEPARATOR" better?
        r = re.split(self.FILENAME_TAG_SEPARATOR, fnbase, 1)
        return str(r[0].strip())

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

    # TODO: Move "filetags"-specific code to separate module. (?)
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
        if (self.filenamepart_ts and self.filenamepart_base
                and self.filenamepart_tags):
            return True
        else:
            return False


def filetype_magic(file_path):
    """
    Determine file type by reading "magic" header bytes.
    Uses a wrapper around the 'file' command in *NIX environments.
    :return: the file type if the magic can be determined and mapped to one of
             the keys in "MAGIC_TYPE_LOOKUP", else None.
    """
    def _build_magic():
        """
        Workaround confusion around which magic library actually gets used.

        https://github.com/ahupp/python-magic
          "There are, sadly, two libraries which use the module name magic.
           Both have been around for quite a while.If you are using this
           module and get an error using a method like open, your code is
           expecting the other one."

        http://www.zak.co.il/tddpirate/2013/03/03/the-python-module-for-file-type-identification-called-magic-is-not-standardized/
          "The following code allows the rest of the script to work the same
           way with either version of 'magic'"
        """
        try:
            _mymagic = magic.open(magic.MAGIC_MIME_TYPE)
            _mymagic.load()
        except AttributeError:
            _mymagic = magic.Magic(mime=True)
            _mymagic.file = _mymagic.from_file
        return _mymagic

    mymagic = _build_magic()
    try:
        mtype = mymagic.file(file_path)
    except Exception:
        return None

    # http://stackoverflow.com/a/16588375
    def find_key(input_dict, value):
        return next((k for k, v in list(input_dict.items()) if v == value), None)

    try:
        found_type = find_key(MAGIC_TYPE_LOOKUP, mtype.split()[:2])
    except KeyError:
        return None

    return found_type.lower() if found_type else None