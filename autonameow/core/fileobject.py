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
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
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

from .config_defaults import (
    FILENAME_TAG_SEPARATOR,
    BETWEEN_TAG_SEPARATOR
)
from .util import diskutils

DATE_SEP = '[:\-._ ]?'
TIME_SEP = '[:\-._ T]?'
DATE_REGEX = '[12]\d{3}' + DATE_SEP + '[01]\d' + DATE_SEP + '[0123]\d'
TIME_REGEX = '[012]\d' + TIME_SEP + '[012345]\d' + TIME_SEP + '[012345]\d(.[012345]\d)?'
FILENAMEPART_TS_REGEX = re.compile(DATE_REGEX + '([T_ -]?' + TIME_REGEX + ')?')


class FileObject(object):
    def __init__(self, path):
        assert path is not None

        # Get full absolute path
        self.path = os.path.abspath(path)
        logging.debug('FileObject path: {}'.format(self.path))

        self.filename = os.path.basename(self.path)

        # Extract parts of the file name.
        self.fnbase = diskutils.file_base(self.path)
        self.suffix = diskutils.file_suffix(self.path)

        # Figure out basic file type
        self.type = diskutils.filetype_magic(self.path)

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

        if not re.findall(BETWEEN_TAG_SEPARATOR, fnbase):
            return fnbase

        # NOTE: Handle case with multiple "BETWEEN_TAG_SEPARATOR" better?
        r = re.split(FILENAME_TAG_SEPARATOR, fnbase, 1)
        return str(r[0].strip())

    def _filenamepart_ext(self):
        return self.suffix

    def _filenamepart_tags(self):
        if not re.findall(BETWEEN_TAG_SEPARATOR, self.fnbase):
            return None

        r = re.split(FILENAME_TAG_SEPARATOR, self.fnbase, 1)
        try:
            tags = r[1].split(BETWEEN_TAG_SEPARATOR)
            return tags
        except IndexError:
            return None

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
        if self.filenamepart_ts and self.filenamepart_base and \
               self.filenamepart_tags:
            return True
        else:
            return False
