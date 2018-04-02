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

import re
from collections import namedtuple

from extractors import BaseExtractor
from util import encoding as enc
from util import (
    disk,
    sanity
)


# TODO: [TD0043] Fetch values from the active configuration.
# BETWEEN_TAG_SEPARATOR = enc.bytestring_path(
#     opts.options['FILETAGS_OPTIONS'].get('between_tag_separator')
# )
BETWEEN_TAG_SEPARATOR = enc.bytestring_path(' ')
# FILENAME_TAG_SEPARATOR = enc.bytestring_path(
#     opts.options['FILETAGS_OPTIONS'].get('filename_tag_separator')
# )
FILENAME_TAG_SEPARATOR = enc.bytestring_path(' -- ')


FiletagsParts = namedtuple('FiletagsParts',
                           'datetime description tags extension')


class FiletagsExtractor(BaseExtractor):
    HANDLES_MIME_TYPES = ['*/*']
    IS_SLOW = False

    def __init__(self):
        super().__init__()

    def extract(self, fileobject, **kwargs):
        return self._get_metadata(fileobject.filename)

    def _get_metadata(self, file_basename):
        metadata = self._partition_filename(file_basename)

        if 'tags' in metadata:
            # NOTE(jonas): Assume that consistent output by sorting outweigh
            #              users that would like to keep the order unchanged ..
            metadata['tags'].sort()

        return metadata

    def _partition_filename(self, filename):
        parts = partition_basename(filename)
        follows_convention = follows_filetags_convention(parts)

        parts_dict = dict(parts._asdict())
        parts_dict['follows_filetags_convention'] = follows_convention
        result = self._to_internal_format(parts_dict)
        return result

    def _to_internal_format(self, raw_metadata):
        coerced_metadata = dict()

        for field, value in raw_metadata.items():
            if value is None:
                # Value of field "timestamp" is None if missing.
                continue

            coerced = self.coerce_field_value(field, value)
            if coerced is not None:
                coerced_metadata[field] = coerced

        return coerced_metadata

    @classmethod
    def can_handle(cls, fileobject):
        # File name should not be empty or only whitespace.
        return bool(fileobject.filename.strip())

    @classmethod
    def check_dependencies(cls):
        return True


# TODO: [TD0037] Allow further customizing of "filetags" options.
# TODO: [TD0043] Allow further customizing of "filetags" options.

DATE_SEP = rb'[:\-._ ]?'
TIME_SEP = rb'[:\-._ T]?'
DATE_REGEX = rb'[12]\d{3}' + DATE_SEP + rb'[01]\d' + DATE_SEP + rb'[0123]\d'
TIME_REGEX = (rb'[012]\d' + TIME_SEP + rb'[012345]\d' + TIME_SEP
              + rb'[012345]\d(.[012345]\d)?')
FILENAMEPART_TS_REGEX = re.compile(
    DATE_REGEX + rb'([T_ -]?' + TIME_REGEX + rb')?'
)


def partition_basename(filepath):
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
        filepath: Path whose basename to split, as an "internal bytestring".
    Returns:
        Any identified parts as a tuple of 4 elements (quad);
            'timestamp', 'description', 'tags', 'extension', where 'tags' is a
            list of Unicode strings, and the others are plain Unicode strings.
    """
    sanity.check_internal_bytestring(FILENAME_TAG_SEPARATOR)

    prefix, suffix = disk.split_basename(filepath)

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
        prefix_tags_list = re.split(FILENAME_TAG_SEPARATOR, prefix, 1)
        description = prefix_tags_list[0].strip()
        try:
            tags = prefix_tags_list[1].split(BETWEEN_TAG_SEPARATOR)
        except IndexError:
            tags = []
        else:
            tags = [t.strip() for t in tags if t]

    # Encoding boundary;  Internal filename bytestring --> internal Unicode str
    def _decode_bytestring(bytestring_maybe):
        if bytestring_maybe:
            return enc.decode_(bytestring_maybe)
        return ''

    if timestamp:
        # Set timestamp to None instead of empty string here so that it can be
        # detected and skipped when converting values to the "internal format".
        # Coercing None with 'AW_TIMEDATE' raises a 'AWTypeError' exception,
        # which would happen for every file that do not have a "timestamp"
        # filetags part.
        timestamp = _decode_bytestring(timestamp)
    else:
        timestamp = None

    description = _decode_bytestring(description)
    tags = [_decode_bytestring(t) for t in tags]
    suffix = _decode_bytestring(suffix)

    return FiletagsParts(timestamp, description, tags, suffix)


def follows_filetags_convention(filetags_parts):
    """
    Check if given parts indicate that a filename is in "filetags format".

                                 .------------ FILENAME_TAG_SEPARATOR
                                ||         .-- BETWEEN_TAG_SEPARATOR
                                VV         V
      20160722 Descriptive name -- firsttag tagtwo.txt
      |______| |______________|    |_____________| |_|
        date     description            tags       ext

    Filename parts 'date', 'description' and 'tags' must be present.

    Returns:
        True if the parts probably came from a file name in the "filetags"
        format. Otherwise False.
    """
    return bool(
        filetags_parts.datetime and filetags_parts.description
        and filetags_parts.tags
    )
