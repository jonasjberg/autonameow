# -*- coding: utf-8 -*-
# This file is part of autonameow.
# Copyright 2016, Jonas Sjoberg.

import logging
import os
import re

from config_defaults import (
    FILENAME_TAG_SEPARATOR,
    BETWEEN_TAG_SEPARATOR
)
from util import diskutils


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

        # Do "filename partitioning" -- split the file name into three parts:
        #
        #   * filenamepart_base   Descriptive text.
        #   * filenamepart_ext    File extension/suffix.
        #   * filenamepart_tags   Tags created within the "filetags" workflow.
        #
        # Example basename '20160722 Descriptive name -- firsttag tagtwo.txt':
        #
        #    20160722 Descriptive name -- firsttag tagtwo.txt
        #    |_______________________|    |_____________| |_|
        #              base                    tags       ext
        #
        self.filenamepart_base = self._filenamepart_base()
        self.filenamepart_ext = self._filenamepart_ext()
        self.filenamepart_tags = self._filenamepart_tags() or []

    def _filenamepart_base(self):
        if not re.findall(BETWEEN_TAG_SEPARATOR, self.fnbase):
            return self.fnbase

        # NOTE: Handle case with multiple "BETWEEN_TAG_SEPARATOR" better?
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

