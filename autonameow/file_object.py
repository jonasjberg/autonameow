# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import datetime
import logging
import magic
import os

import re

from util import diskutils

from config_defaults import (
    FILENAME_TAG_SEPARATOR,
    BETWEEN_TAG_SEPARATOR
)


class FileObject(object):
    def __init__(self, path):
        assert path is not None

        # Get full absolute path
        self.path = os.path.abspath(path)
        logging.debug('FileObject path: {}'.format(self.path))

        # Extract parts of the file name.
        self.fnbase = diskutils.file_base(self.path)
        self.suffix = diskutils.file_suffix(self.path)

        # Figure out basic file type
        self.type = diskutils.filetype_magic(self.path)

        self.filenamepart_base = self._filenamepart_base()
        self.filenamepart_ext = self._filenamepart_ext()
        self.filenamepart_tags = self._filenamepart_tags() or []

    def _filenamepart_base(self):
        if not re.findall(BETWEEN_TAG_SEPARATOR, self.fnbase):
            return self.fnbase

        r = re.split(FILENAME_TAG_SEPARATOR + '?', self.fnbase)
        return r[0]

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

