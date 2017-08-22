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

import logging as log
import re

from analyzers import BaseAnalyzer

from core import (
    util,
    types,
    exceptions
)
from core.util import diskutils

# TODO: [TD0037][TD0043] Allow further customizing of "filetags" options.

DATE_SEP = b'[:\-._ ]?'
TIME_SEP = b'[:\-._ T]?'
DATE_REGEX = b'[12]\d{3}' + DATE_SEP + b'[01]\d' + DATE_SEP + b'[0123]\d'
TIME_REGEX = (b'[012]\d' + TIME_SEP + b'[012345]\d' + TIME_SEP
              + b'[012345]\d(.[012345]\d)?')
FILENAMEPART_TS_REGEX = re.compile(
    DATE_REGEX + b'([T_ -]?' + TIME_REGEX + b')?')


# TODO: [TD0043][TD0009] Fetch values from the active configuration.
# BETWEEN_TAG_SEPARATOR = util.bytestring_path(
#     opts.options['FILETAGS_OPTIONS'].get('between_tag_separator')
# )
BETWEEN_TAG_SEPARATOR = util.bytestring_path(' ')
# FILENAME_TAG_SEPARATOR = util.bytestring_path(
#     opts.options['FILETAGS_OPTIONS'].get('filename_tag_separator')
# )
FILENAME_TAG_SEPARATOR = util.bytestring_path(' -- ')


class FiletagsAnalyzer(BaseAnalyzer):
    run_queue_priority = 1
    handles_mime_types = ['*/*']
    meowuri_root = 'analysis.filetags'

    def __init__(self, file_object, add_results_callback,
                 request_data_callback):
        super(FiletagsAnalyzer, self).__init__(
            file_object, add_results_callback, request_data_callback
        )

        self._timestamp = None
        self._description = None
        self._tags = None
        self._extension = None

    def _add_results(self, meowuri_leaf, data):
        if data is None:
            return

        meowuri = '{}.{}'.format(self.meowuri_root, meowuri_leaf)
        log.debug(
            '{!s} passing "{}" to "add_results" callback'.format(self, meowuri)
        )
        self.add_results(meowuri, data)

    def run(self):
        (self._timestamp, self._description, self._tags,
         self._extension) = partition_basename(self.file_object.abspath)

        try:
            self._add_results('datetime', types.AW_TIMEDATE(self._timestamp))
        except exceptions.AWTypeError as e:
            pass
        try:
            self._add_results('description', types.AW_STRING(self._description))
        except exceptions.AWTypeError as e:
            pass

        self._add_results('tags', sorted(self._tags))
        self._add_results('extension', self._extension)
        self._add_results('follows_filetags_convention',
                          self.follows_filetags_convention())

    def follows_filetags_convention(self):
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
        if self._timestamp and self._description and self._tags:
            return True
        else:
            return False

    @classmethod
    def can_handle(cls, file_object):
        # Assume 'FileObject' has a path and a basename.
        return True


def partition_basename(file_path):
    """
    Splits a basename into parts as per the "filetags" naming convention.

    Does "filename partitioning" -- split the file name into four parts:

    * timestamp     Date-/timestamp.
    * description   Descriptive text.
    * tags          List of tags created within the "filetags" workflow.
    * extension     File extension (really the "compound suffix").

    Example basename '20160722 Descriptive name -- firsttag tagtwo.txt':

                                    .------------ FILENAME_TAG_SEPARATOR
                                   ||         .-- BETWEEN_TAG_SEPARATOR
                                   VV         V
         20160722 Descriptive name -- firsttag tagtwo.txt
         |______| |______________|    |_____________| |_|
        timestamp   description            tags       ext

    Args:
        file_path: Path whose basename to split, as an "internal bytestring".
    Returns:
        Any identified parts as a tuple of 4 elements (quad);
            'timestamp', 'description', 'tags', 'extension', where 'tags' is a
            list of Unicode strings, and the others are plain Unicode strings.
    """
    prefix, suffix = diskutils.split_basename(file_path)

    timestamp = FILENAMEPART_TS_REGEX.match(prefix)
    if timestamp:
        timestamp = timestamp.group(0)
        prefix = prefix.lstrip(timestamp)

    if not re.findall(FILENAME_TAG_SEPARATOR, prefix):
        if prefix:
            description = prefix.strip()
        else:
            description = None
        tags = []
    else:
        # NOTE: Handle case with multiple "BETWEEN_TAG_SEPARATOR" better?
        r = re.split(FILENAME_TAG_SEPARATOR, prefix, 1)
        description = r[0].strip()
        try:
            tags = r[1].split(BETWEEN_TAG_SEPARATOR)
        except IndexError:
            tags = []

    # Encoding boundary;  Internal filename bytestring --> internal Unicode str
    def decode_if_not_none_or_empty(bytestring_maybe):
        if bytestring_maybe:
            return util.decode_(bytestring_maybe)
        else:
            return None

    timestamp = decode_if_not_none_or_empty(timestamp)
    description = decode_if_not_none_or_empty(description)
    tags = [decode_if_not_none_or_empty(t) for t in tags]
    suffix = decode_if_not_none_or_empty(suffix)

    return timestamp, description, tags or [], suffix
